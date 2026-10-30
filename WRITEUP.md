# Write-up: AI Proposal Triage Design (MATACS-TH-2026-02)

**Flow:** upload → read text → **AI extracts facts** → rules check mandatory criteria → **code scores** → **AI words the reason** → reviewer checks → human awards. See `diagram/flow.png`; `python prototype/score.py` reproduces the sample ranking.

## 1. AI vs. rules

| Step | Who does it | Why |
|---|---|---|
| Upload, PDF-to-text, file checks | Code | Fixed and testable. Scanned PDFs with no text go to manual entry. |
| Load admin criteria for the category | Code | Criteria live in the database, never in prompts or code. |
| Pull facts out of each proposal (licence, installs, price, weeks, warranties, team items) | **AI** | Proposals are free text and worded differently. Reading them is the one job rules do badly. |
| Mandatory pass/fail | Code | A yes/no on extracted facts. Must be exact and defensible. |
| Weighted scoring and ranking | Code | Arithmetic must be identical every time and explainable. An AI "feeling" for a score is not. |
| One-line reason | **AI** (optional) | Turns numbers into readable text, but cannot change them. |
| Final decision | Human | Awarding a contract is a business and legal call. |

The line is: **AI reads, code decides.** AI only converts messy text into structured facts, each with a quote. Everything after that is rules.

## 2. Consistency and explainability

- Extraction runs at temperature 0 with a fixed prompt version, and the result is **saved**. Re-ranking reads the saved facts, so the same proposals give the same ranking. Only a re-upload or prompt change re-runs the AI, and that is logged.
- Scoring formulas are fixed and shown to the reviewer: experience = installs ÷ 12 (capped); price and timeline = best eligible bid ÷ this bid; warranty = half panel, half workmanship; team = four items at 25 each. Ties go to the lower price, then the earlier upload.
- Each rank has a "why" panel: the quoted evidence, the facts, the score per criterion, weight and formula, and a side-by-side view against the proposal above it. For the samples: A scores 96.8 and E 86.2, because E has 8 qualifying installs versus 14 (experience 66.7 vs 100) even though E has the better warranty.

## 3. Human in the loop

Reviewer checkpoints:
1. **Extraction check:** every extracted fact is shown beside its quote; the reviewer can correct it. Facts from low-quality PDFs or with no quote are highlighted.
2. **Flag queue:** proposals that are *flagged* (missing data, ambiguous mandatory item, suspicious text) are not ranked until a person resolves them: ask the bidder, edit the fact, accept or exclude.
3. **Ineligible list:** a person can confirm or reverse each exclusion with a written reason.
4. **Rank override:** the reviewer may move a proposal or change a score with a required comment. The original system result stays visible.
5. **Award:** a person picks the winner. The tool only recommends.

Audit log (append-only): who uploaded what (file hash), prompt version and model, raw AI output, extracted facts, criteria version and weights used, every score, every human edit/override with user, time and reason, and the final decision.

## 4. Changing criteria

- Criteria are **versioned**. Each score records its version; an edit makes a new version and never rewrites old results.
- Because facts are saved and scoring is code, a weight change needs **no AI call**: re-score instantly from stored facts. A new or reworded criterion needs only a new extraction field for that criterion.
- The reviewer sees "scored under v1; v2 is available" and can re-score the batch. Mixed versions are never ranked together.
- Changing rules after seeing results is a fairness risk, so edits after scoring need a logged admin reason and show a before/after rank comparison.

## 5. Risks and safeguards

| Risk | Safeguard |
|---|---|
| **Wrong extraction** | Verbatim quote required for each fact; schema validation; reviewer sees quote next to the value; unknowns are `null`. A test set of known proposals is re-run whenever the prompt changes. |
| **Made-up facts** | "Only what is stated, else null" rule; quote must be found in the source text by code (string match), otherwise the fact is dropped and flagged. |
| **Instructions hidden in a proposal** (sample C contains a line telling reviewers to rank it first) | Proposal text is wrapped as untrusted data; the prompt says never to obey it; the AI has no power to score or rank, so it cannot be talked into a result. A code check also scans for instruction-like phrases. Matches flag the proposal for a person. In the samples C is flagged and the instruction ignored. |
| **Vague answers inflating a score** (B: the licensed electrician is not yet named; D: no schedule yet) | Vague means not stated. B fails the mandatory licence check. D gets 0 on timeline provisionally, is flagged and shown with its score so the reviewer can request a schedule. If D's schedule is 13 weeks or less it edges past E, so it is flagged, not buried. |
| **Date ambiguity** (C: installs dated from 2020 vs a 5-year window) | Flagged with a note that the count may be too high. |
| **Bias** | Only the admin criteria are scored (not names, locations or writing style), with the same formulas for everyone, and the reasoning is visible. |
| **Manipulation of criteria or scores** | Versioned criteria, role-based access (admin edits criteria, reviewer cannot), append-only log. |
| **Cost and data** | One short call per proposal, cached by file hash, so re-ranking is free. Use a vendor under a no-training contract. |
| **Over-trust** | Output is labelled a recommendation; flagged and ineligible items show on the first screen; a person confirms before export. |

## Assumptions

- "Last 5 years" counts from the review date.
- Missing information on a weighted criterion scores 0 and flags the proposal; a bidder saying it does not meet a mandatory item makes it ineligible, and silence flags it.
- Full marks at 12 installs and at 15 years' workmanship are my choices, kept as admin settings.
- Flagged proposals get a provisional score but no rank until reviewed.

# MATACS-TH-2026-02: AI Proposal Triage Design

- **Name:** Hashir Ashraf
- **Reference:** MATACS-TH-2026-02
- **Time actually spent:** [FILL IN: hours/minutes]

## Files

| File | What it is |
|---|---|
| [WRITEUP.md](WRITEUP.md) | Answers to the five questions (under 1,000 words) |
| [diagram/flow.png](diagram/flow.png) | Process flow from upload to ranked output, marking AI, rule and human steps |
| [PROMPTS.md](PROMPTS.md) | The two prompts (extraction, reason writer), exactly as sent |
| [ranking.json](ranking.json) | Expected ranking of proposals A–E |
| [prototype/](prototype/) | Optional: scoring script, criteria and extracted facts |

## Result in short

A is ranked 1st and E 2nd. B is ineligible (electrical work subcontracted, licence not confirmed). C and D are flagged for a person to review: C contains text trying to instruct the reviewer (ignored) and an experience count that may be out of the 5-year window; D gives no completion time. Both still get a provisional score (C 80.9, D 72.5).

## Run the prototype

```
python prototype/score.py
```

This needs only Python 3. It scores the saved extracted facts with the admin criteria and prints the result, which matches `ranking.json`. `prototype/extract.py` runs the extraction prompt through the Anthropic API on proposal text files you keep locally; it has **not** been run against the live API, and no proposal text is included in this repo. Copy `prototype/.env.example` to `.env` and add your own key.

## How I used AI tools

I used Claude Code (Anthropic) to draft the write-up, prompts, flow diagram, ranking and the scoring script, working from the assessment brief, and I reviewed the output before submitting. The design choices to check and own are: AI only extracts facts, code does all scoring, and people review flagged and ineligible proposals.

**Where the AI's output was corrected:** the first draft of the write-up was over the 1,000-word limit and quoted short phrases from the sample proposals, which the brief says not to copy; it was cut to about 950 words and the phrases were reworded. The first draft of the flow diagram also had a label overlapping a box, which was fixed. On the design itself, the AI's first scoring pass was checked by hand against the script output (A 96.8, E 86.2, C 80.9, D 72.5) before the ranking was written.

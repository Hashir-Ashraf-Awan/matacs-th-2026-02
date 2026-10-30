"""Deterministic scoring step. Takes extracted facts + admin criteria, returns scores.

No AI runs here: the same inputs always give the same numbers.
Usage: python score.py [criteria.json] [extractions.json]
"""
import json
import sys
from pathlib import Path

here = Path(__file__).parent
criteria = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else here / "criteria.json").read_text())
extractions = json.loads(Path(sys.argv[2] if len(sys.argv) > 2 else here / "extractions.json").read_text())
extractions = {k: v for k, v in extractions.items() if not k.startswith("_")}
W = {c["id"]: c for c in criteria["weighted"]}


def gate(p):
    """Mandatory pass/fail. Returns (status, notes): ineligible / needs_review / pass."""
    if p["licence"] == "not_held":
        return "ineligible", ["licence not held by bidder"]
    notes = []
    if p["licence"] != "held":
        notes.append("licence unclear")
    if not (p["wsib"] and p["liability_5m"]):
        return "ineligible", ["WSIB or $5M insurance not confirmed"]
    return ("needs_review" if notes else "pass"), notes


def main():
    gates = {k: gate(v) for k, v in extractions.items()}
    pool = [k for k, (s, _) in gates.items() if s != "ineligible"]
    best_price = min(extractions[k]["price_cad"] for k in pool)
    weeks = [extractions[k]["timeline_weeks"] for k in pool if extractions[k]["timeline_weeks"]]
    best_weeks = min(weeks)

    results = {}
    for k, (status, notes) in gates.items():
        if status == "ineligible":
            results[k] = {"status": "ineligible", "score": None, "notes": notes}
            continue
        p = extractions[k]
        flags = list(notes)
        flags += p["integrity_flags"]
        crit = {}
        crit["experience"] = 100 * min(p["installs_100kw_plus"], W["experience"]["full_marks_at_installs"]) / W["experience"]["full_marks_at_installs"]
        if p["installs_in_window_uncertain"]:
            flags.append("experience count may include installs outside the 5-year window")
        crit["price"] = 100 * best_price / p["price_cad"] if p["price_cad"] <= criteria["budget_ceiling_cad"] else 0
        if p["timeline_weeks"] and p["timeline_weeks"] <= criteria["max_weeks"]:
            crit["timeline"] = 100 * best_weeks / p["timeline_weeks"]
        else:
            crit["timeline"] = 0
            flags.append("timeline missing or over limit: scored 0")
        w = W["warranty"]
        crit["warranty"] = 50 * min(p["panel_warranty_years"] / w["panel_full_years"], 1) + 50 * min(p["workmanship_warranty_years"] / w["workmanship_full_years"], 1)
        crit["team"] = 25 * sum(p["team"].values())
        total = sum(crit[c] * W[c]["weight"] / 100 for c in crit)
        results[k] = {
            "status": "flagged" if flags else "ranked",
            "score": round(total, 1),
            "criteria": {c: round(v, 1) for c, v in crit.items()},
            "notes": flags,
        }

    ranked = sorted((k for k, r in results.items() if r["status"] == "ranked"), key=lambda k: -results[k]["score"])
    for i, k in enumerate(ranked, 1):
        results[k]["rank"] = i
    for k in results:
        results[k].setdefault("rank", None)
    print(json.dumps(results, indent=2))


main()

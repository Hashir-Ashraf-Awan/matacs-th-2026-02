"""Optional: run the extraction prompt on proposal text files you keep locally.

NOT run against the live API in this repo (no key was used). Proposal text is never
committed; put your own .txt files in prototype/proposals_local/ (git-ignored).
Usage: python extract.py   (needs ANTHROPIC_API_KEY and ANTHROPIC_MODEL, see .env.example)
"""
import json
import os
from pathlib import Path

import anthropic  # pip install anthropic

here = Path(__file__).parent
prompt_template = (here / "extraction_prompt.txt").read_text()
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
model = os.environ["ANTHROPIC_MODEL"]

out = {}
for f in sorted((here / "proposals_local").glob("*.txt")):
    prompt = prompt_template.replace("{{PROPOSAL_TEXT}}", f.read_text())
    msg = client.messages.create(model=model, max_tokens=1500, temperature=0,
                                 messages=[{"role": "user", "content": prompt}])
    out[f.stem.upper()] = json.loads(msg.content[0].text)  # a bad reply raises: send to human review

(here / "extractions.generated.json").write_text(json.dumps(out, indent=2))
print("wrote extractions.generated.json; run: python score.py criteria.json extractions.generated.json")

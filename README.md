# Queens College Advising FAQ Assistant

A small web tool that answers common student advising questions — registration
deadlines, dropping a class, Pass/No Credit, Writing-Intensive courses, Pathways,
and billing — using [Claude](https://www.anthropic.com/) grounded in the Queens
College Academic Advising Center's published Summer/Fall 2026 information.

I built this because I work at the QC Advising Center, where the same handful of
questions come up dozens of times during registration. The idea: give students
instant, accurate answers to the routine questions so staff time goes to the
cases that actually need a person.

> **Note on data & scope.** This repo uses *publicly available* QC advising
> information (academic calendar, P/NC policy, Pathways offerings, bursar dates)
> as a demo knowledge base. It contains no student data and is not an official QC
> service. Dates change every semester — the tool tells every user to verify
> against official QC sources.

## How it works

1. A student types a question on the web page.
2. The Flask server sends Claude the **knowledge base** (`knowledge.md`) plus the
   question, with strict instructions to answer **only** from that knowledge base
   and to defer to a human advisor when the answer isn't there.
3. The answer is returned and displayed.

The "answer only from the provided information, otherwise say you don't know"
pattern is what keeps the tool from inventing deadlines — the single most
important design choice here.

```
index.html      → the web page students use
app.py          → the server; sends questions to Claude with the rules
knowledge.md    → the advising information Claude is allowed to use (edit this!)
requirements.txt
.gitignore      → keeps your API key out of git
```

## Run it locally

You'll need Python 3.9+ and an Anthropic API key (from https://console.anthropic.com).

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key (do NOT paste it into any file)
#    macOS / Linux:
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
#    Windows (PowerShell):
#    $env:ANTHROPIC_API_KEY="sk-ant-your-key-here"

# 3. Start the server
python app.py
```

Then open http://127.0.0.1:5000 in your browser and ask a question.

Cost is pay-per-use and tiny — it uses Claude Haiku, so each answer costs a
fraction of a cent. There is no subscription; idle costs nothing.

## Updating the knowledge base

All the advising content lives in `knowledge.md`. To update for a new semester or
add a topic, just edit that file in plain Markdown and restart the server — no
code changes needed. This was deliberate: a non-technical advisor should be able
to maintain the content.

## What I'd do differently / next steps

- **Source links per answer.** Right now answers cite dates inline; ideally each
  answer would link to the exact official QC page it came from, so students can
  verify in one click.
- **Logging the questions asked** (anonymously) would show which topics to expand
  in the knowledge base — turning real usage into a better tool over time.
- **A "was this helpful?" control** to catch wrong or confusing answers.
- **Handoff to a human** — a clear path to book an advising appointment when the
  tool can't help, rather than a dead end.
- **Evaluation harness.** Before trusting this with real students, I'd write a set
  of known question/answer pairs and automatically check the tool's answers
  against them whenever the knowledge base changes.

## Honest limitations

This is a prototype, not a deployed product. It hasn't been adopted by the
Advising Center, hasn't been load-tested, and its knowledge base is a snapshot.
It's a demonstration of how an LLM can be safely grounded in an organization's
own information to reduce repetitive workload — built end-to-end so I could learn
the pattern and talk about it honestly.

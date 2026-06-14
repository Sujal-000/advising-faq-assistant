"""
Queens College Advising FAQ Assistant
=====================================

A small web tool that answers student advising questions using Claude,
grounded ONLY in the knowledge base in knowledge.md. If the answer isn't
in the knowledge base, it says so and points the student to a human advisor.

How it works (plain English):
  1. The student types a question in the web page.
  2. The browser sends that question to this Python server.
  3. The server sends Claude two things: the knowledge base + the question,
     plus an instruction to answer ONLY from the knowledge base.
  4. Claude's answer is sent back and shown on the page.

Run it with:  python app.py
Then open the link it prints (usually http://127.0.0.1:5000) in your browser.
"""

import os
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
import anthropic

# ---------------------------------------------------------------------------
# 1. Load the knowledge base once when the program starts.
#    This is the only information Claude is allowed to answer from.
# ---------------------------------------------------------------------------
KNOWLEDGE = Path(__file__).parent.joinpath("knowledge.md").read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# 2. The "system prompt" is the standing instruction we give Claude every time.
#    This is where we enforce the rules that keep the tool trustworthy:
#    answer only from the knowledge base, and defer to a human when unsure.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = f"""You are a friendly, accurate FAQ assistant for the Queens College \
Academic Advising Center. You help students with questions about summer and fall \
registration, deadlines, Pass/No Credit, Writing-Intensive courses, Pathways/General \
Education, and bursar basics.

Follow these rules strictly:
- Answer ONLY using the Knowledge Base below. Do not use outside knowledge or guess.
- If the answer is not in the Knowledge Base, say you don't have that information and \
tell the student to contact an academic advisor or check the official QC website / CUNYfirst.
- Always remind students that dates and policies can change and to verify against \
official QC sources for anything time-sensitive or consequential.
- Never give a student definitive advice on decisions with academic or financial \
consequences (like whether to drop a class) — give the relevant facts and point them \
to an advisor for a personal recommendation.
- Be concise and clear. Use plain language. When you cite a date or rule, state it directly.

Knowledge Base:
---
{KNOWLEDGE}
---
"""

# ---------------------------------------------------------------------------
# 3. Set up the Claude client. It reads your API key from an environment
#    variable named ANTHROPIC_API_KEY (never hard-code your key here!).
# ---------------------------------------------------------------------------
client = anthropic.Anthropic()  # automatically reads ANTHROPIC_API_KEY

MODEL = "claude-haiku-4-5-20251001"  # fast + inexpensive; great for FAQ answers

app = Flask(__name__)


@app.route("/")
def home():
    """Serve the web page."""
    return send_from_directory(".", "index.html")


@app.route("/ask", methods=["POST"])
def ask():
    """Receive a question, ask Claude, return the answer."""
    question = (request.json or {}).get("question", "").strip()
    if not question:
        return jsonify({"answer": "Please type a question first."})

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=700,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": question}],
        )
        # Claude's reply comes back as a list of content blocks; we want the text.
        answer = "".join(block.text for block in response.content if block.type == "text")
        return jsonify({"answer": answer})
    except Exception as error:
        # If something goes wrong (e.g. no API key, no credit), tell the user plainly.
        print("Error talking to Claude:", error)
        return jsonify({
            "answer": "Sorry — I couldn't reach the assistant right now. "
                      "Please try again, or contact the Advising Center directly."
        }), 500


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n  WARNING: ANTHROPIC_API_KEY is not set.")
        print("  Set it first, then run again. See the README for how.\n")
    app.run(debug=True, port=5000)

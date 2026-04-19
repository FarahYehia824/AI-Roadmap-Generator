"""
generator.py
────────────
RetrievalResult  →  Build smart prompt  →  Call LLM  →  Structured Roadmap

Run standalone to test:
    python -m pipeline.generator
"""

import os
from dataclasses import dataclass, field
from groq import Groq
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from pipeline.retriever import Retriever, RetrievalResult

load_dotenv()
console = Console()

# ── Config ────────────────────────────────────────────────────────────────────
LLM_MODEL   = os.getenv("LLM_MODEL",   "gpt-4o-mini")
MAX_TOKENS  = int(os.getenv("MAX_TOKENS", 2000))
OPENAI_KEY  = os.getenv("OPENAI_API_KEY", "")


# ── Output dataclass ──────────────────────────────────────────────────────────
@dataclass
class RoadmapOutput:
    query    : str
    roadmap  : str          # final markdown text shown to user
    track    : str = ""
    level    : str = ""


DETECT_LEVEL_PROMPT = """\
You are an expert at understanding a learner's experience level from how they describe themselves.

Based on the user's message, determine their experience level.

Rules:
- If they mention "from scratch", "never coded", "complete beginner", "new to" → Beginner
- If they mention specific tools they know, "I know X and want to learn Y" → Intermediate  
- If they mention production, optimizing, scaling, or advanced concepts → Advanced
- If unclear → default to Beginner

Respond with ONLY one word: Beginner, Intermediate, or Advanced.
"""

def detect_level(query: str, client) -> str:
    """Auto-detect user level from their natural language input."""
    try:
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": DETECT_LEVEL_PROMPT},
                {"role": "user",   "content": query},
            ],
            max_tokens=10,
            temperature=0,
        )
        level = response.choices[0].message.content.strip()
        if level not in ["Beginner", "Intermediate", "Advanced"]:
            return "Beginner"
        return level
    except Exception:
        return "Beginner"
# ══════════════════════════════════════════════════════════════════════════════
# PROMPT BUILDER  ← the most important part
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """\
You are RoadmapRAG — an expert learning path designer with deep knowledge \
of software engineering, data science, cybersecurity, and mobile development.

Your job is to generate a clear, structured, personalized learning roadmap \
based on the user's goal and the knowledge base context provided.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULES YOU MUST FOLLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ONLY use skills, steps, and resources from the CONTEXT provided.
   Never invent skills or courses that are not in the context.

2. ORDER steps logically — prerequisites always come before advanced topics.

3. Every step MUST include:
   - A clear title
   - Why this step matters (1-2 sentences, motivating)
   - Estimated duration in weeks
   - A milestone — what the learner can build or do after this step
   - A resource in EXACTLY this format:
     📚 Resource: [Course Title] — [Platform] (free / free audit / paid)
     🔗 [full link]

4. CRITICAL RESOURCE RULE:
   - ONLY use resources that appear under "=== RECOMMENDED RESOURCES ===" in the context.
   - A valid resource looks like: "Title: Python for Everybody Specialization"
   - NEVER use a skill name as a resource (e.g. never write "SKILL: Python Programming")
   - NEVER use a roadmap step as a resource (e.g. never write "ROADMAP STEP: ...")
   - If no resource is found for a step, write: 📚 Resource: Search "[skill name] course" on Coursera or YouTube

5. Adapt the roadmap to the user's level:
   - Beginner    → start from scratch, more explanation, longer durations
   - Intermediate → skip basics, go deeper, shorter durations
   - Advanced     → focus on production-level and best practices

6. End with a "What's Next" section — 2-3 ideas to go deeper after finishing.

7. Tone: encouraging, direct, practical. No fluff.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT  (strict markdown)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🗺️ [Track Name] Roadmap
**Goal:** [restate the user's goal clearly]
**Level:** [Beginner / Intermediate / Advanced]
**Total Duration:** [X weeks]

---

## Step 1 — [Skill Title]
⏱ **Duration:** X weeks
🎯 **Why:** [why this step is essential, 1-2 sentences]
🏆 **Milestone:** [what they can build or do after this step]
📚 **Resource:** [Course Title] — [Platform] *(free / free audit / paid)*
🔗 [https://full-link-here]

---

## Step 2 — [Skill Title]
... (same format)

---

## 🚀 What's Next
After completing this roadmap, you can explore:
- ...
- ...
- ...
"""


def build_user_prompt(query: str, context: str, level: str = "Beginner") -> str:
    """
    Builds the user-facing part of the prompt.
    Combines the user's goal + their level + the retrieved context.
    """
    return f"""\
USER GOAL:
{query}

USER LEVEL: {level}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KNOWLEDGE BASE CONTEXT
(Use ONLY the information below to build the roadmap)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Now generate a complete, structured roadmap for the user's goal.
Follow the output format exactly. Be specific, practical, and encouraging.
"""


# ══════════════════════════════════════════════════════════════════════════════
# GENERATOR CLASS
# ══════════════════════════════════════════════════════════════════════════════

class Generator:
    """
    Takes a RetrievalResult and generates a structured roadmap using an LLM.
    Designed to be used after Retriever.retrieve().
    """

    def __init__(self):
        self.client = Groq(api_key=OPENAI_KEY)
        logger.success("Generator ready.")

    def generate(
        self,
        result      : RetrievalResult,
        level       : str = "Beginner",
        stream      : bool = True,
    ) -> RoadmapOutput:
        """
        Main entry point.

        Args:
            result : RetrievalResult from retriever.retrieve()
            level  : user's experience level
            stream : stream tokens to terminal (True) or return all at once

        Returns:
            RoadmapOutput with the final roadmap markdown
        """
        logger.info(f'Generating roadmap for: "{result.query}" | Level: {level}')

        # 1. Build context from retrieved chunks
        context = result.as_context_string()

        # 2. Build prompt
        user_prompt = build_user_prompt(result.query, context, level)

        # 3. Call LLM
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ]

        if stream:
            roadmap_text = self._stream(messages)
        else:
            roadmap_text = self._call(messages)

        logger.success("Roadmap generated.")

        return RoadmapOutput(
            query=result.query,
            roadmap=roadmap_text,
            level=level,
        )

    def _call(self, messages: list[dict]) -> str:
        """Single blocking call — returns full response at once."""
        response = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.4,      # low temp = consistent structured output
        )
        return response.choices[0].message.content

    def _stream(self, messages: list[dict]) -> str:
        """
        Streaming call — prints tokens as they arrive (great for UI feel).
        Returns the full text when done.
        """
        console.print("\n[bold yellow]Generating your roadmap...[/bold yellow]\n")

        full_text = ""
        stream = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.4,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            full_text += delta

        print("\n")
        return full_text


# ══════════════════════════════════════════════════════════════════════════════
# FULL PIPELINE  (Retriever → Generator in one call)
# ══════════════════════════════════════════════════════════════════════════════

class RoadmapPipeline:
    """
    Convenience wrapper that combines Retriever + Generator.
    This is what app/main.py (Streamlit) will import and use.

    Usage:
        pipeline = RoadmapPipeline()
        output   = pipeline.run("I want to learn Data Science", level="Beginner")
        print(output.roadmap)
    """

    def __init__(self):
        self.retriever  = Retriever()
        self.generator  = Generator()
        logger.success("RoadmapPipeline ready.")

    def run(
        self,
        query  : str,
        level  : str  = "Beginner",
        top_k  : int  = 5,
        stream : bool = True,
    ) -> RoadmapOutput:
        """
        Full pipeline:
            query → retrieve → generate → RoadmapOutput
        """
        # Step 1: Retrieve relevant chunks
        result = self.retriever.retrieve(query, top_k=top_k)

        # Step 2: Generate roadmap
        output = self.generator.generate(result, level=level, stream=stream)

        return output


# ── Main (standalone test) ────────────────────────────────────────────────────
def main():
    console.rule("[bold cyan]RoadmapRAG — Generator Test[/bold cyan]")

    if not OPENAI_KEY or OPENAI_KEY == "sk-your-key-here":
        console.print(
            "\n[bold red]❌  No OpenAI API key found![/bold red]\n"
            "Add your key to [cyan].env[/cyan]:\n"
            "  OPENAI_API_KEY=sk-...\n"
        )
        return

    pipeline = RoadmapPipeline()

    # Test query
    query = "I want to become a Data Scientist from scratch"
    level = "Beginner"

    console.print(f'\n[bold]Query:[/bold] {query}')
    console.print(f'[bold]Level:[/bold] {level}\n')

    output = pipeline.run(query=query, level=level, stream=True)

    # Show final rendered markdown
    console.rule("[bold green]✅ Final Roadmap[/bold green]")
    console.print(Markdown(output.roadmap))
    console.print(
        "\n[bold green]✅ Generator working correctly![/bold green]\n"
        "Next  →  [bold cyan]streamlit run app/main.py[/bold cyan]\n"
    )


if __name__ == "__main__":
    main()
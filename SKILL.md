---
name: book-to-skill
description: Converts a technical book PDF into a structured Claude Code skill with indexed chapters, core mental models, patterns, glossary, and cheatsheet. Use when the user wants to study a technical book through Claude, reference a book during work, or build a reusable knowledge base from any PDF.
when_to_use: Trigger phrases — "turn this book into a skill", "create a skill from this PDF", "I want to study X book", "add this book to my skills", "convert PDF to skill". Accepts a path to a PDF and optional skill name slug.
disable-model-invocation: true
context: fork
agent: general-purpose
allowed-tools: Bash(python3 *) Bash(pdftotext *) Bash(mkdir *) Bash(cp *) Bash(find *) Bash(wc *) Bash(echo *) Bash(cat *) Bash(date *) Read Write Glob Grep
argument-hint: <path-to-pdf> [skill-name-slug]
arguments: [pdf_path, skill_name]
effort: high
---

# Book-to-Skill Converter

Convert a technical book PDF into a well-structured Claude Code skill optimized for study and reference.

## Input
- `$0` — absolute or relative path to the PDF file
- `$1` — (optional) skill name slug, e.g. `designing-data-apps`. Derived from filename if omitted.

---

## Step 0 — Out-of-scope check

If the argument is NOT a path to a PDF, stop and respond:
> "book-to-skill requires a PDF path. Usage: `/book-to-skill /path/to/book.pdf [skill-name]`"

---

## Step 1 — Validate input

```bash
test -f "$0" && echo "FILE_OK" || echo "FILE_NOT_FOUND: $0"
file "$0" | grep -i pdf && echo "IS_PDF" || echo "NOT_PDF"
```

If the file is not found or not a PDF, stop with a clear error message.

---

## Step 2 — Extract text from PDF

Run the extraction script:

```bash
python3 ~/.claude/skills/book-to-skill/scripts/extract.py "$0"
```

This creates:
- `/tmp/book_skill_work/full_text.txt` — full extracted text
- `/tmp/book_skill_work/metadata.json` — title, estimated pages, token count, size

Read `/tmp/book_skill_work/metadata.json` to understand what was extracted.

---

## Step 3 — Analyze book structure

Read the first 8,000 characters of `/tmp/book_skill_work/full_text.txt` to identify:
- Book **title** and **author(s)**
- **Chapter structure** (look for "Chapter N", "PART I", numbered headings, table of contents)
- **Core themes** and subject domain
- Approximate number of chapters

Then read the Table of Contents section if present to map all chapters.

---

## Step 4 — Determine skill name

If `$1` was provided, use it as the skill slug.
Otherwise, derive from the book title: lowercase, hyphens, no special chars.
Example: "Designing Data-Intensive Applications" → `designing-data-intensive-apps`

Check that `~/.claude/skills/<skill_name>/` does NOT already exist.
If it does, append `-2` or ask the user before overwriting.

---

## Step 5 — Create skill directory structure

```bash
mkdir -p ~/.claude/skills/<skill_name>/chapters
```

---

## Step 6 — Generate chapter summaries

**TOKEN BUDGET RULE — CRITICAL:**
- Each chapter summary file: **800–1,200 tokens** (dense, not verbose)
- Files are loaded on-demand — they are NOT capped per se, but keep them useful and tight

For EACH chapter/major section identified in Step 3:

Read the corresponding section of `/tmp/book_skill_work/full_text.txt` (use character offsets or grep for chapter headings).

Create `~/.claude/skills/<skill_name>/chapters/ch<NN>-<slug>.md` with this structure:

```markdown
# Chapter N: <Full Title>

## Core Idea
<1–2 sentences: the single most important thing this chapter teaches>

## Key Concepts
- **<Term>**: <precise definition in 1 sentence>
- **<Term>**: <precise definition in 1 sentence>
(5–10 most important terms from this chapter)

## Mental Models
<2–4 frameworks or thinking tools introduced. Write as "Use X when Y" or "Think of X as Y">

## Patterns & Techniques
<Concrete approaches, algorithms, or methods. Numbered list. Action-oriented.>

## Key Takeaways
1. <Actionable insight>
2. <Actionable insight>
3. <Actionable insight>
(3–7 takeaways that a practitioner must remember)

## Connects To
- **Ch N**: <why this chapter relates>
- **<Concept>**: <external concept or standard it connects with>
```

---

## Step 7 — Generate supporting files

### glossary.md
Create `~/.claude/skills/<skill_name>/glossary.md`:
- Every significant term from the book, alphabetically sorted
- Format: `**Term** — definition (Ch N)`
- Max 1,500 tokens

### patterns.md
Create `~/.claude/skills/<skill_name>/patterns.md`:
- All concrete techniques, design patterns, algorithms from the book
- Format: `## Pattern Name\n**When to use**: ...\n**How**: ...\n**Trade-offs**: ...`
- Max 2,000 tokens

### cheatsheet.md
Create `~/.claude/skills/<skill_name>/cheatsheet.md`:
- Decision tables, comparison matrices, quick-reference rules
- The content you'd want on a single printed page
- Max 1,000 tokens

---

## Step 8 — Generate the master SKILL.md

**CRITICAL TOKEN BUDGET: Keep SKILL.md body under 4,000 tokens.**
Compaction truncates from the END — put the most important content FIRST.

Create `~/.claude/skills/<skill_name>/SKILL.md`:

```markdown
---
name: <skill_name>
description: Knowledge base from "<Full Title>" by <Author(s)>. Use when working with <key topics, 3–6 terms>. Covers <N> chapters on <brief scope sentence>.
when_to_use: <10–15 trigger phrases based on book topics and terms. Comma-separated.>
allowed-tools: Read Grep
argument-hint: [topic, chapter number, or concept]
---

# <Full Title>
**Author**: <Author(s)> | **Pages**: ~<N> | **Chapters**: <N> | **Generated**: <YYYY-MM-DD>

## How to Use This Skill

- **Without arguments** — `/skill-name` loads core mental models for reference
- **With a topic** — `/skill-name replication` → I find and read the relevant chapter
- **With chapter** — `/skill-name ch05` → I load that specific chapter
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not covered in Core Mental Models below, I will read
the relevant chapter file before answering.

---

## Core Mental Models
<!-- ~2,000 tokens: the 10–15 most important concepts from the ENTIRE book.
     Written as dense, actionable knowledge. Not summaries — practitioner insights.
     Use imperative: "Use X when Y", "Prefer X over Y because Z", "When X, always Y". -->

<generate 2,000 tokens of the most critical insights from the entire book here>

---

## Chapter Index

| # | Title | Key Topics |
|---|-------|------------|
| [ch01](chapters/ch01-<slug>.md) | <Title> | <topic1>, <topic2>, <topic3> |
| [ch02](chapters/ch02-<slug>.md) | <Title> | <topic1>, <topic2>, <topic3> |
...

## Topic Index

<!-- Alphabetical. Major terms → chapter(s) that cover them. -->
- **<Term>** → ch<N>[, ch<N>]
- **<Term>** → ch<N>

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the book content only. For hands-on implementation in your codebase,
combine with project-specific tools. For topics beyond this book, check related skills
or ask Claude directly.
```

---

## Step 9 — Cleanup and report

```bash
rm -rf /tmp/book_skill_work
```

Then report to the user:

```
✅ Skill created: ~/.claude/skills/<skill_name>/

📚 Book: <Full Title> — <Author>
📄 Pages: ~<N> | Chapters: <N>

Files generated:
  SKILL.md         — core concepts + index   (~X tokens)
  chapters/        — <N> chapter summaries   (~X tokens each)
  glossary.md      — key terms
  patterns.md      — techniques & patterns
  cheatsheet.md    — quick reference

Usage:
  /<skill_name>                    → load core mental models
  /<skill_name> <topic>            → find and explain a topic
  /<skill_name> ch<N>              → dive into a specific chapter
```

---

## Quality Rules

1. **Density over completeness** — a 1,000-token summary beats a 10,000-token excerpt
2. **Practitioner voice** — write "Use X when Y", not "The book explains X"
3. **Front-load SKILL.md** — compaction keeps the first 5,000 tokens; most important content comes first
4. **Chapter files are on-demand** — they don't count against skill budget until loaded
5. **Never copy raw book text** — always synthesize, summarize, extract signal
6. **Topic index is critical** — it's how Claude navigates to the right chapter file

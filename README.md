<h1 align="center">📚 book-to-skill</h1>

<p align="center">
  <strong>Turn any technical book PDF into a Claude Code skill — ready to study, reference, and use while you work.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=for-the-badge" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/effort-high-orange?style=for-the-badge" alt="Effort: high">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License">
</p>

<p align="center">
  <a href="#-why">Why</a> ·
  <a href="#-what-it-generates">What it generates</a> ·
  <a href="#-usage">Usage</a> ·
  <a href="#-requirements">Requirements</a> ·
  <a href="#-how-it-works">How it works</a> ·
  <a href="#-install">Install</a>
</p>

---

## 🤔 Why

You buy a great technical book. You read it once. Three months later you can't remember chapter 7 existed.

The usual workarounds don't help:
- 📄 "Let me just search the PDF" → you get a list of pages, not answers
- 🧠 "I'll ask Claude about this book" → it either hallucinates or says it doesn't have the content
- 📝 "I'll take notes as I read" → you end up with a 200-line doc you never open again

**book-to-skill solves this by turning the PDF into a structured skill Claude loads on demand.**

Once installed, you just type `/your-book-slug replication` and Claude reads the right chapter and answers from the actual content. No hallucination. No digging through PDFs. The book becomes part of your workflow.

---

## 📦 What it generates

Running `/book-to-skill your-book.pdf` creates a full skill at `~/.claude/skills/<slug>/`:

| File | Purpose | Size |
|------|---------|------|
| `SKILL.md` | Core mental models + chapter index | ~4,000 tokens |
| `chapters/ch01-*.md` … | One file per chapter, loaded on-demand | ~1,000 tokens each |
| `glossary.md` | Every key term, alphabetically sorted with chapter refs | ~1,500 tokens |
| `patterns.md` | All techniques, algorithms, and design patterns | ~2,000 tokens |
| `cheatsheet.md` | Decision tables and quick-reference rules | ~1,000 tokens |

**Chapter files are loaded on-demand** — they don't count against the skill budget until you ask about that topic.

---

## 🚀 Usage

```
/book-to-skill <path-to-pdf> [skill-name-slug]
```

**Examples:**

```bash
# Derive skill name from filename
/book-to-skill ~/Downloads/designing-data-intensive-applications.pdf

# Specify a custom slug
/book-to-skill ~/books/clean-code.pdf clean-code

# Full path with explicit name
/book-to-skill /tmp/ddd-evans.pdf domain-driven-design
```

After the skill is created, use it like any other Claude Code skill:

```bash
/designing-data-intensive-apps                  # load core mental models
/designing-data-intensive-apps replication      # find and explain a topic
/designing-data-intensive-apps ch05             # dive into chapter 5
/designing-data-intensive-apps "what chapters do you have?"
```

---

## 🔧 Requirements

At least one PDF extraction tool must be installed:

| Tool | Install | Quality |
|------|---------|---------|
| `pdftotext` (poppler) | `sudo apt install poppler-utils` | ⭐⭐⭐ Best layout fidelity |
| `PyPDF2` | `pip3 install PyPDF2` | ⭐⭐ Good |
| `pdfminer.six` | `pip3 install pdfminer.six` | ⭐⭐ Good fallback |

The extraction script tries them in order and uses the first available. If none is found, it tells you exactly which command to run.

---

## ⚙️ How it works

```
PDF
 │
 ▼
scripts/extract.py          ← tries pdftotext → PyPDF2 → pdfminer
 │
 ├── /tmp/book_skill_work/full_text.txt
 └── /tmp/book_skill_work/metadata.json
          │
          ▼
     Claude analyzes structure
     (title, author, chapters, ToC)
          │
          ▼
     Generates per-chapter summaries  (800–1,200 tokens each)
     Generates glossary, patterns, cheatsheet
     Generates master SKILL.md with core mental models
          │
          ▼
     ~/.claude/skills/<slug>/  ✅ written
     /tmp/book_skill_work/     🗑️  cleaned up
```

<details>
<summary>Design principles (click to expand)</summary>

1. **Density over completeness** — a 1,000-token summary beats a 10,000-token excerpt
2. **Practitioner voice** — "Use X when Y", not "The book explains X"
3. **Front-loaded SKILL.md** — compaction keeps the first ~5,000 tokens; the most important content comes first
4. **On-demand chapters** — the topic index tells Claude which file to read; chapters load only when needed
5. **Never raw text** — always synthesize, summarize, extract signal from the source

</details>

---

## 📥 Install

Copy this into your Claude Code session:

```
Install book-to-skill: https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/SKILL.md
```

Or manually:

```bash
mkdir -p ~/.claude/skills/book-to-skill/scripts

curl -o ~/.claude/skills/book-to-skill/SKILL.md \
  https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/SKILL.md

curl -o ~/.claude/skills/book-to-skill/scripts/extract.py \
  https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/scripts/extract.py
```

Then in any Claude Code session:

```bash
/book-to-skill ~/path/to/your-book.pdf
```

---

## 📁 Repository structure

```
book-to-skill/
├── SKILL.md              # Skill definition + step-by-step instructions
├── scripts/
│   └── extract.py        # PDF extraction (pdftotext / PyPDF2 / pdfminer)
└── README.md             # This file
```

---

## License

MIT

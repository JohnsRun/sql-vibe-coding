---
name: prompt-coach
description: Convert user statements into AI-ready prompts by translating Chinese to English, filtering noise, and structuring content in a clean, reusable format.
tags:
  - prompt
  - coaching
  - prompt-engineering
  - translation
  - ai-optimization
---

# Prompt Coach

Transform raw notes and statements into polished, AI-ready prompts. This skill helps you convert messy, conversational input into structured, actionable prompt content suitable for any AI model.

## When to Use This Skill

Use this skill when you need to:

- Convert rough notes or brainstorms into formal AI prompts
- Translate Chinese text to English for international AI usage
- Clean up conversational noise and extract core requirements
- Structure user intent into a standardized prompt format
- Prepare content for prompt engineering or model optimization

## How It Works

### Input Processing

The skill follows a systematic approach:

1. **Language Detection** – Identifies if input is Chinese, English, or mixed
2. **Translation** – Converts Chinese content to natural English (skipped if already English)
3. **Noise Removal** – Strips conversational filler, greetings, repetition, and irrelevant wording
4. **Structuring** – Reorganizes content into a clean, prompt-ready format

### Output Format

The final prompt is structured as:

```
Goal: One sentence describing the core objective.

Context: Key background information needed by the AI.

Requirements:
- Explicit requirement 1
- Explicit requirement 2
- ...

Constraints:
- Restriction or boundary 1
- Restriction or boundary 2
- ...

Output Expectations:
Describe the expected response format and tone in simple, concise language.
```

## Processing Rules

The skill applies these rules during conversion:

1. Always produce final output in English
2. Remove conversational filler, greetings, repetition, and language noise
3. Exclude off-topic or public-facing wording that doesn't affect the core request
4. Rewrite in a structured format suitable for direct AI use
5. Preserve user intent, constraints, and required output style
6. Omit introductions, self-introductions, process commentary, or explanatory preamble
7. Keep output under 150 words by default (expand only if input is substantially long)
8. Never invent requirements that weren't provided

## Quality Checklist

Before finalizing, ensure:

- ✓ All Chinese content has been translated to English
- ✓ Irrelevant conversational noise and language clutter removed
- ✓ No introductions or self-introductions in the output
- ✓ Result is simple, concise, specific, and actionable
- ✓ Final output stays within 150 words (unless input requires more)
- ✓ Prompt can be directly pasted into another AI chat without modification

## Example

**Input (Raw notes):**
```
嗨，我想要创建一个Python脚本来处理数据，
需要能够读取CSV文件，然后进行一些数据清洗，
还要输出成JSON。不过我希望代码注释要中英文对照。
```

**Output (Structured prompt):**
```
Goal: Create a Python script that processes CSV data and outputs JSON.

Context: Working with tabular data that needs cleaning before export.

Requirements:
- Read CSV file input
- Perform data cleaning operations
- Export results as JSON
- Include bilingual (Chinese-English) code comments

Constraints:
- Use Python only
- Maintain data integrity during transformation

Output Expectations:
Provide working Python code with clear comments in both Chinese and English.
```

## Tips for Best Results

- **Be specific** – Provide detailed requirements rather than vague requests
- **Clarify constraints** – What are the limitations or boundaries?
- **Define output format** – How should the AI present the response?
- **Include examples** – If possible, show what good output looks like
- **State your context** – What problem are you solving?


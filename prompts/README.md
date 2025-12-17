# Prompts Directory

This directory contains prompt templates and evaluation fixtures for the KlarText simplification engine.

## Structure

```
prompts/
├── templates/          # LLM prompt templates
│   ├── simplify_de.txt
│   └── simplify_en.txt
├── eval/               # Evaluation fixtures
│   ├── inputs/         # Sample input texts
│   └── expected/       # Expected outputs for testing
└── README.md
```

## Prompt Guidelines

When writing prompts for text simplification:

1. **Output must be easy to read:**
   - Short sentences
   - Common words
   - Explain technical words if unavoidable
   - Keep structure: headings + bullet points when helpful
   - Do not add new facts

2. **Levels:**
   - `very_easy`: Very short sentences; define anything uncommon; extra whitespace
   - `easy`: Short sentences; clear structure; minimal jargon
   - `medium`: Plain language; normal sentence length; less repetition

3. **Special content:**
   - If input is legal/medical/financial, add a short "not advice" note
   - Preserve meaning; avoid hallucinating facts
   - If something is unclear, say so

## Adding New Prompts

1. Create the template file in `templates/`
2. Add corresponding test cases in `eval/inputs/` and `eval/expected/`
3. Test with the evaluation script (TODO)


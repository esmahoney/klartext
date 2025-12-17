# Data Sources

This document provides an overview of datasets explored and used for training KlarText text simplification models.

## Summary Table

| Dataset | Language | Size | Type | License | Status |
|---------|----------|------|------|---------|--------|
| DEplain | German | ~600K pairs | Web-crawled easy language | Research | 🔍 Exploring |
| Klexikon | German | ~3K articles | Simple Wikipedia for kids | CC-BY-SA | 🔍 Exploring |
| GEOLino | German | ~2K articles | Children's science | Restricted | 🔍 Exploring |
| Newsela | English | 1.9K articles | Multi-level news | Research | 🔍 Exploring |
| WikiLarge | English | 296K pairs | Wikipedia simplification | CC-BY-SA | 🔍 Exploring |
| ASSET | English | 2.4K sentences | Simplification benchmark | CC-BY-NC | 🔍 Exploring |
| TurkCorpus | English | 2.4K sentences | MTurk simplifications | CC-BY-NC | 🔍 Exploring |

**Legend:** ✅ In Use | 🔍 Exploring | ❌ Not Suitable

---

## German Datasets

### DEplain (DEplain-web)

**Description:** Large-scale German plain language corpus created from web-crawled content. Contains aligned pairs of standard German text and their simplified versions.

| Attribute | Value |
|-----------|-------|
| **Language** | German |
| **Size** | ~600,000 sentence pairs |
| **Source** | Web-crawled from German easy language websites |
| **License** | Research use |
| **HuggingFace** | `DEplain/DEplain-web` |

**Usage in KlarText:**
- Primary training data for German simplification
- Good coverage of administrative/legal language

**Sample:**
```
Source: Der Antragsteller muss die erforderlichen Unterlagen fristgerecht einreichen.
Target: Sie müssen die Papiere rechtzeitig abgeben.
```

**Reference:** [DEplain Paper](https://aclanthology.org/2022.acl-long.343/)

---

### Klexikon

**Description:** Simple German Wikipedia written for children. Articles explain complex topics in accessible language.

| Attribute | Value |
|-----------|-------|
| **Language** | German |
| **Size** | ~3,000 articles |
| **Source** | klexikon.zum.de |
| **License** | CC-BY-SA 4.0 |
| **Pairs with** | German Wikipedia (for alignment) |

**Usage in KlarText:**
- Aligned with standard German Wikipedia articles
- Good for factual/educational content simplification

**Notes:**
- Requires alignment with Wikipedia to create training pairs
- High quality but limited domain (encyclopedia topics)

---

### GEOLino

**Description:** Children's science magazine articles written in accessible German.

| Attribute | Value |
|-----------|-------|
| **Language** | German |
| **Size** | ~2,000 articles |
| **Source** | GEO magazine (children's edition) |
| **License** | Restricted (check with publisher) |

**Usage in KlarText:**
- Science/nature domain simplification
- May require licensing for commercial use

---

### APA/Capito

**Description:** Austrian news agency content translated to easy language by Capito.

| Attribute | Value |
|-----------|-------|
| **Language** | German (Austrian) |
| **Size** | Varies |
| **Source** | Austrian Press Agency |
| **License** | Restricted |

**Notes:**
- High quality, professionally simplified
- Licensing required for use

---

## English Datasets

### Newsela

**Description:** News articles rewritten at 5 different reading levels by professional editors.

| Attribute | Value |
|-----------|-------|
| **Language** | English |
| **Size** | 1,911 articles × 5 levels |
| **Source** | newsela.com |
| **License** | Research agreement required |
| **Levels** | 0 (original) → 4 (simplest) |

**Usage in KlarText:**
- Multi-level simplification training
- High quality professional rewrites
- Good for understanding gradual simplification

**Access:** Requires application at [newsela.com/research](https://newsela.com/research)

---

### WikiLarge / WikiSmall

**Description:** Wikipedia sentence simplification dataset. Pairs of complex English Wikipedia sentences with their Simple English Wikipedia equivalents.

| Attribute | Value |
|-----------|-------|
| **Language** | English |
| **Size** | 296K train / 2K valid / 359 test (WikiLarge) |
| **Source** | Wikipedia & Simple Wikipedia alignment |
| **License** | CC-BY-SA |
| **HuggingFace** | `wiki_lingua` |

**Usage in KlarText:**
- Primary training data for English simplification
- Large scale, good coverage

**Sample:**
```
Source: The city is located in the southeastern part of the state.
Target: The city is in the southeast of the state.
```

---

### ASSET

**Description:** Human-written simplifications with multiple references per source. Focuses on varied simplification strategies.

| Attribute | Value |
|-----------|-------|
| **Language** | English |
| **Size** | 2,359 sentences × 10 references |
| **Source** | Crowdsourced from TurkCorpus sources |
| **License** | CC-BY-NC 4.0 |
| **HuggingFace** | `asset` |

**Usage in KlarText:**
- Evaluation benchmark
- Multiple valid simplifications per source

**Reference:** [ASSET Paper](https://aclanthology.org/2020.acl-main.424/)

---

### TurkCorpus

**Description:** Mechanical Turk crowdsourced simplifications with 8 references per source.

| Attribute | Value |
|-----------|-------|
| **Language** | English |
| **Size** | 2,359 sentences × 8 references |
| **Source** | Amazon Mechanical Turk |
| **License** | CC-BY-NC 4.0 |

**Usage in KlarText:**
- Evaluation benchmark
- Comparison with ASSET

---

## Multilingual / Supporting Datasets

### mC4 (Multilingual C4)

**Description:** Multilingual Common Crawl corpus for pre-training.

| Attribute | Value |
|-----------|-------|
| **Languages** | 101 languages including DE, EN |
| **Size** | Terabytes |
| **Use** | Pre-training, not simplification |

---

### OPUS Parallel Corpora

**Description:** Collection of translated texts for machine translation.

| Attribute | Value |
|-----------|-------|
| **Languages** | Many pairs including DE-EN |
| **Use** | Translation component of pipeline |
| **Link** | [opus.nlpl.eu](https://opus.nlpl.eu/) |

---

## Evaluation Datasets

For evaluation, we use held-out portions of training data plus dedicated benchmarks:

| Dataset | Purpose | Metrics |
|---------|---------|---------|
| ASSET (EN) | Multi-reference evaluation | SARI, BLEU, FKGL |
| TurkCorpus (EN) | Multi-reference evaluation | SARI, BLEU |
| DEplain-test (DE) | German evaluation | SARI, BLEU |

---

## Data Quality Considerations

### What Makes Good Training Data

1. **Aligned pairs** — Clear source → target mapping
2. **Meaning preservation** — Target doesn't add/remove facts
3. **Actual simplification** — Target is genuinely simpler
4. **Diverse domains** — Legal, medical, news, educational
5. **Clean text** — No OCR errors, encoding issues

### Red Flags

- ❌ Target longer than source (usually wrong)
- ❌ Source == Target (no simplification happened)
- ❌ Machine-translated pairs (quality issues)
- ❌ Inconsistent simplification levels

---

## Adding New Datasets

When adding a new dataset:

1. Document it in this file
2. Add loading code to `notebooks/01_eda.ipynb`
3. Run quality checks before training
4. Note any licensing restrictions
5. Update the summary table above

---

## References

- Alva-Manchego et al. (2020). ASSET: A Dataset for Tuning and Evaluation of Sentence Simplification Models with Multiple Rewriting Transformations. ACL 2020.
- Stodden & Kallmeyer (2022). DEplain: A German Parallel Corpus with Intralingual Translations into Plain Language. ACL 2022.
- Xu et al. (2016). Optimizing Statistical Machine Translation for Text Simplification. TACL.


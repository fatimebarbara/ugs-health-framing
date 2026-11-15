# What Is a Park For? Data, lexicon, codebook and code

Replication materials for:

> Hegyi, F.B. *What Is a Park For? Measuring the Health Framing of Urban Green Space Across 22 European Capitals.* [Journal, year, DOI to be added on publication.]

The paper asks whether European mayors, when they post about urban green space, present it as a health matter, and compares four ways of measuring that: a standard SDG vocabulary, a purpose-built two-layer lexicon (T1, T2), a human reader (T3) and a classifier trained on the reader's labels (T4). This repository holds everything needed to check the measurement, except the post texts themselves (see [Post texts](#post-texts)).

## Contents

| Path | What it is |
|---|---|
| `docs/S1_lexicon.md` | Supplementary file S1, complementing Appendix A: how the lexicon was built, what the match counts show, the language searched for each account, and every term's variants in 22 languages |
| `docs/S2_collision_taxonomy.md` | Supplementary file S2, complementing Appendix B: full decision rules, triggers and examples for the seven collision classes, what each coding pass caught, and known inconsistencies |
| `docs/S3_codebook.md` | Supplementary file S3, complementing Appendix C: what the coder saw, full definitions of the six functions with examples, all boundary cases, procedure, and changes proposed for a second version |
| `lexicon/lexicon_v2.1.csv` | The lexicon: 92 terms (44 Layer A green space referents, 48 Layer B health pathway terms), 22 language columns, codes, provenance and match counts |
| `lexicon/CHANGELOG.md` | Changes from version 2 (used in the census) to version 2.1 |
| `data/census_coded_v3.csv` | The census: 1,520 retrieved posts with post identifiers, final and first-pass coding, reject class and pass, coder notes. No post texts |
| `data/collision_log.csv` | The 741 rejected posts with their collision class and pass |
| `data/recode_sample_128.csv` | The intra-coder re-code sample: first-pass and blind second-pass codes |
| `code/census_tables.py` | Reproduces the census counts (Tables 1, 2, 6, 7; Tables B1, B2) |
| `code/reliability_alpha.py`, `code/reliability_alpha.R` | Reproduce Table 4 (Krippendorff's alpha) |
| `code/t1_t2_matching.py` | Reproduces Table 3, T2 recall by city, the code counts in Section 4.3, and the term counts of Tables A2 and A3. Needs post texts |
| `code/t4_classifier.py` | Reproduces Table 5. Needs post texts |
| `code/census_coding.R` | The interactive coding script used for the first pass, archived as used (folder paths removed) |

## Quick start

```bash
pip install -r requirements.txt
python code/census_tables.py        # runs on the deposited files
python code/reliability_alpha.py    # runs on the deposited files
```

The two lexicon and classifier scripts need the post texts in `data/texts.csv` (columns `tweet_id`, `text`):

```bash
python code/t1_t2_matching.py
python code/t4_classifier.py
```

## What the scripts reproduce

All figures below were checked against the deposited files before release. Tables A2, A3, B1, B2 and B3 are printed in the paper's appendices; S1–S3 hold the material the appendices leave out.

- `census_tables.py`: 1,520 retrieved; 1,278 valid after the first pass; 779 valid in the final census; 185 health-framed. Reject classes by pass, function shares and city figures as in Tables 2, 6, 7, B1 and B2 of the paper.
- `reliability_alpha.py` / `.R`: Table 4 on the 59 posts that stayed valid with their first-pass codes (health alpha 0.44, climate 0.43, amenity 0.46, equity 0.43, economic 0.88, ceremonial or none 0.11).
- `t1_t2_matching.py`: Table 3 (T1: 32 flagged, 28 correct, F1 0.26; T2: 169 flagged, 86 correct, F1 0.49; T2 without beneficiary: 144 flagged, 82 correct, F1 0.50) and T2 recall by city.
- `t4_classifier.py`: relevance P 0.82, R 0.83, F1 0.82; health P 0.52, R 0.61, F1 0.56; climate F1 0.69; amenity 0.62; equity 0.52; ceremonial or none 0.50; economic 0.26. Results can differ slightly with other scikit-learn versions; tested with scikit-learn 1.9.1.

Matching, scoring and alpha are computed exactly as described in Appendix A of the paper and in S1.3.

## Post texts

The post texts are not included. The posts were published on X (formerly Twitter), and the platform's terms restrict redistribution of post content; the files therefore carry the `tweet_id` of every post, from which posts that are still online can be retrieved. Some accounts have since been deleted or made inactive, so not every post can be recovered. The short quotations in S2 and S3 are given for documentation, as in the paper.

To run the two scripts that need texts, create `data/texts.csv` with one row per post and the columns `tweet_id` and `text`. That file is listed in `.gitignore` so that it is not committed by accident.

## The census file

`data/census_coded_v3.csv`, one row per retrieved post:

| Column | Meaning |
|---|---|
| `row` | Census row identifier, used in the paper and in S1–S3 (e.g. r608) |
| `city`, `account`, `tweet_id`, `date` | Where and when the post was published |
| `retrieval_stem` | The stem that retrieved the post: green, park or green+park |
| `status` | valid or rejected in the final census |
| `reject_class` | One of seven collision classes (S2); empty for valid posts |
| `reject_pass` | 1 = rejected on the first reading; 2 = rejected in the re-screen of 29 September 2026 |
| `function_health` … `function_none` | Final function codes, 1 = present (valid posts only) |
| `recoded_in_rescreen` | 1 = the post's function codes come from the re-screen rather than the first pass |
| `pilot` | 1 = one of the 105 pilot posts |
| `pass1_status`, `pass1_health` … `pass1_none` | Status and codes on the first pass |
| `first_coded_date` | Date of first coding |
| `coder_notes` | The coder's notes |

## Licence

Data, lexicon and documentation (`data/`, `lexicon/`, `docs/`): Creative Commons Attribution 4.0 International (CC BY 4.0), see `LICENSE-DATA`. Code (`code/`): MIT, see `LICENSE`.

The SDG vocabulary terms carried into the lexicon come from Duran-Silva, N., Fuster, E., Massucci, F.A. and Quinquillà, A. (2019) *A controlled vocabulary defining the semantic perimeter of Sustainable Development Goals* (Version 1.2), Zenodo, doi:10.5281/zenodo.3567769. Please cite that work as well when reusing those terms.

## How to cite

Please cite the paper and this archive. Citation metadata is in `CITATION.cff`; the archive DOI is issued by Zenodo for each release.

## Use of generative AI

A large language model (Claude, Anthropic) assisted with candidate lexicon terms in languages the author does not read, translation, and writing analysis code and documentation. All outputs were reviewed by the author. The human coding was produced without model involvement.

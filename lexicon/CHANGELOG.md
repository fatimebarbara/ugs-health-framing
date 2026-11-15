# Lexicon changelog

## v2.1 (November 2026)

Correction of a row shift in ten Layer B terms. In version 2 the English column was correct, but in the 21 other language columns each of the following terms carried the variants of the next term in the list, and *clean air* carried those of *green lung*:

green lung, shade, cooling, cool island, heat, urban heat island, heatwave, air quality, air pollution, clean air.

Version 2.1 puts each set of variants back on its own term. No term or variant was added or removed. The correction does not change T1 (outcome terms only) or T2 (all 48 Layer B terms together); it changes only the code under which a match is counted. Among the 185 health-framed posts, harm terms now appear in 11 posts instead of 12.

The column `mechanism` was renamed `code`, and three match-count columns were added (`posts_retrieved`, `posts_valid`, `posts_health_framed`), computed with `code/t1_t2_matching.py`.

## v2 (August 2026)

The version used for the census (17 August – 22 September 2026) and for all figures in the paper. The five-value code column was added on 21 September 2026 without changing any term.

# Accessibility

Accessibility is a requirement, not an extra. This page lists the rules for figures, infographics and written findings, the checks that run automatically, and the checks that need a person.

Terms such as alt text, WCAG and the Okabe-Ito palette are defined in the [glossary](guide.md#appendix-glossary).

## 1. Rules

| # | Rule | Status | Where it is checked |
|---|---|---|---|
| 1 | **Alt text.** Every figure has alt text that states the finding in plain words. It lives in `infographic.yaml` (at least 12 words) and in the analysis README. | Enforced (presence, non-empty, length). Accuracy: Review | `aab/validate.py`; a person reads it |
| 2 | **Written equivalent.** Each chart has a table of the same numbers in its results file (`table.csv` or a Markdown table in `results.md`). | Review | Pull request checklist |
| 3 | **Colour.** Use the Okabe-Ito palette. Colour is never the only cue: region is also shown by hatching, and series by line style. The chart must still read in greyscale. | Review | Pull request checklist; greyscale check |
| 4 | **Contrast.** Text contrast at least 4.5:1, and graphical elements at least 3:1 (WCAG 2.2, criteria 1.4.3 and 1.4.11). | Review | Person, with a contrast tool |
| 5 | **Text size.** No text smaller than 8 pt at final size. | Review | Pull request checklist |
| 6 | **Formats.** PNG at 200 dpi for analyses, 1920 x 1080 px for infographics, and SVG. A clear title that states what the chart shows. | Enforced (size warning for infographics) | `aab/validate.py` |
| 7 | **Plain language.** Use plain words. Define technical terms the first time they appear, using the [glossary](guide.md#appendix-glossary). | Review | Pull request checklist |
| 8 | **Claims.** An infographic's headline must match its analysis. `claim: no_clear_trend` is checked by `make.py`. | Enforced | `make.py` |
| 9 | **Numbers in text.** Give the year and unit with each number, and state the limits. | Review | Pull request checklist |
| 10 | **Catalogue.** Alt text is shown under each image in `CATALOG.md`. | Enforced (generated) | Pipeline |
| 11 | **Right-to-left text.** Arabic-script labels are shaped and reordered before drawing, and a native speaker checks them. See [section 5](#5-languages-and-right-to-left-text). | Review | Person |

## 2. Colour and patterns

The palette is defined in `aab/analyses.py`. Use these colours for series, in this order:

| Order | Colour | Hex |
|---|---|---|
| 1 | Blue | `#0072B2` |
| 2 | Orange | `#E69F00` |
| 3 | Bluish green | `#009E73` |
| 4 | Reddish purple | `#CC79A7` |
| 5 | Sky blue | `#56B4E9` |
| 6 | Vermillion | `#D55E00` |
| 7 | Yellow | `#F0E442` |
| 8 | Black | `#000000` |

Region is shown by colour and pattern together. In the water access ranking, Central Asia is solid blue and South Asia is orange with diagonal hatching. Trend lines are blue, and the mean line is dashed. Check every chart in greyscale: if two series become indistinguishable, add a pattern or a line style.

## 3. Writing alt text

Alt text describes what the figure shows and what it means. It is not a list of colours. A good alt text:

- states the finding first, in one sentence,
- gives the period, the unit and the key values,
- names the limits that matter for reading the chart,
- is checked against the figure after the last rebuild.

*Illustrative example (not a published alt text):* "Annual rainfall in Afghanistan, 1975 to 2023, shown as bars with a 10-year average line. The line rises and falls, with no clear long-term change. The wettest and driest years are labelled."

## 4. Pre-publication checklist

Use this list for every new or changed figure. Copy it into the pull request.

- [ ] The alt text states the finding and matches the figure after the latest build.
- [ ] Every number in the alt text has its year and unit.
- [ ] The chart has a written equivalent (`table.csv` or a Markdown table).
- [ ] Series are distinguished by something other than colour alone.
- [ ] The chart was viewed in greyscale and still reads.
- [ ] Text is at least 8 pt at final size, and contrast meets 4.5:1 for text and 3:1 for graphics.
- [ ] The title says what the chart shows.
- [ ] For infographics: viewed at projector size, and the alt text was read aloud.
- [ ] For translations: a native speaker has checked the labels, and right-to-left text has been shaped.

## 5. Languages and right-to-left text

English comes first. Other languages are welcome.

Dari and Pashto use Arabic script, which is written right to left. Standard matplotlib does not shape or reorder this text. The optional `rtl` extra in `pyproject.toml` lists two helper libraries (`arabic-reshaper` and `python-bidi`). Install them on your own machine, then pass each Arabic-script label through the reshaper and bidi functions before drawing. Use a font that supports Arabic script, such as Noto Naskh Arabic or Noto Sans Arabic. Have a native speaker check every translated figure before publishing.

Keep the translated alt text in the same `infographic.yaml` field, with a language tag, and check it against the translated figure.

## 6. What is automated and what is not

Automated checks confirm that alt text exists and is long enough, that figures exist and are the right size, and that claims match the analysis. They cannot confirm that alt text is accurate, that colours are distinguishable in greyscale, or that contrast meets WCAG.

Known gaps, tracked in [questions](questions.md#3-open-items):

- Contrast and greyscale are checked by people, not by CI.
- CI does not compare PNG files, so a font difference between machines can change a figure without a failed check (open item O05).
- Alt text accuracy needs a reviewer who has read the figure.
- Translated labels need a native speaker's review.

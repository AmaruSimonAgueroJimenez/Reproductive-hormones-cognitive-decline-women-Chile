# Neurodegenerative disease and reproductive health in Chile

This repository contains the English, 29-slide presentation combining the two parts of the research project: recorded neurodegenerative burden and reproductive histories, ovarian surgery and menopausal hormone therapy.

## View the presentation

Open the [online presentation](https://AmaruSimonAgueroJimenez.github.io/Reproductive-hormones-cognitive-decline-women-Chile/), or download this repository and open `docs/combined_project_key_results_slides.html` in a browser. The slide menu, keyboard navigation and speaker notes are included. Arrow keys move between slides; **F** opens fullscreen and **O** opens the slide overview.

The presentation retains the original 15 figure PNGs, used in 24 slide placements, and three tables containing 36 cells. Figure links open the complete original panels. Scientific source links point to the institutions and their documentation. `publication_manifest.json` records file hashes and the exact original figure identities.

## Repository contents

- `docs/`: the presentation HTML, editable Quarto source, its byte-identical downloadable text copy, presentation stylesheet and bibliography.
- `outputs/`: only the 15 original aggregate figure PNGs linked by the slides.
- `scripts/prepare_online.py`: a Python standard-library utility that replaces embedded PNG copies with relative links to the identical original PNGs and verifies the presentation structure.

The HTML is prepared for efficient online viewing: each original figure is downloaded once and reused without changing the figure bytes, panel crops, slide text or tables. The presentation runtime, styles and fonts remain embedded. Scientific references require an internet connection when followed.

## Recreate the presentation HTML

Install [Quarto](https://quarto.org/docs/get-started/) and Python 3.10 or newer. From the repository root, run:

```sh
quarto render docs/combined_project_key_results_slides.qmd --to revealjs
python3 scripts/prepare_online.py
python3 scripts/prepare_online.py --check
```

The original presentation was rendered with Quarto 1.10.18. Rendering with another version can change the generated runtime or styling. The utility verifies 29 slides, 24 image placements, 15 distinct original figure hashes and 36 table cells; it refreshes the public file manifest after preparation. It does not change the QMD or figure files.

These steps reproduce the slide presentation from its stored text, tables and original aggregate figures. The underlying analyses, analytical code, source records and research manuscripts are outside the scope of this presentation repository; these instructions do not claim to regenerate the scientific estimates from source data. The slides describe the distinct observation units and limitations of each analysis.

## Verify the published files

```sh
python3 scripts/prepare_online.py --check
```

This checks the manifest, local links, original figure hashes and slide structure. It also checks that the downloadable slide source exactly matches the QMD. No Word or PowerPoint files or individual-level data are included.

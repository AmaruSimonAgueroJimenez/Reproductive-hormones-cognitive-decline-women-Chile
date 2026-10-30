# Neurodegeneration and reproductive health in Chile

The [research website](https://amarusimonaguerojimenez.github.io/Reproductive-hormones-cognitive-decline-women-Chile/) provides an English index linking three full reports and both presentations.

## Full methods, results and extended analyses

- [Part I: descriptive evidence](docs/descriptive_methods_results.html): recorded dementia and neurodegenerative disease across mortality, hospital and primary-care sources, with the extended figure and table bank.
- [Part II: connected analyses](docs/reproductive_life_course.html): reproductive history, ovarian surgery and menopause-care context, including the survey, surgery and care extensions.
- [Administrative extension](docs/access_diagnostic_recording_extension.html): the 29 October 2026 REM, DEIS and GRD update, with source-completeness checks, geographic analyses and sensitivity analyses for diagnostic recording.

The analyses in the first two reports retain their reviewed 28 October 2026 snapshots, and the administrative extension remains dated 29 October 2026. On 30 October 2026, the comorbidity figures were updated with adjacent bar panels showing raw coded prevalence; this presentation revision did not refit the analyses or networks. The administrative extension documents corrected source handling and definitions; its facility associations remain exploratory and sensitive to denominators and programme intensity.

## Presentations

- [Combined presentation of both parts: 29 slides](docs/combined_project_key_results_slides.html).
- [Part II key results: 18 slides](docs/reproductive_key_results_slides.html).

Arrow keys navigate between slides. **F** opens fullscreen and **O** opens the overview. Complete original figures and institutional source references remain linked from the slides. PowerPoint files stay outside this public repository through case-insensitive `.gitignore` rules.

## Figures, tables and documents

Each full report links its reviewed line-numbered Word document and its original vector figures. The descriptive report includes its complete Word figure/table bank and figure/table asset archive. The administrative extension links its public reconstruction archive and all 26 displayed source tables. Original PNG, SVG and PDF figure files preserve their scientific content and bytes.

The public HTML copies use relative links to the original PNG files, so a figure is downloaded once and reused. Report navigation has been added, and the unavailable PowerPoint download anchor has been removed from the public Part II HTML. No analytical values, scientific prose, tables, figure scales, crops, folded code or report runtime have been changed. Quarto sources are retained exactly; the downloadable `*_source.txt` copies are byte-identical to the QMD files.

## Reproducibility and verification

From a downloaded copy of the repository, verify the delivered pages, every local link, the original figures, numerical table structure and complete file manifest with Python 3.10 or newer:

```sh
python3 scripts/prepare_site.py --check
```

`python3 scripts/prepare_site.py` prepares the online delivery of the recorded HTML snapshots and refreshes the delivery manifest. It is idempotent and permits only the documented publishing changes. The script uses the Python standard library.

The QMD and folded report code make the analysis specifications inspectable. Rendering the first two reports from their QMD files also requires their complete analytical project, software and authorised source/intermediate data; this delivery does not claim that those analyses can be recalculated from the website files alone. The administrative report provides a separately documented [public reconstruction package](outputs/access_diagnostic_extension_2026-10-29/Access_Diagnostic_Recording_Assets_EN.zip), including public aggregate inputs, analysis sources, environment pins and rebuild instructions. Its original-record refresh requires authorised external data and upstream preparation, as described in that package. Its public metadata uses relative project paths and `EXTERNAL_DATA_ROOT` labels.

`publication_manifest.json` and `site_provenance.json` record file integrity and the relationship to the reviewed snapshots. They are technical provenance records; scientific references point to [DEIS](https://deis.minsal.cl/#datosabiertos), [FONASA](https://datosabiertos.fonasa.cl/dimensiones-financiamientos/), [INE](https://www.ine.gob.cl/estadisticas-por-tema/demografia-y-poblacion/estimaciones-y-proyecciones-de-poblacion) and the other original institutions cited in the reports.

No individual-level records are included in this repository. The public site retains the distinct observation units, measurement limits and analysis populations described in each report.

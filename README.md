# ReDLat/Tangl Variant Viewer

A Dash-based web application to visualize case/control variant counts. You may generate graphs from our predefined datasets or upload custom `.txt` files yourself.

![psen1-variants](docs/psen1-variants.png)

## Contents

- [Introduction](#introduction)
- [Generating the `.txt` Files](#generating-the-txt-files)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [App Structure](#app-structure)
- [Usage](#usage)
- [Citations](#citations)

---

## Introduction

This application reads variant data from tab-delimited `.txt` files containing columns for exon number, amino-acid position (AA), variant identifier, and case/control counts. It clusters nearby variants within the same exon, renders vertical lines and scatter points to represent counts, and draws exon-range bars with a legend.

## Generating the `.txt` Files

The `.txt` file of your dataset must be tab-delimited. Here's an example.

```text
Gene.refGene	AA	variant	case	control	exon
PSEN1	35	R35W	0	1	exon4
PSEN1	38	H38Q	0	1	exon4
PSEN1	40	D40N	0	0	exon4
PSEN1	63	V63A	0	0	exon4
```

To generate these `.txt` files from a annotated `.tsv` file, the following script can be used, specifying the desired variants and isoform.

```bash
python extract_variants.py \
    --input raw_data/redlat/redlat.genes.chr.counts.hg38_multianno.tsv \
    --isoforms '{"PSEN1": "NM_000021", "PSEN2": "NM_000447", "TARDBP": "NM_007375", "MAPT": "NM_005910"}' \
    --output-dir data/custom
```

---

## Installation

1. **Clone** this repository:
   ```bash
   git clone https://github.com/ThePickleGawd/redlat-variant-graphs.git
   cd redlat-variant-graphs
   ```
2. **Create** a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Running the App

```bash
python main.py
```

By default, the app runs on `http://127.0.0.1:8050`.

---

## Usage

1. Select a dataset tab (`TANGL`, `REDLAT`, or `CUSTOM`).
2. If `CUSTOM`, upload your `.txt` file.
3. Choose a file from the dropdown.
4. View the generated plot below.

## Citations

If you use any of our data, please cite us:

- **TANGL**: Acosta-Uribe, J., Aguillón, D., Cochran, J. N., Giraldo, M., Madrigal, L., Killingsworth, B. W., ... & Kosik, K. S. (2022). _A neurodegenerative disease landscape of rare mutations in Colombia due to founder effects._ Genome Medicine, 14(1), 27.
- **ReDLat**: Acosta-Uribe, J., Escudero, S. D. P., Cochran, J. N., Taylor, J. W., Castruita, P. A., Jonson, C., ... & Yokoyama, J. S. (2024). _Genetic Contributions to Alzheimer’s Disease and Frontotemporal Dementia in Admixed Latin American Populations._ medRxiv.

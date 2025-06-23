
# Variant Visualizer

### Developed by:

- Dylan Lu `dylanlu@ucsb.edu`
- Juliana Acosta-Uribe `acostauribe@ucsb.edu`


The **Variant Visualizer** is a dash-based web application designed to visualize and compare allelic counts in selected genes across multiple cohorts. \
We have used it to plot the allelic counts of variant in neurodegeneration associated genes in the TANGL<sup>1</sup> and ReDLat<sup>2</sup> cohorts. \
You can see it in action [here](https://doi.org/10.5062/F4BR8QFB)

![plot](assets/image.png)

You can follow the following steps to plot your own data with the variant visualizer

### Contents

- [Introduction](#introduction)
- [Generating the `gene` files](#generating-the-gene-files)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [References](#references)



### Introduction

This application reads variant data from tab-delimited files named after genes (e.g., `PSEN1`, `MAPT`). Each file contains columns for exon number, amino-acid position (AA), variant identifier, and case/control counts, including subgroup counts (e.g., AD, EOD, FTLD, AAO<65, Healthy). It clusters nearby variants within the same exon, renders vertical lines and scatter points to represent counts, and draws exon-range bars with a legend.

### Generating the gene files

Each gene file must be tab-delimited with no file extension. Here's an example of the content inside a file (e.g., `ANXA11:NM_001157`):

```text
Gene.refGene	variant	AA	exon	all.Hom_A1	all.Het	ad.Hom_A1	ad.Het	ftd.Hom_A1	ftd.Het	aao.Hom_A1	aao.Het	healthy.Hom_A1	healthy.Het
ANXA11	G503R	503	15	0	3	0	3	0	0	0	0	0	0
ANXA11	S486L	486	14	0	4	0	3	0	0	0	0	0	0
ANXA11	I457V	457	14	0	15	0	7	0	6	0	0	0	0
```

These gene-named files can be generated using `extract_variants.py`:

```bash
# Extract tangl variants
python ./data_preprocessing/extract_variants.py \
  --input data/tangl/tangl_id.hg38_multianno.annotated-variant-counts.tsv \
  --isoforms '{
      "ANXA11": "NM_001157",
      "APOE":  "NM_000041",
      "APP":   "NM_000484",
      "CHMP2B":"NM_014043",
      "CSF1R": "NM_005211",
      "DNAJC5":"NM_025219",
      "FUS":   "NM_001170634",
      "GRN":   "NM_002087",
      "LRRK2": "NM_198578",
      "MAPT":  "NM_005910",
      "NOTCH3":"NM_000435",
      "PSEN1": "NM_000021",
      "PSEN2": "NM_000447",
      "RELN":  "NM_005045",
      "SOD1":  "NM_000454",
      "SQSTM1":"NM_003900",
      "TARDBP":"NM_007375",
      "TBK1":  "NM_013254",
      "TREM2": "NM_018965",
      "VCP":   "NM_007126"
  }' \
  --output-dir data/tangl
```

### Installation

1. **Clone** this repository:

   ```bash
   git clone https://github.com/ThePickleGawd/variant-visualizer.git
   cd variant-visualizer
   ```

2. **Create** a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   You need to have Python ≥ 3.11 installed. If you do `python --version` inside that environment and it’s < 3.11, follow the troubleshooting guide at the end.

### Running the App

Run the following command from the terminal

```bash
# Deploy/Run locally
gunicorn app:server --bind 0.0.0.0:8050
```

By default, the app runs on `http://127.0.0.1:8050`
You can change the port number if 8050 is being used, or if you want to re-lauch the app, you can reset the 8050 port by doing `lsof -i :8050`


### Usage

1. Select a cohort
2. Choose a category
3. Choose a gene from the dropdown
4. View the generated plot below

> You will have to edit the `app.py` file to match your own cohort and categories

---

### Troubleshooting

**Use the correct python version for your virtual environment**  

   - **Install Python 3.11** 
   
   For example, with Homebrew on an Intel Mac:  

   ```bash
   brew install python@3.11
   ```  

   This will give you a `python3.11` executable (typically at `/usr/local/opt/python@3.11/libexec/bin/python3`). \
   You can search for the path by typing in the terminal `which python3`

   - **Recreate your venv using that binary**:  

   ```bash
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip    # optional but recommended
   pip install -r requirements.txt
   ```

   - **Verify**  
   
   ```bash
   python --version   # Python 3.11.x
   pip list           # shows your project’s dependencies
   ```


### References

If you use this app to visualize your data, please cite us:

- Dylan Lu, & Juliana Acosta-Uribe. (2025). TauConsortium/variant-visualizer (v1.0.0). Zenodo. [![DOI](https://zenodo.org/badge/943586959.svg)](https://doi.org/10.5281/zenodo.15652735)


If you use any of the TANGL or ReDLat data, please cite the corresponding paper:

1. **TANGL**: Acosta-Uribe, J., Aguillón, D., Cochran, J. N., Giraldo, M., Madrigal, L., Killingsworth, B. W., ... & Kosik, K. S. (2022). _A neurodegenerative disease landscape of rare mutations in Colombia due to founder effects._ Genome Medicine, 14(1), 27.
2. **ReDLat**: Acosta-Uribe, J., Piña-Escudero, S. D., Cochran, J. N., Taylor, J. W., Castruita, P. A., Jonson, C., ... Kosik, K. S. & Yokoyama, J. S. (2024). _Genetic Contributions to Alzheimer’s Disease and Frontotemporal Dementia in Admixed Latin American Populations._ medRxiv.

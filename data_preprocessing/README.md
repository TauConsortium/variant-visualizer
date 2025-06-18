## How to Run This Script

This script processes a VCF file using PLINK and ANNOVAR, and generates a merged table containing variant annotations and genotype counts across all samples and optional sub-cohorts.

This script requires the following software:
bcftools
ANNOVAR (https://annovar.openbioinformatics.org/en/latest/user-guide/download/)
Plink 1.9 (https://www.cog-genomics.org/plink2/)
Python3 and pandas


### Required Arguments

You must provide the following arguments when running the script:

* `--vcf_file`
  Specify the **base path** to the VCF file **(do not include `.vcf` or `.vcf.gz`)**.
  The file should contain the regions and samples you want to analyze.
  It must be aligned to the `hg38` reference genome and preprocessed (e.g., normalized using `bcftools norm`).

  Example:

  ```bash
  --vcf_file genome_exome_redlat
  ```

* `--annovar`
  Provide the full path to the ANNOVAR script (`table_annovar.pl`).

  Example:

  ```bash
  --annovar /home/usr/bin/table_annovar.pl
  ```

* `--annovar_database_PATH`
  Provide the path to the directory containing the ANNOVAR database (e.g., `humandb`).

  Example:

  ```bash
  --annovar_database_PATH /home/usr/bin/annovar/humandb/
  ```

---

### Optional Arguments

* `--cohorts`
  Provide a file listing cohort names, one per line.
  This allows subsetting the dataset to analyze variation within each group.

  Example:

  ```bash
  --cohorts cohorts-redlat.txt
  ```

  The cohort file should look like:

  ```
  ad
  ftld-mnd
  eod
  ```

  For each cohort listed, a corresponding file must exist with:

  * One sample ID per line
  * No header
  * The file name must match the cohort name exactly (e.g., `ad`, `ftld-mnd`, `eod`)

  Example file `ad`:

  ```
  sample_001
  sample_002
  sample_003
  ```

* `--keep-intermediates`
  If this flag is included, intermediate files (such as `.plink`, `.geno`, `.frqx`) will be **preserved**.
  By default, the script will delete them after it finishes.

---

### Example Usage

```bash
bash count-variation.sh \
  --vcf_file genome_exome_redlat \
  --annovar /home/acostauribe/bin/table_annovar.pl \
  --annovar_database_PATH /home/acostauribe/bin/annovar/humandb/ \
  --cohorts cohorts-redlat.txt \
  --keep-intermediates
```

If you omit the `--keep-intermediates` flag, the script will clean up intermediate files automatically.

---

### Output

* A tab-delimited file with annotated variants and their genotype counts across all samples
* If cohort files are provided, additional columns will include counts for each subgroup


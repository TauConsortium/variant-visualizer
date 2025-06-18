#!/bin/bash
## Script to extract and annotate a vcf 
## Juliana Acosta-Uribe April 2025

## This script requires the following software:
# ANNOVAR (https://annovar.openbioinformatics.org/en/latest/user-guide/download/)
# Plink 1.9 (https://www.cog-genomics.org/plink2/)
# bcftools, python3 and pandas

# To run this script start by adding the neccessaty files and paths in lines 20, 24, 25 and 33. 
# Then do:
# chmod u+x annotate_variants.sh
# ./count-variation.sh | tee count-variation.log

## PART ONE: ANNOTATE VCF

# Specify the base path to the VCF file (without the .vcf or .vcf.gz extension).
# The file should contain the regions and samples you want to analyze.
# It must be aligned to hg38 and preprocessed (e.g., normalized with bcftools norm).
vcf_file='genome_exome_redlat'  # Do not include the .vcf or .vcf.gz extension in this variable

# Provide the full path to the ANNOVAR script (table_annovar.pl)
# and the directory containing the ANNOVAR database (e.g., humandb).
annovar='/home/acostauribe/bin/table_annovar.pl'
annovar_database_PATH='/home/acostauribe/bin/annovar/humandb/'


## PART TWO: COUNT CASES AND CONTROLS CARRYING EACH VARIANT

# Subset your dataset into smaller cohorts to analyze variation within each group.
# For example, the Tangl dataset includes cohorts like "ad", "ftld-mnd", and "eod".

cohorts='cohorts-redlat.txt'  
# This file should list one cohort name per line 
# Example: the "cohorts-study" file should look like this:
#   ad
#   ftld-mnd
#   eod

# For each cohort listed in the 'cohorts' file, you need a corresponding file.
# Each of these files should be named after the cohort (e.g., "ad", "ftld-mnd", "eod").
# Each file should contain one sample ID per line, with no header.
# Example: the "ad" file should look like this:
#   sample_001
#   sample_002
#   sample_003


#================SCRIPT

## PART ONE: ANNOTATE VCF

echo "Starting script on $(date)"

## 1. Locate and prepare the input VCF file

# Check for an uncompressed VCF file
if [[ -f "${vcf_file}.vcf" && -s "${vcf_file}.vcf" ]]; then
    echo "Found uncompressed VCF: ${vcf_file}.vcf"
    echo "Compressing with bgzip..."
    bgzip "${vcf_file}.vcf"
    echo "Starting analysis of ${vcf_file}.vcf.gz"

# Check for an already compressed VCF
elif [[ -f "${vcf_file}.vcf.gz" && -s "${vcf_file}.vcf.gz" ]]; then
    echo "Found compressed VCF: ${vcf_file}.vcf.gz"
    echo "Starting analysis of ${vcf_file}.vcf.gz"

# If neither file exists or is non-empty, exit with an error
else
    echo "Error: No valid VCF file found at ${vcf_file}.vcf or ${vcf_file}.vcf.gz"
    exit 1 
fi


## 2. Assign Variant Identifiers and Remove Monomorphic Variants

echo "Assigning variant identifiers..."
# Ensure every variant in the VCF has a unique ID.
# Variants missing an ID will be assigned one in the format: CHROM_POS_REF_ALT
# This is important for downstream matching between VCF and PLINK files.
bcftools annotate \
    --set-id '+%CHROM\_%POS\_%REF\_%FIRST_ALT' \
    --output-type z "${vcf_file}.vcf.gz" > "${vcf_file}_id.vcf.gz"

# Update the vcf_file variable to point to the new ID-annotated file
vcf_file="${vcf_file}_id"

echo "Removing monomorphic variants..."
# Filter out monomorphic variants (i.e., variants with allele count = 0 or only homozygous reference)
# Only retain variants with at least one alternate allele observed in the cohort
bcftools view \
    --min-ac 1 \
    --output-type z "${vcf_file}.vcf.gz" > "${vcf_file}.tmp.vcf.gz"

# Replace the original file with the filtered version
mv "${vcf_file}.tmp.vcf.gz" "${vcf_file}.vcf.gz"

# Index the final VCF file
tabix -p vcf "${vcf_file}.vcf.gz"

    

## 3. Annotate the VCF using ANNOVAR

echo "Annotating ${vcf_file}.vcf.gz with ANNOVAR..."

"${annovar}" "${vcf_file}.vcf.gz" \
    "${annovar_database_PATH}" \
    --buildver hg38 \
    --outfile "${vcf_file}" \
    --protocol refGene \
    --operation g \
    --nastring . \
    --vcfinput \
    --remove

# Output:
# - ${vcf_file}.hg38_multianno.vcf: VCF file annotated with gene information
# - ${vcf_file}.hg38_multianno.txt: Tab-delimited annotation table (used as 'ANNOVAR results' in this script)
annovar_file="${vcf_file}.hg38_multianno"


## 4. Update the ANNOVAR Results Header with Sample IDs

echo "Editing ANNOVAR header..."

# Extract the VCF header line that contains sample IDs
# This is the line starting with '#CHROM'
grep '#CHROM' "${annovar_file}.vcf" > "${annovar_file}.chrom_line"

# Re-compress the VCF file after extracting the header line
bgzip "${annovar_file}.vcf"

# Extract the first line (header) of the ANNOVAR results and ensure fields are tab-delimited
head -1 "${annovar_file}.txt" > "${annovar_file}.header"
sed -i 's/ /\t/g' "${annovar_file}.header"

# Keep only the first 13 columns of the ANNOVAR header
cut -f -13 "${annovar_file}.header" > "${annovar_file}.header_13"

# Append the sample IDs from the VCF to form a complete new header
paste "${annovar_file}.header_13" "${annovar_file}.chrom_line" > "${annovar_file}.header_new"
rm "${annovar_file}.chrom_line"

# Remove the original header from the ANNOVAR results
sed '1d' "${annovar_file}.txt" > "${annovar_file}.header_removed"

# Combine the new header with the rest of the data. 
# This is useful for identifying the sample carrying the annotated variant
cat "${annovar_file}.header_new" "${annovar_file}.header_removed" > "${annovar_file}.txt"

# Clean up temporary header files
rm "${annovar_file}.header"*

# Verify that the ANNOVAR results file was successfully generated and is not empty
if [[ -f "${annovar_file}.txt" && -s "${annovar_file}.txt" ]]; then
    echo "ANNOVAR annotation completed successfully: ${annovar_file}.txt"
else
    echo "Error: ANNOVAR annotation failed. ${annovar_file}.txt was not created or is empty."
    exit 1
fi


## PART TWO: COUNT CARRIERS OF EACH VARIANT

## 1. Import VCF into PLINK

echo "Importing VCF into PLINK format..."

# Define the output base name for PLINK files
plink_file="${annovar_file}.plink"

# Convert annotated VCF to PLINK binary format
plink --vcf "${annovar_file}.vcf.gz" \
    --vcf-half-call m \
    --allow-extra-chr \
    --double-id \
    --keep-allele-order \
    --make-bed \
    --out "${plink_file}"

# --vcf-half-call  Treat half-calls (e.g., 0/.) as missing
# --allow-extra-chr Allow non-standard chromosome names
# --double-id Use the same string for both FID and IID
# --keep-allele-order Preserve REF/ALT allele ordering from VCF

## 2. Count Genotypes for All Variants and All Samples in the Dataset

# More info in: https://www.cog-genomics.org/plink/1.9/formats#frqx

echo "Using PLINK to count genotype frequencies for all samples..."

plink --bfile "${plink_file}" \
    --freqx \
    --allow-no-sex \
    --nonfounders \
    --out "${plink_file}.all"

# --freqx Outputs extended count information per variant
# --allow-no-sex  Skip sex check (useful if sex data is missing)
# --nonfounders Allow inclusion of samples with parental information in the .fam file
# Output will end in ".frqx"

# Retain Variant ID and Genotypic Counts from PLINK Output

echo "Retaining variant ID and genotypic counts..."

# Replace spaces with underscores in the .frqx file (ensures compatibility with parsing tools)
sed -i 's/ /_/g' "${plink_file}.all.frqx"

# Extract relevant columns:
# $2 = SNP ID
# $3 = Allele1
# $4 = Allele2
# $5 = HOM_A1 count
# $6 = HET count
# $7 = HOM_A2 count
awk -v OFS='\t' '{print $2, $3, $4, $5, $6, $7}' "${plink_file}.all.frqx" > "${plink_file}.cohort-counts.txt"

# Clean and standardize header names for downstream compatibility
sed -i 's/SNP/ID/g' "${plink_file}.cohort-counts.txt"
sed -i 's/C(HOM_A1)/Hom_A1/g' "${plink_file}.cohort-counts.txt"
sed -i 's/C(HET)/Het/g' "${plink_file}.cohort-counts.txt"
sed -i 's/C(HOM_A2)/Hom_A2/g' "${plink_file}.cohort-counts.txt"


## 3. Count SNPs in Sub-Cohorts

if [[ -f "$cohorts" && -s "$cohorts" ]]; then
    echo "Using PLINK to count variant carriers in sub-cohorts listed in '$cohorts'..."

    # Append a new line to ensure all the values in your list are inlcuded in the while read loop
    [ -s "$cohorts" ] && [ "$(tail -c1 "$cohorts")" != "" ] && echo >> "$cohorts"
     
    # Step 1: Prepare .plink sample lists for each cohort

    while read -r line; do
        # Create a two-column file for PLINK (FID and IID — here both are the sample ID)
        awk '{ print $1, $1 }' "$line" > "${line}.plink"
    done < "$cohorts"

    # Step 2: Process each cohort and extract genotype counts
    while read -r line; do 
        echo "Processing cohort: $line"

        # Count genotype frequencies for the cohort
        plink --bfile "$plink_file" \
            --keep "${line}.plink" \
            --freqx \
            --allow-no-sex \
            --nonfounders \
            --out "${plink_file}.$line"

        # Create a 3-column genotype matrix: Hom_A1, Het, Hom_A2
        cat <(awk -v OFS='\t' 'BEGIN { print "Hom_A1", "Het", "Hom_A2" }') \
            <(awk -v OFS='\t' 'NR > 1 { print $5, $6, $7 }' "${plink_file}.$line.frqx") \
            > "${plink_file}.$line.geno"

        # Prefix headers with the cohort name for clarity
        sed -i "s/Hom_A1/${line}.Hom_A1/" "${plink_file}.$line.geno" 
        sed -i "s/Het/${line}.Het/" "${plink_file}.$line.geno"
        sed -i "s/Hom_A2/${line}.Hom_A2/" "${plink_file}.$line.geno"

        # Append this cohort's genotype counts to the main cohort counts matrix
        echo "Adding counts for $line to the aggregated cohort count file..."
        paste "${plink_file}.cohort-counts.txt" "${plink_file}.$line.geno" > "${plink_file}.cohort-counts.temp"
        mv "${plink_file}.cohort-counts.temp" "${plink_file}.cohort-counts.txt"

    done < "$cohorts"

    # Move final result to annovar_file prefix for consistency
    mv "${plink_file}.cohort-counts.txt" "${annovar_file}.cohort-counts.txt"

else    
    echo "Cohorts file not found or empty. Skipping sub-cohort analysis."
    echo "Using counts from the entire cohort only."
fi


## Final Check: Confirm that the variant counts file was generated successfully

if [[ -s "${annovar_file}.cohort-counts.txt" ]]; then
    echo "Variant counts successfully written to: ${annovar_file}.cohort-counts.txt"
else
    echo "Error: ${annovar_file}.cohort-counts.txt was not generated or is empty. Exiting."
    exit 1  # return with a status code of 1 to indicate an error.
fi


## Remove Intermediate Files.
# You can set this to FALSE for debugging. It will keep all the plink .log files

remove_intermediate='TRUE'

if [ "$remove_intermediate" = "TRUE" ]; then
    echo "Removing intermediate files..."
    
    # Remove all files matching the .plink.* pattern
    rm -f ./*.plink* 2>/dev/null

    echo "Intermediate files removed."
fi


## 4. Merge Variant Annotations and Genotype Counts Using Python

# Extract selected annotation columns (1–10 and 16) from the ANNOVAR results
cut -f1-10,16 "${annovar_file}.txt" > "${annovar_file}.variants.txt"

echo "Merging annotations and genotype counts using Python..."

# Execute embedded Python code using a heredoc
python3 - <<EOF
import pandas as pd

# Load the annotation and genotype count tables
annotations = pd.read_table("${annovar_file}.variants.txt", low_memory=False)
counts = pd.read_table("${annovar_file}.cohort-counts.txt", low_memory=False)

# Merge on 'ID' to align variant annotations with genotype counts
# A left join ensures all variants from the annotation file are preserved,
# even if they are absent in the PLINK count results (e.g., multiallelic variants)
merged = pd.merge(annotations, counts, on='ID', how='left')

# Output the merged table to a TSV file
merged.to_csv("${annovar_file}.annotated-variant-counts.tsv", sep='\t', index=False)
EOF


## Final Check: Confirm Annotated Variant Counts Were Generated

if [[ -s "${annovar_file}.annotated-variant-counts.tsv" ]]; then
    echo "Annotated variants and their respective allele counts were written to: ${annovar_file}.annotated-variant-counts.tsv"
else
    echo "Error: ${annovar_file}.annotated-variant-counts.tsv was not properly generated. Exiting script."
    exit 1  # Use 'exit' in standalone scripts
fi

echo "Finished at: $(date)"

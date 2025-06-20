#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:      Dylan Lu
# Created:     2025-06-18
# Description: Script to process tsv output from "count-variation.sh"

import argparse 
import pandas as pd
import json
import os 
import sys


# Given a DataFrame row and a mapping of gene→isoform IDs, extract the protein change, amino acid, and exon number for matching isoforms.
# Only applies to rows where Func.refGene == 'exonic'.
# Returns (variant, AA_number, exon_num) or (None, None, "") if no match.

def extract_variant(row, desired_isoforms):

    # Skip extraction if this row isn't exonic
    if row.get("Func.refGene") != "exonic":
        return None, None, ""

    # Split the AAChange.refGene field into individual isoform entries
    isoform_entries = row.get("AAChange.refGene", "").split(",")
    for entry in isoform_entries:
        parts = entry.split(":")
        if len(parts) < 4:
            continue  # skip non-matching entries

        gene_name, isoform_id, exon_field = parts[0], parts[1], parts[2]
        # Only proceed if this gene and isoform match our desired list
        if gene_name not in desired_isoforms or desired_isoforms[gene_name] != isoform_id:
            continue

        # Extract exon number by removing non-digits
        exon_num = ''.join(filter(str.isdigit, exon_field))

        # Extract the variant string (remove leading 'p.' if present)
        var = parts[-1]
        if var.startswith("p."):
            var = var[2:]
        # Extract amino acid position inside parentheses
        aa_number = var[1:-1] if len(var) > 2 else ""

        return var, aa_number, exon_num

    # No matching isoform found
    return None, None, ""

# Load the gene→isoform mapping from either a JSON file or a JSON string.
# Exits on parse errors.

def load_isoforms(mapping_str):

    if os.path.isfile(mapping_str):
        with open(mapping_str) as f:
            return json.load(f)
    try:
        return json.loads(mapping_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing isoforms mapping: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    # Set up argument Parser with descriptions and defaults
    parser = argparse.ArgumentParser(
        description="Extract SNVs for specified isoforms and include extra columns, excluding any column containing 'A2'."
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="Path to the input TSV file with annotated variant counts"
    )
    parser.add_argument(
        "-m", "--isoforms", required=True,
        help="JSON mapping or path to JSON file of gene to isoform IDs"
    )
    parser.add_argument(
        "-o", "--output-dir", default="data",
        help="Directory where per-gene TSV outputs will be written"
    )
    parser.add_argument(
        "--func-refGene", dest="func_ref",
        nargs="+", choices=["exonic", "splicing"], default=["exonic", "splicing"],
        help="One or more Func.refGene annotation values to include (default: exonic and splicing)"
    )
    parser.add_argument(
        "--exonicFunc-refGene", dest="exonic_func",
        nargs="+",
        choices=[
            "synonymous SNV", "nonsynonymous SNV",
            "frameshift deletion", "nonframeshift deletion",
            "stopgain", "stoploss"
        ],
        default=[
            "nonsynonymous SNV", "frameshift deletion",
            "nonframeshift deletion", "stopgain", "stoploss"
        ],
        help="One or more ExonicFunc.refGene values to include; default excludes synonymous SNV"
    )
    args = parser.parse_args()

    # Load the desired isoform mapping
    desired_isoforms = load_isoforms(args.isoforms)

    # Read input TSV into a DataFrame (fill missing with empty strings)
    df = pd.read_csv(args.input, sep="\t", low_memory=False).fillna("")

    # Filter rows by Func.refGene and ExonicFunc.refGene values
    df_filtered = df[
        df.get("Func.refGene").isin(args.func_ref) &
        df.get("ExonicFunc.refGene").isin(args.exonic_func)
    ]
    if df_filtered.empty:
        print("No rows after filtering. Check filter criteria.", file=sys.stderr)
        sys.exit(1)

    # Determine extra columns: from the 14th onward, skipping any containing 'A2'
    all_cols = df.columns.tolist()
    extra_cols = [c for c in all_cols[13:] if 'A2' not in c]

    # Iterate over filtered rows and extract variants + extra data
    records = []
    for _, row in df_filtered.iterrows():
        variant, aa, exon = extract_variant(row, desired_isoforms)
        if variant is None:
            continue  # skip if no matching isoform

        # Build output record
        record = {
            "Gene.refGene": row["Gene.refGene"],
            "variant": variant,
            "AA": aa,
            "exon": exon,
        }
        # Append values for extra columns
        for col in extra_cols:
            record[col] = row[col]
        records.append(record)

    # Create output DataFrame and ensure output directory exists
    result_df = pd.DataFrame(records)
    os.makedirs(args.output_dir, exist_ok=True)

    # Write one TSV per gene in the mapping
    for gene in desired_isoforms:
        gene_df = result_df[result_df["Gene.refGene"] == gene]
        if gene_df.empty:
            print(f"No variants found for {gene} selected isoform {desired_isoforms[gene]}. Skipping.", file=sys.stderr)
            continue
        out_path = os.path.join(args.output_dir, f"{gene}:{desired_isoforms[gene]}")
        # The file will be saved as a tab-separated file, but without the .tsv extension unless you include it in the filename.
        # out_path = os.path.join(args.output_dir, f"{gene}:{desired_isoforms[gene]}.tsv")
        gene_df.to_csv(out_path, sep="\t", index=False)
        print(f"Wrote {len(gene_df)} records to {out_path}")

if __name__ == "__main__":
    main()

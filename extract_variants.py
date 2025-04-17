"""
extract_variants.py

Extracts exonic nonsynonymous SNV variants for specified isoforms from a tab-delimited annotated TSV file
and exports per-gene variant files.

Usage:
    python extract_variants.py \
        --input raw_data/redlat/redlat.genes.chr.counts.hg38_multianno.tsv \
        --isoforms '{"PSEN1": "NM_000021", "PSEN2": "NM_000447", "TARDBP": "NM_007375", "MAPT": "NM_005910"}' \
        --output-dir data/custom
"""
import argparse
import pandas as pd
import json
import os
import sys

def extract_variant(row, desired_isoforms):
    isoform_entries = row.get("AAChange.refGene", "").split(",")
    all_affected = row.get("All_affected", "")
    all_unaffected = row.get("All_unaffected", "")

    # parse counts: expecting format "x/total"
    try:
        case_cnt = int(all_affected.split("/")[1])
    except (IndexError, ValueError):
        case_cnt = 0
    try:
        control_cnt = int(all_unaffected.split("/")[1])
    except (IndexError, ValueError):
        control_cnt = 0

    for entry in isoform_entries:
        parts = entry.split(":")
        if len(parts) < 4:
            continue
        gene_name, isoform_id, exon = parts[0], parts[1], parts[2]
        if gene_name not in desired_isoforms:
            continue
        if desired_isoforms[gene_name] != isoform_id:
            continue
        # extract amino acid variant (strip 'p.' prefix if present)
        var = parts[-1]
        if var.startswith("p."):
            var = var[2:]
        aa_number = var[1:-1] if len(var) > 2 else ""
        return var, aa_number, case_cnt, control_cnt, exon

    return None, None, 0, 0, ""

def load_isoforms(mapping_str):
    # load JSON mapping from string or file path
    if os.path.isfile(mapping_str):
        with open(mapping_str) as f:
            return json.load(f)
    try:
        return json.loads(mapping_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing isoforms mapping: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Extract exonic nonsynonymous SNV variants for specified isoforms.")
    parser.add_argument("-i", "--input", required=True, help="Input TSV file path")
    parser.add_argument("-m", "--isoforms", required=True, help="JSON mapping or path to JSON file of gene to isoform IDs")
    parser.add_argument("-o", "--output-dir", default="data", help="Directory to write output files")
    parser.add_argument("--func-refGene", dest="func_ref", default="exonic", help="Value for Func.refGene to filter")
    parser.add_argument("--exonicFunc-refGene", dest="exonic_func", default="nonsynonymous SNV", help="Value for ExonicFunc.refGene to filter")
    args = parser.parse_args()

    desired_isoforms = load_isoforms(args.isoforms)

    df = pd.read_csv(args.input, sep="\t", low_memory=False)
    df_filtered = df[
        (df.get("Func.refGene") == args.func_ref) &
        (df.get("ExonicFunc.refGene") == args.exonic_func)
    ]

    if df_filtered.empty:
        print("No rows after filtering. Check filter criteria.", file=sys.stderr)
        sys.exit(1)

    # apply variant extraction
    variants = df_filtered.apply(lambda row: extract_variant(row, desired_isoforms), axis=1, result_type="expand")
    variants.columns = ["variant", "AA", "case", "control", "exon"]

    df_filtered = pd.concat([df_filtered, variants], axis=1)
    df_filtered = df_filtered.dropna(subset=["AA"])
    df_filtered["case"] = df_filtered["case"].astype(int)
    df_filtered["control"] = df_filtered["control"].astype(int)

    os.makedirs(args.output_dir, exist_ok=True)
    for gene in desired_isoforms:
        gene_df = df_filtered[df_filtered.get("Gene.refGene") == gene]
        if gene_df.empty:
            print(f"No variants found for {gene}")
            continue
        out_file = os.path.join(args.output_dir, f"{gene}_variants.txt")
        cols = ["Gene.refGene", "AA", "variant", "case", "control", "exon"]
        gene_df.to_csv(out_file, sep="\t", index=False, columns=cols)
        print(f"Wrote {len(gene_df)} records to {out_file}")

if __name__ == "__main__":
    main()

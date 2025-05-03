import argparse
import pandas as pd
import json
import os
import sys

def parse_counts(cell):
    try:
        parts = cell.split("/")
        return int(parts[0]), int(parts[1])  # het, hom
    except (AttributeError, IndexError, ValueError):
        return 0, 0

def extract_variant(row, desired_isoforms):
    isoform_entries = row.get("AAChange.refGene", "").split(",")
    for entry in isoform_entries:
        parts = entry.split(":")
        if len(parts) < 4:
            continue
        gene_name, isoform_id, exon = parts[0], parts[1], parts[2]
        if gene_name not in desired_isoforms:
            continue
        if desired_isoforms[gene_name] != isoform_id:
            continue
        var = parts[-1]
        if var.startswith("p."):
            var = var[2:]
        aa_number = var[1:-1] if len(var) > 2 else ""
        return var, aa_number, exon
    return None, None, ""

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
    parser = argparse.ArgumentParser(description="Extract SNVs with cohort-level counts for specified isoforms.")
    parser.add_argument("-i", "--input", required=True, help="Input TSV file path")
    parser.add_argument("-m", "--isoforms", required=True, help="JSON mapping or path to JSON file of gene to isoform IDs")
    parser.add_argument("-o", "--output-dir", default="data", help="Directory to write output files")
    parser.add_argument("--func-refGene", dest="func_ref", default="exonic", help="Value for Func.refGene to filter")
    parser.add_argument("--exonicFunc-refGene", dest="exonic_func", default="nonsynonymous SNV", help="Value for ExonicFunc.refGene to filter")
    args = parser.parse_args()

    desired_isoforms = load_isoforms(args.isoforms)
    df = pd.read_csv(args.input, sep="\t", low_memory=False).fillna("0/0/0")

    df_filtered = df[
        (df.get("Func.refGene") == args.func_ref) &
        (df.get("ExonicFunc.refGene") == args.exonic_func)
    ]

    if df_filtered.empty:
        print("No rows after filtering. Check filter criteria.", file=sys.stderr)
        sys.exit(1)

    records = []
    for _, row in df_filtered.iterrows():
        variant, aa, exon = extract_variant(row, desired_isoforms)
        if variant is None:
            continue

        gene = row["Gene.refGene"]

        het_case, hom_case = parse_counts(row["All_affected"])
        het_control, hom_control = parse_counts(row["All_unaffected"])

        ad_het, ad_hom = parse_counts(row["AD"])
        eod_het, eod_hom = parse_counts(row["EOD"])
        ftld_het, ftld_hom = parse_counts(row["FTLD-MND"])
        aao65_het, aao65_hom = parse_counts(row["Neurodegeneration_aao<65"])
        healthy_het, healthy_hom = parse_counts(row["Healthy>70"])

        records.append({
            "Gene.refGene": gene,
            "variant": variant,
            "AA": aa,
            "exon": exon,
            "het_case": het_case,
            "hom_case": hom_case,
            "het_control": het_control,
            "hom_control": hom_control,
            "ad_het": ad_het,
            "ad_hom": ad_hom,
            "eod_het": eod_het,
            "eod_hom": eod_hom,
            "ftld_het": ftld_het,
            "ftld_hom": ftld_hom,
            "aao65_het": aao65_het,
            "aao65_hom": aao65_hom,
            "healthy_het": healthy_het,
            "healthy_hom": healthy_hom,
        })

    result_df = pd.DataFrame(records)
    os.makedirs(args.output_dir, exist_ok=True)

    for gene in desired_isoforms:
        gene_df = result_df[result_df["Gene.refGene"] == gene]
        if gene_df.empty:
            print(f"No variants found for {gene}")
            continue

        out_path = os.path.join(args.output_dir, f"{gene}")
        gene_df.to_csv(out_path, sep="\t", index=False)
        print(f"Wrote {len(gene_df)} records to {out_path}")

if __name__ == "__main__":
    main()

from shiny import App, ui, render
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text
import os

# Get available files in output directory
def get_files(pattern):
    return [f"output/{f}" for f in os.listdir("output") if pattern in f]

# Shiny UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("domain_file", "Select Domain File:", get_files("_domains.txt")),
        ui.input_select("variant_file", "Select Variant File:", get_files("_variants.txt"))
    ),
    ui.output_plot("gene_variant_plot")
)

# Server logic
def server(input, output, session):
    
    @output
    @render.plot
    def gene_variant_plot():
        df_var = pd.read_csv(input.variant_file(), sep="\t")
        df_dom = pd.read_csv(input.domain_file(), sep="\t")
        
        fig, ax = plt.subplots(figsize=(12, 4))
        
        # Plot gene domains
        for _, row in df_dom.iterrows():
            ax.plot([row['AA_start'], row['AA_end']], [0, 0], linewidth=8)
        
        # Plot variants
        ax.scatter(df_var["AA"], [0] * len(df_var), s=50, label="Variants")
        
        # Add labels with adjustText
        texts = []
        for _, row in df_var.iterrows():
            texts.append(ax.text(row['AA'], 0.1, row['variant'], rotation=90, fontsize=8, ha='center'))
            texts.append(ax.text(row['AA'], 0.2, str(row['case']), fontsize=8, ha='center'))
            texts.append(ax.text(row['AA'], 0.25, str(row['control']), fontsize=8, ha='center'))
        
        adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))
        
        ax.set_xlim(0, max(df_var['AA']) + 50)
        ax.set_xticks(range(0, max(df_var['AA']) + 100, 200))
        ax.set_yticks([])
        ax.set_xlabel("NPC1")
        ax.set_title("NPC1 Variants and Domains")
        
        return fig

app = App(app_ui, server)
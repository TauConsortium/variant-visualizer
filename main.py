import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import itertools
import os

# Get predefined files from the output directory
output_dir = "output"
files = [f for f in os.listdir(output_dir) if f.endswith(".txt")]

def load_data(variant_file):
    variants = pd.read_csv(f"{output_dir}/{variant_file}", delimiter="\t")
    return variants

def create_figure(variants):
    fig = go.Figure()

    # Define a visually distinct color palette
    colors = itertools.cycle([
        "#1f77b4",  # Muted Blue
        "#ff7f0e",  # Safety Orange
        "#2ca02c",  # Cooked Asparagus Green
        "#d62728",  # Brick Red
        "#9467bd",  # Muted Purple
        "#8c564b",  # Chestnut Brown
        "#e377c2",  # Raspberry Pink
        "#7f7f7f",  # Middle Gray
        "#bcbd22",  # Curry Yellow-Green
        "#17becf"   # Blue-Teal
    ])

    # Assign a unique color to each exon
    exon_colors = {}
    legend_shown = set()

    # Add variants as points colored by exon
    for _, row in variants.iterrows():
        exon_name = row['exon']

        if exon_name not in exon_colors:
            exon_colors[exon_name] = next(colors)  # Assign a new color

        show_legend = exon_name not in legend_shown
        legend_shown.add(exon_name)

        fig.add_trace(go.Scatter(
            x=[row['AA']],
            y=[0],
            mode='markers+text',
            marker=dict(color=exon_colors[exon_name], size=10),
            text=row['variant'],
            textposition='top center',
            name=exon_name if show_legend else None,  # Show legend only once
            showlegend=show_legend,
            hoverinfo='skip'  # Disable hover
        ))

        # Add case count label
        fig.add_trace(go.Scatter(
            x=[row['AA']],
            y=[0.2],
            mode='text',
            text=str(row['case']),
            textposition='top center',
            textfont=dict(size=14),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Add control count label
        fig.add_trace(go.Scatter(
            x=[row['AA']],
            y=[0.3],
            mode='text',
            text=str(row['control']),
            textposition='top center',
            textfont=dict(size=14),
            showlegend=False,
            hoverinfo='skip'
        ))

    fig.add_trace(go.Scatter(
        x=[0], y=[0.2], mode='text', text="Cases", textposition='top center',
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=[0], y=[0.3], mode='text', text="Controls", textposition='top center',
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        title="Gene Variant Visualization (Colored by Exon)",
        xaxis=dict(title="Amino Acid Position", tickmode='linear', dtick=200),
        yaxis=dict(visible=False),
        showlegend=True,
        height=500
    )

    return fig

# Dash App Setup
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Gene Variant Visualization"),
    dcc.Dropdown(
        id='variant-file-dropdown',
        options=[{'label': f, 'value': f} for f in files if "variants" in f],
        value=files[0] if files else None,
        clearable=False
    ),
    dcc.Graph(id='variant-graph')
])

@app.callback(
    Output('variant-graph', 'figure'),
    Input('variant-file-dropdown', 'value')
)
def update_graph(selected_variant_file):
    if not selected_variant_file:
        return go.Figure()
    variants = load_data(selected_variant_file)
    return create_figure(variants)

if __name__ == "__main__":
    app.run_server(debug=True)

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
    exon_points = {}
    legend_shown = set()

    # Group variants by exon, collecting x, y, and hover text
    for _, row in variants.iterrows():
        exon_name = row['exon']
        if exon_name not in exon_colors:
            exon_colors[exon_name] = next(colors)  # Assign a new color
        
        if exon_name not in exon_points:
            exon_points[exon_name] = {
                'x': [],
                'y': [],
                'hover': []
            }
        
        exon_points[exon_name]['x'].append(row['AA'])
        exon_points[exon_name]['y'].append(0)  # all points at y=0
        # Build a hover string with variant, case, and control info
        hover_str = (
            f"Variant: {row['variant']}<br>"
            f"Cases: {row['case']}<br>"
            f"Controls: {row['control']}"
        )
        exon_points[exon_name]['hover'].append(hover_str)

    # Add one scatter trace per exon
    for exon_name, points in exon_points.items():
        show_legend = exon_name not in legend_shown
        legend_shown.add(exon_name)

        fig.add_trace(go.Scatter(
            x=points['x'],
            y=points['y'],
            mode='lines+markers',
            line=dict(color=exon_colors[exon_name], width=2),
            marker=dict(color=exon_colors[exon_name], size=10),
            text=points['hover'],
            hoverinfo='text',         # Only show the text on hover
            name=exon_name if show_legend else None,
            showlegend=show_legend
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

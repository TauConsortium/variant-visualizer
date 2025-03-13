import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import os

# Get predefined files from the output directory
output_dir = "output"
files = [f for f in os.listdir(output_dir) if f.endswith(".txt")]

def load_data(variant_file):
    variants = pd.read_csv(f"{output_dir}/{variant_file}", delimiter="\t")
    domain_file = variant_file.replace("variants", "domains")
    if os.path.exists(f"{output_dir}/{domain_file}"):
        domains = pd.read_csv(f"{output_dir}/{domain_file}", delimiter="\t")
    else:
        domains = None
    return domains, variants

import itertools

import itertools
import plotly.graph_objects as go

def create_figure(domains, variants):
    fig = go.Figure()

    # ChatGPT colors lol
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

    # Assign a unique color to each domain
    domain_colors = {}
    legend_shown = set()  # Keep track of which domains are already in the legend

    # Add gene domains if available
    if domains is not None:
        for _, row in domains.iterrows():
            domain_name = row['Domain']

            if domain_name not in domain_colors:
                domain_colors[domain_name] = next(colors)  # Assign a new color

            show_legend = domain_name not in legend_shown  # Show in legend only once
            legend_shown.add(domain_name)

            fig.add_trace(go.Scatter(
                x=[row['AA_start'], row['AA_end']],
                y=[0, 0],
                mode='lines',
                line=dict(width=8, color=domain_colors[domain_name]),
                name=domain_name if show_legend else None,  # Avoid duplicate names
                showlegend=show_legend,
                hoverinfo="skip"
            ))

    # Add variants as points with case/control counts
    for _, row in variants.iterrows():
        color = "red" if row['control'] == 0 else "black"
        fig.add_trace(go.Scatter(
            x=[row['AA']],
            y=[0],
            mode='markers+text',
            marker=dict(color=color, size=10),
            text=row['variant'],
            textposition='top center',
            name=row['variant'],
            showlegend=False
        ))

        # Add case count label
        fig.add_trace(go.Scatter(
            x=[row['AA']],
            y=[0.2],
            mode='text',
            text=str(row['case']),
            textposition='top center',
            textfont=dict(size=14),
            showlegend=False
        ))

        # Add control count label
        fig.add_trace(go.Scatter(
            x=[row['AA']],
            y=[0.3],
            mode='text',
            text=str(row['control']),
            textposition='top center',
            textfont=dict(size=14),
            showlegend=False
        ))

    fig.add_trace(go.Scatter(
        x=[0], y=[0.2], mode='text', text="Cases", textposition='top center',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=[0], y=[0.3], mode='text', text="Controls", textposition='top center',
        showlegend=False
    ))

    fig.update_layout(
        title="NPC1 Gene and Variant Visualization",
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
    domains, variants = load_data(selected_variant_file)
    return create_figure(domains, variants)

if __name__ == "__main__":
    app.run_server(debug=True)

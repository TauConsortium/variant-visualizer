import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import os

# Get predefined files from the output directory
output_dir = "output"
files = [f for f in os.listdir(output_dir) if f.endswith(".txt")]

def load_data(variant_file):
    NPC1_variants = pd.read_csv(f"{output_dir}/{variant_file}", delimiter="\t")
    domain_file = variant_file.replace("variants", "domains")
    if os.path.exists(f"{output_dir}/{domain_file}"):
        NPC1_domains = pd.read_csv(f"{output_dir}/{domain_file}", delimiter="\t")
    else:
        NPC1_domains = None
    return NPC1_domains, NPC1_variants

def create_figure(NPC1_domains, NPC1_variants):
    fig = go.Figure()
    
    # Add gene domains if available
    if NPC1_domains is not None:
        unique_domains = set()
        for _, row in NPC1_domains.iterrows():
            if row['Domain'] not in unique_domains:
                fig.add_trace(go.Scatter(
                    x=[row['AA_start'], row['AA_end']],
                    y=[0, 0],
                    mode='lines',
                    line=dict(width=8),
                    name=row['Domain']
                ))
                unique_domains.add(row['Domain'])
            else:
                fig.add_trace(go.Scatter(
                    x=[row['AA_start'], row['AA_end']],
                    y=[0, 0],
                    mode='lines',
                    line=dict(width=8),
                    showlegend=False
                ))
    
    # Add variants as points with case/control counts
    for _, row in NPC1_variants.iterrows():
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
    NPC1_domains, NPC1_variants = load_data(selected_variant_file)
    return create_figure(NPC1_domains, NPC1_variants)

if __name__ == "__main__":
    app.run_server(debug=True)

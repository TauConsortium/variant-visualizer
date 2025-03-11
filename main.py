import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

# Load data
NPC1_domains = pd.read_csv("output/NPC1_domains.txt", delimiter="\t")
NPC1_variants = pd.read_csv("output/NPC1_variants.txt", delimiter="\t")

# Create figure combining gene domains and variants
fig = go.Figure()

# Add gene domains without duplicate legend entries
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
        textfont=dict(size=10),
        showlegend=False
    ))
    
    # Add control count label
    fig.add_trace(go.Scatter(
        x=[row['AA']],
        y=[0.3],
        mode='text',
        text=str(row['control']),
        textposition='top center',
        textfont=dict(size=10),
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

# Dash App Layout
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Gene Variant Visualization"),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run_server(debug=True)

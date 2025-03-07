import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the variants data
variants = pd.read_csv("variants.txt", sep="\t")  # Adjust separator if needed

# Create scatter plot
fig = go.Figure()

for _, row in variants.iterrows():
    color = "crimson" if row["control"] == 0 else "black"
    if row["case"] == 0 and row["control"] == 0:
        continue
    
    fig.add_trace(go.Scatter(
        x=[row["AA"]],
        y=[0],
        mode="markers+text",
        marker=dict(color=color, size=10),
        text=[row["variant"]],
        textposition="top center",
        name=row["variant"]
    ))
    
    fig.add_trace(go.Scatter(
        x=[row["AA"]],
        y=[0.1],
        mode="text",
        text=[str(row["case"])],
        textposition="middle center",
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=[row["AA"]],
        y=[0.15],
        mode="text",
        text=[str(row["control"])],
        textposition="middle center",
        showlegend=False
    ))

# Update layout
fig.update_layout(
    title="Variants and Case/Control Counts",
    xaxis_title="Amino Acid Position",
    yaxis=dict(
        title="Case / Control Counts",
        tickvals=[0.1, 0.15],
        ticktext=["Cases", "Controls"],
        showgrid=False
    ),
    showlegend=False
)

# Dash app setup
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Variants Visualization"),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run_server(debug=True)
import matplotlib
matplotlib.use("Agg")  # Use a non-GUI backend

import dash
from dash import dcc, html, Input, Output
import pandas as pd
import matplotlib.pyplot as plt
import os
from adjustText import adjust_text
import io
import base64


# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server  # Needed for deployment

# Path to the output directory
output_dir = "output"

# Get available files in the output directory
files = [f for f in os.listdir(output_dir) if f.endswith(".txt")]

# Layout of the app
app.layout = html.Div([
    html.H1("Variants Visualizer"),
    dcc.Dropdown(
        id="file-dropdown",
        options=[{"label": f, "value": f} for f in files],
        placeholder="Select a file",
    ),
    html.Img(id="plot-image"),
])

@app.callback(
    Output("plot-image", "src"),
    Input("file-dropdown", "value")
)
def update_plot(selected_file):
    if not selected_file:
        return ""
    
    file_path = os.path.join(output_dir, selected_file)
    
    # Load the data
    variants = pd.read_csv(file_path, sep="\t")  # Adjust separator if needed

    # Set up the figure
    fig, ax = plt.subplots(figsize=(12, 4))
    texts = []
    
    # Scatter plot for variants
    for _, row in variants.iterrows():
        color = "red" if row["control"] == 0 else "black"
        if row["case"] == 0 and row["control"] == 0:
            continue
        ax.scatter(row["AA"], 0, color=color, s=50)
        texts.append(ax.text(
            row["AA"], 0.05, f"{row['variant']} ({row['case']} / {row['control']})", 
            rotation=90, ha="center", fontsize=8, color=color
        ))
    
    # Adjust text to prevent overlap
    adjust_text(texts, arrowprops=dict(arrowstyle="-", color="gray", lw=0.5))

    # Formatting
    ax.set_xlim(0, variants["AA"].max() + 50)
    ax.set_ylim(-0.05, 0.2)
    ax.set_xlabel("Amino Acid Position", fontsize=12)
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    plt.title("Variants and Case/Control Counts", fontsize=14)
    
    # Save the plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    encoded_image = base64.b64encode(buf.read()).decode("utf-8")
    
    return f"data:image/png;base64,{encoded_image}"

if __name__ == "__main__":
    app.run_server(debug=True)

import matplotlib
matplotlib.use("Agg")

import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import matplotlib.pyplot as plt
import os
import io
import base64

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Needed for deployment

# Path to the output directory
data_dir = "data"
datasets = ["tangl", "redlat", "custom"]

# Layout of the app
app.layout = html.Div([
    dcc.Tabs(
        id="dataset-tabs",
        value='redlat',
        children=[dcc.Tab(label=ds.upper(), value=ds) for ds in datasets],
        style={"marginBottom": "20px", "fontSize": "12px", "height": "36px"}
    ),

    html.Div(id="upload-container"),

    dcc.Store(id="custom-file-store"),

    dcc.Dropdown(
        id="file-dropdown",
        placeholder="Select a file",
        value=os.path.join("redlat", "TARDBP_variants.txt")
    ),

    html.Img(id="plot-image", style={'width': '100%', 'height': 'auto'}),

    html.Div([
        html.P("If you use any of our data, please cite us:", style={"fontWeight": "bold"}),
        html.P("TANGL: Acosta-Uribe, J., Aguill\u00f3n, D., Cochran, J. N., Giraldo, M., Madrigal, L., Killingsworth, B. W., ... & Kosik, K. S. (2022). A neurodegenerative disease landscape of rare mutations in Colombia due to founder effects. *Genome Medicine*, 14(1), 27."),
        html.P("ReDLat: Acosta-Uribe, J., Escudero, S. D. P., Cochran, J. N., Taylor, J. W., Castruita, P. A., Jonson, C., ... & Yokoyama, J. S. (2024). Genetic Contributions to Alzheimer\u2019s Disease and Frontotemporal Dementia in Admixed Latin American Populations. *medRxiv*.")
    ], style={"marginTop": "40px", "padding": "10px", "borderTop": "1px solid #ccc", "fontSize": "16px"})
])

@app.callback(
    Output("upload-container", "children"),
    Input("dataset-tabs", "value")
)
def toggle_upload(tab):
    if tab != "custom":
        return []
    return dcc.Upload(
        id="upload-data",
        children=html.Div(["Drag and Drop or ", html.A("Select a .txt File")]),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "marginBottom": "10px",
        },
        multiple=False,
    )

@app.callback(
    Output("custom-file-store", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def store_uploaded_file(content, filename):
    if content is None or not filename.endswith(".txt"):
        return None

    content_type, content_string = content.split(",")
    decoded = base64.b64decode(content_string)

    os.makedirs(os.path.join(data_dir, "custom"), exist_ok=True)
    save_path = os.path.join("custom", filename)
    with open(os.path.join(data_dir, save_path), "wb") as f:
        f.write(decoded)

    return save_path

@app.callback(
    Output("file-dropdown", "options"),
    Input("dataset-tabs", "value"),
    Input("custom-file-store", "data")
)
def update_file_options(selected_dataset, uploaded_path):
    options = []
    if selected_dataset:
        folder_path = os.path.join(data_dir, selected_dataset)
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
            options = [{"label": f, "value": os.path.join(selected_dataset, f)} for f in files]

    if selected_dataset == "custom" and uploaded_path and uploaded_path.endswith(".txt"):
        options.append({"label": f"[Uploaded] {os.path.basename(uploaded_path)}", "value": uploaded_path})

    return options

@app.callback(
    Output("plot-image", "src"),
    Input("file-dropdown", "value")
)
def update_plot(selected_file):
    if not selected_file:
        return ""

    file_path = os.path.join(data_dir, selected_file)

    variants = pd.read_csv(file_path, sep="\t")
    exon_ranges = variants.groupby("exon")["AA"].agg(["min", "max"]).reset_index()

    fig, ax = plt.subplots(figsize=(12, 4), dpi=100)

    variants = variants.sort_values("AA").reset_index(drop=True)
    grouped_variants = []
    cluster = [variants.iloc[0]]
    cluster_distance = 10

    for i in range(1, len(variants)):
        current = variants.iloc[i]
        previous = cluster[-1]
        same_exon = current["exon"] == previous["exon"]
        close_by = abs(current["AA"] - previous["AA"]) <= cluster_distance

        if same_exon and close_by:
            cluster.append(current)
        else:
            grouped_variants.append(cluster)
            cluster = [current]
    grouped_variants.append(cluster)

    for cluster in grouped_variants:
        x = sum(v["AA"] for _, v in pd.DataFrame(cluster).iterrows()) / len(cluster)
        base_y = -0.07
        y = -0.03
        color = "crimson" if all(v["control"] == 0 for _, v in pd.DataFrame(cluster).iterrows()) else "black"

        ax.vlines(x, base_y, y, color=color, linewidth=1)

        for i, (_, v) in enumerate(pd.DataFrame(cluster).iterrows()):
            offset = -i * 0.005
            ax.scatter(x, y + offset, color=color, s=10, zorder=3)

        label = "\n".join([f"{v['variant']} ({v['case']} / {v['control']})" for _, v in pd.DataFrame(cluster).iterrows()])
        ax.text(x, y + len(cluster)*0.003 + 0.01, label, rotation=90, ha="center", fontsize=8, color=color)

    exon_y = -0.08
    colors = plt.cm.Paired.colors
    exon_legend = {}

    for i, (_, exon) in enumerate(exon_ranges.iterrows()):
        exon_color = colors[i % len(colors)]
        min_width = 5
        exon_start, exon_end = exon["min"], exon["max"]
        if exon_end - exon_start < min_width:
            exon_start -= min_width / 2
            exon_end += min_width / 2

        ax.hlines(exon_y, exon_start, exon_end, colors=exon_color, linewidth=6, label=exon["exon"])
        exon_legend[exon["exon"]] = exon_color

    ax.set_xlim(0, variants["AA"].max() + 50)
    ax.set_ylim(-0.1, 0.25)
    ax.set_xlabel("Amino Acid Position", fontsize=12)
    ax.set_ylabel("(Case / Control)", fontsize=12)
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    handles = [plt.Line2D([0], [0], color=color, linewidth=5, label=exon) for exon, color in exon_legend.items()]
    ax.legend(handles=handles, title="Exons", loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)

    plt.title("Variants Counts in Case/Control", fontsize=14)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    encoded_image = base64.b64encode(buf.read()).decode("utf-8")

    return f"data:image/png;base64,{encoded_image}"

if __name__ == "__main__":
    app.run(debug=True)

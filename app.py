import matplotlib
matplotlib.use("Agg")

import dash
from dash import dcc, html, Input, Output, State
from dash.dependencies import ALL
import dash_bootstrap_components as dbc
import pandas as pd
import matplotlib.pyplot as plt
import os
import io
import base64
import json


# Path to the output directory
data_dir = "data"

# Specify the datasets that will be included in the app
datasets = ["tangl", "redlat"]

# Define the cohort categories and their labels
cohort_categories = [
    ("all", "All Participants"),
    ("ad", "AD"),
    ("eod", "EOD"),
    ("ftld-mnd", "FTLD-MND"),
    ("ftd", "FTD"),
    ("aao", "AAO < 65"),
    ("healthy", "Healthy > 70"),
]

# Assign the titles for each plot based on the cohort
custom_titles = {
    "all": "Variant counts in all participants",
    "ad": " Variant counts in the Alzheimer’s disease cohort",
    "eod": "Variant counts in the Early Onset Dementia cohort",
    "ftd": "Variant counts in the Frontotemporal Dementia cohort",
    "ftld-mnd": "Variant counts in the Frontotemporal Dementia and Motor Neuron Disease cohort patients",
    "aao": "Variant counts in all the patients with early onset neurodegenerative illness (=< 65 years)",
    "healthy": "Variant counts in all the cognitively healthy individuals aged 70 and older"
}

# Legend for additional information about each dataset and cohort
legend_map = {
    "tangl": {
        "all": (
            "Variant counts represent all the 900 individuals in the TANGL cohort.\n"
            "It includes carriers of pathogenic variants like PSEN1 E280A.\n"
            "The dataset includes related individuals."
        ),
        "ad": (
            "Variant counts represent the 378 participants of the Alzheimer's disease (AD) cohort in the TANGL study.\n"
            "It includes carriers of pathogenic variants like PSEN1 E280A.\n"
            "The dataset includes related individuals."
        ),
        "eod": (
            "Variant counts represent the 74 participants of the Early Onset Dementia (EOD) cohort in the TANGL study.\n"
            "The dataset includes related individuals."
        ),
        "ftld-mnd": (
            "Variant counts represent the 193 participants of the Frontotemporal Dementia and Motor Neuron Disease (FTLD-MND) cohort patients cohort in the TANGL study.\n"
            "The dataset includes related individuals."
        ),  
        "aao": (
            "Variant counts represent the 484 patients diagnosed with AD, FTLD-MND or EOD at 65 years or younger.\n"
            "The dataset includes related individuals."
        ),
        "healthy": "Variant counts represent 119 unrelated individuals with normal cognition aged 70 years or older."
    },
    "redlat": {
        "all": (
            "Variant counts represent all the 900 individuals in the TANGL cohort.\n"
            "It includes carriers of pathogenic variants like PSEN1 E280A.\n"
            "The dataset includes related individuals."
            ),
        "ad": (
            "Variant counts represent participants with whole genome or exome from the AD cohort in the ReDLat study.\n" 
            "The dataset includes related individuals."
            ),
        "ftd": (
            "Variant counts represent participants with whole genome or exome from the FTD cohort in the ReDLat study.\n"
            "The dataset includes related individuals."
            ),
        "aao": (
            "Variant counts represent the patients diagnosed with AD or FTD at 65 years or younger.\n"
            "Some of the patients from the retrospective cohort did not have record of their age at onset and were excluded from this analysis.\n"
            "The dataset includes related individuals."
        ),
        "healthy": (
            "Variant counts represent  individuals with normal cognition aged 70 years or older.\n"
            "Some of the participants from the retrospective cohort did not have record of their age at evaluation and were excluded from this analysis.\n"
            "The dataset includes related individuals."
        )
    }
}

# Initialize the Dash app
app = dash.Dash(__name__, 
                suppress_callback_exceptions=True, 
                external_stylesheets=[dbc.themes.MINTY])
server = app.server

# Layout of the app
app.layout = html.Div([
    html.Div([
        html.H1("Variant Visualizer", style={"marginBottom": "0", "fontWeight": "bold"}),
        html.H5("Explore allelic counts in neurodegenerative disease cohorts", style={"color": "#555", "marginTop": "3"})
    ], style={"textAlign": "center", "marginTop": "30px", "marginBottom": "20px"}),

    html.Div(
        [dbc.Button(ds.upper(),
                    id={"type": "dataset-button", "index": ds},
                    n_clicks=0,
                    color="primary",
                    className="me-2 mb-2") for ds in datasets],
        className="d-flex flex-wrap mb-3 justify-content-center"
    ),

    dcc.Store(id="selected-dataset"),
    dcc.Store(id="selected-cohort"),
    html.Div(id="cohort-button-container"),
    html.Div(id="upload-container"),
    dcc.Store(id="custom-file-store"),

    dcc.Dropdown(
        id="file-dropdown",
        placeholder="Select a gene"
    ),

    html.Img(id="plot-image", style={'width': '100%', 'height': 'auto'}),

    html.Div([
        html.P(
            "The Variant visualizer was developed by Dylan Lu, & Juliana Acosta-Uribe (2025) for Tau Bioinformatics; part of the Tau Consortium data collaboration initiative",
            style={"fontWeight": "bold", "marginBottom": "0"}
        ),
        html.P(
            "You can find the code for the variant visualizer in: https://github.com/TauConsortium/variant-visualizer ",
            style={"fontWeight": "bold", "marginTop": "0", "marginBottom": "10px"}
        ),
        html.P(
            "If you use any of our data, please cite us:",
            style={"fontWeight": "bold", "marginBottom": "3px"}
        ),
        html.P(
            "TANGL: Acosta-Uribe, J., Aguillón, D., Cochran, J. N., Giraldo, M., Madrigal, L., Killingsworth, B. W., ... & Kosik, K. S. (2022). A neurodegenerative disease landscape of rare mutations in Colombia due to founder effects. Genome Medicine, 14(1), 27.",
            style={"marginTop": "0", "marginBottom": "3px"}   
        ),
        html.P(
            "ReDLat: Acosta-Uribe, J., Piña-Escudero, S. D., Cochran, J. N., Taylor, J. W., Castruita, P. A., Jonson, C., ... Kosik, K. S. & Yokoyama, J. S. (2024). Genetic Contributions to Alzheimer’s Disease and Frontotemporal Dementia in Admixed Latin American Populations. medRxiv.",
            style={"marginTop": "0"}
        ),
    ], style={"marginTop": "40px", "padding": "5px", "borderTop": "1px solid #ccc", "fontSize": "14px"}),

    html.Img(
        src="/assets/logo.png",
        style={"display": "block", "margin": "40px auto 0 auto", "height": "60px"}
    )
])

@app.callback(
    Output("selected-dataset", "data"),
    Input({"type": "dataset-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def store_selected_dataset(n_clicks_list):
    from dash import callback_context
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    triggered_id = json.loads(triggered_id)
    return triggered_id["index"]

@app.callback(
    Output("cohort-button-container", "children"),
    Input("selected-dataset", "data"),
    prevent_initial_call=True
)
def update_cohort_buttons(selected_dataset):
    if not selected_dataset:
        return dash.no_update
    if selected_dataset == "redlat":
        allowed = {"all", "ad", "ftd", "aao", "healthy"}
    else:  # tangl
        allowed = {"all", "ad", "eod", "ftld-mnd", "aao", "healthy"}
    return html.Div(
        [dbc.Button(label, id={"type": "cohort-button", "index": val}, n_clicks=0, color="secondary", className="me-2 mb-2")
         for val, label in cohort_categories if val in allowed],
        className="d-flex flex-wrap mb-3 justify-content-center"
    )

@app.callback(
    Output("selected-cohort", "data"),
    Input({"type": "cohort-button", "index": ALL}, "n_clicks"),
    State("selected-dataset", "data"),
    prevent_initial_call=True
)
def store_selected_cohort(n_clicks_list, selected_dataset):
    from dash import callback_context
    ctx = callback_context
    if not ctx.triggered or not selected_dataset:
        return dash.no_update
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    triggered_id = json.loads(triggered_id)
    return triggered_id["index"]

@app.callback(
    Output("upload-container", "children"),
    Input("selected-dataset", "data")
)
def toggle_upload(selected_dataset):
    if selected_dataset != "custom":
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
    if content is None:
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
    Input("selected-dataset", "data"),
    Input("custom-file-store", "data")
)
def update_file_options(selected_dataset, uploaded_path):
    options = []
    if selected_dataset:
        folder_path = os.path.join(data_dir, selected_dataset)
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if not f.startswith(".")]
            files = sorted(files)  # Sort files alphabetically
            options = [{"label": f, "value": os.path.join(selected_dataset, f)} for f in files]
    if selected_dataset == "custom" and uploaded_path:
        options.append({"label": f"[Uploaded] {os.path.basename(uploaded_path)}", "value": uploaded_path})
    return options

@app.callback(
    Output("plot-image", "src"),
    Input("file-dropdown", "value"),
    Input("selected-dataset", "data"),
    Input("selected-cohort", "data"),
    State("file-dropdown", "options")
)
def update_plot(selected_file, selected_dataset, selected_cohort, dropdown_options):
    if not selected_file or not selected_dataset or not selected_cohort:
        return ""
    file_path = os.path.join(data_dir, selected_file)
    if not os.path.exists(file_path):
        return ""
    variants = pd.read_csv(file_path, sep="\t")
    variants["AA"] = pd.to_numeric(variants["AA"], errors="coerce")
    variants = variants.dropna(subset=["AA"])
    variants = variants.sort_values("AA").reset_index(drop=True)
    exon_ranges = variants.groupby("exon")["AA"].agg(["min", "max"]).reset_index()
    fig, ax = plt.subplots(figsize=(12, 4), dpi=100)
    grouped_variants = []
    cluster = [variants.iloc[0]] if not variants.empty else []
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
    if cluster:
        grouped_variants.append(cluster)
    for cluster in grouped_variants:
        het_col = f"{selected_cohort}.Het"
        hom_col = f"{selected_cohort}.Hom_A1"
        if not any((v.get(hom_col, 0) + v.get(het_col, 0)) > 0 for v in cluster):
            continue
        x = sum(v["AA"] for v in cluster) / len(cluster)
        base_y = -0.07
        y = -0.03
        color = "black"
        ax.vlines(x, base_y, y, color=color, linewidth=1)
        for i, v in enumerate(cluster):
            offset = -i * 0.005
            ax.scatter(x, y + offset, color=color, s=10, zorder=3)
        label = "\n".join([
            f"{v['variant']} ({v.get(hom_col, 0)} / {v.get(het_col, 0)})"
            for v in cluster
            if (v.get(hom_col, 0) + v.get(het_col, 0)) > 0
        ])
        ax.text(x, y + len(cluster) * 0.003 + 0.01, label, rotation=90, ha="center", fontsize=8, color=color)
    exon_y = -0.08
    exon_height = 0.005
    ax.fill_between(
        [1, variants["AA"].max() + 50],
        exon_y - exon_height / 2,
        exon_y + exon_height / 2,
        color="lightgray",
        zorder=0
    )
    colors = plt.cm.Paired.colors
    exon_legend = {}
    for i, (_, exon) in enumerate(exon_ranges.iterrows()):
        exon_color = colors[i % len(colors)]
        min_width = 5
        exon_start, exon_end = exon["min"], exon["max"]
        if exon_end - exon_start < min_width:
            exon_start -= min_width / 2
            exon_end += min_width / 2
        ax.hlines(exon_y, exon_start, exon_end, colors=exon_color, linewidth=6, label=exon["exon"], zorder=1)
        exon_legend[exon["exon"]] = exon_color
    ax.set_xlim(0, variants["AA"].max() + 50)
    ax.set_ylim(-0.1, 0.25)
    ax.set_xlabel("Amino Acid Position", fontsize=12)
    y_label = (
        "Carriers (Homozygous/Heterozygous)"
    )
    ax.set_ylabel(y_label, fontsize=8)
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    handles = [plt.Line2D([0], [0], color=color, linewidth=5, label=exon) for exon, color in exon_legend.items()]
    ax.legend(handles=handles, title="Exons", loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)
    title = custom_titles.get(selected_cohort, f"Variants in {selected_cohort.replace('_', ' ').title()}")
    plt.title(title, fontsize=14)
    if selected_dataset in legend_map and selected_cohort in legend_map[selected_dataset]:
        plt.figtext(
            0.5,
            -0.1,
            legend_map[selected_dataset][selected_cohort],
            wrap=True,
            ha="center",
            fontsize=8
        )
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    plt.close(fig)
    buf.seek(0)
    encoded_image = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded_image}"

# Uncomment to run locally
# if __name__ == "__main__":
#     app.run_server(debug=True)

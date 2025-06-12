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
server = app.server

# Path to the output directory
data_dir = "data"
datasets = ["tangl", "redlat"]
cohort_categories = [
    ("case_control", "All Participants"),
    ("ad", "AD"),
    ("eod", "EOD"),
    ("ftld-mnd", "FTLD-MND"),
    ("aao", "AAO < 65"),
    ("healthy", "Healthy > 70"),
]

custom_titles = {
    "ad": "Genetic variants in the Alzheimer’s disease sub-cohort",
    "eod": "Genetic variants in the Early Onset Dementia sub-cohort",
    "ftld-mnd": "Genetic variants in the Frontotemporal Dementia and Motor Neuron Disease  sub-cohort",
    "aao": "Genetic variants in all the patients with early onset neurodegenerative illness < 65 years",
    "healthy": "Genetic variants in all the cognitively healthy individuals aged 70 and older"
}

legend_map = {
    "tangl": {
        "case_control": (
            "Cases represents all affected individuals in the TANGL cohort. "
            "It includes carriers of pathogenic variants like PSEN1 E280A. (n=646)\n"
            "Controls represents unaffected individuals in the TANGL cohort. (n=254)\n"
            "The dataset includes related individuals."
        ),
        "ad": "Includes the 378 participants of the AD cohort in the TANGL study. The dataset includes related individuals.",
        "eod": "Includes the 74 participants of the EOD cohort in the TANGL study. The dataset includes related individuals.",
        "ftld-mnd": "Includes the 193 participants of the FTLD-MND cohort in the TANGL study. The dataset includes related individuals.",
        "aao": "Includes the 484 patients diagnosed with AD, FTLD-MND or EOD at 65 years or younger.",
        "healthy": "Includes 119 unrelated individuals with normal cognition and who are age 70 or older."
    },
    "redlat": {
        "ad": "Includes the 843 participants with whole genome or exome from the AD cohort in the ReDLat study. The dataset includes related individuals.",
        "ftld-mnd": "Includes the 272 participants with whole genome or exome from the FTD cohort in the ReDLat study. The dataset includes related individuals.",
        "healthy": "Includes 548 asymptomatic participants with whole genome or exome from the ReDLat study. The dataset includes related individuals."
    }
}



# Layout of the app
app.layout = html.Div([
    dcc.Tabs(
        id="dataset-tabs",
        value='tangl',
        children=[dcc.Tab(label=ds.upper(), value=ds) for ds in datasets],
        style={"marginBottom": "20px", "fontSize": "12px", "height": "36px"}
    ),

    html.Div(id="cohort-tab-container"),


    html.Div(id="upload-container"),
    dcc.Store(id="custom-file-store"),

    dcc.Dropdown(
        id="file-dropdown",
        placeholder="Select a file",
        value=os.path.join("tangl", "PSEN2")
    ),

    html.Img(id="plot-image", style={'width': '100%', 'height': 'auto'}),

    html.Div([
        html.P("If you use any of our data, please cite us:", style={"fontWeight": "bold"}),
        html.P("TANGL: Acosta-Uribe, J., Aguill\u00f3n, D., Cochran, J. N., Giraldo, M., Madrigal, L., Killingsworth, B. W., ... & Kosik, K. S. (2022). A neurodegenerative disease landscape of rare mutations in Colombia due to founder effects. *Genome Medicine*, 14(1), 27."),
        html.P("ReDLat: Acosta-Uribe, J., Escudero, S. D. P., Cochran, J. N., Taylor, J. W., Castruita, P. A., Jonson, C., ... & Yokoyama, J. S. (2024). Genetic Contributions to Alzheimer\u2019s Disease and Frontotemporal Dementia in Admixed Latin American Populations. *medRxiv*.")
    ], style={"marginTop": "40px", "padding": "10px", "borderTop": "1px solid #ccc", "fontSize": "16px"})
])

@app.callback(
    Output("cohort-tab-container", "children"),
    Input("dataset-tabs", "value")
)
def update_cohort_tabs(selected_dataset):
    if selected_dataset == "redlat":
        allowed = {"ad", "ftld-mnd", "healthy"}
    else:
        allowed = {val for val, _ in cohort_categories}

    filtered_tabs = [
        dcc.Tab(label=label, value=val)
        for val, label in cohort_categories if val in allowed
    ]

    # Set default tab to first in filtered list
    return dcc.Tabs(
        id="cohort-tabs",
        value=filtered_tabs[0].value if filtered_tabs else None,
        children=filtered_tabs,
        style={"marginBottom": "20px", "fontSize": "12px", "height": "36px"}
    )


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
    Input("dataset-tabs", "value"),
    Input("custom-file-store", "data")
)
def update_file_options(selected_dataset, uploaded_path):
    options = []
    if selected_dataset:
        folder_path = os.path.join(data_dir, selected_dataset)
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path)]
            options = [{"label": f, "value": os.path.join(selected_dataset, f)} for f in files]

    if selected_dataset == "custom" and uploaded_path:
        options.append({"label": f"[Uploaded] {os.path.basename(uploaded_path)}", "value": uploaded_path})

    return options

@app.callback(
    Output("plot-image", "src"),
    Input("file-dropdown", "value"),
    Input("cohort-tabs", "value"),
    Input("dataset-tabs", "value")
)
def update_plot(selected_file, selected_cohort, selected_dataset):
    if not selected_file:
        return ""

    file_path = os.path.join(data_dir, selected_file)
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
        het_col = "het_case" if selected_cohort == "case_control" else f"{selected_cohort}_het"
        hom_col = "hom_case" if selected_cohort == "case_control" else f"{selected_cohort}_hom"

        # Skip cluster if all variants are 0/0
        if not any((v.get(het_col, 0) + v.get(hom_col, 0)) > 0 for v in cluster):
            continue

        x = sum(v["AA"] for v in cluster) / len(cluster)
        base_y = -0.07
        y = -0.03

        if selected_cohort == "case_control":
            is_control_zero = all((v["het_control"] + v["hom_control"]) == 0 for v in cluster)
        else:
            is_control_zero = False  # can't define "control" for subcohorts, mark as black

        color = "crimson" if is_control_zero else "black"

        ax.vlines(x, base_y, y, color=color, linewidth=1)
        for i, v in enumerate(cluster):
            offset = -i * 0.005
            ax.scatter(x, y + offset, color=color, s=10, zorder=3)

        het_col = "het_case" if selected_cohort == "case_control" else f"{selected_cohort}_het"
        hom_col = "hom_case" if selected_cohort == "case_control" else f"{selected_cohort}_hom"

        label = "\n".join([
            f"{v['variant']} ({v.get(het_col, 0)} / {v.get(hom_col, 0)})"
            for v in cluster
            if (v.get(het_col, 0) + v.get(hom_col, 0)) > 0
        ])
        ax.text(x, y + len(cluster) * 0.003 + 0.01, label, rotation=90, ha="center", fontsize=8, color=color)


    # Fill the entire bottom with gray first
    exon_y = -0.08
    exon_height = 0.005
    ax.fill_between(
        [variants["AA"].min() - 10, variants["AA"].max() + 50],
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
        "Carriers (Hom/Het)"
    )
    ax.set_ylabel(y_label, fontsize=12)

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
            fontsize=6
        )


    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    plt.close(fig)
    buf.seek(0)
    encoded_image = base64.b64encode(buf.read()).decode("utf-8")

    return f"data:image/png;base64,{encoded_image}"

# Testing locally with `python app.py`
# if __name__ == "__main__":
#     app.run_server(debug=True)

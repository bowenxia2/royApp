from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
# ci/cd test 2

app = Dash(__name__)
server = app.server

df = pd.DataFrame({
    "x": list(range(1, 11)),
    "y1": [2, 4, 3, 5, 7, 8, 7, 9, 10, 12],
    "y2": [1, 2, 2, 3, 4, 3, 5, 6, 5, 7],
})

FEATURE_BADGE = {
    "display": "inline-block",
    "background": "#4CAF50",
    "color": "white",
    "padding": "2px 8px",
    "borderRadius": "4px",
    "fontSize": "11px",
    "fontWeight": "bold",
    "marginLeft": "8px",
    "verticalAlign": "middle",
}

app.layout = html.Div(
    [
        html.H1("Student Plotly Dash App"),
        html.P("A simple dynamic app for testing Azure VM deployment."),

        # --- EXISTING: series selector ---
        html.Label("Choose a series:"),
        dcc.Dropdown(
            id="series-dropdown",
            options=[
                {"label": "Series 1", "value": "y1"},
                {"label": "Series 2", "value": "y2"},
            ],
            value="y1",
            clearable=False,
            style={"width": "300px"},
        ),

        html.Br(),

        # --- EXISTING: multiplier slider ---
        html.Label("Multiply values by:"),
        dcc.Slider(
            id="multiplier-slider",
            min=1,
            max=5,
            step=1,
            value=1,
            marks={i: str(i) for i in range(1, 6)},
        ),

        html.Br(),

        # --- NEW FEATURE 1: Chart Type Selector ---
        html.Div([
            html.Label([
                "Chart type:",
                html.Span("NEW", style=FEATURE_BADGE),
            ]),
            dcc.RadioItems(
                id="chart-type",
                options=[
                    {"label": " Line", "value": "line"},
                    {"label": " Bar", "value": "bar"},
                    {"label": " Scatter", "value": "scatter"},
                ],
                value="line",
                inline=True,
                style={"marginTop": "6px", "gap": "20px"},
            ),
        ], style={"marginBottom": "16px"}),

        # --- NEW FEATURE 2: Show Both Series Toggle ---
        html.Div([
            html.Label([
                "Show both series:",
                html.Span("NEW", style=FEATURE_BADGE),
            ]),
            dcc.Checklist(
                id="show-both",
                options=[{"label": " Overlay Series 1 & 2 on same chart", "value": "both"}],
                value=[],
                style={"marginTop": "6px"},
            ),
        ], style={"marginBottom": "16px"}),

        dcc.Graph(id="line-chart"),

        # --- NEW FEATURE 3: Expanded Stats Panel ---
        html.Div([
            html.H4([
                "Statistics",
                html.Span("NEW", style=FEATURE_BADGE),
            ], style={"marginBottom": "8px"}),
            html.Div(id="stats-panel", style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
        ], style={"marginTop": "24px"}),

        html.Div(id="summary-text", style={"marginTop": "12px", "fontSize": "16px", "color": "#555"}),
    ],
    style={"maxWidth": "960px", "margin": "40px auto", "fontFamily": "Arial"},
)


def stat_card(label, value, color):
    return html.Div([
        html.Div(label, style={"fontSize": "12px", "color": "#888", "textTransform": "uppercase"}),
        html.Div(value, style={"fontSize": "24px", "fontWeight": "bold", "color": color}),
    ], style={
        "background": "#f9f9f9",
        "border": f"2px solid {color}",
        "borderRadius": "8px",
        "padding": "12px 20px",
        "minWidth": "120px",
        "textAlign": "center",
    })


@app.callback(
    Output("line-chart", "figure"),
    Output("stats-panel", "children"),
    Output("summary-text", "children"),
    Input("series-dropdown", "value"),
    Input("multiplier-slider", "value"),
    Input("chart-type", "value"),
    Input("show-both", "value"),
)
def update_graph(selected_series, multiplier, chart_type, show_both):
    plot_df = df.copy()
    plot_df["y1_scaled"] = plot_df["y1"] * multiplier
    plot_df["y2_scaled"] = plot_df["y2"] * multiplier
    plot_df["selected"] = plot_df[selected_series] * multiplier

    overlay = "both" in show_both

    def make_trace(y_col, name, color):
        if chart_type == "bar":
            return go.Bar(x=plot_df["x"], y=plot_df[y_col], name=name, marker_color=color)
        elif chart_type == "scatter":
            return go.Scatter(x=plot_df["x"], y=plot_df[y_col], mode="markers",
                              name=name, marker=dict(color=color, size=10))
        else:
            return go.Scatter(x=plot_df["x"], y=plot_df[y_col], mode="lines+markers",
                              name=name, line=dict(color=color))

    fig = go.Figure()
    if overlay:
        fig.add_trace(make_trace("y1_scaled", "Series 1", "#636EFA"))
        fig.add_trace(make_trace("y2_scaled", "Series 2", "#EF553B"))
        fig.update_layout(title=f"Series 1 & 2 scaled by {multiplier} — {chart_type.capitalize()}")
    else:
        fig.add_trace(make_trace("selected", selected_series, "#636EFA"))
        fig.update_layout(title=f"{selected_series} scaled by {multiplier} — {chart_type.capitalize()}")

    fig.update_layout(xaxis_title="X", yaxis_title="Value", legend_title="Series")

    # Stats for the primary (or both) series
    vals = pd.concat([plot_df["y1_scaled"], plot_df["y2_scaled"]]) if overlay else plot_df["selected"]
    avg_val = vals.mean()
    min_val = vals.min()
    max_val = vals.max()
    std_val = vals.std()

    stats = [
        stat_card("Average", f"{avg_val:.2f}", "#636EFA"),
        stat_card("Min", f"{min_val:.2f}", "#00CC96"),
        stat_card("Max", f"{max_val:.2f}", "#EF553B"),
        stat_card("Std Dev", f"{std_val:.2f}", "#AB63FA"),
    ]

    summary = f"Showing {'both series' if overlay else selected_series} · scaled ×{multiplier} · chart type: {chart_type}"

    return fig, stats, summary


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)

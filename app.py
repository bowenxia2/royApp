from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)
server = app.server  # useful later if you switch deployment styles

# simple starter dataset
df = pd.DataFrame({
    "x": list(range(1, 11)),
    "y1": [2, 4, 3, 5, 7, 8, 7, 9, 10, 12],
    "y2": [1, 2, 2, 3, 4, 3, 5, 6, 5, 7],
})

app.layout = html.Div(
    [
        html.H1("Student Plotly Dash App"),
        html.P("A simple dynamic app for testing Azure VM deployment."),

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

        dcc.Graph(id="line-chart"),

        html.Div(id="summary-text", style={"marginTop": "20px", "fontSize": "18px"}),
    ],
    style={"maxWidth": "900px", "margin": "40px auto", "fontFamily": "Arial"},
)


@app.callback(
    Output("line-chart", "figure"),
    Output("summary-text", "children"),
    Input("series-dropdown", "value"),
    Input("multiplier-slider", "value"),
)
def update_graph(selected_series, multiplier):
    plot_df = df.copy()
    plot_df["selected"] = plot_df[selected_series] * multiplier

    fig = px.line(
        plot_df,
        x="x",
        y="selected",
        markers=True,
        title=f"{selected_series} scaled by {multiplier}",
    )

    avg_value = plot_df["selected"].mean()
    summary = f"Average displayed value: {avg_value:.2f}"

    return fig, summary


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
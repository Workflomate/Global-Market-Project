import mysql.connector
import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output, State
import plotly.express as px
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

def get_table_data(table_name):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()

    if table_name == "fct_market_summary":
        df["volatility"] = df["volatility"].fillna(0)
    elif table_name == "forecast_metrics":
        df = df.drop_duplicates(subset=["model_name", "rmse", "mae", "mape"])
    return df


# -------------------- APP --------------------

app = Dash(__name__)
app.title = "🌍 Global Market Dashboard"

tables = {
    "fct_market_summary": "Market Summary 📈",
    "forecast_metrics": "Forecast Metrics 📊",
    "forecast_results": "Forecast Results 🔮"
}

# ---------- Global Styles ----------
BACKGROUND = "#f5f7fb"
CARD_BG = "#ffffff"
PRIMARY = "#1b3b6f"
ACCENT = "#007acc"

def card(children):
    return html.Div(
        children,
        style={
            "backgroundColor": CARD_BG,
            "boxShadow": "0 2px 8px rgba(0,0,0,0.1)",
            "borderRadius": "14px",
            "padding": "20px",
            "marginBottom": "25px",
        }
    )

app.layout = html.Div(
    style={
        "backgroundColor": BACKGROUND,
        "fontFamily": "Segoe UI, sans-serif",
        "padding": "40px",
        "maxWidth": "1300px",
        "margin": "auto"
    },
    children=[
        html.H1("🌍 Global Market Dashboard",
                style={"textAlign": "center", "color": PRIMARY,
                       "marginBottom": "40px"}),

        card([
            html.Label("اختر الجدول:", style={"fontSize": 18, "fontWeight": "bold", "color": PRIMARY}),
            dcc.Dropdown(
                id='table-dropdown',
                options=[{"label": name, "value": key} for key, name in tables.items()],
                value="fct_market_summary",
                style={"width": "60%", "margin": "20px auto"},
                clearable=False
            ),
            html.Div([
                html.Button("🔁 تحديث البيانات", id="refresh-btn", n_clicks=0,
                            style={"marginRight": "10px", "padding": "10px 20px",
                                   "backgroundColor": PRIMARY, "color": "white",
                                   "border": "none", "borderRadius": "8px",
                                   "cursor": "pointer", "fontWeight": "bold"}),
                html.Button("⬇️ تحميل CSV", id="download-btn", n_clicks=0,
                            style={"padding": "10px 20px",
                                   "backgroundColor": ACCENT, "color": "white",
                                   "border": "none", "borderRadius": "8px",
                                   "cursor": "pointer", "fontWeight": "bold"}),
                dcc.Download(id="download-dataframe-csv")
            ], style={"textAlign": "center"})
        ]),

        card([html.Div(id='table-container')]),
        card([html.Div(id='graph-container')])
    ]
)


# ---------- CALLBACKS ----------

@app.callback(
    [Output('table-container', 'children'),
     Output('graph-container', 'children')],
    [Input('table-dropdown', 'value'),
     Input('refresh-btn', 'n_clicks')]
)
def update_table(selected_table, n_clicks):
    df = get_table_data(selected_table)

    table = dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        page_size=8,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'padding': '8px'},
        style_header={'backgroundColor': PRIMARY, 'color': 'white', 'fontWeight': 'bold'},
        style_data={'backgroundColor': 'white'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f0f4fa'}
        ]
    )

    # --------- Graphs per Table ---------
    if selected_table == "fct_market_summary":
        fig1 = px.line(df, x="trade_date", y="avg_return",
                       title="Average Return Over Time", markers=True,
                       color_discrete_sequence=[ACCENT])
        fig2 = px.line(df, x="trade_date", y="volatility",
                       title="Market Volatility Over Time", markers=True,
                       color_discrete_sequence=["#ff7f0e"])
        fig3 = px.scatter(df, x="avg_return", y="volatility",
                          title="Return vs Volatility", color="volatility",
                          color_continuous_scale="Blues")

        figs = [fig1, fig2, fig3]

    elif selected_table == "forecast_metrics":
        fig = px.bar(df, x="model_name", y=["rmse", "mae", "mape"],
                     title="Model Performance Comparison",
                     barmode='group', color_discrete_sequence=px.colors.qualitative.Set2)
        figs = [fig]

    elif selected_table == "forecast_results":
        fig1 = px.line(df, x="ds", y="yhat", title="Forecast Results Over Time",
                       color_discrete_sequence=[ACCENT])
        fig1.add_scatter(x=df["ds"], y=df["yhat_upper"], mode="lines", name="Upper Bound",
                         line=dict(dash="dot", color="#999"))
        fig1.add_scatter(x=df["ds"], y=df["yhat_lower"], mode="lines", name="Lower Bound",
                         line=dict(dash="dot", color="#999"))
        fig2 = px.histogram(df, x="yhat", nbins=30,
                            title="Distribution of Forecasted Values",
                            color_discrete_sequence=["#2ca02c"])
        fig3 = px.box(df, y="yhat", title="Spread of Forecasted Values",
                      color_discrete_sequence=["#9467bd"])
        figs = [fig1, fig2, fig3]
    else:
        figs = []

    for fig in figs:
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor=BACKGROUND,
            title_font=dict(size=20, color=PRIMARY),
            font=dict(color="#333"),
            margin=dict(t=60, l=30, r=30, b=30),
        )

    graph_div = html.Div(
        [dcc.Graph(figure=fig, style={"marginBottom": "30px"}) for fig in figs]
    )

    return table, graph_div


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-btn", "n_clicks"),
    State("table-dropdown", "value"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, selected_table):
    df = get_table_data(selected_table)
    return dcc.send_data_frame(df.to_csv, f"{selected_table}.csv", index=False)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)

import mysql.connector
import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output, State
import plotly.express as px
from dotenv import load_dotenv
import os
import io
import base64

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

app = Dash(__name__)
app.title = "🌍 Global Market Dashboard"

tables = {
    "fct_market_summary": "Market Summary 📈",
    "forecast_metrics": "Forecast Metrics 📊",
    "forecast_results": "Forecast Results 🔮"
}

app.layout = html.Div(
    style={"backgroundColor": "#f7f9fc", "fontFamily": "Arial, sans-serif", "padding": "20px"},
    children=[
        html.H1("🌍 Global Market Dashboard", style={"textAlign": "center", "color": "#1f77b4"}),

        html.Div([
            html.Label("اختر الجدول:", style={"fontSize": 18, "fontWeight": "bold"}),
            dcc.Dropdown(
                id='table-dropdown',
                options=[{"label": name, "value": key} for key, name in tables.items()],
                value="fct_market_summary",
                style={"width": "50%", "margin": "auto"}
            ),
            html.Br(),
            html.Div([
                html.Button("🔁 تحديث البيانات", id="refresh-btn", n_clicks=0,
                            style={"marginRight": "10px", "padding": "8px 16px",
                                   "backgroundColor": "#1f77b4", "color": "white",
                                   "border": "none", "borderRadius": "6px",
                                   "cursor": "pointer"}),

                html.Button("⬇️ تحميل CSV", id="download-btn", n_clicks=0,
                            style={"padding": "8px 16px",
                                   "backgroundColor": "#2ca02c", "color": "white",
                                   "border": "none", "borderRadius": "6px",
                                   "cursor": "pointer"}),

                dcc.Download(id="download-dataframe-csv")
            ], style={"textAlign": "center", "marginTop": "20px"})
        ], style={"textAlign": "center", "marginBottom": "40px"}),

        html.Div(id='table-container'),
        html.Br(),
        html.Div(id='graph-container')
    ]
)

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
        style_table={'overflowX': 'auto', 'border': '1px solid #ddd'},
        style_cell={'textAlign': 'center', 'padding': '8px'},
        style_header={'backgroundColor': '#1f77b4', 'color': 'white', 'fontWeight': 'bold'},
        style_data={'backgroundColor': '#ffffff'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f2f2f2'}]
    )

    if selected_table == "fct_market_summary":
        fig1 = px.line(df, x="trade_date", y="avg_return", title="Average Return Over Time", markers=True)
        fig2 = px.line(df, x="trade_date", y="volatility", title="Market Volatility Over Time", markers=True)
        fig3 = px.scatter(df, x="avg_return", y="volatility", title="Return vs Volatility")

        for fig in [fig1, fig2, fig3]:
            fig.update_layout(plot_bgcolor="#f9f9f9", paper_bgcolor="#f7f9fc",
                              title_font=dict(size=20, color="#1f77b4"),
                              font=dict(color="#333"))

        graph_div = html.Div([
            html.H3("📊 Visual Analysis", style={"color": "#1f77b4"}),
            html.Div([
                dcc.Graph(figure=fig1, style={"width": "33%", "display": "inline-block"}),
                dcc.Graph(figure=fig2, style={"width": "33%", "display": "inline-block"}),
                dcc.Graph(figure=fig3, style={"width": "33%", "display": "inline-block"})
            ], style={"textAlign": "center"})
        ])

    elif selected_table == "forecast_metrics":
        fig = px.bar(df, x="model_name", y=["rmse", "mae", "mape"],
                     title="Model Performance Comparison", barmode='group')

        fig.update_layout(plot_bgcolor="#f9f9f9", paper_bgcolor="#f7f9fc",
                          title_font=dict(size=20, color="#1f77b4"), font=dict(color="#333"))

        graph_div = html.Div([
            html.H3("📊 Model Metrics", style={"color": "#1f77b4"}),
            dcc.Graph(figure=fig, style={"width": "80%", "margin": "auto"})
        ])

    elif selected_table == "forecast_results":
        fig1 = px.line(df, x="ds", y="yhat", title="Forecast Results Over Time", markers=True)
        fig1.add_scatter(x=df["ds"], y=df["yhat_upper"], mode="lines", name="Upper Bound", line=dict(dash="dot"))
        fig1.add_scatter(x=df["ds"], y=df["yhat_lower"], mode="lines", name="Lower Bound", line=dict(dash="dot"))

        fig2 = px.histogram(df, x="yhat", nbins=30, title="Distribution of Forecasted Values")
        fig3 = px.box(df, y="yhat", title="Spread of Forecasted Values")

        for fig in [fig1, fig2, fig3]:
            fig.update_layout(plot_bgcolor="#f9f9f9", paper_bgcolor="#f7f9fc",
                              title_font=dict(size=20, color="#1f77b4"),
                              font=dict(color="#333"))

        graph_div = html.Div([
            html.H3("📊 Forecast Analysis", style={"color": "#1f77b4"}),
            dcc.Graph(figure=fig1, style={"width": "100%", "marginBottom": "40px"}),
            dcc.Graph(figure=fig2, style={"width": "100%", "marginBottom": "40px"}),
            dcc.Graph(figure=fig3, style={"width": "100%"})
        ])

    else:
        graph_div = html.Div([html.H3("No chart available")])

    return html.Div([html.H3("📋 Table Data", style={"color": "#1f77b4"}), table]), graph_div


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

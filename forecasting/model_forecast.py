import pandas as pd
import mysql.connector
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

print("Connecting to MySQL and loading final data...")

conn = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="admin",
    database="marketdb"
)

query = """
SELECT trade_date, index_name, max_price
FROM fct_market_summary
ORDER BY trade_date
"""
df = pd.read_sql(query, conn)
conn.close()

print(f"Data loaded successfully: {df.shape[0]} rows")

df = df.rename(columns={'trade_date': 'ds', 'max_price': 'y'})

print("Training Prophet model...")
model = Prophet(daily_seasonality=True)
model.fit(df)

print("Generating 7-day forecast...")
future = model.make_future_dataframe(periods=7)
forecast = model.predict(future)

print("Forecast created successfully.")
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(7))

print("Saving forecast results to MySQL...")
conn = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="admin",
    database="marketdb"
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS forecast_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ds DATE,
    yhat DOUBLE,
    yhat_lower DOUBLE,
    yhat_upper DOUBLE
)
""")

for _, row in forecast.iterrows():
    cursor.execute("""
        INSERT INTO forecast_results (ds, yhat, yhat_lower, yhat_upper)
        VALUES (%s, %s, %s, %s)
    """, (
        row['ds'].date(),
        float(row['yhat']),
        float(row['yhat_lower']),
        float(row['yhat_upper'])
    ))

conn.commit()
conn.close()
print("Forecast results stored in table `forecast_results`.")

print("Evaluating model accuracy...")
conn = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="admin",
    database="marketdb"
)

query = """
SELECT trade_date AS ds, max_price AS actual
FROM fct_market_summary
ORDER BY trade_date
"""
actual_df = pd.read_sql(query, conn)
conn.close()

actual_df['ds'] = pd.to_datetime(actual_df['ds'])
forecast['ds'] = pd.to_datetime(forecast['ds'])

merged = pd.merge(actual_df, forecast[['ds', 'yhat']], on='ds', how='inner')

rmse = np.sqrt(mean_squared_error(merged['actual'], merged['yhat']))
mae = mean_absolute_error(merged['actual'], merged['yhat'])
mape = np.mean(np.abs((merged['actual'] - merged['yhat']) / merged['actual'])) * 100

print(f"Model Evaluation Complete → RMSE: {rmse:.2f}, MAE: {mae:.2f}, MAPE: {mape:.2f}%")

print("Saving evaluation metrics to `forecast_metrics`...")
conn = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="admin",
    database="marketdb"
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS forecast_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(50),
    rmse DOUBLE,
    mae DOUBLE,
    mape DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
INSERT INTO forecast_metrics (model_name, rmse, mae, mape)
VALUES (%s, %s, %s, %s)
""", ("Prophet", rmse, mae, mape))

conn.commit()
conn.close()

print("Forecast metrics saved successfully to `forecast_metrics`.")
print("Forecasting & Evaluation step completed successfully.")

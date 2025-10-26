{{ config(materialized='table') }}

WITH base AS (
    SELECT
        index_name,
        trade_date,
        daily_return,
        close_price
    FROM {{ ref('int_market_metrics') }}
)

SELECT
    index_name,
    trade_date,
    ROUND(AVG(daily_return) OVER (
        PARTITION BY index_name
        ORDER BY trade_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 6) AS avg_return,
    ROUND(STDDEV_SAMP(daily_return) OVER (
        PARTITION BY index_name
        ORDER BY trade_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 6) AS volatility,
    MAX(close_price) OVER (
        PARTITION BY index_name
        ORDER BY trade_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS max_price,
    MIN(close_price) OVER (
        PARTITION BY index_name
        ORDER BY trade_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS min_price
FROM base
ORDER BY index_name, trade_date

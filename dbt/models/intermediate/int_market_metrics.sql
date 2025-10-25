{{ config(materialized='view') }}

WITH base AS (
    SELECT
        index_name,
        trade_date,
        close_price,
        LAG(close_price) OVER (PARTITION BY index_name ORDER BY trade_date) AS prev_close
    FROM {{ ref('stg_global_index') }}
)

SELECT
    index_name,
    trade_date,
    close_price,
    (close_price - prev_close) / prev_close AS daily_return,
    LOG(close_price / prev_close) AS log_return,
    AVG(close_price) OVER (
        PARTITION BY index_name 
        ORDER BY trade_date 
        ROWS BETWEEN 7 PRECEDING AND CURRENT ROW
    ) AS moving_avg,
    STDDEV_SAMP(close_price) OVER (
        PARTITION BY index_name 
        ORDER BY trade_date 
        ROWS BETWEEN 7 PRECEDING AND CURRENT ROW
    ) AS rolling_volatility
FROM base
WHERE prev_close IS NOT NULL

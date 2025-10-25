{{ config(materialized='view') }}

WITH source AS (
    SELECT
        CAST(`date` AS DATE) AS trade_date,
        TRIM(`index_code`) AS index_name,
        CAST(`open` AS DECIMAL(15,2)) AS open_price,
        CAST(`high` AS DECIMAL(15,2)) AS high_price,
        CAST(`low` AS DECIMAL(15,2)) AS low_price,
        CAST(`close` AS DECIMAL(15,2)) AS close_price,
        CAST(`adj_close` AS DECIMAL(15,2)) AS adj_close_price,
        CAST(`volume` AS SIGNED) AS volume
    FROM {{ source('raw', 'index_data') }}
)
SELECT
    trade_date,
    index_name,
    open_price,
    high_price,
    low_price,
    close_price,
    adj_close_price,
    volume
FROM source
WHERE close_price IS NOT NULL

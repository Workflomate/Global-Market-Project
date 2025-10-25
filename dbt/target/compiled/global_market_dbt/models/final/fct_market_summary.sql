

SELECT
    index_name,
    trade_date,
    ROUND(AVG(daily_return), 6) AS avg_return,
    ROUND(STDDEV_SAMP(daily_return), 6) AS volatility,
    MAX(close_price) AS max_price,
    MIN(close_price) AS min_price
FROM `marketdb`.`int_market_metrics`
GROUP BY index_name, trade_date
ORDER BY index_name, trade_date
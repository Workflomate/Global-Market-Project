USE marketdb;

DROP TABLE IF EXISTS index_data;
DROP TABLE IF EXISTS index_info;

CREATE TABLE index_info (
    index_code VARCHAR(50) PRIMARY KEY,
    region VARCHAR(50),
    exchange VARCHAR(50),
    currency VARCHAR(10)
);

CREATE TABLE index_data (
    index_code VARCHAR(50),
    date DATE,
    open DECIMAL(15, 2),
    high DECIMAL(15, 2),
    low DECIMAL(15, 2),
    close DECIMAL(15, 2),
    adj_close DECIMAL(15, 2),
    volume BIGINT,
    PRIMARY KEY (index_code, date),
    FOREIGN KEY (index_code) REFERENCES index_info(index_code)
);

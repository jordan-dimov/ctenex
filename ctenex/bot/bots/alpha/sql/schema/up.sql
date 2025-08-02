-- Price moments table

CREATE TABLE IF NOT EXISTS price_moments (
    id INTEGER PRIMARY KEY NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    volume DECIMAL(10,2) NOT NULL,
    best_bid DECIMAL(10,2) NOT NULL,
    best_ask DECIMAL(10,2) NOT NULL
);

-- EMA (Exponential Moving Average) calculations table

CREATE TABLE IF NOT EXISTS ema_calculations (
    id INTEGER PRIMARY KEY NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    ema_short DECIMAL(10,2) NOT NULL,  -- e.g., 12-period EMA
    ema_long DECIMAL(10,2) NOT NULL,   -- e.g., 26-period EMA
    momentum DECIMAL(10,2) NOT NULL     -- ema_short - ema_long
);

-- Spread analysis table

CREATE TABLE IF NOT EXISTS spread_analysis (
    id INTEGER PRIMARY KEY NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    best_bid DECIMAL(10,2) NULL,
    best_ask DECIMAL(10,2) NULL,
    spread DECIMAL(10,2) NULL,
    spread_percentage DECIMAL(5,2) NULL,
    volume DECIMAL(10,2) NULL
);

-- Trading signals table

CREATE TABLE IF NOT EXISTS trading_signals (
    id INTEGER PRIMARY KEY NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    momentum DECIMAL(10,2) NOT NULL,
    spread DECIMAL(10,2) NULL,
    spread_percentage DECIMAL(5,2) NULL,
    signal_strength DECIMAL(5,2) NOT NULL,
    recommended_action VARCHAR(10) NOT NULL
);

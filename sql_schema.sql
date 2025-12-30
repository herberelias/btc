-- ═══════════════════════════════════════════════════════════
-- SCHEMA COMPLETO DE BASE DE DATOS - CRYPTO TRADING ML
-- ═══════════════════════════════════════════════════════════
-- Este archivo contiene todas las tablas y vistas necesarias
-- Ejecutar en MySQL Workbench sobre la base de datos 'btc'

USE btc;

-- Eliminar tablas existentes (en orden correcto por foreign keys)
DROP TABLE IF EXISTS notifications_log;
DROP TABLE IF EXISTS feature_engineering;
DROP TABLE IF EXISTS backtests;
DROP TABLE IF EXISTS model_performance;
DROP TABLE IF EXISTS winning_patterns;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS market_context;
DROP TABLE IF EXISTS indicators;
DROP TABLE IF EXISTS candles;

-- ═══════════════════════════════════════════════════════════
-- TABLA: candles
-- Descripción: Almacena velas OHLCV históricas
-- ═══════════════════════════════════════════════════════════
CREATE TABLE candles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    open_time BIGINT NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    close_time BIGINT NOT NULL,
    quote_volume DECIMAL(20, 8),
    trades_count INT,
    taker_buy_volume DECIMAL(20, 8),
    taker_buy_quote_volume DECIMAL(20, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_candle (symbol, timeframe, open_time),
    INDEX idx_symbol_timeframe (symbol, timeframe),
    INDEX idx_open_time (open_time),
    INDEX idx_lookup (symbol, timeframe, open_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ═══════════════════════════════════════════════════════════
-- TABLA: indicators
-- Descripción: Almacena indicadores técnicos calculados
-- ═══════════════════════════════════════════════════════════
CREATE TABLE indicators (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    candle_id BIGINT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    rsi_14 DECIMAL(10, 4),
    rsi_7 DECIMAL(10, 4),
    macd DECIMAL(20, 8),
    macd_signal DECIMAL(20, 8),
    macd_histogram DECIMAL(20, 8),
    ema_9 DECIMAL(20, 8),
    ema_20 DECIMAL(20, 8),
    ema_50 DECIMAL(20, 8),
    ema_100 DECIMAL(20, 8),
    ema_200 DECIMAL(20, 8),
    sma_20 DECIMAL(20, 8),
    sma_50 DECIMAL(20, 8),
    sma_200 DECIMAL(20, 8),
    bb_upper DECIMAL(20, 8),
    bb_middle DECIMAL(20, 8),
    bb_lower DECIMAL(20, 8),
    bb_width DECIMAL(10, 4),
    atr DECIMAL(20, 8),
    volume_avg_20 DECIMAL(20, 8),
    volume_ratio DECIMAL(10, 4),
    stoch_k DECIMAL(10, 4),
    stoch_d DECIMAL(10, 4),
    adx DECIMAL(10, 4),
    cci DECIMAL(10, 4),
    willr DECIMAL(10, 4),
    obv DECIMAL(20, 2),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candle_id) REFERENCES candles(id) ON DELETE CASCADE,
    INDEX idx_candle (candle_id),
    INDEX idx_symbol_timeframe (symbol, timeframe),
    INDEX idx_rsi (rsi_14),
    INDEX idx_calculated (calculated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ═══════════════════════════════════════════════════════════
-- TABLA: market_context
-- Descripción: Contexto del mercado (Fear & Greed, Dominance)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE market_context (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp BIGINT NOT NULL,
    btc_dominance DECIMAL(10, 4),
    eth_dominance DECIMAL(10, 4),
    total_market_cap DECIMAL(20, 2),
    total_volume_24h DECIMAL(20, 2),
    fear_greed_index INT,
    fear_greed_classification VARCHAR(50),
    market_regime ENUM('bull', 'bear', 'sideways', 'volatile', 'unknown') DEFAULT 'unknown',
    volatility_index DECIMAL(10, 4),
    btc_price DECIMAL(20, 8),
    eth_price DECIMAL(20, 8),
    altcoin_season_index DECIMAL(10, 4),
    defi_dominance DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_market_regime (market_regime),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ═══════════════════════════════════════════════════════════
-- TABLA: predictions
-- Descripción: Predicciones generadas por el modelo ML
-- ═══════════════════════════════════════════════════════════
CREATE TABLE predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    prediction_type ENUM('LONG', 'SHORT', 'NEUTRAL', 'STRONG_LONG', 'STRONG_SHORT') NOT NULL,
    confidence_score DECIMAL(5, 2) NOT NULL,
    entry_price DECIMAL(20, 8) NOT NULL,
    current_price DECIMAL(20, 8),
    suggested_stop_loss DECIMAL(20, 8),
    suggested_take_profit DECIMAL(20, 8),
    stop_loss_percentage DECIMAL(10, 4),
    take_profit_percentage DECIMAL(10, 4),
    risk_reward_ratio DECIMAL(10, 4),
    position_size_recommended DECIMAL(10, 4),
    max_position_size DECIMAL(10, 4),
    model_version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50),
    features_used JSON,
    market_context_id BIGINT,
    prediction_time BIGINT NOT NULL,
    expiration_time BIGINT,
    time_horizon_hours INT,
    status ENUM('PENDING', 'EXECUTED', 'EXPIRED', 'CANCELLED', 'MONITORING') DEFAULT 'PENDING',
    priority ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
    tags JSON,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (market_context_id) REFERENCES market_context(id) ON DELETE SET NULL,
    INDEX idx_symbol_timeframe (symbol, timeframe),
    INDEX idx_status_confidence (status, confidence_score),
    INDEX idx_prediction_time (prediction_time),
    INDEX idx_expiration (expiration_time),
    INDEX idx_model_version (model_version),
    INDEX idx_active_signals (status, confidence_score, expiration_time),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ═══════════════════════════════════════════════════════════
-- TABLA: results
-- Descripción: Resultados reales de las predicciones
-- ═══════════════════════════════════════════════════════════
CREATE TABLE results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    prediction_id BIGINT NOT NULL,
    actual_outcome ENUM('WIN', 'LOSS', 'NEUTRAL', 'PARTIAL_WIN', 'PARTIAL_LOSS') NOT NULL,
    entry_price DECIMAL(20, 8) NOT NULL,
    exit_price DECIMAL(20, 8) NOT NULL,
    highest_price DECIMAL(20, 8),
    lowest_price DECIMAL(20, 8),
    profit_loss_percentage DECIMAL(10, 4) NOT NULL,
    profit_loss_usd DECIMAL(20, 8),
    max_favorable_excursion DECIMAL(10, 4),
    max_adverse_excursion DECIMAL(10, 4),
    hit_stop_loss BOOLEAN DEFAULT FALSE,
    hit_take_profit BOOLEAN DEFAULT FALSE,
    exit_reason ENUM('STOP_LOSS', 'TAKE_PROFIT', 'MANUAL', 'TIMEOUT', 'REVERSAL_SIGNAL', 'OTHER'),
    duration_minutes INT,
    duration_hours DECIMAL(10, 4),
    slippage DECIMAL(10, 4),
    fees_paid DECIMAL(20, 8),
    net_profit_loss DECIMAL(20, 8),
    trade_quality_score DECIMAL(5, 2),
    market_condition_during_trade VARCHAR(50),
    volatility_during_trade DECIMAL(10, 4),
    result_time BIGINT NOT NULL,
    evaluation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE CASCADE,
    INDEX idx_prediction (prediction_id),
    INDEX idx_outcome (actual_outcome),
    INDEX idx_profit_loss (profit_loss_percentage),
    INDEX idx_quality (trade_quality_score),
    INDEX idx_result_time (result_time),
    INDEX idx_analysis (actual_outcome, profit_loss_percentage, duration_hours)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ═══════════════════════════════════════════════════════════
-- TABLA: winning_patterns
-- Descripción: Patrones que han demostrado ser exitosos
-- ═══════════════════════════════════════════════════════════
CREATE TABLE winning_patterns (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pattern_name VARCHAR(100) NOT NULL,
    pattern_description TEXT,
    symbol VARCHAR(20),
    timeframe VARCHAR(10),
    conditions JSON NOT NULL,
    win_rate DECIMAL(5, 2) NOT NULL,
    avg_profit DECIMAL(10, 4) NOT NULL,
    avg_loss DECIMAL(10, 4) NOT NULL,
    max_profit DECIMAL(10, 4),
    max_loss DECIMAL(10, 4),
    risk_reward DECIMAL(10, 4) NOT NULL,
    profit_factor DECIMAL(10, 4),
    occurrences INT DEFAULT 0,
    winning_trades INT DEFAULT 0,
    losing_trades INT DEFAULT 0,
    last_occurrence BIGINT,
    first_occurrence BIGINT,
    market_regime_best ENUM('bull', 'bear', 'sideways', 'volatile', 'any') DEFAULT 'any',
    confidence_threshold DECIMAL(5, 2),
    min_volume_required DECIMAL(20, 8),
    optimal_entry_conditions JSON,
    optimal_exit_conditions JSON,
    pattern_strength ENUM('WEAK', 'MODERATE', 'STRONG', 'VERY_STRONG') DEFAULT 'MODERATE',
    is_active BOOLEAN DEFAULT TRUE,
    reliability_score DECIMAL(5, 2),
    consistency_score DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_pattern (pattern_name, symbol, timeframe),
    INDEX idx_win_rate (win_rate),
    INDEX idx_symbol_timeframe (symbol, timeframe),
    INDEX idx_market_regime (market_regime_best),
    INDEX idx_active (is_active),
    INDEX idx_strength (pattern_strength, win_rate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ═══════════════════════════════════════════════════════════
-- TABLA: model_performance
-- Descripción: Métricas de performance de modelos ML
-- ═══════════════════════════════════════════════════════════
CREATE TABLE model_performance (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_version VARCHAR(20) NOT NULL UNIQUE,
    model_type VARCHAR(50) NOT NULL,
    model_architecture TEXT,
    training_date TIMESTAMP NOT NULL,
    dataset_size INT NOT NULL,
    training_duration_minutes INT,
    accuracy DECIMAL(5, 2),
    precision_score DECIMAL(5, 2),
    recall_score DECIMAL(5, 2),
    f1_score DECIMAL(5, 2),
    auc_roc DECIMAL(5, 4),
    sharpe_ratio DECIMAL(10, 4),
    sortino_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    avg_profit_per_trade DECIMAL(10, 4),
    avg_loss_per_trade DECIMAL(10, 4),
    total_trades_analyzed INT,
    winning_trades INT,
    losing_trades INT,
    win_rate DECIMAL(5, 2),
    profit_factor DECIMAL(10, 4),
    expectancy DECIMAL(10, 4),
    best_timeframe VARCHAR(10),
    worst_timeframe VARCHAR(10),
    best_symbol VARCHAR(20),
    worst_symbol VARCHAR(20),
    best_market_condition VARCHAR(50),
    features_importance JSON,
    hyperparameters JSON,
    training_config JSON,
    validation_metrics JSON,
    test_metrics JSON,
    is_active BOOLEAN DEFAULT FALSE,
    deployment_date TIMESTAMP NULL,
    retirement_date TIMESTAMP NULL,
    performance_trend ENUM('IMPROVING', 'STABLE', 'DEGRADING', 'UNKNOWN') DEFAULT 'UNKNOWN',
    confidence_interval_lower DECIMAL(5, 2),
    confidence_interval_upper DECIMAL(5, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_version (model_version),
    INDEX idx_active (is_active),
    INDEX idx_performance (win_rate, sharpe_ratio),
    INDEX idx_training_date (training_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ═══════════════════════════════════════════════════════════
-- VISTAS (VIEWS)
-- ═══════════════════════════════════════════════════════════

-- Vista: active_signals
-- Descripción: Señales activas con alta confianza
CREATE OR REPLACE VIEW active_signals AS
SELECT 
    p.id,
    p.symbol,
    p.timeframe,
    p.prediction_type,
    p.confidence_score,
    p.entry_price,
    p.current_price,
    p.suggested_stop_loss,
    p.suggested_take_profit,
    p.risk_reward_ratio,
    p.model_version,
    p.prediction_time,
    p.expiration_time,
    p.status,
    p.priority,
    mc.market_regime,
    mc.fear_greed_index,
    mc.fear_greed_classification,
    mc.btc_dominance,
    mc.volatility_index,
    p.created_at
FROM predictions p
LEFT JOIN market_context mc ON p.market_context_id = mc.id
WHERE p.status = 'PENDING' 
  AND p.confidence_score >= 70
  AND (p.expiration_time IS NULL OR p.expiration_time > UNIX_TIMESTAMP() * 1000)
ORDER BY p.confidence_score DESC, p.created_at DESC;

-- Vista: model_statistics
-- Descripción: Estadísticas de performance del modelo
CREATE OR REPLACE VIEW model_statistics AS
SELECT 
    p.model_version,
    p.symbol,
    p.timeframe,
    COUNT(*) as total_predictions,
    COUNT(r.id) as evaluated_predictions,
    SUM(CASE WHEN r.actual_outcome = 'WIN' THEN 1 ELSE 0 END) as winning_trades,
    SUM(CASE WHEN r.actual_outcome = 'LOSS' THEN 1 ELSE 0 END) as losing_trades,
    ROUND(SUM(CASE WHEN r.actual_outcome = 'WIN' THEN 1 ELSE 0 END) / COUNT(r.id) * 100, 2) as win_rate,
    ROUND(AVG(r.profit_loss_percentage), 4) as avg_return,
    ROUND(AVG(CASE WHEN r.actual_outcome = 'WIN' THEN r.profit_loss_percentage END), 4) as avg_win,
    ROUND(AVG(CASE WHEN r.actual_outcome = 'LOSS' THEN r.profit_loss_percentage END), 4) as avg_loss,
    ROUND(MAX(r.profit_loss_percentage), 4) as max_profit,
    ROUND(MIN(r.profit_loss_percentage), 4) as max_loss,
    ROUND(AVG(p.confidence_score), 2) as avg_confidence,
    ROUND(AVG(r.duration_hours), 2) as avg_duration_hours,
    DATE(p.created_at) as date
FROM predictions p
LEFT JOIN results r ON p.id = r.prediction_id
WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY p.model_version, p.symbol, p.timeframe, DATE(p.created_at)
ORDER BY date DESC, win_rate DESC;

-- ═══════════════════════════════════════════════════════════
-- FIN DEL SCRIPT
-- ═══════════════════════════════════════════════════════════
SELECT 'Schema creado exitosamente!' as message;

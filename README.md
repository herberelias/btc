# Crypto Trading Backend with Machine Learning

Backend en Python con FastAPI para trading de criptomonedas que utiliza Machine Learning para generar señales Long/Short.

## 🚀 Características

- **FastAPI**: API REST moderna y rápida
- **Machine Learning**: Predicciones con Random Forest (o reglas si no hay modelo)
- **Indicadores Técnicos**: RSI, MACD, EMAs, Bollinger Bands, ATR, Stochastic, ADX, CCI, Williams %R, OBV
- **Base de Datos MySQL**: Almacenamiento de velas, indicadores, predicciones y resultados
- **Contexto de Mercado**: Fear & Greed Index, BTC Dominance
- **Sistema Automático**: Calcula indicadores y genera predicciones automáticamente al recibir velas

## 📋 Requisitos

- Python 3.10+
- MySQL 8.0+
- 2GB RAM mínimo
- 1GB espacio en disco

## 🔧 Instalación

### 1. Clonar repositorio

```bash
git clone <tu-repositorio>
cd btc_backend
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar `.env.example` a `.env` y editar con tus credenciales:

```bash
cp .env.example .env
```

Editar `.env`:
```env
DB_HOST=localhost
DB_USER=crypto_user
DB_PASSWORD=CryptoSenales2025!
DB_NAME=btc
DB_PORT=3306
PORT=3001
```

### 5. Crear base de datos

En MySQL Workbench o cliente MySQL, ejecutar el siguiente script que ya creaste:

```sql
USE btc;

-- Ejecutar todo el script SQL que te proporcioné anteriormente
-- (Las 10 tablas + 5 vistas)
```

### 6. Ejecutar servidor

```bash
python run.py
```

El servidor estará disponible en `http://localhost:3001`

## 📡 Endpoints Principales

### POST /api/v1/candles
Crea una vela nueva y automáticamente calcula indicadores y genera predicción.

**Request:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "open": 43500.50,
  "high": 43800.20,
  "low": 43400.10,
  "close": 43700.80,
  "volume": 1250.5,
  "open_time": 1704067200000,
  "close_time": 1704070800000
}
```

**Response:**
```json
{
  "success": true,
  "candle_id": 12345,
  "indicators_calculated": true,
  "prediction": {
    "id": 789,
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "type": "LONG",
    "confidence": 85.5,
    "entry_price": 43700.80,
    "stop_loss": 43200.00,
    "take_profit": 44500.00,
    "risk_reward": 1.6,
    "model_version": "1.0",
    "expires_at": 1704074400000
  }
}
```

### GET /api/v1/predictions/active
Obtiene señales activas con alta confianza.

**Query params:**
- `symbol` (opcional): Filtrar por símbolo
- `timeframe` (opcional): Filtrar por timeframe
- `min_confidence` (opcional): Confianza mínima (default: 70%)

**Response:**
```json
{
  "signals": [
    {
      "id": 789,
      "symbol": "BTCUSDT",
      "timeframe": "1h",
      "type": "LONG",
      "confidence": 85.5,
      "entry_price": 43700.80,
      "current_price": 43750.20,
      "stop_loss": 43200.00,
      "take_profit": 44500.00,
      "risk_reward": 1.6,
      "market_context": {
        "regime": "bull",
        "fear_greed_index": 65,
        "btc_dominance": 52.3
      }
    }
  ],
  "total": 1
}
```

### GET /api/v1/health
Health check del sistema.

**Response:**
```json
{
  "status": "healthy",
  "database": "healthy",
  "ml_model": "loaded",
  "version": "1.0.0",
  "model_version": "1.0"
}
```

## 📚 Documentación API

Disponible en:
- Swagger UI: `http://localhost:3001/docs`
- ReDoc: `http://localhost:3001/redoc`

## 🔄 Flujo del Sistema

1. **Flutter envía vela** → POST /api/v1/candles
2. **Backend guarda vela** en tabla `candles`
3. **Calcula indicadores** automáticamente → tabla `indicators`
4. **Obtiene contexto** (Fear & Greed, Dominance) → tabla `market_context`
5. **ML genera predicción** con features → tabla `predictions`
6. **Si confidence ≥ 70%** → Retorna señal a Flutter
7. **Flutter muestra señal** al usuario

## 🎯 Machine Learning

### Modelo Actual
El sistema usa **reglas básicas** si no hay modelo ML entrenado:
- RSI < 30 → señal de compra
- RSI > 70 → señal de venta
- MACD cruces
- EMA 20/50 cruces

### Entrenar Modelo (futuro)
Para entrenar un modelo Random Forest con datos históricos:

```bash
# TODO: Implementar script de entrenamiento
python scripts/train_model.py
```

## 🗂️ Estructura del Proyecto

```
btc_backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuración
│   ├── database.py          # Conexión MySQL
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routes/              # Endpoints API
│   ├── services/            # Lógica de negocio
│   ├── ml/                  # Machine Learning
│   │   ├── feature_engineer.py
│   │   ├── predictor.py
│   │   └── models/          # Modelos .pkl
│   └── utils/               # Utilidades
├── logs/                    # Archivos de log
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py                   # Punto de entrada
└── README.md
```

## 🐛 Troubleshooting

### Error: "Can't connect to MySQL server"
- Verificar que MySQL esté corriendo
- Verificar credenciales en `.env`
- Verificar que la base de datos `btc` exista

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Error: "Address already in use"
- El puerto 3001 está ocupado
- Cambiar `PORT` en `.env` a otro valor (ej: 3002)

## 📝 Logs

Los logs se guardan en:
- **Consola**: Output en tiempo real con colores
- **Archivo**: `logs/app.log` (rotación automática)

## 🚀 Deployment en Servidor

### Opción 1: Con systemd (recomendado)

Crear servicio `/etc/systemd/system/crypto-trading.service`:

```ini
[Unit]
Description=Crypto Trading Backend
After=network.target mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/home/btc_backend
Environment="PATH=/home/btc_backend/venv/bin"
ExecStart=/home/btc_backend/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable crypto-trading
sudo systemctl start crypto-trading
sudo journalctl -u crypto-trading -f  # Ver logs
```

### Opción 2: Con screen (simple)

```bash
screen -S crypto-backend
python run.py
# Ctrl+A, D para detach
```

## 🔐 Seguridad

- Las API keys NO están en el código
- Usa HTTPS en producción
- Configura firewall para el puerto 3001
- Limita acceso a IPs conocidas

## 📈 Próximas Mejoras

- [ ] Entrenar modelo Random Forest real con datos históricos
- [ ] Sistema de re-entrenamiento nocturno automático
- [ ] Backtesting integrado
- [ ] Detección de patrones ganadores
- [ ] Más APIs externas (CoinGecko, etc.)
- [ ] Sistema de notificaciones
- [ ] Panel web de monitoreo

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en `logs/app.log`
2. Verifica el health check: `http://localhost:3001/api/v1/health`
3. Revisa la documentación: `http://localhost:3001/docs`

## 📄 Licencia

Proyecto privado - Todos los derechos reservados

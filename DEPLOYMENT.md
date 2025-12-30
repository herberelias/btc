# Guía de Deployment en /var/www

## 📍 Servidor: 64.23.132.230

Esta guía te muestra cómo hacer el deployment del backend en `/var/www`.

## 🚀 Pasos de Instalación

### 1. Conectarse al Servidor

```bash
ssh root@64.23.132.230
# O tu usuario con sudo
```

### 2. Navegar al Directorio Web

```bash
cd /var/www
```

### 3. Clonar el Repositorio

```bash
git clone https://github.com/herberelias/btc.git
cd btc
```

### 4. Instalar Python 3 y pip (si no están instalados)

```bash
# Verificar versión de Python
python3 --version

# Si no está instalado:
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

### 5. Crear Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

**Importante**: Siempre activa el entorno virtual antes de trabajar:
```bash
cd /var/www/btc
source venv/bin/activate
```

### 6. Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Nota**: Si da error con `pandas-ta`, instalar primero pandas:
```bash
pip install pandas numpy
pip install pandas-ta
```

### 7. Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar con nano o vi
nano .env
```

**Configuración del .env**:
```env
# Puerto del servidor
PORT=3001

# Base de datos MySQL (SERVIDOR)
DB_HOST=localhost
DB_USER=crypto_user
DB_PASSWORD=CryptoSenales2025!
DB_NAME=btc
DB_PORT=3306

# Entorno
ENVIRONMENT=production

# Machine Learning
MODEL_VERSION=1.0
MODEL_PATH=./app/ml/models/
AUTO_RETRAIN=true
RETRAIN_HOUR=3
MIN_CONFIDENCE_THRESHOLD=70

# Logs
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# CORS (para Flutter)
CORS_ORIGINS=*

# Workers
WORKERS=4
```

**Guardar**: `Ctrl + O`, Enter, `Ctrl + X`

### 8. Verificar Base de Datos

```bash
# Conectar a MySQL
mysql -u crypto_user -p
# Password: CryptoSenales2025!

# Verificar base de datos
USE btc;
SHOW TABLES;

# Debe mostrar las 7 tablas
# Si no existen, ejecutar sql_schema.sql
```

**Si las tablas NO existen**:
```bash
# Ejecutar script SQL
mysql -u crypto_user -p btc < sql_schema.sql
```

### 9. Crear Directorio de Logs

```bash
mkdir -p logs
chmod 755 logs
```

### 10. Probar Ejecución Manual

```bash
# Activar entorno virtual si no está activo
source venv/bin/activate

# Ejecutar
python run.py
```

**Verificar**:
- Debe mostrar: "Iniciando Crypto Trading Backend"
- "✓ Modelo ML cargado" o "⚠ Modelo ML no encontrado"
- "Uvicorn running on http://0.0.0.0:3001"

**Probar desde otro terminal**:
```bash
curl http://localhost:3001/api/v1/health
```

**Debe retornar**:
```json
{
  "status": "healthy",
  "database": "healthy",
  "ml_model": "not loaded",
  "version": "1.0.0"
}
```

Si funciona, presiona `Ctrl + C` para detener.

## 🔧 Configurar como Servicio Systemd

Para que corra automáticamente y se reinicie si falla:

### 1. Crear Archivo de Servicio

```bash
sudo nano /etc/systemd/system/crypto-trading.service
```

### 2. Agregar Configuración

```ini
[Unit]
Description=Crypto Trading Backend with ML
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/btc
Environment="PATH=/var/www/btc/venv/bin"
ExecStart=/var/www/btc/venv/bin/python /var/www/btc/run.py
Restart=always
RestartSec=10
StandardOutput=append:/var/www/btc/logs/app.log
StandardError=append:/var/www/btc/logs/error.log

[Install]
WantedBy=multi-user.target
```

**Guardar**: `Ctrl + O`, Enter, `Ctrl + X`

### 3. Activar y Iniciar Servicio

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable crypto-trading

# Iniciar servicio
sudo systemctl start crypto-trading

# Verificar estado
sudo systemctl status crypto-trading
```

**Debe mostrar**: `Active: active (running)`

### 4. Comandos Útiles del Servicio

```bash
# Ver estado
sudo systemctl status crypto-trading

# Iniciar
sudo systemctl start crypto-trading

# Detener
sudo systemctl stop crypto-trading

# Reiniciar
sudo systemctl restart crypto-trading

# Ver logs en tiempo real
sudo journalctl -u crypto-trading -f

# Ver últimas 100 líneas de logs
sudo journalctl -u crypto-trading -n 100
```

## 🔥 Configurar Firewall (si está activo)

```bash
# Permitir puerto 3001
sudo ufw allow 3001/tcp

# Verificar reglas
sudo ufw status
```

## 🌐 Verificar desde Internet

Desde tu navegador o Postman:

```
http://64.23.132.230:3001/api/v1/health
http://64.23.132.230:3001/docs
```

## 📊 Monitoreo y Logs

### Ver Logs de la Aplicación

```bash
# Logs de la app
tail -f /var/www/btc/logs/app.log

# Logs de errores
tail -f /var/www/btc/logs/error.log

# Logs del servicio systemd
sudo journalctl -u crypto-trading -f
```

### Verificar Uso de Recursos

```bash
# CPU y RAM
top

# Buscar proceso python
ps aux | grep python

# Espacio en disco
df -h
```

## 🔄 Actualizar el Backend

Cuando hagas cambios en el código:

```bash
# Ir al directorio
cd /var/www/btc

# Pull cambios
git pull origin main

# Activar entorno virtual
source venv/bin/activate

# Actualizar dependencias (si cambiaron)
pip install -r requirements.txt

# Reiniciar servicio
sudo systemctl restart crypto-trading

# Verificar
sudo systemctl status crypto-trading
```

## 🐛 Troubleshooting

### Error: "Can't connect to MySQL"

```bash
# Verificar MySQL corriendo
sudo systemctl status mysql

# Iniciar MySQL si está detenido
sudo systemctl start mysql

# Verificar credenciales
mysql -u crypto_user -p
```

### Error: "Address already in use"

```bash
# Ver qué está usando el puerto 3001
sudo lsof -i :3001

# Matar proceso si es necesario
sudo kill -9 <PID>

# O cambiar puerto en .env
```

### Error: "Module not found"

```bash
# Asegurarse de estar en entorno virtual
source /var/www/btc/venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Servicio no inicia

```bash
# Ver logs completos
sudo journalctl -u crypto-trading -n 200

# Verificar permisos
ls -la /var/www/btc

# Probar manualmente
cd /var/www/btc
source venv/bin/activate
python run.py
```

## ✅ Checklist de Verificación

- [ ] Repositorio clonado en `/var/www/btc`
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Archivo `.env` configurado
- [ ] Base de datos MySQL con tablas creadas
- [ ] Directorio `logs/` creado
- [ ] Ejecución manual funciona
- [ ] Servicio systemd configurado
- [ ] Servicio iniciado y corriendo
- [ ] Puerto 3001 accesible desde internet
- [ ] Health check funciona
- [ ] Docs API accesibles

## 🎯 Próximo Paso

Una vez que el servicio esté corriendo, puedes:

1. **Probar con curl**:
```bash
curl -X POST http://64.23.132.230:3001/api/v1/candles \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "open": 43500,
    "high": 43800,
    "low": 43400,
    "close": 43700,
    "volume": 1250,
    "open_time": 1704067200000,
    "close_time": 1704070800000
  }'
```

2. **Integrar con Flutter** siguiendo `FLUTTER_INTEGRATION.md`

## 📞 Soporte

Si tienes problemas:
1. Revisar logs: `tail -f /var/www/btc/logs/app.log`
2. Verificar servicio: `sudo systemctl status crypto-trading`
3. Revisar salud: `curl http://localhost:3001/api/v1/health`

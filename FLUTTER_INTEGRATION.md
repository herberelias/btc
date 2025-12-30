# Guía Rápida - Integración Flutter con Backend

## 📍 Información del Servidor

- **URL Base**: `http://64.23.132.230:3001/api/v1`
- **Documentación API**: `http://64.23.132.230:3001/docs`
- **Health Check**: `http://64.23.132.230:3001/api/v1/health`

## 🚀 Endpoints Disponibles

### 1. POST /candles
Envía una vela y recibe predicción automáticamente.

**Request:**
```dart
final response = await http.post(
  Uri.parse('$baseUrl/candles'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'symbol': 'BTCUSDT',      // Requerido
    'timeframe': '1h',         // Requerido: 5m, 15m, 1h, 4h, 1d
    'open': 43500.50,          // Requerido
    'high': 43800.20,          // Requerido
    'low': 43400.10,           // Requerido
    'close': 43700.80,         // Requerido
    'volume': 1250.5,          // Requerido
    'open_time': 1704067200000,   // Timestamp en milisegundos
    'close_time': 1704070800000,  // Timestamp en milisegundos
  }),
);
```

**Response (si genera señal):**
```json
{
  "success": true,
  "candle_id": 12345,
  "indicators_calculated": true,
  "prediction": {
    "id": 789,
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "type": "LONG",              // o "SHORT" o "NEUTRAL"
    "confidence": 85.5,          // 0-100%
    "entry_price": 43700.80,
    "stop_loss": 43200.00,
    "take_profit": 44500.00,
    "risk_reward": 1.6,
    "position_size": 5.0,        // % recomendado
    "model_version": "1.0",
    "expires_at": 1704074400000,
    "market_context": {
      "regime": "bull",          // bull, bear, sideways
      "fear_greed_index": 65,    // 0-100
      "fear_greed_classification": "Greed",
      "btc_dominance": 52.3
    }
  }
}
```

**Response (si NO genera señal - confidence baja):**
```json
{
  "success": true,
  "candle_id": 12345,
  "indicators_calculated": true,
  "prediction": null,
  "message": "No high-confidence signal generated"
}
```

### 2. GET /predictions/active
Consulta señales activas con alta confianza.

**Request:**
```dart
// Sin filtros
final response = await http.get(
  Uri.parse('$baseUrl/predictions/active')
);

// Con filtros
final response = await http.get(
  Uri.parse('$baseUrl/predictions/active')
    .replace(queryParameters: {
      'symbol': 'BTCUSDT',
      'min_confidence': '75',
    })
);
```

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
      // ... más campos
    }
  ],
  "total": 1
}
```

### 3. GET /health
Verifica estado del sistema.

**Request:**
```dart
final response = await http.get(
  Uri.parse('$baseUrl/health')
);
```

**Response:**
```json
{
  "status": "healthy",
  "database": "healthy",
  "ml_model": "loaded",  // o "not loaded"
  "version": "1.0.0",
  "model_version": "1.0"
}
```

## 📦 Modelos Dart Sugeridos

### Signal Model
```dart
class Signal {
  final int id;
  final String symbol;
  final String timeframe;
  final SignalType type;
  final double confidence;
  final double entryPrice;
  final double? stopLoss;
  final double? takeProfit;
  final double? riskReward;
  final double? positionSize;
  final MarketContext? marketContext;
  final DateTime createdAt;

  Signal({
    required this.id,
    required this.symbol,
    required this.timeframe,
    required this.type,
    required this.confidence,
    required this.entryPrice,
    this.stopLoss,
    this.takeProfit,
    this.riskReward,
    this.positionSize,
    this.marketContext,
    required this.createdAt,
  });

  factory Signal.fromJson(Map<String, dynamic> json) {
    return Signal(
      id: json['id'],
      symbol: json['symbol'],
      timeframe: json['timeframe'],
      type: SignalType.fromString(json['type']),
      confidence: (json['confidence'] as num).toDouble(),
      entryPrice: (json['entry_price'] as num).toDouble(),
      stopLoss: json['stop_loss'] != null 
          ? (json['stop_loss'] as num).toDouble() 
          : null,
      takeProfit: json['take_profit'] != null 
          ? (json['take_profit'] as num).toDouble() 
          : null,
      riskReward: json['risk_reward'] != null 
          ? (json['risk_reward'] as num).toDouble() 
          : null,
      positionSize: json['position_size'] != null 
          ? (json['position_size'] as num).toDouble() 
          : null,
      marketContext: json['market_context'] != null
          ? MarketContext.fromJson(json['market_context'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
    );
  }
  
  // Helper para mostrar color según tipo
  Color get signalColor {
    switch (type) {
      case SignalType.long:
      case SignalType.strongLong:
        return Colors.green;
      case SignalType.short:
      case SignalType.strongShort:
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}

enum SignalType {
  long,
  short,
  neutral,
  strongLong,
  strongShort;
  
  static SignalType fromString(String value) {
    switch (value.toUpperCase()) {
      case 'LONG':
        return SignalType.long;
      case 'SHORT':
        return SignalType.short;
      case 'STRONG_LONG':
        return SignalType.strongLong;
      case 'STRONG_SHORT':
        return SignalType.strongShort;
      default:
        return SignalType.neutral;
    }
  }
  
  String get displayName {
    switch (this) {
      case SignalType.long:
        return 'LONG';
      case SignalType.short:
        return 'SHORT';
      case SignalType.strongLong:
        return 'STRONG LONG';
      case SignalType.strongShort:
        return 'STRONG SHORT';
      default:
        return 'NEUTRAL';
    }
  }
}

class MarketContext {
  final String regime;
  final int fearGreedIndex;
  final String fearGreedClassification;
  final double? btcDominance;

  MarketContext({
    required this.regime,
    required this.fearGreedIndex,
    required this.fearGreedClassification,
    this.btcDominance,
  });

  factory MarketContext.fromJson(Map<String, dynamic> json) {
    return MarketContext(
      regime: json['regime'],
      fearGreedIndex: json['fear_greed_index'],
      fearGreedClassification: json['fear_greed_classification'],
      btcDominance: json['btc_dominance'] != null
          ? (json['btc_dominance'] as num).toDouble()
          : null,
    );
  }
  
  Color get regimeColor {
    switch (regime.toLowerCase()) {
      case 'bull':
        return Colors.green;
      case 'bear':
        return Colors.red;
      case 'volatile':
        return Colors.orange;
      default:
        return Colors.blue;
    }
  }
}
```

## 🔧 Service Flutter

### TradingApiService
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class TradingApiService {
  static const String baseUrl = 'http://64.23.132.230:3001/api/v1';
  
  /// Envía una vela al backend y recibe predicción si hay señal
  Future<Signal?> sendCandle({
    required String symbol,
    required String timeframe,
    required double open,
    required double high,
    required double low,
    required double close,
    required double volume,
    required int openTime,
    required int closeTime,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/candles'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'symbol': symbol,
          'timeframe': timeframe,
          'open': open,
          'high': high,
          'low': low,
          'close': close,
          'volume': volume,
          'open_time': openTime,
          'close_time': closeTime,
        }),
      ).timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        
        if (data['prediction'] != null) {
          return Signal.fromJson(data['prediction']);
        }
      } else if (response.statusCode == 409) {
        print('Vela duplicada - ignorando');
        return null;
      } else {
        print('Error: ${response.statusCode} - ${response.body}');
        return null;
      }
      
      return null;
    } catch (e) {
      print('Error enviando vela: $e');
      return null;
    }
  }
  
  /// Obtiene señales activas
  Future<List<Signal>> getActiveSignals({
    String? symbol,
    String? timeframe,
    double? minConfidence,
  }) async {
    try {
      final queryParams = <String, String>{};
      if (symbol != null) queryParams['symbol'] = symbol;
      if (timeframe != null) queryParams['timeframe'] = timeframe;
      if (minConfidence != null) {
        queryParams['min_confidence'] = minConfidence.toString();
      }
      
      final uri = Uri.parse('$baseUrl/predictions/active')
          .replace(queryParameters: queryParams);
      
      final response = await http.get(uri)
          .timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List signalsJson = data['signals'];
        return signalsJson.map((json) => Signal.fromJson(json)).toList();
      }
      
      return [];
    } catch (e) {
      print('Error obteniendo señales: $e');
      return [];
    }
  }
  
  /// Health check
  Future<bool> isHealthy() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health')
      ).timeout(const Duration(seconds: 5));
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['status'] == 'healthy';
      }
      
      return false;
    } catch (e) {
      print('Error en health check: $e');
      return false;
    }
  }
}
```

## 💡 Uso Recomendado en Flutter

### 1. Al obtener nueva vela de CoinGecko:
```dart
final apiService = TradingApiService();

// Cada vez que recibes una vela nueva
final signal = await apiService.sendCandle(
  symbol: 'BTCUSDT',
  timeframe: '1h',
  open: candle.open,
  high: candle.high,
  low: candle.low,
  close: candle.close,
  volume: candle.volume,
  openTime: candle.openTime.millisecondsSinceEpoch,
  closeTime: candle.closeTime.millisecondsSinceEpoch,
);

if (signal != null) {
  // ¡Hay una señal con alta confianza!
  if (signal.confidence >= 80) {
    // Mostrar notificación importante
    showHighConfidenceAlert(signal);
  } else {
    // Guardar en lista de señales
    addSignalToList(signal);
  }
}
```

### 2. Consultar señales activas periódicamente:
```dart
// Por ejemplo, cada 5 minutos
Timer.periodic(const Duration(minutes: 5), (timer) async {
  final signals = await apiService.getActiveSignals(
    minConfidence: 75,
  );
  
  // Actualizar UI con señales
  updateSignalsList(signals);
});
```

### 3. Al iniciar la app:
```dart
@override
void initState() {
  super.initState();
  _checkBackendHealth();
}

Future<void> _checkBackendHealth() async {
  final isHealthy = await apiService.isHealthy();
  
  if (!isHealthy) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Error de Conexión'),
        content: Text('No se puede conectar al servidor de señales'),
      ),
    );
  }
}
```

## 🎯 Threshold de Confianza Recomendado

- **≥ 85%**: Señal MUY fuerte - Notificación push + alerta visual
- **75-84%**: Señal fuerte - Mostrar destacada
- **70-74%**: Señal moderada - Mostrar en lista normal
- **< 70%**: No se genera señal (el backend ya filtra)

## 🔒 Notas Importantes

1. **Velas duplicadas**: El backend rechaza velas duplicadas (409 Conflict) - es normal
2. **Timeout**: Configurar timeout de 10 segundos para requests
3. **Error handling**: Siempre manejar errores de red
4. **Cache**: Considerar cachear señales localmente
5. **Timestamps**: Usar milisegundos (JavaScript format)

## 📞 Testing Rápido

### Con curl:
```bash
# Health check
curl http://64.23.132.230:3001/api/v1/health

# Enviar vela de prueba
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

### En navegador:
- Docs interactivas: `http://64.23.132.230:3001/docs`
- Probar endpoints desde la UI de Swagger

## ✅ Checklist de Integración

- [ ] Implementar modelos Dart (Signal, MarketContext)
- [ ] Crear TradingApiService
- [ ] Conectar al obtener nuevas velas
- [ ] Implementar consulta periódica de señales activas
- [ ] Agregar UI para mostrar señales
- [ ] Implementar notificaciones para señales >85%
- [ ] Agregar manejo de errores
- [ ] Probar con datos reales

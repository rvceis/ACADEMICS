# System Architecture Diagram

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        SOLAR SHARING AIML SYSTEM                 │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────────┐
│   DATA SOURCES         │
├────────────────────────┤
│ • NSRDB Solar CSV      │  ml-service/data/raw/
│ • Meter Consumption    │  ├── solar_site_1_2024.csv
│ • Weather Data         │  ├── meter_consumption_2024.csv
│ • Real-time MQTT       │  └── weather_2024.csv
└───────────┬────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────────┐
│  BATCH PREPROCESSING (scripts/batch_preprocess.py)             │
│                                                                 │
│  • Auto-detect CSV format (NSRDB/meter/weather)               │
│  • NSRDB header skip (first 2 metadata rows)                  │
│  • Schema validation (DataContractValidator)                  │
│  • Missing value imputation                                   │
│  • Outlier removal & scaling                                  │
│  • Feature engineering (temporal, seasonal, rolling avg)       │
│  • Parallel processing (4 workers default)                    │
└───────────┬────────────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────────┐
│  PROCESSED DATA (ml-service/data/processed/)                   │
│                                                                 │
│  ├── solar_processed_*.csv (1000s rows, 40+ cols)             │
│  ├── meter_processed_*.csv (8760 rows, 12+ cols)              │
│  └── All NaN, outliers, invalid rows removed                  │
└───────────┬────────────────────────────────────────────────────┘
            │
            ├─────────────────────┬──────────────────┬─────────────┐
            │                     │                  │             │
            ▼                     ▼                  ▼             ▼
    ┌──────────────────┐  ┌──────────────────┐  ┌─────────┐  ┌──────────┐
    │ LSTM Training    │  │ XGBoost Training │  │ Risk RF │  │Anomaly IF│
    │ (24h lookback)   │  │ (max_depth=6)    │  │ Clf     │  │Detector  │
    │ 50 epochs        │  │ 200 estimators   │  │(100 est)│  │(contam=5)│
    └────────┬─────────┘  └────────┬─────────┘  └────┬────┘  └──────┬───┘
             │                    │               │          │
             └────────────────┬───┴───────────────┼──────────┘
                              │                  │
                              ▼                  ▼
                      ┌─────────────────────────────────────┐
                      │  MLflow Tracking Server :5000       │
                      │  • All metrics logged (MAE/RMSE)   │
                      │  • Model versions registered        │
                      │  • Artifacts persisted              │
                      │  • Stage transitions tracked        │
                      └──────────────┬──────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
            ┌──────────────────┐          ┌──────────────────┐
            │ Model Registry   │          │ ml-service/      │
            │ (Production)     │          │ models/          │
            │ ├─ solar_lstm:v3 │          │ ├─ solar_lstm.h5 │
            │ ├─ demand_xgb:v2 │          │ ├─ solar_xgb.pkl │
            │ └─ risk_rf:v1    │          │ └─ anomaly_if.pkl│
            └────────┬─────────┘          └────────┬─────────┘
                     │                            │
                     └────────────┬────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────┐
                    │   ML SERVICE (FastAPI) :8000    │
                    │  • /api/v1/forecast/solar       │
                    │  • /api/v1/forecast/demand      │
                    │  • /api/v1/risk/score           │
                    │  • /api/v1/anomaly/detect       │
                    │  • /api/v1/batch/forecast       │
                    │  • /health                      │
                    └──────────────┬──────────────────┘
                                   │
                                   ▼
        ┌──────────────────────────────────────────────────────┐
        │           ML CLIENT (mlClient.js)                    │
        │  • Exponential backoff retry logic                   │
        │  • Circuit breaker (opens after 5 failures)         │
        │  • Timeout: 30s per request                         │
        │  • Max retries: 3 (configurable)                    │
        │  • Fallback to cached predictions                   │
        └──────────────┬───────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────────────────┐
        │       BACKEND (Node.js/Express) :3000               │
        │                                                      │
        │  IoT Routes:                                        │
        │  ├─ POST /api/iot/devices/register                 │
        │  ├─ GET /api/iot/devices                           │
        │  ├─ GET /api/iot/devices/:id/forecast              │
        │  ├─ POST /api/iot/devices/:id/command              │
        │  ├─ GET /api/iot/health                            │
        │  └─ GET /health                                    │
        │                                                      │
        │  IoT Manager:                                       │
        │  ├─ MQTT subscriptions (solar/+/data, status)      │
        │  ├─ Device registration & tracking                 │
        │  ├─ Batch buffering (100 records)                  │
        │  ├─ ML calls for predictions                        │
        │  └─ Forecast publishing (solar/+/forecast)         │
        └──────────────┬───────────────────────────────────────┘
                       │
                ┌──────┴──────┐
                │             │
                ▼             ▼
    ┌──────────────────┐  ┌───────────────────────┐
    │   MQTT Broker    │  │   Data Storage        │
    │  Mosquitto:1883  │  │  • Redis :6380        │
    │                  │  │  • PostgreSQL :5434   │
    │ Topics:          │  │  • TimescaleDB :5433  │
    │ • solar/+/data   │  │                       │
    │ • solar/+/status │  │ Device history,       │
    │ • solar/+/       │  │ forecasts, anomalies  │
    │   forecast       │  │ persisted             │
    │ • solar/+/       │  └───────────────────────┘
    │   anomaly        │
    │ • solar/+/       │
    │   command        │
    └──────────────────┘
            ▲
            │
    ┌───────┴────────────────────────────────────┐
    │         IoT DEVICES (Real Hardware)        │
    │                                            │
    │  • Solar Inverters (via MQTT)             │
    │  • Smart Meters (via MQTT)                │
    │  • Weather Stations (via MQTT)            │
    │                                            │
    │  Publish: solar/{id}/data every 15min     │
    │  Subscribe: solar/{id}/forecast           │
    │  Subscribe: solar/{id}/command            │
    └────────────────────────────────────────────┘
```

---

## Component Responsibilities

### ML Service Layer
```
┌─────────────────────────────────────────────────┐
│ src/config/schemas.py                           │
│ └─ DataContractValidator                        │
│    ├─ NSRDB_SCHEMA (37 columns, units, ranges) │
│    ├─ METER_SCHEMA (10 columns)                │
│    └─ WEATHER_SCHEMA (6 columns)               │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ src/services/training_service.py                │
│ ├─ SolarGenerationTrainer (LSTM + XGBoost)    │
│ ├─ DemandTrainer (XGBoost)                     │
│ ├─ RiskScoringTrainer (Random Forest)          │
│ ├─ AnomalyDetectorTrainer (Isolation Forest)   │
│ └─ train_all_models() → all to MLflow          │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ src/services/evaluation_service.py              │
│ ├─ ModelEvaluator                              │
│ │  ├─ compute_regression_metrics()             │
│ │  ├─ compute_classification_metrics()         │
│ │  ├─ compare_models()                         │
│ │  └─ generate_report()                        │
│ ├─ ModelSelector                               │
│ │  ├─ select_best_regression_model()           │
│ │  └─ select_best_classification_model()       │
│ └─ MLflowHelper                                │
│    ├─ register_model_to_registry()             │
│    └─ get_best_model_version()                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ scripts/batch_preprocess.py                     │
│ ├─ detect_data_source() → auto-detect format   │
│ ├─ preprocess_file() → per-file pipeline       │
│ └─ batch_preprocess() → multi-worker entry     │
└─────────────────────────────────────────────────┘
```

### Backend Layer
```
┌─────────────────────────────────────────────────┐
│ src/services/mlClient.js                        │
│ ├─ CircuitBreaker                              │
│ │  ├─ state (CLOSED/OPEN/HALF_OPEN)           │
│ │  └─ failureThreshold (5)                     │
│ └─ MLClient                                    │
│    ├─ _withRetry() exponential backoff         │
│    ├─ predictSolarGeneration()                 │
│    ├─ predictDemand()                          │
│    ├─ scoreRisk()                              │
│    ├─ detectAnomaly()                          │
│    ├─ batchPredict()                           │
│    └─ healthCheck()                            │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ src/services/iotManager.js                      │
│ ├─ initMQTT() → connect broker                 │
│ ├─ handleMQTTMessage() → solar/+/data          │
│ ├─ processDeviceData() → buffer & call ML      │
│ ├─ predictForDevice() → ML client wrapper      │
│ ├─ publishForecast() → solar/{id}/forecast     │
│ └─ Graceful shutdown → flush & disconnect      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ src/routes/iotRoutes.js                         │
│ ├─ POST /api/iot/devices/register               │
│ ├─ GET /api/iot/devices                         │
│ ├─ GET /api/iot/devices/:id                     │
│ ├─ GET /api/iot/devices/:id/forecast            │
│ ├─ POST /api/iot/devices/:id/command            │
│ ├─ GET /api/iot/health                          │
│ └─ GET /health                                  │
└─────────────────────────────────────────────────┘
```

---

## Data Flow: Real-time Forecast

```
1. MQTT Publish (Solar Inverter)
   solar/device_01/data: {"ghi": 500, "temperature": 25, ...}

2. Backend MQTT Subscribe
   iotManager.js receives → handleMQTTMessage()

3. Buffer Data
   Device buffer accumulates up to 100 records

4. Call ML Service
   MLClient.predictSolarGeneration()
   ├─ Attempt 1: Try direct call
   ├─ Retry with backoff if transient error
   └─ Circuit breaker: Skip if too many failures

5. ML Service Prediction
   LSTM/XGBoost model
   → Solar forecast: 3.5 kW, confidence: 0.92

6. Backend Response
   Response routed back to iotManager

7. MQTT Publish Forecast
   solar/device_01/forecast: {"forecast_kw": 3.5, "confidence": 0.92}

8. Database Log
   Redis/PostgreSQL record: timestamp, device, prediction, confidence

9. Device Subscribe
   Solar controller receives forecast → optimizes battery charging
```

---

## Failure Handling: Circuit Breaker in Action

```
Normal Operation (CLOSED):
  Request 1 ✓ → failureCount = 0
  Request 2 ✓ → failureCount = 0
  Request 3 ✓ → state = CLOSED

ML Service Down (FAILURES):
  Request 4 ✗ → failureCount = 1
  Request 5 ✗ → failureCount = 2
  Request 6 ✗ → failureCount = 3
  Request 7 ✗ → failureCount = 4
  Request 8 ✗ → failureCount = 5 → state = OPEN ❌

Circuit Open (60s timeout):
  Request 9 → REJECTED (circuit open)
  Request 10 → REJECTED (circuit open)
  ...
  After 60s → state = HALF_OPEN (test recovery)

Half-Open (Test Recovery):
  Request N ✓ → failureCount = 0, state = CLOSED ✓✓
  OR
  Request N ✗ → failureCount = 1, state = OPEN (back to blocking)
```

---

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python 3.10 | 3.10.x | ML pipeline |
| | Node.js | 18+ | Backend |
| **ML Frameworks** | TensorFlow/Keras | 2.14 | LSTM training |
| | XGBoost | 1.7+ | Gradient boosting |
| | scikit-learn | 1.3+ | RF, IF, preprocessing |
| **API** | FastAPI | 0.100+ | ML service REST |
| | Express.js | 4.18+ | Backend REST |
| **Tracking** | MLflow | 2.9+ | Model versioning |
| **Message Bus** | MQTT | 3.1.1 | Pub/sub (Mosquitto 2.0+) |
| **Database** | PostgreSQL | 15+ | Time-series (TimescaleDB) |
| | Redis | 7+ | Caching, feature store |
| **Containerization** | Docker | 24+ | Images |
| | Docker Compose | 2.20+ | Orchestration |
| **Preprocessing** | Pandas | 2.0+ | Data manipulation |
| | NumPy | 1.24+ | Numerical ops |

---

## Deployment Targets

- **Local Development:** Docker Compose (all-in-one)
- **Production:** Kubernetes (recommended) or Docker Swarm
- **Scaling:** Horizontal scaling via service replicas
- **Monitoring:** Prometheus + Grafana (future)
- **CI/CD:** GitHub Actions / GitLab CI (future)

---

**Architecture Version:** 1.0  
**Last Updated:** 2024-01-17  
**Status:** Production-Ready

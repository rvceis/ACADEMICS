# Solar Sharing Platform - IoT Implementation Guide

## 🔌 Overview

The IoT system enables real-time solar energy monitoring, device management, and ML-powered forecasting. It uses MQTT for device communication and supports multiple meter types.

---

## 📡 Architecture

```
┌─────────────────┐      MQTT      ┌──────────────┐
│  Solar Devices  │ ════════════> │ IoT Manager  │
│  (ESP32/Rasp.)  │               │  (Node.js)   │
└─────────────────┘               └──────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
            ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
            │  PostgreSQL  │    │    Redis     │    │  ML Service  │
            │  (TimescaleDB)│    │   (Cache)    │    │  (Python)    │
            └──────────────┘    └──────────────┘    └──────────────┘
```

---

## 🎯 Supported Device Types

### 1. **Solar Meter** (Solar Panel/Inverter)
- Measures: Power generation, voltage, current, energy
- Use case: Track solar production
- MQTT Topic: `solar/{device_id}/data`

### 2. **Consumption Meter**
- Measures: Power consumption, load profile
- Use case: Track energy usage
- MQTT Topic: `solar/{device_id}/data`

### 3. **Battery BMS**
- Measures: SOC, voltage, current, temperature
- Use case: Monitor battery storage
- MQTT Topic: `solar/{device_id}/data`

### 4. **Weather Station**
- Measures: Irradiance, temperature, humidity, wind
- Use case: Forecast optimization
- MQTT Topic: `solar/{device_id}/data`

---

## 🚀 Quick Start

### Backend Setup

1. **Install Dependencies**
```bash
cd backend
npm install mqtt axios
```

2. **Configure Environment**
```env
# .env
MQTT_URL=mqtt://localhost:1883
ML_SERVICE_URL=http://localhost:8001
```

3. **Start MQTT Broker (Docker)**
```bash
docker run -d \
  --name mqtt-broker \
  -p 1883:1883 \
  -p 9001:9001 \
  eclipse-mosquitto
```

4. **Start Backend**
```bash
npm run dev
```

The IoT Manager auto-initializes and subscribes to:
- `solar/+/data` - Device readings
- `solar/+/status` - Device status updates

---

## 📤 Device Registration

### Frontend (React Native)

```typescript
import { deviceApi } from './api/deviceService';

const registerDevice = async () => {
  const response = await deviceApi.registerDevice({
    deviceType: 'solar_meter',  // or 'solar_panel' mapped to solar_meter
    deviceModel: 'SMA SunnyBoy 5.0',
    firmwareVersion: 'v2.1.0'
  });
  
  console.log('Device ID:', response.device.device_id);
  console.log('MQTT Topic:', `solar/${response.device.device_id}/data`);
};
```

### Backend API

**POST** `/api/v1/iot/devices`
```json
{
  "deviceType": "solar_meter",
  "deviceModel": "SMA SunnyBoy 5.0",
  "firmwareVersion": "v2.1.0"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "device": {
      "device_id": "device_abc123",
      "device_type": "solar_meter",
      "status": "pending",
      "user_id": "user_xyz"
    }
  }
}
```

---

## 📡 MQTT Communication

### Message Format

#### Device → Backend (Data)

**Topic:** `solar/{device_id}/data`

```json
{
  "timestamp": "2026-01-19T10:30:00Z",
  "power_kw": 4.5,
  "voltage": 230.5,
  "current": 19.6,
  "frequency": 50.0,
  "energy_kwh": 2.3,
  "temperature": 35.2,
  "power_factor": 0.98
}
```

#### Device → Backend (Status)

**Topic:** `solar/{device_id}/status`

```json
{
  "status": "online",
  "signal_strength": 85,
  "error_code": null
}
```

#### Backend → Device (Forecast)

**Topic:** `solar/{device_id}/forecast`

```json
{
  "timestamp": "2026-01-19T10:30:00Z",
  "predictions": [4.5, 4.8, 5.1, 5.3, 4.9, 4.2],
  "confidence": [
    {"lower": 4.0, "upper": 5.0},
    {"lower": 4.3, "upper": 5.3}
  ]
}
```

#### Backend → Device (Command)

**Topic:** `solar/{device_id}/command`

```json
{
  "command": "restart",
  "timestamp": "2026-01-19T10:30:00Z"
}
```

---

## 🔧 ESP32/Arduino Example

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASS";
const char* mqtt_server = "your-backend-ip";
const char* device_id = "device_abc123";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  client.setServer(mqtt_server, 1883);
  reconnect();
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect(device_id)) {
      Serial.println("MQTT Connected");
      
      // Subscribe to commands
      String cmdTopic = "solar/" + String(device_id) + "/command";
      client.subscribe(cmdTopic.c_str());
    } else {
      delay(5000);
    }
  }
}

void publishData() {
  StaticJsonDocument<256> doc;
  
  doc["timestamp"] = "2026-01-19T10:30:00Z";
  doc["power_kw"] = readPower();
  doc["voltage"] = readVoltage();
  doc["current"] = readCurrent();
  doc["temperature"] = readTemperature();
  
  char buffer[256];
  serializeJson(doc, buffer);
  
  String topic = "solar/" + String(device_id) + "/data";
  client.publish(topic.c_str(), buffer);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
  
  // Publish every 10 seconds
  static unsigned long lastPublish = 0;
  if (millis() - lastPublish > 10000) {
    publishData();
    lastPublish = millis();
  }
}
```

---

## 🧪 Testing with Mosquitto Client

### 1. Subscribe to All Solar Topics
```bash
mosquitto_sub -h localhost -t 'solar/#' -v
```

### 2. Publish Test Data
```bash
mosquitto_pub -h localhost \
  -t 'solar/test_device_001/data' \
  -m '{
    "timestamp": "2026-01-19T10:30:00Z",
    "power_kw": 4.5,
    "voltage": 230.5,
    "current": 19.6,
    "temperature": 35.2
  }'
```

### 3. Publish Status
```bash
mosquitto_pub -h localhost \
  -t 'solar/test_device_001/status' \
  -m '{
    "status": "online",
    "signal_strength": 85
  }'
```

### 4. Test Command
```bash
mosquitto_pub -h localhost \
  -t 'solar/test_device_001/command' \
  -m '{"command": "restart"}'
```

---

## 📊 Data Validation

The backend validates all incoming data:

| Field | Valid Range | Unit |
|-------|-------------|------|
| `power_kw` | 0 - 100 | kW |
| `voltage` | 200 - 260 | V |
| `current` | 0 - 500 | A |
| `temperature` | -20 - 60 | °C |
| `battery_soc` | 0 - 100 | % |
| `frequency` | 49 - 51 | Hz |

Invalid data is logged and discarded.

---

## 🤖 ML Forecasting

Every 100 readings, the system:
1. Batches data by device
2. Calls ML service at `http://localhost:8001/api/v1/forecast/solar`
3. Receives 24-hour forecast
4. Publishes to `solar/{device_id}/forecast`

### ML Service Payload
```json
{
  "host_id": "device_abc123",
  "panel_capacity_kw": 5.0,
  "historical_data": [
    {
      "timestamp": "2026-01-19T10:00:00Z",
      "power_kw": 4.2,
      "voltage": 230,
      "current": 18.3
    }
  ],
  "forecast_hours": 24
}
```

---

## 🔌 API Endpoints

### Device Management

#### Register Device
```http
POST /api/v1/iot/devices
Authorization: Bearer {token}

{
  "deviceType": "solar_meter",
  "deviceModel": "SMA SunnyBoy",
  "firmwareVersion": "v2.1.0"
}
```

#### Get All Devices
```http
GET /api/v1/iot/devices
Authorization: Bearer {token}
```

#### Get Device Details
```http
GET /api/v1/iot/devices/{deviceId}
Authorization: Bearer {token}
```

#### Update Device
```http
PUT /api/v1/iot/devices/{deviceId}
Authorization: Bearer {token}

{
  "status": "active",
  "deviceModel": "Updated Model"
}
```

#### Delete Device
```http
DELETE /api/v1/iot/devices/{deviceId}
Authorization: Bearer {token}
```

### Data Access

#### Get Latest Reading
```http
GET /api/v1/iot/latest
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "reading": {
      "device_id": "device_abc123",
      "timestamp": "2026-01-19T10:30:00Z",
      "power_kw": 4.5,
      "voltage": 230.5,
      "current": 19.6
    },
    "lastUpdated": "2026-01-19T10:30:05Z"
  }
}
```

#### Get Reading History
```http
GET /api/v1/iot/history?startDate=2026-01-18&endDate=2026-01-19&interval=hourly
Authorization: Bearer {token}
```

#### Ingest Data (Manual)
```http
POST /api/v1/iot/data
Authorization: Bearer {token}

{
  "device_id": "device_abc123",
  "user_id": "user_xyz",
  "timestamp": "2026-01-19T10:30:00Z",
  "measurements": {
    "power_kw": 4.5,
    "voltage": 230.5
  }
}
```

### Device Control

#### Send Command
```http
POST /api/v1/iot/devices/{deviceId}/command
Authorization: Bearer {token}

{
  "command": "restart",
  "value": null
}
```

#### Get Forecast
```http
GET /api/v1/iot/devices/{deviceId}/forecast
Authorization: Bearer {token}
```

---

## 💾 Database Schema

### `devices` Table
```sql
CREATE TABLE devices (
  device_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  device_type VARCHAR(50) NOT NULL,
  device_model VARCHAR(100),
  firmware_version VARCHAR(50),
  status VARCHAR(20) DEFAULT 'pending',
  last_seen_at TIMESTAMPTZ,
  last_reading JSONB,
  configuration JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_devices_user_id ON devices(user_id);
CREATE INDEX idx_devices_status ON devices(status);
```

### `energy_readings` Table (TimescaleDB)
```sql
CREATE TABLE energy_readings (
  time TIMESTAMPTZ NOT NULL,
  device_id UUID NOT NULL,
  user_id UUID NOT NULL,
  measurement_type VARCHAR(50),
  power_kw DECIMAL(10, 4),
  energy_kwh DECIMAL(12, 4),
  voltage DECIMAL(8, 2),
  current DECIMAL(8, 2),
  frequency DECIMAL(5, 2),
  power_factor DECIMAL(4, 2),
  battery_soc DECIMAL(5, 2),
  battery_voltage DECIMAL(8, 2),
  battery_current DECIMAL(8, 2),
  temperature DECIMAL(5, 2),
  metadata JSONB
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('energy_readings', 'time');

-- Create indexes
CREATE INDEX idx_readings_device ON energy_readings(device_id, time DESC);
CREATE INDEX idx_readings_user ON energy_readings(user_id, time DESC);
```

---

## 🔐 Security

### MQTT Authentication
```javascript
// Add to backend .env
MQTT_USERNAME=solar_backend
MQTT_PASSWORD=secure_password_here
```

### API Authentication
All IoT endpoints require JWT token:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Device Ownership
Backend validates:
- Device belongs to authenticated user
- Status is not 'decommissioned'
- Readings are within valid time window

---

## 📈 Monitoring & Debugging

### Health Check
```http
GET /api/v1/iot/health
```

**Response:**
```json
{
  "status": "ok",
  "mqtt_connected": true,
  "total_devices": 15,
  "online_devices": 12,
  "timestamp": "2026-01-19T10:30:00Z"
}
```

### Backend Logs
```bash
# Watch real-time logs
tail -f logs/app.log | grep IoT

# Check MQTT connection
curl http://localhost:3000/api/v1/iot/health
```

### Device Logs
```bash
# Monitor all device data
mosquitto_sub -h localhost -t 'solar/+/data' -v

# Monitor specific device
mosquitto_sub -h localhost -t 'solar/device_abc123/#' -v
```

---

## 🛠️ Troubleshooting

### Device Not Receiving Forecast

**Check:**
1. Device registered: `GET /api/v1/iot/devices`
2. MQTT connected: `GET /api/v1/iot/health`
3. ML service running: `curl http://localhost:8001/health`
4. Subscribe to forecast topic: `mosquitto_sub -t 'solar/{device_id}/forecast'`

### Data Not Appearing

**Check:**
1. Valid MQTT topic format: `solar/{device_id}/data`
2. JSON payload valid
3. Timestamp not too old (< 1 hour)
4. Values within valid ranges
5. Backend logs: `grep "device_id" logs/app.log`

### MQTT Connection Failed

**Solutions:**
```bash
# Check broker running
docker ps | grep mosquitto

# Restart broker
docker restart mqtt-broker

# Test connection
mosquitto_pub -h localhost -t test -m "hello"
```

---

## 🚦 Production Deployment

### 1. Set Up MQTT Broker (Render.com)

**Option A: External MQTT Service**
- Use CloudMQTT, HiveMQ, or AWS IoT Core
- Update `MQTT_URL` in environment

**Option B: Self-hosted on Render**
```yaml
# render.yaml
services:
  - type: web
    name: mqtt-broker
    env: docker
    dockerfilePath: ./mqtt/Dockerfile
    envVars:
      - key: MQTT_PORT
        value: 1883
```

### 2. Update Backend Environment
```env
MQTT_URL=mqtt://your-mqtt-broker.com:1883
MQTT_USERNAME=production_user
MQTT_PASSWORD=secure_prod_password
ML_SERVICE_URL=https://ml-service.render.com
```

### 3. Deploy
```bash
git add .
git commit -m "Add IoT implementation"
git push origin main
```

Render auto-deploys and:
- Initializes MQTT connection
- Subscribes to device topics
- Starts processing data

---

## 📱 Frontend Integration

### Device Management Screen

Already implemented in:
- `frontend/src/screens/host/AddDeviceScreen.tsx`
- `frontend/src/screens/devices/DeviceManagementScreen.tsx`

### Real-Time Energy Display

```typescript
import { iotApi } from './api/iotService';

const EnergyScreen = () => {
  const [reading, setReading] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      const response = await iotApi.getLatestReading();
      setReading(response.data.reading);
    };
    
    fetchData();
    const interval = setInterval(fetchData, 10000); // Poll every 10s
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <View>
      <Text>Current Power: {reading?.power_kw} kW</Text>
      <Text>Voltage: {reading?.voltage} V</Text>
      <Text>Temperature: {reading?.temperature} °C</Text>
    </View>
  );
};
```

---

## 🎓 Next Steps

1. **Add WebSocket** for true real-time updates (replace polling)
2. **Implement Alerts** for device offline/anomalies
3. **Build Dashboard** for energy analytics
4. **Add Geolocation** for weather correlation
5. **Create Mobile App** for device provisioning

---

## 📞 Support

For issues:
1. Check logs: `docker logs solar-backend`
2. Test MQTT: `mosquitto_sub -h localhost -t '#' -v`
3. Validate data: Review validation ranges
4. Check API: `curl -H "Authorization: Bearer {token}" http://localhost:3000/api/v1/iot/devices`

---

**IoT system is fully functional and ready for device connections!** 🚀

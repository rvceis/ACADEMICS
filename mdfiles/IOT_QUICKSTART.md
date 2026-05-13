# IoT Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install MQTT Broker (Docker)

```bash
docker run -d \
  --name mqtt-broker \
  -p 1883:1883 \
  -p 9001:9001 \
  eclipse-mosquitto
```

**Or use Mosquitto directly:**
```bash
# Ubuntu/Debian
sudo apt-get install mosquitto mosquitto-clients

# macOS
brew install mosquitto
brew services start mosquitto
```

### 2. Start Backend

```bash
cd backend
npm install mqtt axios
npm run dev
```

The IoT Manager will auto-connect to MQTT at `mqtt://localhost:1883`.

### 3. Register a Device (Frontend)

Open the app → **Devices** → **Add New Device**:
- Device Type: **Solar Panel (device)**
- Model: **SMA SunnyBoy 5.0**
- Firmware: **v2.1.0**

You'll get a `device_id` like `device_abc123`.

### 4. Simulate Device Data

Run the simulator:
```bash
cd backend
DEVICE_ID=device_abc123 node scripts/device-simulator.js
```

You'll see:
```
========================================================
Solar Device Simulator
========================================================
Device ID: device_abc123
MQTT Broker: mqtt://localhost:1883
Publish Interval: 10000ms
========================================================

✓ Connected to MQTT broker
✓ Subscribed to commands: solar/device_abc123/command
✓ Subscribed to forecasts: solar/device_abc123/forecast

📡 Starting to publish sensor data...

[10:30:15] 📊 Power: 4.5 kW | Voltage: 230.2V | Temp: 35.1°C
[10:30:25] 📊 Power: 4.7 kW | Voltage: 229.8V | Temp: 36.3°C
```

### 5. View Data (Frontend)

Go to **Energy** screen → You'll see real-time updates:
- Current Power: **4.5 kW**
- Voltage: **230V**
- Temperature: **35°C**
- Last Updated: **10:30:15**

---

## 📡 Test MQTT Manually

### Subscribe to All Device Data
```bash
mosquitto_sub -h localhost -t 'solar/#' -v
```

### Publish Test Reading
```bash
mosquitto_pub -h localhost \
  -t 'solar/test_device/data' \
  -m '{
    "timestamp": "2026-01-19T10:30:00Z",
    "power_kw": 4.5,
    "voltage": 230.5,
    "current": 19.6,
    "temperature": 35.2
  }'
```

### Send Command to Device
```bash
mosquitto_pub -h localhost \
  -t 'solar/device_abc123/command' \
  -m '{"command": "restart"}'
```

---

## 🔌 Connect Real Hardware (ESP32)

### Arduino Code

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";
const char* mqtt_server = "192.168.1.100"; // Your backend IP
const char* device_id = "device_abc123";   // From registration

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  
  // Connect WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  
  // Connect MQTT
  client.setServer(mqtt_server, 1883);
  reconnect();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect(device_id)) {
      Serial.println("connected");
      
      // Subscribe to commands
      String cmdTopic = "solar/" + String(device_id) + "/command";
      client.subscribe(cmdTopic.c_str());
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void publishData() {
  StaticJsonDocument<256> doc;
  
  doc["timestamp"] = "2026-01-19T10:30:00Z"; // Use NTP in production
  doc["power_kw"] = analogRead(A0) * 0.01;   // Read from sensor
  doc["voltage"] = 230.0;                     // Read from sensor
  doc["current"] = 19.5;                      // Read from sensor
  doc["temperature"] = 35.2;                  // Read from temp sensor
  
  char buffer[256];
  serializeJson(doc, buffer);
  
  String topic = "solar/" + String(device_id) + "/data";
  client.publish(topic.c_str(), buffer);
  
  Serial.println("Data published");
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

### Flash to ESP32
```bash
arduino-cli compile --fqbn esp32:esp32:esp32 solar_device.ino
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 solar_device.ino
```

---

## 📊 API Examples

### Get Latest Reading
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:3000/api/v1/iot/latest
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
      "current": 19.6,
      "temperature": 35.2
    },
    "lastUpdated": "2026-01-19T10:30:05Z"
  }
}
```

### Get Reading History
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:3000/api/v1/iot/history?startDate=2026-01-18&interval=hourly"
```

### List Devices
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:3000/api/v1/iot/devices
```

---

## 🐛 Troubleshooting

### "MQTT connection failed"

**Check broker:**
```bash
docker ps | grep mosquitto
```

**Restart broker:**
```bash
docker restart mqtt-broker
```

**Test connection:**
```bash
mosquitto_pub -h localhost -t test -m "hello"
```

### "Device not receiving data"

**Check device registration:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:3000/api/v1/iot/devices
```

**Monitor MQTT traffic:**
```bash
mosquitto_sub -h localhost -t 'solar/+/data' -v
```

**Check backend logs:**
```bash
tail -f logs/app.log | grep IoT
```

### "Invalid sensor data"

**Validation ranges:**
- Power: 0-100 kW
- Voltage: 200-260 V
- Current: 0-500 A
- Temperature: -20 to 60 °C

Make sure your readings are within these ranges.

---

## 🎯 Next Steps

1. **View real-time data** in the app Energy screen
2. **Set up ML forecasting** (see main IoT guide)
3. **Add multiple devices** for comparison
4. **Create energy listings** from your production

---

## 📞 Need Help?

Check the full guide: `IOT_IMPLEMENTATION.md`

Or test health endpoint:
```bash
curl http://localhost:3000/api/v1/iot/health
```

Expected:
```json
{
  "status": "ok",
  "mqtt_connected": true,
  "total_devices": 1,
  "online_devices": 1
}
```

**You're all set! Start generating solar data!** ⚡🌞

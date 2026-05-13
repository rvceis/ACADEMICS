/*
ESP32 SOLAR PANEL IOT DEVICE CODE
Connects to WiFi -> MQTT Broker -> Backend System

HARDWARE REQUIRED:
- ESP32 development board
- DHT22 temperature sensor (GPIO 4)
- ACS712-5A current sensor (GPIO 36/A0)
- Voltage divider circuit (GPIO 35/A7)
- 1 x 10µF capacitor (for sensor stability)

WIRING:
DHT22 Data -> GPIO 4
Current Sensor Output -> GPIO 36 (ADC)
Voltage Sensor -> GPIO 35 (ADC)
All sensors: GND to ESP32 GND, VCC to 3.3V with pull-up resistors
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ===== CONFIGURATION - CHANGE THESE VALUES =====
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"
#define MQTT_BROKER "192.168.1.100"  // MQTT broker IP
#define MQTT_PORT 1883
#define DEVICE_ID "ESP32_SOL_001"    // Unique device identifier

// ===== PIN DEFINITIONS =====
#define DHT_PIN 4                     // DHT22 data pin
#define DHT_TYPE DHT22                // DHT 22 (AM2302)
#define CURRENT_SENSOR_PIN 36         // ACS712 current sensor
#define VOLTAGE_SENSOR_PIN 35         // Voltage divider

// ===== SENSOR OBJECTS =====
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient espClient;
PubSubClient client(espClient);

// ===== CALIBRATION CONSTANTS =====
const float ACS712_SENSITIVITY = 0.185;  // 185mV per A for ACS712-5A
const float VOLTAGE_MULTIPLIER = 3.3;    // ADC to real voltage conversion
const float BATTERY_VOLTAGE = 3.3;       // Reference voltage
const float ADC_MAX = 4095.0;             // ESP32 ADC max value (12-bit)

// ===== GLOBAL VARIABLES =====
unsigned long lastReadTime = 0;
unsigned long lastPublishTime = 0;
const unsigned long READ_INTERVAL = 5000;      // Read sensors every 5 seconds
const unsigned long PUBLISH_INTERVAL = 30000;  // Publish every 30 seconds
float accumulatedEnergy = 0.0;                 // kWh accumulated today
float dailyEnergy = 0.0;                        // Daily energy total
float maxTemperature = 0.0;                     // Daily max temperature
float minTemperature = 100.0;                   // Daily min temperature
int connectionAttempts = 0;
const int MAX_CONNECTION_ATTEMPTS = 20;

// ===== FUNCTION DECLARATIONS =====
void setupWiFi();
void setupMQTT();
void reconnectMQTT();
void publishTelemetry();
void readSensors();
void handleMQTTMessage(char* topic, byte* payload, unsigned int length);

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Serial.println("\n\n=== ESP32 Solar Panel IoT Device ===");
  Serial.printf("Device ID: %s\n", DEVICE_ID);
  
  // Initialize DHT sensor
  dht.begin();
  Serial.println("DHT22 initialized");
  
  // Setup ADC
  analogReadResolution(12);
  Serial.println("ADC configured (12-bit)");
  
  // Connect to WiFi
  setupWiFi();
  
  // Setup MQTT
  setupMQTT();
  
  Serial.println("Setup complete. Ready to operate.\n");
}

void loop() {
  // Ensure WiFi is connected
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, reconnecting...");
    setupWiFi();
  }
  
  // Ensure MQTT is connected
  if (!client.connected()) {
    reconnectMQTT();
  } else {
    client.loop();  // MQTT processing
  }
  
  // Read sensors periodically
  unsigned long currentTime = millis();
  if (currentTime - lastReadTime >= READ_INTERVAL) {
    lastReadTime = currentTime;
    readSensors();
  }
  
  // Publish telemetry periodically
  if (currentTime - lastPublishTime >= PUBLISH_INTERVAL) {
    lastPublishTime = currentTime;
    publishTelemetry();
  }
  
  delay(100);  // Small delay to prevent watchdog trigger
}

// ===== WIFI SETUP =====
void setupWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  connectionAttempts = 0;
  while (WiFi.status() != WL_CONNECTED && connectionAttempts < MAX_CONNECTION_ATTEMPTS) {
    delay(500);
    Serial.print(".");
    connectionAttempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect WiFi. Retrying...");
  }
}

// ===== MQTT SETUP =====
void setupMQTT() {
  Serial.print("Connecting to MQTT broker: ");
  Serial.print(MQTT_BROKER);
  Serial.print(":");
  Serial.println(MQTT_PORT);
  
  client.setServer(MQTT_BROKER, MQTT_PORT);
  client.setCallback(handleMQTTMessage);
  
  // Create subscribe topic
  String subscribeTopic = "/command/" + String(DEVICE_ID) + "/#";
  
  reconnectMQTT();
}

// ===== MQTT RECONNECT =====
void reconnectMQTT() {
  if (client.connected()) {
    return;
  }
  
  // Create connection ID
  String clientId = "solar_" + String(DEVICE_ID);
  
  Serial.print("Attempting MQTT connection as ");
  Serial.println(clientId);
  
  // Attempt to connect
  if (client.connect(clientId.c_str())) {
    Serial.println("Connected to MQTT broker!");
    
    // Subscribe to command topics
    String controlTopic = "/command/" + String(DEVICE_ID) + "/#";
    client.subscribe(controlTopic.c_str());
    Serial.print("Subscribed to: ");
    Serial.println(controlTopic);
    
    // Publish online status
    String statusTopic = "/solar/" + String(DEVICE_ID) + "/status";
    client.publish(statusTopic.c_str(), "online");
  } else {
    Serial.print("MQTT connection failed, rc=");
    Serial.print(client.state());
    Serial.println(" retrying in 5 seconds");
  }
}

// ===== SENSOR READING =====
void readSensors() {
  // Read Temperature from DHT22
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("ERROR: Failed to read from DHT sensor!");
    return;
  }
  
  // Track temperature extremes
  if (temperature > maxTemperature) maxTemperature = temperature;
  if (temperature < minTemperature) minTemperature = temperature;
  
  // Read Current from ACS712
  int rawCurrent = analogRead(CURRENT_SENSOR_PIN);
  // ACS712 middle point is at ADC_MAX/2 (2048 for 12-bit)
  float voltage = (rawCurrent / ADC_MAX) * VOLTAGE_MULTIPLIER;
  float offsetVoltage = voltage - (BATTERY_VOLTAGE / 2);  // Center at 1.65V
  float current = offsetVoltage / ACS712_SENSITIVITY * 1000;  // Convert to mA
  if (current < 0.1) current = 0;  // Filter noise
  
  // Read Voltage from voltage divider
  // Assuming 1:5 voltage divider (e.g., 300V solar -> 60V -> 3.3V)
  // Adjust multiplier based on your actual divider ratio
  int rawVoltage = analogRead(VOLTAGE_SENSOR_PIN);
  float solarVoltage = (rawVoltage / ADC_MAX) * VOLTAGE_MULTIPLIER * 100;  // Adjust 100 based on divider
  
  // Calculate Power (W) = Voltage (V) × Current (A)
  float power = (solarVoltage / 1000) * (current / 1000);  // Convert to Watts
  if (power < 0) power = 0;
  
  // Accumulate energy
  // Energy = Power × Time, for 5-second interval: 5s / 3600s = 0.00138889 hours
  float energyIncrement = (power / 1000) * (5.0 / 3600.0);  // kWh per 5 seconds
  accumulatedEnergy += energyIncrement;
  dailyEnergy += energyIncrement;
  
  // Log to Serial for debugging
  Serial.println("\n=== SENSOR READINGS ===");
  Serial.printf("Temperature: %.2f°C, Humidity: %.2f%%\n", temperature, humidity);
  Serial.printf("Voltage: %.2fV, Current: %.2fmA\n", solarVoltage, current);
  Serial.printf("Power: %.2fW\n", power);
  Serial.printf("Daily Energy: %.4fkWh\n", dailyEnergy);
}

// ===== PUBLISH TELEMETRY =====
void publishTelemetry() {
  if (!client.connected()) {
    Serial.println("MQTT not connected, skipping publish");
    return;
  }
  
  // Read latest sensor values
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  int rawCurrent = analogRead(CURRENT_SENSOR_PIN);
  int rawVoltage = analogRead(VOLTAGE_SENSOR_PIN);
  
  // Convert raw values
  float voltage = (rawVoltage / ADC_MAX) * VOLTAGE_MULTIPLIER * 100;
  float current = ((rawCurrent / ADC_MAX) * VOLTAGE_MULTIPLIER - (BATTERY_VOLTAGE / 2)) / ACS712_SENSITIVITY * 1000;
  float power = (voltage / 1000) * (current / 1000);
  if (power < 0) power = 0;
  
  // Publish individual metrics
  char topic[80];
  char payload[50];
  
  // Voltage
  sprintf(topic, "/solar/%s/voltage", DEVICE_ID);
  sprintf(payload, "%.2f", voltage);
  client.publish(topic, payload);
  
  // Current
  sprintf(topic, "/solar/%s/current", DEVICE_ID);
  sprintf(payload, "%.2f", current);
  client.publish(topic, payload);
  
  // Power
  sprintf(topic, "/solar/%s/power", DEVICE_ID);
  sprintf(payload, "%.2f", power);
  client.publish(topic, payload);
  
  // Temperature
  sprintf(topic, "/solar/%s/temperature", DEVICE_ID);
  sprintf(payload, "%.2f", temperature);
  client.publish(topic, payload);
  
  // Daily Energy
  sprintf(topic, "/solar/%s/energy_today", DEVICE_ID);
  sprintf(payload, "%.4f", dailyEnergy);
  client.publish(topic, payload);
  
  // Status
  sprintf(topic, "/solar/%s/status", DEVICE_ID);
  client.publish(topic, "online");
  
  // Publish health check as JSON
  StaticJsonDocument<256> doc;
  doc["device_id"] = DEVICE_ID;
  doc["voltage"] = voltage;
  doc["current"] = current;
  doc["power"] = power;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["daily_energy"] = dailyEnergy;
  doc["max_temp"] = maxTemperature;
  doc["min_temp"] = minTemperature;
  doc["uptime_seconds"] = millis() / 1000;
  doc["signal_strength"] = WiFi.RSSI();
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  sprintf(topic, "/solar/%s/health", DEVICE_ID);
  client.publish(topic, jsonString.c_str());
  
  Serial.println("Telemetry published");
}

// ===== HANDLE MQTT MESSAGES =====
void handleMQTTMessage(char* topic, byte* payload, unsigned int length) {
  String topicStr = String(topic);
  String command = "";
  
  // Extract command from topic: /command/{device_id}/{command}
  int lastSlash = topicStr.lastIndexOf('/');
  if (lastSlash != -1) {
    command = topicStr.substring(lastSlash + 1);
  }
  
  Serial.print("Command received: ");
  Serial.println(command);
  
  if (command == "shutdown") {
    Serial.println("Emergency shutdown command received!");
    // Implement emergency shutdown logic
    // For now, just disconnect
    client.publish(("/solar/" + String(DEVICE_ID) + "/status").c_str(), "shutdown");
    delay(1000);
    ESP.restart();
  }
  else if (command == "reset") {
    Serial.println("Reset command received!");
    // Reset daily counters
    dailyEnergy = 0;
    maxTemperature = 0;
    minTemperature = 100;
    accumulatedEnergy = 0;
    client.publish(("/solar/" + String(DEVICE_ID) + "/status").c_str(), "reset_complete");
  }
  else if (command == "config") {
    // Parse JSON configuration
    StaticJsonDocument<256> configDoc;
    deserializeJson(configDoc, payload, length);
    
    Serial.println("Configuration update received");
    // Implement configuration updates here
  }
}

/*
TESTING & VERIFICATION:

1. Upload sketch to ESP32
2. Open Serial Monitor (115200 baud)
3. Verify WiFi connection
4. Verify MQTT connection
5. Check sensor readings in Serial Monitor
6. Test MQTT messages with:
   mosquitto_sub -h broker_ip -t "solar/ESP32_SOL_001/#"

TROUBLESHOOTING:

WiFi Connection Issues:
- Check SSID spelling
- Verify password correct
- Check WiFi signal strength
- Ensure 2.4GHz band (ESP32 doesn't support 5GHz)

MQTT Connection Issues:
- Verify broker IP correct (use hostname if available)
- Check firewall port 1883 open
- Verify mosquitto running: docker logs mqtt-broker
- Check broker logs for connection errors

Sensor Reading Issues:
- For DHT22: Verify data pin secure, try 4.7kΩ pull-up resistor
- For Current sensor: Check offset voltage at center (should be ~1.65V)
- For Voltage sensor: Verify divider ratio matches multiplier in code
- Add debug prints in readSensors() function

Memory Issues:
- Check free heap: Serial.printf("Free heap: %d\n", ESP.getFreeHeap());
- Reduce JSON buffer size if memory critical
- Implement MQTT message size limits

Performance Issues:
- Increase READ_INTERVAL if CPU usage high
- Reduce PUBLISH_INTERVAL if missing data points
- Check WiFi signal strength (should be > -70 dBm)
- Monitor MQTT broker for connection count
*/

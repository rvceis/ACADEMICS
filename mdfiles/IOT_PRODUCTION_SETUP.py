"""
STEP-BY-STEP IoT DEVICE CONNECTION GUIDE
Production Ready Setup with Separate MQTT Microservice

=== ARCHITECTURE ===
IoT Devices (ESP32) -> MQTT Broker (Separate Container:1883) -> Backend Service -> Database

=== STEP 1: MQTT BROKER SETUP (Separate Microservice) ===

Prerequisites:
- Docker installed
- Port 1883 available (MQTT default)
- Port 9001 available (WebSocket optional)

Create docker-compose.yml:

version: '3.8'
services:
  # Main IoT Solar Sharing Backend
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/solar_sharing
      REDIS_URL: redis://redis:6379
      MQTT_BROKER_URL: mqtt://mqtt-broker:1883
      ML_MATCHING_URL: http://ml-service:8002
    depends_on:
      - postgres
      - redis
      - mqtt-broker
    volumes:
      - ./backend:/app

  # ML Matching Service (FastAPI)
  ml-service:
    build: ./ml-services
    ports:
      - "8002:8002"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/solar_sharing
    depends_on:
      - postgres
    volumes:
      - ./ml-services:/app

  # MQTT Broker (Eclipse Mosquitto)
  mqtt-broker:
    image: eclipse-mosquitto:latest
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mqtt/config/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - ./mqtt/data:/mosquitto/data
      - ./mqtt/log:/mosquitto/log
    environment:
      - TZ=UTC
    networks:
      - solar-network
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: solar_sharing
      POSTGRES_USER: solar_user
      POSTGRES_PASSWORD: secure_password_here
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - solar-network
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - solar-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  solar-network:
    driver: bridge

=== STEP 2: MQTT BROKER CONFIGURATION ===

File: mqtt/config/mosquitto.conf

persistence true
persistence_location /mosquitto/data/

listener 1883
protocol mqtt
allow_anonymous true

listener 9001
protocol websockets
allow_anonymous true

log_dest file /mosquitto/log/mosquitto.log
log_dest stdout

=== STEP 3: ESP32 SENSOR CODE ===

Arduino Code for ESP32:
- Reads solar panel voltage, current, temperature
- Connects to WiFi
- Publishes to MQTT broker
- Subscribes to control commands

Install Libraries:
- PubSubClient (MQTT)
- DHT sensor library
- ArduinoJSON

Connection Format:
WiFi SSID: [Your WiFi Name]
WiFi Password: [Your WiFi Password]
MQTT Broker: [BROKER_IP]:1883
Device ID: [Unique device identifier from database]

MQTT Topics:

Publishing (Device -> Broker):
- /solar/{device_id}/voltage       → Voltage reading (V)
- /solar/{device_id}/current       → Current reading (A)
- /solar/{device_id}/power         → Power generation (W)
- /solar/{device_id}/temperature   → Panel temperature (°C)
- /solar/{device_id}/energy_today  → Daily energy (kWh)
- /solar/{device_id}/status        → Device online/offline
- /solar/{device_id}/health        → System health check

Subscribing (Broker -> Device):
- /command/{device_id}/shutdown    → Emergency shutdown
- /command/{device_id}/reset       → System reset
- /command/{device_id}/config      → Configuration update

=== STEP 4: START SERVICES ===

1. Initialize MQTT volumes:
   mkdir -p mqtt/config mqtt/data mqtt/log
   chmod 755 mqtt/config mqtt/data mqtt/log

2. Start all services:
   docker-compose up -d

3. Verify MQTT broker running:
   docker logs [mqtt-broker-container-id]

4. Test MQTT connection:
   # Terminal 1: Subscribe to topics
   mosquitto_sub -h localhost -p 1883 -t "solar/#"
   
   # Terminal 2: Publish test message
   mosquitto_pub -h localhost -p 1883 -t "solar/test/voltage" -m "220.5"

=== STEP 5: DEVICE ONBOARDING PROCESS ===

1. Register Device in Backend:
   POST /api/v1/devices/register
   {
     "device_id": "ESP32_SOL_001",
     "device_name": "Rooftop Solar Panel",
     "location": {"latitude": 28.6139, "longitude": 77.2090},
     "rated_capacity_kw": 5.0,
     "device_type": "solar_panel",
     "firmware_version": "1.2.0"
   }

2. Receive Configuration:
   Response includes:
   - auth_token (for MQTT authentication if needed)
   - publishing_interval (milliseconds between updates)
   - data_format_version
   - timezone

3. Program ESP32 with credentials from response

4. Device connects to MQTT broker and starts publishing

=== STEP 6: MQTT LISTENER IN BACKEND ===

Node.js Backend listens to MQTT:

const mqtt = require('mqtt');
const logger = require('./utils/logger');

const mqttClient = mqtt.connect(process.env.MQTT_BROKER_URL);

mqttClient.on('connect', () => {
  logger.info('Connected to MQTT broker');
  mqttClient.subscribe('solar/#');
});

mqttClient.on('message', async (topic, message) => {
  const [, deviceId, metric] = topic.split('/');
  const value = parseFloat(message.toString());

  try {
    // Store in database
    await db.query(
      `INSERT INTO device_readings 
       (device_id, metric, value, timestamp) 
       VALUES ($1, $2, $3, NOW())`,
      [deviceId, metric, value]
    );

    // Check for anomalies
    if (metric === 'temperature' && value > 80) {
      logger.warn(`High temperature detected on ${deviceId}: ${value}°C`);
      // Trigger alert
    }

    // Update device status
    if (metric === 'status') {
      await db.query(
        `UPDATE devices SET last_heartbeat = NOW(), status = $1 
         WHERE device_id = $2`,
        [value, deviceId]
      );
    }
  } catch (err) {
    logger.error(`Error processing MQTT message: ${err.message}`);
  }
});

=== STEP 7: PRODUCTION DEPLOYMENT ===

AWS EC2 / Docker Swarm / Kubernetes:

1. Create environment file (.env.production):
   DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/solar
   MQTT_BROKER_URL=mqtt://mqtt.solar-sharing.com:1883
   ML_MATCHING_URL=http://ml-service:8002
   REDIS_URL=redis://elasticache-endpoint:6379
   NODE_ENV=production

2. Deploy MQTT broker separately:
   - AWS ECS task for Mosquitto
   - Elastic IP for static address
   - Security group: Allow 1883/tcp from VPC
   - CloudWatch logs integration

3. SSL/TLS for MQTT (Production):
   mqtt/config/mosquitto.conf:
   
   listener 8883
   protocol mqtt
   cafile /mosquitto/config/ca.crt
   certfile /mosquitto/config/server.crt
   keyfile /mosquitto/config/server.key
   require_certificate true

4. Health checks:
   - MQTT broker: Connect test every 30s
   - Device heartbeat: Expected every 5 minutes
   - Alert if no data for 30 minutes

=== STEP 8: MONITORING & TROUBLESHOOTING ===

Monitor MQTT Connections:
mosquitto_sub -v -t '$SYS/broker/clients/#'

Check Device Logs:
docker logs [container-id] --follow

Common Issues:

1. Device Can't Connect:
   - Check firewall port 1883 open
   - Verify MQTT_BROKER_URL environment variable
   - Ensure WiFi credentials correct on ESP32
   - Check device IP with: telnet broker_ip 1883

2. Messages Not Being Stored:
   - Verify topic format: /solar/{device_id}/{metric}
   - Check database connection
   - Review backend logs for parsing errors
   - Ensure device_id exists in devices table

3. High Memory Usage:
   - Check mosquitto.log for connection floods
   - Verify clients disconnecting properly
   - Monitor Redis memory
   - Check for duplicate device IDs

4. Latency Issues:
   - Check network bandwidth
   - Monitor CPU on MQTT broker: docker stats
   - Increase publishing interval if > 100ms
   - Consider MQTT 5.0 queueing features

=== STEP 9: DATA FLOW EXAMPLE ===

Timeline of message from device to matching:

1. 10:00:00 - ESP32 reads voltage=230V, current=15A, power=3450W
2. 10:00:01 - ESP32 publishes: /solar/ESP32_001/power → 3450
3. 10:00:01 - MQTT broker receives and stores
4. 10:00:02 - Backend listener receives message
5. 10:00:02 - Backend stores in device_readings table
6. 10:00:02 - Update device.available_kwh = total_today + (3450W/1000/2600s)
7. 10:00:05 - Buyer searches for energy
8. 10:00:06 - ML Matching Service queries recent device_readings
9. 10:00:07 - ML calculates match scores with current availability
10. 10:00:08 - Frontend shows matches with latest availability data

=== STEP 10: SCALING FOR 1000+ DEVICES ===

1. MQTT Broker:
   - Use AWS IoT Core (managed MQTT)
   - Or self-host with clustering (HiveMQ Enterprise)
   - Implement QoS 1 for message reliability
   - Set max_connections to device count + 20%

2. Data Storage:
   - Use time-series database: InfluxDB or TimescaleDB
   - Partition device_readings by device_id
   - Archive old readings (>30 days) to S3

3. Backend Processing:
   - Horizontally scale backend instances
   - Use message queue (RabbitMQ) for MQTT listeners
   - Batch database inserts for performance

4. Matching Service:
   - Cache availability data (5 min TTL)
   - Pre-compute distances between popular locations
   - Use vector search for nearest neighbor queries

=== ENVIRONMENT VARIABLES FOR PRODUCTION ===

Backend:
DATABASE_URL=postgresql://[user]:[pass]@[host]:[port]/[database]
REDIS_URL=redis://[host]:[port]
MQTT_BROKER_URL=mqtt://[broker-host]:1883
ML_MATCHING_URL=http://ml-service:8002
JWT_SECRET=[strong-random-string-32-chars]
NODE_ENV=production
PORT=3000
LOG_LEVEL=info

MQTT Broker:
persistence=true
max_connections=5000
autosave_interval=1800

ML Service:
DATABASE_URL=postgresql://[user]:[pass]@[host]:[port]/[database]
LOG_LEVEL=info

=== VERIFICATION CHECKLIST ===

Before going live:
☐ MQTT broker accepting 100+ simultaneous connections
☐ All environment variables configured
☐ Database backups automated
☐ SSL/TLS certificates valid for 12+ months
☐ Device data arriving in real-time (<2s latency)
☐ Matching algorithm returning in <500ms
☐ No data loss during broker restarts
☐ Alert system working for high temperature/low voltage
☐ Device disconnection detected within 30 seconds
☐ Admin dashboard showing live device status
"""

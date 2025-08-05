#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// Wi-Fi credentials
const char* ssid = "NVISADMIN";
const char* password = "Nv2024#@!";

// Pin Definitions
#define LM35_PIN        34
#define SOIL_AO_PIN     32
#define SOIL_DO_PIN     33

#define WATER_PUMP_PIN  18
#define FAN_PIN         19
#define HEATER_PIN      22

WebServer server(80);

// Sensor variables
float temperature = 0.0;
int soilMoisture = 0;
int soilDry = 0;

// Target temperature
float targetTemperature = NAN;

// Tolerance in °C
const float TEMP_TOLERANCE = 1.0;

// Utility: activate a relay pin LOW for duration
void activateDevice(int pin, unsigned long duration_ms) {
  digitalWrite(pin, LOW);
  delay(duration_ms);
  digitalWrite(pin, HIGH);
}

// Timing variables
unsigned long controlPauseStart = 0;
unsigned long heaterFanStartTime = 0;
bool heaterFanActive = false;
bool inPausePeriod = false;

void readSensorsAndControl() {
  unsigned long now = millis();

  // === Temperature Reading (always real-time) ===
  analogRead(LM35_PIN);  // Dummy read
  delay(10);
  int raw = analogRead(LM35_PIN);
  float voltage = raw * (3.3 / 4095.0);
  temperature = voltage * 100.0;

  // === Soil Sensor Reading ===
  int soilRaw = analogRead(SOIL_AO_PIN);
  soilMoisture = map(soilRaw, 4095, 1500, 0, 100);
  soilMoisture = constrain(soilMoisture, 0, 100);
  soilDry = digitalRead(SOIL_DO_PIN);

  // === Debug Output ===
  Serial.println("----- SENSOR READINGS -----");
  Serial.print("Temperature: "); Serial.print(temperature); Serial.println(" °C");
  Serial.print("Soil Moisture: "); Serial.print(soilMoisture); Serial.println(" %");
  Serial.print("Soil is: "); Serial.println(soilDry == LOW ? "WET" : "DRY");
  Serial.print("Target Temperature: "); Serial.println(isnan(targetTemperature) ? "Not set" : String(targetTemperature));

  // === Handle heater/fan timing ===
  if (heaterFanActive && now - heaterFanStartTime >= 45000) {
    Serial.println("45s passed. Turning OFF Heater & Fan.");
    digitalWrite(FAN_PIN, HIGH);
    digitalWrite(HEATER_PIN, HIGH);
    heaterFanActive = false;
    inPausePeriod = true;
    controlPauseStart = now;
  }

  if (inPausePeriod && now - controlPauseStart < 15000) {
    Serial.println("Waiting 15s before re-evaluating control logic...");
    Serial.println("----------------------------");
    return; // Don't make control decisions during pause
  } else if (inPausePeriod && now - controlPauseStart >= 15000) {
    inPausePeriod = false; // End pause
    Serial.println("Pause ended. Resuming control logic.");
  }

  // === Temperature Control (only if not in pause) ===
  if (!isnan(targetTemperature) && !heaterFanActive && !inPausePeriod) {
    if (temperature > targetTemperature + TEMP_TOLERANCE) {
      Serial.println("Temperature too high. Turning ON Fan for 45s.");
      digitalWrite(FAN_PIN, LOW);
      digitalWrite(HEATER_PIN, HIGH);
      heaterFanActive = true;
      heaterFanStartTime = now;
    }
    else if (temperature < targetTemperature - TEMP_TOLERANCE) {
      Serial.println("Temperature too low. Turning ON Heater & Fan for 45s.");
      digitalWrite(FAN_PIN, LOW);
      digitalWrite(HEATER_PIN, LOW);
      heaterFanActive = true;
      heaterFanStartTime = now;
    }
    else {
      Serial.println("Temperature within range. Heater & Fan OFF.");
      digitalWrite(FAN_PIN, HIGH);
      digitalWrite(HEATER_PIN, HIGH);
    }
  }

  // === Soil Moisture Control ===
  if (soilDry == HIGH) {
    Serial.println("Soil is dry. Activating water pump.");
    activateDevice(WATER_PUMP_PIN, 3000);
  }

  Serial.println("----------------------------");
}

// ========== HTTP HANDLERS ==========

void handleRoot() {
  String data = "Temperature: " + String(temperature) + " °C\n";
  data += "Soil Moisture: " + String(soilMoisture) + " %\n";
  data += "Soil is: " + String(soilDry == LOW ? "WET" : "DRY") + "\n";
  data += "Target Temp: " + (isnan(targetTemperature) ? "Not set" : String(targetTemperature)) + " °C";
  server.send(200, "text/plain", data);
}

void handleAssign() {
  if (server.hasArg("plain")) {
    String body = server.arg("plain");
    Serial.println("Received POST body:");
    Serial.println(body);

    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, body);

    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      server.send(400, "text/plain", "Invalid JSON.");
      return;
    }

    if (doc.containsKey("temperature")) {
      targetTemperature = doc["temperature"];
      Serial.print("Target temperature set to: ");
      Serial.println(targetTemperature);
    }

    server.send(200, "text/plain", "Temperature received.");
  } else {
    server.send(400, "text/plain", "Missing POST body.");
  }
}

// ========== SETUP ==========

void setup() {
  Serial.begin(115200);

  pinMode(SOIL_DO_PIN, INPUT);
  pinMode(WATER_PUMP_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(HEATER_PIN, OUTPUT);

  digitalWrite(WATER_PUMP_PIN, HIGH);
  digitalWrite(FAN_PIN, HIGH);
  digitalWrite(HEATER_PIN, HIGH);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
  Serial.print("IP Address: "); Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/assign", HTTP_POST, handleAssign);
  server.begin();
  Serial.println("HTTP server started.");
}

// ========== LOOP ==========

unsigned long lastRead = 0;
void loop() {
  server.handleClient();

  if (millis() - lastRead > 5000) {
    lastRead = millis();
    readSensorsAndControl();
  }
}
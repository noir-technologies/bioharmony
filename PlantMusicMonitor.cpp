/*
 * ESP32 Plant Music Monitor
 * Reads soil moisture and light sensors, plays musical patterns based on plant conditions
 * Designed for easy integration with LLM-based pattern selection via WiFi
 * 
 * Hardware Connections:
 * - Soil Moisture Sensor: Analog pin A0 (GPIO36)
 * - Light Sensor (LDR): Analog pin A3 (GPIO39)
 * - Piezo Buzzer: Digital PWM pin D5 (GPIO5)
 * 
 * Author: ESP32 Plant Monitor System
 * Date: 2025
 * 
 * Compatible with: Arduino IDE, PlatformIO, ESP-IDF, and any Ideaboard
 */

// ==================== INCLUDES ====================
#include <Arduino.h>

// ==================== FUNCTION PROTOTYPES ====================
void readSensors();
void interpretSensorData();
void selectMusicalPattern();
void playSelectedMelody();
void playMelody(const Note melody[], int length);
void playStartupSequence();
void printConfiguration();
void printStatus();
void printHealthIndicator();

// ==================== PIN DEFINITIONS ====================
// Define analog pins for cross-platform compatibility
#ifndef A0
#define A0 36  // ESP32 analog pin mapping
#endif
#ifndef A3
#define A3 39  // ESP32 analog pin mapping
#endif

#define SOIL_MOISTURE_PIN A0    // GPIO36 - Analog input for soil moisture sensor
#define LIGHT_SENSOR_PIN A3     // GPIO39 - Analog input for light sensor (LDR)
#define BUZZER_PIN 5            // GPIO5 - PWM output for piezo buzzer

// ==================== ESP32 COMPATIBILITY LAYER ====================
// Ensure tone() function is available
#ifndef TONE_CHANNEL
#define TONE_CHANNEL 0
#endif

// Tone function wrapper for ESP32 compatibility
void tone(uint8_t pin, unsigned int frequency, unsigned long duration = 0) {
  ledcSetup(TONE_CHANNEL, frequency, 8);
  ledcAttachPin(pin, TONE_CHANNEL);
  ledcWriteTone(TONE_CHANNEL, frequency);
  
  if (duration > 0) {
    delay(duration);
    ledcWriteTone(TONE_CHANNEL, 0);
  }
}

void noTone(uint8_t pin) {
  ledcWriteTone(TONE_CHANNEL, 0);
  ledcDetachPin(pin);
}

// ==================== TIMING FUNCTIONS ====================
// Cross-platform millis() and delay() - Arduino.h should provide these
// but included here for explicit compatibility
#ifndef millis
unsigned long millis() {
  return esp_timer_get_time() / 1000ULL;
}
#endif
// ==================== SENSOR THRESHOLDS ====================
// Configurable thresholds for sensor interpretation
const int MOISTURE_DRY_THRESHOLD = 1500;      // Below this = dry soil
const int MOISTURE_WET_THRESHOLD = 3000;      // Above this = wet soil
const int LIGHT_DARK_THRESHOLD = 1000;        // Below this = dark conditions
const int LIGHT_BRIGHT_THRESHOLD = 3000;      // Above this = bright conditions

// ==================== MUSICAL NOTES DEFINITIONS ====================
// Note frequencies in Hz
#define NOTE_C4  262
#define NOTE_D4  294
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_G4  392
#define NOTE_A4  440
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_D5  587
#define NOTE_E5  659
#define NOTE_F5  698
#define NOTE_G5  784
#define NOTE_A5  880
#define NOTE_REST 0

// ==================== MUSICAL PATTERNS ====================
// Structure for musical notes
struct Note {
  int frequency;
  int duration;
};

// Happy/Active Pattern - Upbeat melody for healthy, well-lit plants
const Note HAPPY_MELODY[] = {
  {NOTE_C5, 200}, {NOTE_E5, 200}, {NOTE_G5, 200}, {NOTE_C5, 200},
  {NOTE_F5, 300}, {NOTE_E5, 200}, {NOTE_D5, 200}, {NOTE_C5, 400},
  {NOTE_G5, 200}, {NOTE_F5, 200}, {NOTE_E5, 200}, {NOTE_G5, 400},
  {NOTE_REST, 100}
};
const int HAPPY_MELODY_LENGTH = sizeof(HAPPY_MELODY) / sizeof(HAPPY_MELODY[0]);

// Relaxed/Soft Pattern - Gentle melody for content plants
const Note RELAXED_MELODY[] = {
  {NOTE_C4, 400}, {NOTE_E4, 400}, {NOTE_G4, 600}, {NOTE_REST, 200},
  {NOTE_F4, 400}, {NOTE_A4, 400}, {NOTE_C5, 600}, {NOTE_REST, 200},
  {NOTE_G4, 400}, {NOTE_C5, 400}, {NOTE_E5, 800}, {NOTE_REST, 200}
};
const int RELAXED_MELODY_LENGTH = sizeof(RELAXED_MELODY) / sizeof(RELAXED_MELODY[0]);

// Neutral Pattern - Simple melody for stable conditions
const Note NEUTRAL_MELODY[] = {
  {NOTE_A4, 300}, {NOTE_REST, 100}, {NOTE_A4, 300}, {NOTE_REST, 100},
  {NOTE_C5, 400}, {NOTE_B4, 400}, {NOTE_A4, 600}, {NOTE_REST, 200},
  {NOTE_G4, 400}, {NOTE_A4, 400}, {NOTE_C5, 600}, {NOTE_REST, 200}
};
const int NEUTRAL_MELODY_LENGTH = sizeof(NEUTRAL_MELODY) / sizeof(NEUTRAL_MELODY[0]);

// Alert Pattern - Warning melody for problematic conditions
const Note ALERT_MELODY[] = {
  {NOTE_C5, 150}, {NOTE_REST, 50}, {NOTE_C5, 150}, {NOTE_REST, 50},
  {NOTE_C5, 150}, {NOTE_REST, 100}, {NOTE_G4, 200}, {NOTE_REST, 100},
  {NOTE_C5, 150}, {NOTE_REST, 50}, {NOTE_C5, 150}, {NOTE_REST, 200}
};
const int ALERT_MELODY_LENGTH = sizeof(ALERT_MELODY) / sizeof(ALERT_MELODY[0]);

// ==================== CROSS-PLATFORM SERIAL WRAPPER ====================
// Ensure Serial communication works across platforms
class SerialWrapper {
public:
  void begin(unsigned long baud) {
    Serial.begin(baud);
    // Wait for serial to initialize on some platforms
    #if defined(ESP32) || defined(ESP8266)
    delay(100);
    #endif
  }
  
  void println(const String& message) {
    Serial.println(message);
  }
  
  void println(const char* message) {
    Serial.println(message);
  }
  
  void println() {
    Serial.println();
  }
  
  void print(const String& message) {
    Serial.print(message);
  }
  
  void print(const char* message) {
    Serial.print(message);
  }
};

SerialWrapper DebugSerial;
// ==================== GLOBAL VARIABLES ====================
struct SensorData {
  int moistureRaw;
  int lightRaw;
  String moistureState;
  String lightState;
  String overallState;
  String selectedPattern;
};

SensorData currentReading;
unsigned long lastMelodyTime = 0;
const unsigned long MELODY_INTERVAL = 10000; // Play melody every 10 seconds

// ==================== MAIN ENTRY POINT ====================
// For platforms that don't use setup()/loop() pattern
#ifdef CUSTOM_MAIN
int main() {
  setup();
  while(1) {
    loop();
  }
  return 0;
}
#endif

// ==================== SETUP FUNCTION ====================
void setup() {
  // Initialize serial communication with cross-platform compatibility
  DebugSerial.begin(115200);
  delay(1000);
  
  // Initialize pins
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initialize ADC for ESP32 compatibility
  #ifdef ESP32
  analogReadResolution(12);  // Set 12-bit resolution for ESP32
  analogSetAttenuation(ADC_11db);  // Set input voltage range
  #endif
  
  // Print startup message
  DebugSerial.println("=================================");
  DebugSerial.println("ESP32 Plant Music Monitor Started");
  DebugSerial.println("=================================");
  DebugSerial.println("Monitoring soil moisture and light conditions...");
  DebugSerial.println();
  
  // Print threshold configuration
  printConfiguration();
  
  // Play startup melody
  playStartupSequence();
}

// ==================== MAIN LOOP ====================
void loop() {
  // Read sensors
  readSensors();
  
  // Interpret sensor data and determine plant state
  interpretSensorData();
  
  // Select musical pattern based on current state
  selectMusicalPattern();
  
  // Print status to Serial Monitor
  printStatus();
  
  // Play melody at regular intervals
  if (millis() - lastMelodyTime >= MELODY_INTERVAL) {
    playSelectedMelody();
    lastMelodyTime = millis();
  }
  
  // Wait before next reading
  delay(2000);
}

// ==================== SENSOR FUNCTIONS ====================
void readSensors() {
  // Read analog values from sensors
  currentReading.moistureRaw = analogRead(SOIL_MOISTURE_PIN);
  currentReading.lightRaw = analogRead(LIGHT_SENSOR_PIN);
  
  // Add some filtering to reduce noise
  static int moistureBuffer[5] = {0};
  static int lightBuffer[5] = {0};
  static int bufferIndex = 0;
  
  moistureBuffer[bufferIndex] = currentReading.moistureRaw;
  lightBuffer[bufferIndex] = currentReading.lightRaw;
  bufferIndex = (bufferIndex + 1) % 5;
  
  // Calculate average of last 5 readings
  int moistureSum = 0, lightSum = 0;
  for (int i = 0; i < 5; i++) {
    moistureSum += moistureBuffer[i];
    lightSum += lightBuffer[i];
  }
  
  currentReading.moistureRaw = moistureSum / 5;
  currentReading.lightRaw = lightSum / 5;
}

void interpretSensorData() {
  // Interpret moisture levels
  if (currentReading.moistureRaw < MOISTURE_DRY_THRESHOLD) {
    currentReading.moistureState = "DRY";
  } else if (currentReading.moistureRaw > MOISTURE_WET_THRESHOLD) {
    currentReading.moistureState = "WET";
  } else {
    currentReading.moistureState = "OPTIMAL";
  }
  
  // Interpret light levels
  if (currentReading.lightRaw < LIGHT_DARK_THRESHOLD) {
    currentReading.lightState = "DARK";
  } else if (currentReading.lightRaw > LIGHT_BRIGHT_THRESHOLD) {
    currentReading.lightState = "BRIGHT";
  } else {
    currentReading.lightState = "MODERATE";
  }
  
  // Determine overall plant state
  if (currentReading.moistureState == "OPTIMAL" && 
      (currentReading.lightState == "MODERATE" || currentReading.lightState == "BRIGHT")) {
    currentReading.overallState = "HAPPY";
  } else if (currentReading.moistureState == "DRY" || currentReading.lightState == "DARK") {
    currentReading.overallState = "STRESSED";
  } else if (currentReading.moistureState == "WET") {
    currentReading.overallState = "ALERT";
  } else {
    currentReading.overallState = "NEUTRAL";
  }
}

// ==================== PATTERN SELECTION ====================
void selectMusicalPattern() {
  // This function determines which musical pattern to play
  // based on the current sensor readings and plant state
  // NOTE: This logic can be replaced with LLM-based selection
  
  if (currentReading.overallState == "HAPPY") {
    currentReading.selectedPattern = "HAPPY";
  } else if (currentReading.overallState == "STRESSED") {
    currentReading.selectedPattern = "ALERT";
  } else if (currentReading.overallState == "ALERT") {
    currentReading.selectedPattern = "ALERT";
  } else {
    // Default cases
    if (currentReading.moistureState == "OPTIMAL") {
      currentReading.selectedPattern = "RELAXED";
    } else {
      currentReading.selectedPattern = "NEUTRAL";
    }
  }
}

// ==================== MUSIC PLAYBACK FUNCTIONS ====================
void playSelectedMelody() {
  Serial.println("♪ Playing melody: " + currentReading.selectedPattern);
  
  if (currentReading.selectedPattern == "HAPPY") {
    playMelody(HAPPY_MELODY, HAPPY_MELODY_LENGTH);
  } else if (currentReading.selectedPattern == "RELAXED") {
    playMelody(RELAXED_MELODY, RELAXED_MELODY_LENGTH);
  } else if (currentReading.selectedPattern == "ALERT") {
    playMelody(ALERT_MELODY, ALERT_MELODY_LENGTH);
  } else {
    playMelody(NEUTRAL_MELODY, NEUTRAL_MELODY_LENGTH);
  }
}

void playMelody(const Note melody[], int length) {
  for (int i = 0; i < length; i++) {
    if (melody[i].frequency == NOTE_REST) {
      // Rest - no sound
      noTone(BUZZER_PIN);
    } else {
      // Play note
      tone(BUZZER_PIN, melody[i].frequency);
    }
    
    delay(melody[i].duration);
    
    // Small pause between notes for clarity
    noTone(BUZZER_PIN);
    delay(20);
  }
  
  // Ensure buzzer is off after melody
  noTone(BUZZER_PIN);
}

void playStartupSequence() {
  Serial.println("♪ Playing startup sequence...");
  
  // Simple ascending scale
  int startupNotes[] = {NOTE_C4, NOTE_D4, NOTE_E4, NOTE_F4, NOTE_G4, NOTE_A4, NOTE_B4, NOTE_C5};
  
  for (int i = 0; i < 8; i++) {
    tone(BUZZER_PIN, startupNotes[i]);
    delay(150);
    noTone(BUZZER_PIN);
    delay(50);
  }
  
  delay(500);
  Serial.println("♪ Startup sequence complete!");
  Serial.println();
}

// ==================== DISPLAY FUNCTIONS ====================
void printConfiguration() {
  Serial.println("Configuration:");
  Serial.println("- Moisture Dry Threshold: " + String(MOISTURE_DRY_THRESHOLD));
  Serial.println("- Moisture Wet Threshold: " + String(MOISTURE_WET_THRESHOLD));
  Serial.println("- Light Dark Threshold: " + String(LIGHT_DARK_THRESHOLD));
  Serial.println("- Light Bright Threshold: " + String(LIGHT_BRIGHT_THRESHOLD));
  Serial.println("- Melody Interval: " + String(MELODY_INTERVAL / 1000) + " seconds");
  Serial.println();
}

void printStatus() {
  Serial.println("=== Plant Status Report ===");
  Serial.println("Timestamp: " + String(millis() / 1000) + "s");
  Serial.println();
  
  // Sensor raw values
  Serial.println("Raw Sensor Readings:");
  Serial.println("  Soil Moisture: " + String(currentReading.moistureRaw) + " (0-4095)");
  Serial.println("  Light Level:   " + String(currentReading.lightRaw) + " (0-4095)");
  Serial.println();
  
  // Interpreted states
  Serial.println("Interpreted States:");
  Serial.println("  Moisture: " + currentReading.moistureState);
  Serial.println("  Light:    " + currentReading.lightState);
  Serial.println("  Overall:  " + currentReading.overallState);
  Serial.println();
  
  // Selected pattern
  Serial.println("Selected Musical Pattern: " + currentReading.selectedPattern);
  
  // Visual plant health indicator
  printHealthIndicator();
  
  Serial.println("========================");
  Serial.println();
}

void printHealthIndicator() {
  Serial.print("Plant Health: ");
  
  if (currentReading.overallState == "HAPPY") {
    Serial.println("😊 THRIVING");
  } else if (currentReading.overallState == "STRESSED") {
    Serial.println("😟 NEEDS ATTENTION");
  } else if (currentReading.overallState == "ALERT") {
    Serial.println("⚠️  REQUIRES IMMEDIATE CARE");
  } else {
    Serial.println("😐 STABLE");
  }
}

// ==================== FUTURE LLM INTEGRATION PLACEHOLDER ====================
/*
 * PLACEHOLDER FOR LLM INTEGRATION
 * 
 * Replace the selectMusicalPattern() function with this structure
 * when integrating with an LLM over WiFi:
 * 
 * String getLLMPatternSelection(SensorData data) {
 *   // 1. Connect to WiFi if not connected
 *   // 2. Prepare JSON payload with sensor data
 *   // 3. Send HTTP request to LLM API endpoint
 *   // 4. Parse response and extract pattern selection
 *   // 5. Return pattern name (HAPPY, RELAXED, NEUTRAL, ALERT)
 *   
 *   // Example payload structure:
 *   // {
 *   //   "moistureRaw": data.moistureRaw,
 *   //   "lightRaw": data.lightRaw,
 *   //   "moistureState": data.moistureState,
 *   //   "lightState": data.lightState,
 *   //   "overallState": data.overallState,
 *   //   "timestamp": millis()
 *   // }
 *   
 *   return "NEUTRAL"; // Fallback pattern
 * }
 * 
 * Then modify selectMusicalPattern() to:
 * void selectMusicalPattern() {
 *   currentReading.selectedPattern = getLLMPatternSelection(currentReading);
 * }
 */

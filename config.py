# Hardware pin assignments
SOIL_HUMIDITY_SENSOR_PIN = "IO4"
AMBIENT_SENSOR_PIN = "IO18"  # DHT11 data pin (digital)
BUZZER_PIN = "IO26"
LCD_I2C_ADDRESS = 0x27

# LCD settings
LCD_ROWS = 2
LCD_COLS = 16

# Humidity thresholds (adjust based on your sensor calibration)
SOIL_HUMIDITY_THRESHOLDS = {
    'dry': 26000,      # Values above this are considered dry
    'normal': 20000    # Values between normal and dry are normal, below is humid
}

# For backward compatibility
HUMIDITY_THRESHOLDS = SOIL_HUMIDITY_THRESHOLDS

# Ambient environment thresholds (adjusted for DHT11 range)
AMBIENT_THRESHOLDS = {
    'humidity': {
        'low': 40,      # Below 40% is too dry for most plants (DHT11 range: 20-90%)
        'high': 75      # Above 75% might indicate poor ventilation
    },
    'temperature': {
        'low': 18,      # Below 18°C might be too cold  
        'high': 30      # Above 30°C might be too hot (DHT11 range: 0-50°C)
    }
}

# Alert frequencies (Hz)
ALERT_FREQUENCIES = {
    'dry': [262, 220, 196],      # C4, A3, G3 - Descending (warning)
    'normal': [330, 392, 523],   # E4, G4, C5 - Ascending (good)
    'humid': [659, 784, 880]     # E5, G5, A5 - High (alert)
}

# Timing settings
MAIN_LOOP_DELAY = 6.0  # seconds between readings
BUZZER_NOTE_DURATION = 0.2  # seconds
BUZZER_NOTE_PAUSE = 0.05    # seconds between notes
BUZZER_DUTY_CYCLE = 32768   # 50% duty cycle

# Display messages
DISPLAY_MESSAGES = {
    'humidity_label': 'Humidity:',
    'dry': 'Dry',
    'normal': 'Normal', 
    'humid': 'Humid'
}

# AI and WiFi settings
ENABLE_AI_MELODIES = True  # Set to False to disable AI features
AI_REQUEST_INTERVAL = 30   # Seconds between AI melody requests (don't spam the API)
WIFI_TIMEOUT = 10         # Seconds to wait for WiFi connection
MAX_WIFI_RETRIES = 3      # Number of WiFi connection attempts

# Plant information for AI context
PLANT_INFO = {
    'type': 'houseplant',      # Adjust based on your plant type
    'location': 'indoor',      # indoor/outdoor/greenhouse
    'name': 'My Plant'         # Name for the AI to reference
}

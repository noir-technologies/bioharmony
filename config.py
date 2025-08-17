# Hardware pin assignments
HUMIDITY_SENSOR_PIN = "IO4"
BUZZER_PIN = "IO13"
LCD_I2C_ADDRESS = 0x27

# LCD settings
LCD_ROWS = 2
LCD_COLS = 16

# Humidity thresholds (adjust based on your sensor calibration)
HUMIDITY_THRESHOLDS = {
    'dry': 26000,      # Values above this are considered dry
    'normal': 20000    # Values between normal and dry are normal, below is humid
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

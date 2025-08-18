import board
import adafruit_dht
import time
from config import AMBIENT_SENSOR_PIN

class DHT11AmbientSensor:
    """Manages DHT11 digital humidity and temperature sensor"""
    
    def __init__(self, pin_name=AMBIENT_SENSOR_PIN):
        """Initialize the DHT11 sensor
        
        Args:
            pin_name (str): Board pin name for the sensor data line
        """
        self.pin_name = pin_name
        
        # Initialize the DHT11 sensor
        pin = getattr(board, pin_name)
        self.dht = adafruit_dht.DHT11(pin)
        
        # Cache for last readings
        self._last_humidity = None
        self._last_temperature = None
        self._last_read_time = 0
        self._min_read_interval = 2.0  # DHT11 needs 2+ seconds between reads
        self._consecutive_errors = 0
        self._max_consecutive_errors = 3
        
        print(f"Initialized DHT11 sensor on pin {pin_name}")
    
    def read_humidity_and_temperature(self):
        """Read humidity and temperature from DHT11 sensor
        
        Returns:
            tuple: (humidity_percent, temperature_celsius) or (None, None) if error
        """
        current_time = time.monotonic()
        
        # Respect minimum read interval for DHT11
        if current_time - self._last_read_time < self._min_read_interval:
            # Return cached values if too soon
            return self._last_humidity, self._last_temperature
        
        try:
            # Read from sensor
            humidity = self.dht.humidity
            temperature = self.dht.temperature
            
            # DHT11 sometimes returns None on first read or if too frequent
            if humidity is not None and temperature is not None:
                self._last_humidity = humidity
                self._last_temperature = temperature
                self._last_read_time = current_time
                self._consecutive_errors = 0
                return humidity, temperature
            else:
                # Return cached values if current read failed but we have previous data
                if self._last_humidity is not None and self._last_temperature is not None:
                    return self._last_humidity, self._last_temperature
                else:
                    return None, None
                    
        except RuntimeError as e:
            # DHT sensors commonly throw RuntimeError for timing issues
            self._consecutive_errors += 1
            print(f"DHT11 read error: {e}")
            
            # Return cached values if available
            if self._last_humidity is not None and self._last_temperature is not None:
                return self._last_humidity, self._last_temperature
            else:
                return None, None
        
        except Exception as e:
            self._consecutive_errors += 1
            print(f"DHT11 unexpected error: {e}")
            return None, None
    
    def get_last_readings(self):
        """Get the last sensor readings without taking new measurements
        
        Returns:
            tuple: (humidity, temperature) or (None, None) if no reading taken
        """
        return self._last_humidity, self._last_temperature
    
    def is_sensor_connected(self):
        """Check if sensor appears to be connected and working
        
        Returns:
            bool: True if sensor seems connected and responsive
        """
        try:
            humidity, temperature = self.read_humidity_and_temperature()
            return humidity is not None and temperature is not None
        except:
            return False
    
    def has_consecutive_errors(self):
        """Check if sensor has too many consecutive errors
        
        Returns:
            bool: True if sensor might be disconnected or faulty
        """
        return self._consecutive_errors >= self._max_consecutive_errors
    
    def reset_error_count(self):
        """Reset the consecutive error counter"""
        self._consecutive_errors = 0
    
    def get_sensor_info(self):
        """Get sensor information
        
        Returns:
            dict: Sensor specifications and status
        """
        return {
            'model': 'DHT11',
            'pin': self.pin_name,
            'accuracy_temp': '±2°C',
            'accuracy_humidity': '±5%RH',
            'range_temp': '0-50°C',
            'range_humidity': '20-90%RH',
            'last_humidity': self._last_humidity,
            'last_temperature': self._last_temperature,
            'consecutive_errors': self._consecutive_errors
        }

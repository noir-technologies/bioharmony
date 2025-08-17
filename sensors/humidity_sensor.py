import board
import analogio
from config import HUMIDITY_SENSOR_PIN

class HumiditySensor:
    """Manages soil humidity sensor readings"""
    
    def __init__(self, pin_name=HUMIDITY_SENSOR_PIN):
        """Initialize the humidity sensor
        
        Args:
            pin_name (str): Board pin name for the sensor
        """
        self.sensor = analogio.AnalogIn(getattr(board, pin_name))
        self._last_reading = None
    
    def read_raw_value(self):
        """Read raw analog value from sensor
        
        Returns:
            int: Raw sensor reading (0-65535)
        """
        self._last_reading = self.sensor.value
        return self._last_reading
    
    def get_last_reading(self):
        """Get the last sensor reading without taking a new measurement
        
        Returns:
            int: Last sensor reading, or None if no reading taken yet
        """
        return self._last_reading
    
    def is_sensor_connected(self):
        """Check if sensor appears to be connected
        
        Returns:
            bool: True if sensor seems connected (reading is reasonable)
        """
        reading = self.read_raw_value()
        # If reading is 0 or max value, sensor might be disconnected
        return 0 < reading < 65535
    
    def calibrate_dry(self):
        """Helper method to get reading for dry soil calibration
        
        Returns:
            int: Current sensor reading for dry soil
        """
        return self.read_raw_value()
    
    def calibrate_wet(self):
        """Helper method to get reading for wet soil calibration
        
        Returns:
            int: Current sensor reading for wet soil  
        """
        return self.read_raw_value()

from config import SOIL_HUMIDITY_THRESHOLDS, AMBIENT_THRESHOLDS, DISPLAY_MESSAGES

class PlantAnalyzer:
    """Analyzes both soil moisture and ambient conditions for comprehensive plant health assessment"""
    
    def __init__(self, soil_thresholds=None, ambient_thresholds=None):
        """Initialize the plant analyzer
        
        Args:
            soil_thresholds (dict): Custom soil threshold values
            ambient_thresholds (dict): Custom ambient threshold values
        """
        self.soil_thresholds = soil_thresholds or SOIL_HUMIDITY_THRESHOLDS.copy()
        self.ambient_thresholds = ambient_thresholds or AMBIENT_THRESHOLDS.copy()
    
    def interpret_soil_moisture(self, sensor_value):
        """Interpret raw soil sensor value into moisture status
        
        Args:
            sensor_value (int): Raw soil sensor reading
            
        Returns:
            str: Status string ('dry', 'normal', or 'humid')
        """
        if sensor_value > self.soil_thresholds['dry']:
            return 'dry'
        elif sensor_value >= self.soil_thresholds['normal']:
            return 'normal'
        else:
            return 'humid'
    
    def interpret_moisture_level(self, sensor_value):
        """Interpret raw sensor value into moisture status (legacy method name)
        
        Args:
            sensor_value (int): Raw sensor reading
            
        Returns:
            str: Status string ('dry', 'normal', or 'humid')
        """
        return self.interpret_soil_moisture(sensor_value)
    
    def get_status_message(self, status):
        """Get display-friendly status message
        
        Args:
            status (str): Status from interpret_soil_moisture()
            
        Returns:
            str: Human-readable status message
        """
        # Get message from config, or create a capitalized version manually
        if status in DISPLAY_MESSAGES:
            return DISPLAY_MESSAGES[status]
        else:
            # Manual capitalization for CircuitPython compatibility
            status_str = str(status)
            if len(status_str) > 0:
                return status_str[0].upper() + status_str[1:].lower()
            return status_str
    
    def interpret_ambient_conditions(self, humidity, temperature):
        """Interpret ambient humidity and temperature conditions
        
        Args:
            humidity (float): Ambient humidity percentage
            temperature (float): Ambient temperature in Celsius
            
        Returns:
            dict: Analysis of ambient conditions
        """
        conditions = {
            'humidity_status': 'normal',
            'temperature_status': 'normal',
            'overall_ambient': 'good'
        }
        
        # Analyze humidity
        if humidity < self.ambient_thresholds['humidity']['low']:
            conditions['humidity_status'] = 'low'
        elif humidity > self.ambient_thresholds['humidity']['high']:
            conditions['humidity_status'] = 'high'
        
        # Analyze temperature
        if temperature < self.ambient_thresholds['temperature']['low']:
            conditions['temperature_status'] = 'low'
        elif temperature > self.ambient_thresholds['temperature']['high']:
            conditions['temperature_status'] = 'high'
        
        # Overall ambient assessment
        if (conditions['humidity_status'] != 'normal' or 
            conditions['temperature_status'] != 'normal'):
            conditions['overall_ambient'] = 'poor'
        
        return conditions
    
    def get_comprehensive_status(self, soil_value, ambient_humidity, ambient_temperature):
        """Get comprehensive plant health status considering all factors
        
        Args:
            soil_value (int): Raw soil moisture reading
            ambient_humidity (float): Ambient humidity percentage
            ambient_temperature (float): Ambient temperature in Celsius
            
        Returns:
            dict: Comprehensive status analysis
        """
        soil_status = self.interpret_soil_moisture(soil_value)
        ambient_conditions = self.interpret_ambient_conditions(ambient_humidity, ambient_temperature)
        
        # Determine overall plant health
        overall_status = 'good'
        priority_action = 'monitor'
        
        # Primary concern: soil moisture
        if soil_status == 'dry':
            overall_status = 'needs_water'
            priority_action = 'water_plant'
        elif soil_status == 'humid':
            overall_status = 'too_wet' 
            priority_action = 'reduce_watering'
        
        # Secondary concerns: ambient conditions
        elif ambient_conditions['overall_ambient'] == 'poor':
            if ambient_conditions['humidity_status'] == 'low':
                overall_status = 'dry_air'
                priority_action = 'increase_humidity'
            elif ambient_conditions['humidity_status'] == 'high':
                overall_status = 'humid_air'
                priority_action = 'improve_ventilation'
            elif ambient_conditions['temperature_status'] != 'normal':
                overall_status = 'temp_stress'
                priority_action = 'adjust_temperature'
        
        return {
            'soil_status': soil_status,
            'ambient_conditions': ambient_conditions,
            'overall_status': overall_status,
            'priority_action': priority_action,
            'soil_value': soil_value,
            'ambient_humidity': ambient_humidity,
            'ambient_temperature': ambient_temperature
        }
    
    def update_soil_thresholds(self, dry_threshold=None, normal_threshold=None):
        """Update soil moisture thresholds for calibration
        
        Args:
            dry_threshold (int): New threshold for dry soil
            normal_threshold (int): New threshold for normal soil
        """
        if dry_threshold is not None:
            self.soil_thresholds['dry'] = dry_threshold
        if normal_threshold is not None:
            self.soil_thresholds['normal'] = normal_threshold
    
    def update_ambient_thresholds(self, humidity_low=None, humidity_high=None, 
                                temp_low=None, temp_high=None):
        """Update ambient condition thresholds
        
        Args:
            humidity_low (float): Low humidity threshold
            humidity_high (float): High humidity threshold
            temp_low (float): Low temperature threshold
            temp_high (float): High temperature threshold
        """
        if humidity_low is not None:
            self.ambient_thresholds['humidity']['low'] = humidity_low
        if humidity_high is not None:
            self.ambient_thresholds['humidity']['high'] = humidity_high
        if temp_low is not None:
            self.ambient_thresholds['temperature']['low'] = temp_low
        if temp_high is not None:
            self.ambient_thresholds['temperature']['high'] = temp_high
    
    def get_current_thresholds(self):
        """Get current threshold values
        
        Returns:
            dict: Current threshold configuration
        """
        return {
            'soil': self.soil_thresholds.copy(),
            'ambient': self.ambient_thresholds.copy()
        }

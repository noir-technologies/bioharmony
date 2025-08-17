from config import HUMIDITY_THRESHOLDS, DISPLAY_MESSAGES

class SoilAnalyzer:
    """Analyzes soil moisture readings and provides status interpretation"""
    
    def __init__(self, thresholds=None):
        """Initialize the soil analyzer
        
        Args:
            thresholds (dict): Custom threshold values, uses config defaults if None
        """
        self.thresholds = thresholds or HUMIDITY_THRESHOLDS.copy()
    
    def interpret_moisture_level(self, sensor_value):
        """Interpret raw sensor value into moisture status
        
        Args:
            sensor_value (int): Raw sensor reading
            
        Returns:
            str: Status string ('dry', 'normal', or 'humid')
        """
        if sensor_value > self.thresholds['dry']:
            return 'dry'
        elif sensor_value >= self.thresholds['normal']:
            return 'normal'
        else:
            return 'humid'
    
    def get_status_message(self, status):
        """Get display-friendly status message
        
        Args:
            status (str): Status from interpret_moisture_level()
            
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
    
    def get_watering_recommendation(self, status):
        """Get watering recommendation based on soil status
        
        Args:
            status (str): Soil moisture status
            
        Returns:
            str: Watering recommendation
        """
        recommendations = {
            'dry': 'Water immediately',
            'normal': 'Monitor regularly',
            'humid': 'Reduce watering'
        }
        return recommendations.get(status, 'Check sensor')
    
    def is_critical_level(self, status):
        """Check if moisture level requires immediate attention
        
        Args:
            status (str): Soil moisture status
            
        Returns:
            bool: True if immediate action needed
        """
        return status in ['dry', 'humid']
    
    def update_thresholds(self, dry_threshold=None, normal_threshold=None):
        """Update moisture thresholds for calibration
        
        Args:
            dry_threshold (int): New threshold for dry soil
            normal_threshold (int): New threshold for normal soil
        """
        if dry_threshold is not None:
            self.thresholds['dry'] = dry_threshold
        if normal_threshold is not None:
            self.thresholds['normal'] = normal_threshold
    
    def get_current_thresholds(self):
        """Get current threshold values
        
        Returns:
            dict: Current threshold configuration
        """
        return self.thresholds.copy()

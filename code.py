import time
from sensors.humidity_sensor import HumiditySensor
from display.lcd_display import LCDDisplay
from alerts.buzzer_alerts import BuzzerAlerts
from utils.soil_analyzer import SoilAnalyzer
from config import MAIN_LOOP_DELAY

class PlantMonitor:
    """Main plant monitoring system coordinator"""
    
    def __init__(self):
        """Initialize all system components"""
        self.humidity_sensor = HumiditySensor()
        self.display = LCDDisplay()
        self.buzzer = BuzzerAlerts()
        self.soil_analyzer = SoilAnalyzer()
        
        # System state
        self.is_running = False
        self.error_count = 0
        self.max_errors = 5
    
    def startup_sequence(self):
        """Run startup sequence"""
        print("Plant Monitor starting...")
        
        # Show startup message on display
        self.display.display_startup_message()
        
        # Play startup sound
        self.buzzer.play_startup_sound()
        
        # Brief pause for startup message
        time.sleep(2)
        
        # Check if sensor is connected
        if not self.humidity_sensor.is_sensor_connected():
            self.display.display_error("Sensor Error")
            self.buzzer.play_error_sound()
            print("Warning: Humidity sensor may not be connected properly")
        
        print("Startup complete!")
    
    def read_and_display_status(self):
        """Read sensor, analyze, and update display and alerts"""
        try:
            # Read humidity sensor
            raw_value = self.humidity_sensor.read_raw_value()
            
            # Analyze soil status
            status = self.soil_analyzer.interpret_moisture_level(raw_value)
            
            # Update display
            self.display.display_humidity_status(status, raw_value)
            
            # Play status alert
            self.buzzer.play_status_alert(status)
            
            # Print to console for debugging
            status_msg = self.soil_analyzer.get_status_message(status)
            print(f"Humidity: {status_msg} (Raw: {raw_value})")
            
            # Reset error count on successful reading
            self.error_count = 0
            
        except Exception as e:
            self.error_count += 1
            error_msg = f"Error {self.error_count}: {str(e)}"
            print(error_msg)
            
            # Display error on LCD
            self.display.display_error(f"Err {self.error_count}")
            self.buzzer.play_error_sound()
            
            # Stop system if too many errors
            if self.error_count >= self.max_errors:
                print(f"Too many errors ({self.max_errors}). Stopping system.")
                self.stop()
    
    def run(self):
        """Run the main monitoring loop"""
        self.startup_sequence()
        self.is_running = True
        
        print("Starting monitoring loop...")
        
        try:
            while self.is_running:
                self.read_and_display_status()
                time.sleep(MAIN_LOOP_DELAY)
                
        except KeyboardInterrupt:
            print("\nShutdown requested by user")
            self.stop()
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
            self.stop()
    
    def stop(self):
        """Stop the monitoring system"""
        self.is_running = False
        self.display.display_custom_message("System", "Stopped")
        self.buzzer.cleanup()
        print("Plant Monitor stopped.")

# Main execution
if __name__ == "__main__":
    monitor = PlantMonitor()
    monitor.run()

import time
from sensors.humidity_sensor import SoilHumiditySensor
from sensors.dht_ambient_sensor import DHT11AmbientSensor
from display.lcd_display import LCDDisplay
from alerts.buzzer_alerts import BuzzerAlerts
from utils.soil_analyzer import PlantAnalyzer
from ai.melody_generator import AIPlantMelodyGenerator
from config import MAIN_LOOP_DELAY, ENABLE_AI_MELODIES

class PlantMonitor:
    """Main plant monitoring system coordinator"""
    
    def __init__(self):
        """Initialize all system components"""
        self.soil_sensor = SoilHumiditySensor()
        self.ambient_sensor = DHT11AmbientSensor()
        self.display = LCDDisplay()
        self.buzzer = BuzzerAlerts()
        self.plant_analyzer = PlantAnalyzer()
        
        # AI melody generator
        self.ai_melody_generator = None
        if ENABLE_AI_MELODIES:
            try:
                self.ai_melody_generator = AIPlantMelodyGenerator()
                print("AI melody generation enabled")
            except Exception as e:
                print(f"Failed to initialize AI melody generator: {e}")
                print("Continuing without AI features")
        
        # System state
        self.is_running = False
        self.error_count = 0
        self.max_errors = 5
        self.use_ai_melodies = True  # Toggle for AI vs standard melodies
    
    def startup_sequence(self):
        """Run startup sequence"""
        print("Plant Monitor starting...")
        
        # Show startup message on display
        self.display.display_startup_message()
        
        # Play startup sound
        self.buzzer.play_startup_sound()
        
        # Brief pause for startup message
        time.sleep(2)
        
        # Check if sensors are connected
        print("Checking soil sensor connection...")
        
        if not self.soil_sensor.is_sensor_connected():
            self.display.display_error("Soil Sensor Err")
            self.buzzer.play_error_sound()
            print("Warning: Soil humidity sensor may not be connected properly")
            time.sleep(2)
        else:
            print("Soil sensor connected successfully")
        
        if not self.ambient_sensor.is_sensor_connected():
            self.display.display_error("Ambient Sens Err")
            self.buzzer.play_error_sound()
            print("Warning: Ambient sensor may not be connected properly")
            time.sleep(2)
        else:
            print("Ambient sensor connected successfully")
        
        print("Startup complete!")
    
    def read_and_display_status(self):
        """Read sensors, analyze, and update display and alerts"""
        try:
            # Read soil moisture sensor
            soil_value = self.soil_sensor.read_raw_value()
            
            # Read ambient conditions (DHT11 can return None)
            ambient_humidity, ambient_temperature = self.ambient_sensor.read_humidity_and_temperature()
            
            # Handle DHT11 read failures gracefully
            if ambient_humidity is None or ambient_temperature is None:
                print("DHT11 read failed, using last known values or defaults")
                # Try to get last known values
                ambient_humidity, ambient_temperature = self.ambient_sensor.get_last_readings()
                
                # If still None, use reasonable defaults to keep system running
                if ambient_humidity is None:
                    ambient_humidity = 50.0  # Default humidity
                if ambient_temperature is None:
                    ambient_temperature = 22.0  # Default temperature
            
            # Get comprehensive analysis
            comprehensive_status = self.plant_analyzer.get_comprehensive_status(
                soil_value, ambient_humidity, ambient_temperature
            )
            
            # Try to generate AI melody and message
            ai_melody = None
            ai_message = None
            
            if self.ai_melody_generator and self.use_ai_melodies:
                try:
                    print("Requesting AI melody generation...")
                    ai_melody, ai_message = self.ai_melody_generator.generate_melody_and_message(comprehensive_status)
                    if ai_melody:
                        print(f"AI generated: {ai_message}")
                        print(f"Melody: {ai_melody[:50]}...")
                except Exception as e:
                    print(f"AI melody generation failed: {e}")
                    ai_melody = None
                    ai_message = None
            
            # Update display - show AI message if available, otherwise standard status
            if ai_message and len(ai_message) > 0:
                # Show AI-generated message with ambient data
                temp_humidity_line = f"{ambient_temperature:.1f}C {ambient_humidity:.0f}%"
                self.display.display_custom_message(ai_message, temp_humidity_line)
            else:
                # Show standard comprehensive status
                self.display.display_comprehensive_status(comprehensive_status)
            
            # Play appropriate melody/alert
            if ai_melody and self.use_ai_melodies:
                # Play AI-generated melody
                print("Playing AI-generated melody...")
                self.buzzer.play_ai_melody(ai_melody)
            else:
                # Play standard alert pattern
                self.buzzer.play_comprehensive_alert(comprehensive_status)
            
            # Print detailed status to console for debugging
            print(f"Soil: {comprehensive_status['soil_status']} ({soil_value})")
            print(f"Ambient: {ambient_temperature:.1f}°C, {ambient_humidity:.0f}%RH")
            print(f"Overall: {comprehensive_status['overall_status']}")
            print(f"Action: {comprehensive_status['priority_action']}")
            print("---")
            
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
                self.stop()            # Reset error count on successful reading
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

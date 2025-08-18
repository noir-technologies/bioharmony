import time
import wifi
import socketpool
import ssl
import adafruit_requests as requests
from secrets import secrets
from config import PLANT_INFO, AI_REQUEST_INTERVAL, WIFI_TIMEOUT, MAX_WIFI_RETRIES

class AIPlantMelodyGenerator:
    """Generates AI-powered melodies based on comprehensive plant status"""
    
    def __init__(self):
        """Initialize the AI melody generator"""
        self.pool = None
        self.https = None
        self.is_wifi_connected = False
        self.last_ai_request_time = 0
        self.last_generated_melody = None
        self.last_status_message = ""
        
        # Enhanced prompt template for plant-specific melodies
        self.prompt_template = """
Plant Status Analysis:
- Plant Type: {plant_type}
- Location: {location}
- Soil Moisture: {soil_status} (Raw: {soil_value})
- Ambient Temperature: {temperature:.1f}°C
- Ambient Humidity: {humidity:.0f}%RH
- Overall Health: {overall_status}
- Priority Action: {priority_action}
- Mood Assessment: {mood}

Generate two things:
1. A brief, encouraging message about the plant's condition (max 30 characters for LCD display)
2. A melodic representation of the plant's "mood" in format "note,duration,note,duration,..." using notes C3-C6 and R for rests. The melody should reflect the emotional state - happy/healthy plants get uplifting melodies, stressed plants get more somber tones, urgent care needs get attention-grabbing patterns.

Format your response as:
MESSAGE: [your message here]
MELODY: [note,duration,note,duration,...]
"""
    
    def connect_wifi(self):
        """Connect to WiFi network"""
        if self.is_wifi_connected:
            return True
            
        print("Connecting to WiFi...")
        
        for attempt in range(MAX_WIFI_RETRIES):
            try:
                wifi.radio.connect(secrets["ssid"], secrets["password"])
                self.pool = socketpool.SocketPool(wifi.radio)
                self.https = requests.Session(self.pool, ssl.create_default_context())
                self.is_wifi_connected = True
                print(f"WiFi connected! IP: {wifi.radio.ipv4_address}")
                return True
                
            except Exception as e:
                print(f"WiFi connection attempt {attempt + 1} failed: {e}")
                if attempt < MAX_WIFI_RETRIES - 1:
                    time.sleep(2)
        
        print("Failed to connect to WiFi after all attempts")
        return False
    
    def generate_plant_mood(self, comprehensive_status):
        """Generate a mood description based on plant status
        
        Args:
            comprehensive_status (dict): Complete plant analysis
            
        Returns:
            str: Mood description for AI prompt
        """
        overall = comprehensive_status['overall_status']
        soil = comprehensive_status['soil_status']
        ambient = comprehensive_status['ambient_conditions']
        
        if overall == 'good':
            return "content and thriving"
        elif overall == 'needs_water':
            return "thirsty and in need of care"
        elif overall == 'too_wet':
            return "overwhelmed by too much water"
        elif overall == 'dry_air':
            return "stressed by dry air conditions"
        elif overall == 'humid_air':
            return "uncomfortable with high humidity"
        elif overall == 'temp_stress':
            if ambient['temperature_status'] == 'low':
                return "cold and seeking warmth"
            else:
                return "overheated and needing cooling"
        else:
            return "uncertain and needing attention"
    
    def should_request_new_melody(self):
        """Check if enough time has passed to request a new melody"""
        current_time = time.monotonic()
        return (current_time - self.last_ai_request_time) >= AI_REQUEST_INTERVAL
    
    def generate_melody_and_message(self, comprehensive_status):
        """Generate AI melody and message based on plant status
        
        Args:
            comprehensive_status (dict): Complete plant analysis
            
        Returns:
            tuple: (melody_string, message_string) or (None, None) if failed
        """
        if not self.should_request_new_melody():
            return self.last_generated_melody, self.last_status_message
        
        if not self.connect_wifi():
            return None, "WiFi Error"
        
        try:
            # Generate mood description
            mood = self.generate_plant_mood(comprehensive_status)
            
            # Prepare prompt data
            prompt_data = {
                'plant_type': PLANT_INFO['type'],
                'location': PLANT_INFO['location'], 
                'soil_status': comprehensive_status['soil_status'],
                'soil_value': comprehensive_status['soil_value'],
                'temperature': comprehensive_status['ambient_temperature'],
                'humidity': comprehensive_status['ambient_humidity'],
                'overall_status': comprehensive_status['overall_status'],
                'priority_action': comprehensive_status['priority_action'],
                'mood': mood
            }
            
            # Prepare API payload
            payload = {
                "location": PLANT_INFO['location'],
                "plant_type": PLANT_INFO['type'],
                "soil_moisture": comprehensive_status['soil_value'],
                "temperature": comprehensive_status['ambient_temperature'],
                "humidity": comprehensive_status['ambient_humidity']
            }
            
            url = secrets["url_mcp"] + "/consulta"
            print("Requesting AI melody from:", url)
            
            # Make API request
            response = self.https.post(url, json=payload)
            
            if response.status_code == 200:
                ai_response = response.json().get("respuesta", "")
                melody, message = self.parse_ai_response(ai_response)
                
                # Update cache
                self.last_ai_request_time = time.monotonic()
                self.last_generated_melody = melody
                self.last_status_message = message
                
                print(f"AI Response: {message}")
                print(f"Generated melody: {melody}")
                
                return melody, message
            else:
                print(f"API Error: {response.status_code}")
                return None, "AI Error"
                
        except Exception as e:
            print(f"Error generating AI melody: {e}")
            return None, "Request Failed"
    
    def parse_ai_response(self, ai_response):
        """Parse AI response to extract message and melody
        
        Args:
            ai_response (str): Raw AI response text
            
        Returns:
            tuple: (melody, message)
        """
        try:
            lines = ai_response.strip().split('\n')
            message = ""
            melody = ""
            
            for line in lines:
                if line.startswith("MESSAGE:"):
                    message = line.replace("MESSAGE:", "").strip()
                elif line.startswith("MELODY:"):
                    melody = line.replace("MELODY:", "").strip()
            
            # Fallback parsing if format is different
            if not melody:
                # Look for comma-separated note patterns
                for line in lines:
                    if ',' in line and any(note in line for note in ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'R']):
                        melody = line.strip()
                        break
            
            # Use defaults if parsing failed
            if not message:
                message = "Plant status updated"
            if not melody:
                melody = "C4,0.5,E4,0.5,G4,0.5"  # Simple default melody
            
            # Ensure message fits LCD display
            if len(message) > 16:
                message = message[:13] + "..."
                
            return melody, message
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return "C4,0.5,E4,0.5,G4,0.5", "Parse Error"
    
    def get_cached_melody(self):
        """Get last generated melody without making new request
        
        Returns:
            tuple: (melody, message) or (None, None) if no cache
        """
        return self.last_generated_melody, self.last_status_message
    
    def is_connected(self):
        """Check if WiFi is connected
        
        Returns:
            bool: True if WiFi is connected
        """
        return self.is_wifi_connected

import time
import board
import pwmio
from config import (
    BUZZER_PIN, 
    ALERT_FREQUENCIES, 
    BUZZER_NOTE_DURATION, 
    BUZZER_NOTE_PAUSE,
    BUZZER_DUTY_CYCLE
)

class BuzzerAlerts:
    """Manages buzzer alerts for different soil moisture conditions"""
    
    def __init__(self, pin_name=BUZZER_PIN):
        """Initialize the buzzer
        
        Args:
            pin_name (str): Board pin name for the buzzer
        """
        self.buzzer = pwmio.PWMOut(
            getattr(board, pin_name), 
            duty_cycle=0, 
            frequency=440, 
            variable_frequency=True
        )
        self.is_enabled = True
    
    def play_note(self, frequency, duration=BUZZER_NOTE_DURATION):
        """Play a single note
        
        Args:
            frequency (int): Note frequency in Hz
            duration (float): Note duration in seconds
        """
        if not self.is_enabled:
            return
            
        self.buzzer.frequency = frequency
        self.buzzer.duty_cycle = BUZZER_DUTY_CYCLE
        time.sleep(duration)
        self.buzzer.duty_cycle = 0
    
    def play_melody(self, frequencies, note_duration=BUZZER_NOTE_DURATION, pause_duration=BUZZER_NOTE_PAUSE):
        """Play a sequence of notes
        
        Args:
            frequencies (list): List of frequencies to play
            note_duration (float): Duration of each note
            pause_duration (float): Pause between notes
        """
        if not self.is_enabled:
            return
            
        for frequency in frequencies:
            self.play_note(frequency, note_duration)
            time.sleep(pause_duration)
    
    def play_status_alert(self, status):
        """Play alert melody based on soil moisture status
        
        Args:
            status (str): Soil moisture status ('dry', 'normal', 'humid')
        """
        if not self.is_enabled:
            return
            
        frequencies = ALERT_FREQUENCIES.get(status, ALERT_FREQUENCIES['normal'])
        self.play_melody(frequencies)
    
    def play_startup_sound(self):
        """Play startup sound sequence"""
        startup_melody = [523, 659, 784]  # C5, E5, G5
        self.play_melody(startup_melody, note_duration=0.15, pause_duration=0.05)
    
    def play_error_sound(self):
        """Play error/warning sound"""
        error_melody = [196, 196, 196]  # Three low G notes
        self.play_melody(error_melody, note_duration=0.3, pause_duration=0.1)
    
    def play_comprehensive_alert(self, comprehensive_status):
        """Play alert based on comprehensive plant status
        
        Args:
            comprehensive_status (dict): Result from PlantAnalyzer.get_comprehensive_status()
        """
        if not self.is_enabled:
            return
        
        overall_status = comprehensive_status['overall_status']
        soil_status = comprehensive_status['soil_status']
        
        # Choose alert pattern based on priority
        if overall_status == 'needs_water':
            # Urgent - soil is dry
            frequencies = ALERT_FREQUENCIES['dry']
        elif overall_status == 'too_wet':
            # Urgent - soil is too wet  
            frequencies = ALERT_FREQUENCIES['humid']
        elif overall_status == 'good':
            # All good
            frequencies = ALERT_FREQUENCIES['normal']
        else:
            # Ambient issues - play modified pattern
            if 'dry_air' in overall_status or 'temp' in overall_status:
                frequencies = [440, 523, 440]  # A4, C5, A4 - Alert pattern
            else:
                frequencies = [330, 440, 330]  # E4, A4, E4 - Warning pattern
        
        self.play_melody(frequencies)
    
    def play_calibration_beep(self):
        """Play single calibration confirmation beep"""
        self.play_note(880, 0.1)  # Short high beep
    
    def enable_alerts(self):
        """Enable buzzer alerts"""
        self.is_enabled = True
    
    def disable_alerts(self):
        """Disable buzzer alerts"""
        self.is_enabled = False
        self.buzzer.duty_cycle = 0  # Ensure buzzer is off
    
    def toggle_alerts(self):
        """Toggle buzzer alerts on/off
        
        Returns:
            bool: New enabled state
        """
        self.is_enabled = not self.is_enabled
        if not self.is_enabled:
            self.buzzer.duty_cycle = 0
        return self.is_enabled
    
    def is_alerts_enabled(self):
        """Check if alerts are enabled
        
        Returns:
            bool: True if alerts are enabled
        """
        return self.is_enabled
    
    def cleanup(self):
        """Clean up buzzer resources"""
        self.buzzer.duty_cycle = 0
        # Note: PWMOut doesn't have a direct cleanup method in CircuitPython
    
    def play_ai_melody(self, melody_string):
        """Play AI-generated melody from string format
        
        Args:
            melody_string (str): Melody in format "note,duration,note,duration,..."
        """
        if not self.is_enabled or not melody_string:
            return
        
        # Musical note frequencies for AI-generated melodies  
        MUSICAL_NOTES = {
            "C3": 131, "C#3": 139, "D3": 147, "D#3": 156, "E3": 165, "F3": 175, "F#3": 185,
            "G3": 196, "G#3": 208, "A3": 220, "A#3": 233, "B3": 247,
            "C4": 262, "C#4": 277, "D4": 294, "D#4": 311, "E4": 330, "F4": 349, "F#4": 370,
            "G4": 392, "G#4": 415, "A4": 440, "A#4": 466, "B4": 494,
            "C5": 523, "C#5": 554, "D5": 587, "D#5": 622, "E5": 659, "F5": 698, "F#5": 740,
            "G5": 784, "G#5": 831, "A5": 880, "A#5": 932, "B5": 988,
            "C6": 1047, "C#6": 1109, "D6": 1175, "D#6": 1245, "E6": 1319, "F6": 1397, "F#6": 1480,
            "G6": 1568, "G#6": 1661, "A6": 1760, "A#6": 1865, "B6": 1976,
            "C7": 2093, "R": 0  # R = Rest/silence
        }
        
        try:
            parts = melody_string.strip().split(",")
            
            # Ensure we have pairs of note,duration
            if len(parts) % 2 != 0:
                print("Invalid melody format: odd number of parts")
                return
            
            print(f"Playing AI melody: {melody_string}")
            
            for i in range(0, len(parts), 2):
                if i + 1 >= len(parts):
                    break
                    
                note = parts[i].strip().upper()
                try:
                    duration = float(parts[i + 1].strip())
                except ValueError:
                    duration = 0.5  # Default duration
                
                # Get frequency for note
                frequency = MUSICAL_NOTES.get(note, 0)
                
                if frequency == 0:  # Rest or invalid note
                    self.buzzer.duty_cycle = 0
                else:
                    self.buzzer.frequency = frequency
                    self.buzzer.duty_cycle = BUZZER_DUTY_CYCLE
                
                time.sleep(duration)
                self.buzzer.duty_cycle = 0
                time.sleep(0.05)  # Brief pause between notes
                
        except Exception as e:
            print(f"Error playing AI melody: {e}")
            # Play a simple fallback melody
            self.play_melody([440, 523, 659])

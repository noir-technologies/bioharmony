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

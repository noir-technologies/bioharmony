import board
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface
from lcd.lcd import CursorMode
from config import LCD_I2C_ADDRESS, LCD_ROWS, LCD_COLS, DISPLAY_MESSAGES

class LCDDisplay:
    """Manages LCD display operations for the plant monitoring system"""
    
    def __init__(self, i2c_address=LCD_I2C_ADDRESS, rows=LCD_ROWS, cols=LCD_COLS):
        """Initialize the LCD display
        
        Args:
            i2c_address (int): I2C address of the LCD controller
            rows (int): Number of display rows
            cols (int): Number of display columns
        """
        self.rows = rows
        self.cols = cols
        
        # Initialize I2C and LCD
        self.i2c = board.I2C()
        self.lcd = LCD(
            I2CPCF8574Interface(self.i2c, i2c_address), 
            num_rows=rows, 
            num_cols=cols
        )
        self.lcd.set_cursor_mode(CursorMode.HIDE)
    
    def clear(self):
        """Clear the display"""
        self.lcd.clear()
    
    def print_at(self, row, col, text):
        """Print text at specific position
        
        Args:
            row (int): Row position (0-based)
            col (int): Column position (0-based) 
            text (str): Text to display
        """
        self.lcd.set_cursor_pos(row, col)
        # Truncate text if it's too long for the display
        max_chars = self.cols - col
        if len(text) > max_chars:
            text = text[:max_chars]
        self.lcd.print(text)
    
    def display_humidity_status(self, status, raw_value):
        """Display humidity status on the LCD
        
        Args:
            status (str): Moisture status ('dry', 'normal', 'humid')
            raw_value (int): Raw sensor reading
        """
        self.clear()
        
        # First line: "Humidity:" label
        self.print_at(0, 0, DISPLAY_MESSAGES['humidity_label'])
        
        # Second line: Status and raw value
        if status in DISPLAY_MESSAGES:
            status_text = DISPLAY_MESSAGES[status]
        else:
            # Manual capitalization for CircuitPython compatibility
            status_str = str(status)
            if len(status_str) > 0:
                status_text = status_str[0].upper() + status_str[1:].lower()
            else:
                status_text = status_str
        value_text = f"{status_text} ({raw_value})"
        self.print_at(1, 0, value_text)
    
    def display_error(self, error_message):
        """Display error message
        
        Args:
            error_message (str): Error message to display
        """
        self.clear()
        self.print_at(0, 0, "ERROR:")
        self.print_at(1, 0, error_message)
    
    def display_startup_message(self):
        """Display startup/initialization message"""
        self.clear()
        self.print_at(0, 0, "Plant Monitor")
        self.print_at(1, 0, "Starting...")
    
    def display_calibration_mode(self, mode_type):
        """Display calibration mode message
        
        Args:
            mode_type (str): Type of calibration ('dry' or 'wet')
        """
        self.clear()
        self.print_at(0, 0, "Calibration:")
        # Manual capitalization for CircuitPython compatibility
        if len(mode_type) > 0:
            capitalized_mode = mode_type[0].upper() + mode_type[1:].lower()
        else:
            capitalized_mode = mode_type
        self.print_at(1, 0, f"{capitalized_mode} soil")
    
    def display_custom_message(self, line1, line2=""):
        """Display custom two-line message
        
        Args:
            line1 (str): First line text
            line2 (str): Second line text (optional)
        """
        self.clear()
        self.print_at(0, 0, line1)
        if line2:
            self.print_at(1, 0, line2)
    
    def get_display_info(self):
        """Get display configuration info
        
        Returns:
            dict: Display configuration (rows, cols, address)
        """
        return {
            'rows': self.rows,
            'cols': self.cols,
            'i2c_address': LCD_I2C_ADDRESS
        }

from pynput import keyboard
import threading
from typing import Callable, Optional, Set, List

class GlobalKeyboardHandler:
    """Global keyboard shortcut handler for recording control."""
    
    def __init__(self):
        """Initialize the keyboard handler."""
        self.listener = None
        self.is_listening = False
        self.recording_callback: Optional[Callable] = None
        self.toggle_key_combination = {keyboard.Key.cmd, keyboard.KeyCode.from_char('r')}  # Cmd+R on macOS
        self.currently_pressed = set()
        self.recording_active = False
        
    def set_recording_callback(self, callback: Callable):
        """Set the callback function to call when recording shortcut is pressed."""
        self.recording_callback = callback
    
    def set_toggle_keys(self, keys: List):
        """Set custom key combination for toggling recording.
        
        Args:
            keys: List of keys for the combination (e.g., [keyboard.Key.ctrl, keyboard.KeyCode.from_char('r')])
        """
        self.toggle_key_combination = set(keys)
    
    def start_listening(self) -> bool:
        """Start listening for global keyboard shortcuts."""
        if self.is_listening:
            return False
        
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.listener.start()
            self.is_listening = True
            print("🎯 Global keyboard listener started. Press Cmd+R to toggle recording.")
            return True
        except Exception as e:
            print(f"❌ Error starting keyboard listener: {e}")
            return False
    
    def stop_listening(self):
        """Stop listening for global keyboard shortcuts."""
        if self.listener:
            self.listener.stop()
            self.is_listening = False
            print("🛑 Global keyboard listener stopped.")
    
    def _on_key_press(self, key):
        """Handle key press events."""
        try:
            self.currently_pressed.add(key)
            
            # Check if the toggle combination is pressed
            if self._is_toggle_combination_pressed():
                if not self.recording_active:
                    self.recording_active = True
                    if self.recording_callback:
                        threading.Thread(target=self.recording_callback, daemon=True).start()
                        
        except Exception as e:
            print(f"Error in key press handler: {e}")
    
    def _on_key_release(self, key):
        """Handle key release events."""
        try:
            if key in self.currently_pressed:
                self.currently_pressed.remove(key)
            
            # Reset recording_active when toggle keys are released
            if not self._is_toggle_combination_pressed():
                self.recording_active = False
                
        except Exception as e:
            print(f"Error in key release handler: {e}")
    
    def _is_toggle_combination_pressed(self) -> bool:
        """Check if the toggle key combination is currently pressed."""
        return self.toggle_key_combination.issubset(self.currently_pressed)
    
    def get_key_combination_string(self) -> str:
        """Get a human-readable string of the current key combination."""
        key_names = []
        for key in self.toggle_key_combination:
            if hasattr(key, 'name'):
                key_names.append(key.name.capitalize())
            elif hasattr(key, 'char'):
                key_names.append(key.char.upper())
            else:
                key_names.append(str(key))
        return '+'.join(key_names)
    
    def is_listening_active(self) -> bool:
        """Check if the keyboard listener is active."""
        return self.is_listening

class KeyboardShortcuts:
    """Predefined keyboard shortcuts for different platforms."""
    
    # macOS shortcuts
    MAC_CMD_R = [keyboard.Key.cmd, keyboard.KeyCode.from_char('r')]
    MAC_CMD_SPACE = [keyboard.Key.cmd, keyboard.Key.space]
    
    # Windows/Linux shortcuts  
    CTRL_R = [keyboard.Key.ctrl, keyboard.KeyCode.from_char('r')]
    CTRL_SPACE = [keyboard.Key.ctrl, keyboard.Key.space]
    
    # Function keys
    F1 = [keyboard.Key.f1]
    F2 = [keyboard.Key.f2]
    F3 = [keyboard.Key.f3]
    
    @staticmethod
    def get_platform_default():
        """Get the default shortcut for the current platform."""
        import platform
        system = platform.system().lower()
        
        if system == 'darwin':  # macOS
            return KeyboardShortcuts.MAC_CMD_R
        else:  # Windows/Linux
            return KeyboardShortcuts.CTRL_R

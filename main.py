#!/usr/bin/env python3
"""
Speech-to-Text Recorder Application

A Python application that allows you to record speech using keyboard shortcuts
and automatically transcribe it using OpenAI Whisper, storing results in a local database.

Usage:
    python main.py [options]

Options:
    --headless      Run without GUI (service mode only)
    --model MODEL   Specify Whisper model (tiny, base, small, medium, large)
    --help         Show this help message
"""

import sys
import argparse
import signal
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from speech_recorder import SpeechRecorder
from ui import SpeechRecorderUI

class SpeechRecorderApp:
    """Main application class."""
    
    def __init__(self, headless=False, model="base"):
        """Initialize the application."""
        self.headless = headless
        self.model = model
        self.speech_recorder = None
        self.ui = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n📨 Received signal {signum}. Shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def run_headless(self):
        """Run the application in headless mode (no GUI)."""
        print("🚀 Starting Speech-to-Text Recorder (Headless Mode)")
        print("=" * 50)
        
        # Initialize speech recorder
        self.speech_recorder = SpeechRecorder(self.model)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Start the service
        success = self.speech_recorder.start_service()
        if not success:
            print("❌ Failed to start speech recording service.")
            return False
        
        print("\n✅ Service started successfully!")
        print(f"🎯 Press {self.speech_recorder.keyboard_handler.get_key_combination_string()} to toggle recording")
        print("🛑 Press Ctrl+C to stop the service")
        print("\n" + "=" * 50)
        
        try:
            # Keep the service running
            while True:
                time.sleep(1)
                
                # Print periodic status updates
                if hasattr(self, '_last_status_time'):
                    if time.time() - self._last_status_time > 30:  # Every 30 seconds
                        self.print_status_update()
                        self._last_status_time = time.time()
                else:
                    self._last_status_time = time.time()
                    
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received.")
        finally:
            self.shutdown()
        
        return True
    
    def run_gui(self):
        """Run the application with GUI."""
        print("🚀 Starting Speech-to-Text Recorder (GUI Mode)")
        
        try:
            self.ui = SpeechRecorderUI()
            self.ui.run()
        except Exception as e:
            print(f"❌ Error starting GUI: {e}")
            return False
        
        return True
    
    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        print("🔍 Checking prerequisites...")
        
        # Check microphone
        if not self.speech_recorder.audio_recorder.is_microphone_available():
            print("❌ No microphone available. Please check your audio input devices.")
            return False
        
        print("✅ Microphone available")
        
        # Check Whisper model
        if not self.speech_recorder.speech_processor.is_model_loaded():
            print("❌ Whisper model failed to load. Check your installation.")
            return False
        
        print(f"✅ Whisper model '{self.model}' loaded successfully")
        
        # List available audio devices
        devices = self.speech_recorder.audio_recorder.list_audio_devices()
        print(f"🎤 Found {len(devices)} audio input device(s):")
        for device in devices[:3]:  # Show first 3 devices
            print(f"   - {device['name']} ({device['channels']} channels)")
        
        return True
    
    def print_status_update(self):
        """Print a status update."""
        if self.speech_recorder:
            stats = self.speech_recorder.get_stats()
            print(f"📊 Status: {stats['total_transcriptions']} transcriptions, "
                  f"{stats['total_duration_seconds']:.1f}s total duration")
    
    def shutdown(self):
        """Shutdown the application gracefully."""
        print("\n🛑 Shutting down...")
        
        if self.speech_recorder and self.speech_recorder.is_service_running():
            self.speech_recorder.stop_service()
            print("✅ Speech recording service stopped")
        
        if hasattr(self, 'ui') and self.ui:
            try:
                self.ui.root.quit()
            except:
                pass
        
        print("👋 Goodbye!")
    
    def run(self):
        """Run the application."""
        if self.headless:
            return self.run_headless()
        else:
            return self.run_gui()

def print_help():
    """Print help message."""
    print(__doc__)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Speech-to-Text Recorder with keyboard shortcuts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without GUI (service mode only)"
    )
    
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model to use (default: base)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Speech-to-Text Recorder v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Create and run the application
    app = SpeechRecorderApp(headless=args.headless, model=args.model)
    
    try:
        success = app.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

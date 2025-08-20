import threading
import time
from typing import Optional
from datetime import datetime

from audio_recorder import AudioRecorder
from speech_to_text import SpeechToTextProcessor
from database import TranscriptionDatabase
from keyboard_handler import GlobalKeyboardHandler, KeyboardShortcuts

class SpeechRecorder:
    """Main speech recorder class that coordinates recording, transcription, and storage."""
    
    def __init__(self, whisper_model: str = "base"):
        """Initialize the speech recorder with all components."""
        self.audio_recorder = AudioRecorder()
        self.speech_processor = SpeechToTextProcessor(whisper_model)
        self.database = TranscriptionDatabase()
        self.keyboard_handler = GlobalKeyboardHandler()
        
        # State tracking
        self.is_recording = False
        self.current_audio_file = None
        
        # Callbacks for UI updates
        self.on_recording_start_callback = None
        self.on_recording_stop_callback = None
        self.on_transcription_complete_callback = None
        
        # Setup keyboard handler
        self.keyboard_handler.set_recording_callback(self.toggle_recording)
        
        # Setup audio recorder callbacks
        self.audio_recorder.on_recording_start = self._on_recording_start
        self.audio_recorder.on_recording_stop = self._on_recording_stop
    
    def start_service(self) -> bool:
        """Start the speech recording service (keyboard listener)."""
        if not self.speech_processor.is_model_loaded():
            print("❌ Speech-to-text model not loaded. Cannot start service.")
            return False
        
        if not self.audio_recorder.is_microphone_available():
            print("❌ No microphone available. Cannot start service.")
            return False
        
        success = self.keyboard_handler.start_listening()
        if success:
            shortcut = self.keyboard_handler.get_key_combination_string()
            print(f"🚀 Speech recording service started! Press {shortcut} to record.")
            print("📊 Database ready for storing transcriptions.")
        
        return success
    
    def stop_service(self):
        """Stop the speech recording service."""
        self.keyboard_handler.stop_listening()
        if self.is_recording:
            self.stop_recording()
        print("🛑 Speech recording service stopped.")
    
    def toggle_recording(self):
        """Toggle recording state (called by keyboard shortcut)."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self) -> bool:
        """Start recording audio."""
        if self.is_recording:
            return False
        
        success = self.audio_recorder.start_recording()
        if success:
            self.is_recording = True
        
        return success
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording and process the audio."""
        if not self.is_recording:
            return None
        
        self.current_audio_file = self.audio_recorder.stop_recording()
        self.is_recording = False
        
        if self.current_audio_file:
            # Process transcription in background thread
            threading.Thread(
                target=self._process_transcription,
                args=(self.current_audio_file,),
                daemon=True
            ).start()
        
        return self.current_audio_file
    
    def _process_transcription(self, audio_file_path: str):
        """Process audio transcription in background."""
        print("🔤 Processing transcription...")
        
        try:
            # Get transcription
            result = self.speech_processor.transcribe_audio_file(audio_file_path)
            
            if result['success'] and result['text'].strip():
                # Save to database
                duration = self.audio_recorder.get_recording_duration()
                transcription_id = self.database.save_transcription(
                    text=result['text'],
                    duration=duration,
                    audio_file_path=audio_file_path,
                    confidence=result.get('confidence', 0.0)
                )
                
                print(f"✅ Transcription saved (ID: {transcription_id})")
                print(f"📝 Text: {result['text']}")
                
                # Callback for UI updates
                if self.on_transcription_complete_callback:
                    self.on_transcription_complete_callback(transcription_id, result['text'])
                    
            else:
                error_msg = result.get('error', 'No speech detected')
                print(f"❌ Transcription failed: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error processing transcription: {e}")
    
    def _on_recording_start(self):
        """Internal callback when recording starts."""
        if self.on_recording_start_callback:
            self.on_recording_start_callback()
    
    def _on_recording_stop(self):
        """Internal callback when recording stops."""
        if self.on_recording_stop_callback:
            self.on_recording_stop_callback()
    
    def get_all_transcriptions(self):
        """Get all transcriptions from database."""
        return self.database.get_all_transcriptions()
    
    def search_transcriptions(self, search_term: str):
        """Search transcriptions by text content."""
        return self.database.search_transcriptions(search_term)
    
    def delete_transcription(self, transcription_id: int) -> bool:
        """Delete a transcription by ID."""
        return self.database.delete_transcription(transcription_id)
    
    def get_stats(self):
        """Get database statistics."""
        return self.database.get_stats()
    
    def change_whisper_model(self, model_name: str) -> bool:
        """Change the Whisper model."""
        return self.speech_processor.change_model(model_name)
    
    def get_available_models(self):
        """Get available Whisper models."""
        return self.speech_processor.get_available_models()
    
    def get_model_info(self):
        """Get current model information."""
        return self.speech_processor.get_model_info()
    
    def set_recording_callbacks(
        self,
        on_start=None,
        on_stop=None,
        on_transcription_complete=None
    ):
        """Set callback functions for UI updates."""
        if on_start:
            self.on_recording_start_callback = on_start
        if on_stop:
            self.on_recording_stop_callback = on_stop
        if on_transcription_complete:
            self.on_transcription_complete_callback = on_transcription_complete
    
    def is_service_running(self) -> bool:
        """Check if the service is running."""
        return self.keyboard_handler.is_listening_active()
    
    def get_recording_status(self) -> dict:
        """Get current recording status."""
        return {
            'is_recording': self.is_recording,
            'service_running': self.is_service_running(),
            'model_loaded': self.speech_processor.is_model_loaded(),
            'microphone_available': self.audio_recorder.is_microphone_available(),
            'current_model': self.speech_processor.model_name,
            'shortcut': self.keyboard_handler.get_key_combination_string()
        }

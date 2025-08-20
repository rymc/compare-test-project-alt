import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import os
from datetime import datetime
from typing import Optional, Callable

class AudioRecorder:
    """Audio recording class that can record audio on command."""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """Initialize the audio recorder with specified settings."""
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.audio_data = []
        self.recording_thread = None
        self.recording_start_time = None
        
        # Callbacks
        self.on_recording_start: Optional[Callable] = None
        self.on_recording_stop: Optional[Callable] = None
        
        # Create audio directory if it doesn't exist
        self.audio_dir = "audio_files"
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def start_recording(self) -> bool:
        """Start recording audio. Returns True if recording started successfully."""
        if self.is_recording:
            return False
        
        self.is_recording = True
        self.audio_data = []
        self.recording_start_time = datetime.now()
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        if self.on_recording_start:
            self.on_recording_start()
        
        print("🎤 Recording started...")
        return True
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording and save the audio file. Returns the file path if successful."""
        if not self.is_recording:
            return None
        
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join()
        
        if self.on_recording_stop:
            self.on_recording_stop()
        
        # Save the recorded audio
        if len(self.audio_data) > 0:
            audio_array = np.concatenate(self.audio_data, axis=0)
            file_path = self._save_audio(audio_array)
            print(f"🔇 Recording stopped. Saved to: {file_path}")
            return file_path
        else:
            print("🔇 Recording stopped. No audio data recorded.")
            return None
    
    def toggle_recording(self) -> bool:
        """Toggle recording state. Returns True if now recording, False if stopped."""
        if self.is_recording:
            self.stop_recording()
            return False
        else:
            return self.start_recording()
    
    def _record_audio(self):
        """Internal method to record audio in chunks."""
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio callback status: {status}")
            if self.is_recording:
                self.audio_data.append(indata.copy())
        
        try:
            with sd.InputStream(
                callback=audio_callback,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype=np.float32
            ):
                while self.is_recording:
                    sd.sleep(100)  # Sleep for 100ms
        except Exception as e:
            print(f"Error during recording: {e}")
            self.is_recording = False
    
    def _save_audio(self, audio_data: np.ndarray) -> str:
        """Save audio data to a file and return the file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        file_path = os.path.join(self.audio_dir, filename)
        
        # Save the audio file
        sf.write(file_path, audio_data, self.sample_rate)
        return file_path
    
    def get_recording_duration(self) -> float:
        """Get the duration of the current/last recording in seconds."""
        if self.recording_start_time is None:
            return 0.0
        
        end_time = datetime.now() if not self.is_recording else datetime.now()
        duration = (end_time - self.recording_start_time).total_seconds()
        return duration
    
    def is_microphone_available(self) -> bool:
        """Check if a microphone is available for recording."""
        try:
            devices = sd.query_devices()
            for device in devices:
                if device['max_input_channels'] > 0:
                    return True
            return False
        except Exception:
            return False
    
    def list_audio_devices(self) -> list:
        """List all available audio input devices."""
        try:
            devices = sd.query_devices()
            input_devices = []
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': device['default_samplerate']
                    })
            return input_devices
        except Exception as e:
            print(f"Error listing audio devices: {e}")
            return []

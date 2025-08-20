import whisper
import os
from typing import Optional, Dict, Any

class SpeechToTextProcessor:
    """Speech-to-text processor using OpenAI Whisper."""
    
    def __init__(self, model_name: str = "base"):
        """Initialize the speech-to-text processor.
        
        Args:
            model_name: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            print(f"Loading Whisper model '{self.model_name}'...")
            self.model = whisper.load_model(self.model_name)
            print("✅ Whisper model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            self.model = None
    
    def transcribe_audio_file(self, audio_file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe an audio file and return the results.
        
        Args:
            audio_file_path: Path to the audio file
            language: Optional language code (e.g., 'en', 'es', 'fr')
        
        Returns:
            Dictionary containing transcription results
        """
        if not self.model:
            return {
                'success': False,
                'error': 'Whisper model not loaded',
                'text': '',
                'confidence': 0.0
            }
        
        if not os.path.exists(audio_file_path):
            return {
                'success': False,
                'error': f'Audio file not found: {audio_file_path}',
                'text': '',
                'confidence': 0.0
            }
        
        try:
            print(f"🔤 Transcribing audio file: {audio_file_path}")
            
            # Transcribe the audio
            options = {}
            if language:
                options['language'] = language
            
            result = self.model.transcribe(audio_file_path, **options)
            
            # Extract text and confidence
            text = result.get('text', '').strip()
            
            # Calculate average confidence from segments if available
            confidence = 0.0
            if 'segments' in result and result['segments']:
                confidences = []
                for segment in result['segments']:
                    if 'avg_logprob' in segment:
                        # Convert log probability to confidence (approximate)
                        conf = min(1.0, max(0.0, (segment['avg_logprob'] + 1.0)))
                        confidences.append(conf)
                
                if confidences:
                    confidence = sum(confidences) / len(confidences)
            
            print(f"✅ Transcription completed: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            return {
                'success': True,
                'text': text,
                'confidence': confidence,
                'language': result.get('language', 'unknown'),
                'full_result': result
            }
            
        except Exception as e:
            print(f"❌ Error transcribing audio: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def is_model_loaded(self) -> bool:
        """Check if the Whisper model is loaded and ready."""
        return self.model is not None
    
    def get_available_models(self) -> list:
        """Get list of available Whisper model sizes."""
        return ['tiny', 'base', 'small', 'medium', 'large']
    
    def change_model(self, model_name: str) -> bool:
        """Change to a different Whisper model.
        
        Args:
            model_name: New model name to load
            
        Returns:
            True if model changed successfully, False otherwise
        """
        if model_name not in self.get_available_models():
            print(f"❌ Invalid model name: {model_name}")
            return False
        
        self.model_name = model_name
        self.model = None
        self._load_model()
        return self.is_model_loaded()
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model."""
        model_info = {
            'tiny': 'Fastest, least accurate (~1GB VRAM)',
            'base': 'Balanced speed/accuracy (~1GB VRAM)',
            'small': 'Good accuracy (~2GB VRAM)',
            'medium': 'Better accuracy (~5GB VRAM)',
            'large': 'Best accuracy (~10GB VRAM)'
        }
        
        return {
            'current_model': self.model_name,
            'description': model_info.get(self.model_name, 'Unknown model'),
            'is_loaded': self.is_model_loaded()
        }

#!/usr/bin/env python3
"""
Simple test script for Speech-to-Text Recorder
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import sqlite3
        print("✅ sqlite3 imported")
    except ImportError as e:
        print(f"❌ Failed to import sqlite3: {e}")
        return False
    
    try:
        import tkinter
        print("✅ tkinter imported")
    except ImportError as e:
        print(f"❌ Failed to import tkinter: {e}")
        return False
    
    try:
        from database import TranscriptionDatabase
        print("✅ TranscriptionDatabase imported")
    except ImportError as e:
        print(f"❌ Failed to import TranscriptionDatabase: {e}")
        return False
    
    try:
        from audio_recorder import AudioRecorder
        print("✅ AudioRecorder imported")
    except ImportError as e:
        print(f"❌ Failed to import AudioRecorder: {e}")
        return False
    
    try:
        from keyboard_handler import GlobalKeyboardHandler
        print("✅ GlobalKeyboardHandler imported")
    except ImportError as e:
        print(f"❌ Failed to import GlobalKeyboardHandler: {e}")
        return False
    
    return True

def test_database():
    """Test database functionality."""
    print("\n🗄️ Testing database...")
    
    try:
        from database import TranscriptionDatabase
        
        # Create test database
        db = TranscriptionDatabase("test.db")
        
        # Test saving a transcription
        trans_id = db.save_transcription("Test transcription", 5.0, None, 0.95)
        print(f"✅ Saved transcription with ID: {trans_id}")
        
        # Test retrieving transcriptions
        transcriptions = db.get_all_transcriptions()
        print(f"✅ Retrieved {len(transcriptions)} transcriptions")
        
        # Test search
        results = db.search_transcriptions("Test")
        print(f"✅ Search found {len(results)} results")
        
        # Test stats
        stats = db.get_stats()
        print(f"✅ Stats: {stats}")
        
        # Clean up
        os.remove("test.db")
        print("✅ Database test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_audio_detection():
    """Test audio device detection."""
    print("\n🎤 Testing audio detection...")
    
    try:
        from audio_recorder import AudioRecorder
        
        recorder = AudioRecorder()
        
        # Test microphone availability
        mic_available = recorder.is_microphone_available()
        print(f"✅ Microphone available: {mic_available}")
        
        # List audio devices
        devices = recorder.list_audio_devices()
        print(f"✅ Found {len(devices)} audio input devices")
        
        for i, device in enumerate(devices[:3]):  # Show first 3
            print(f"   {i+1}. {device['name']} ({device['channels']} channels)")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio detection failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Speech-to-Text Recorder Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test database
    if not test_database():
        all_passed = False
    
    # Test audio detection
    if not test_audio_detection():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The application should work correctly.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run setup script: python setup.py")
        print("3. Start the application: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()

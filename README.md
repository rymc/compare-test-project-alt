# Speech-to-Text Recorder

A Python application that allows you to record speech using keyboard shortcuts and automatically transcribe it using OpenAI Whisper, storing results in a local SQLite database with a GUI for managing transcriptions.

## Features

- 🎤 **Global Keyboard Shortcuts**: Press `Cmd+R` (macOS) or `Ctrl+R` (Windows/Linux) to start/stop recording from anywhere
- 🔤 **Speech-to-Text**: Uses OpenAI Whisper for accurate offline transcription
- 💾 **Local Database**: Stores all transcriptions in a local SQLite database
- 🖥️ **GUI Interface**: Modern Tkinter-based interface for viewing and managing transcriptions
- 🔍 **Search Functionality**: Search through your transcriptions by text content
- 📊 **Statistics**: View statistics about your recordings and transcriptions
- 🎛️ **Model Selection**: Choose from different Whisper model sizes (tiny to large)
- 📤 **Export**: Export all transcriptions to text files
- 🎯 **Manual Recording**: Record manually through the GUI or use keyboard shortcuts

## Installation

### Prerequisites

- Python 3.8 or higher
- Microphone access
- macOS, Windows, or Linux

### Setup

1. **Clone or download** the project files to your local machine

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   If you encounter issues with PyAudio on macOS:
   ```bash
   brew install portaudio
   pip install pyaudio
   ```

   On Ubuntu/Debian:
   ```bash
   sudo apt-get install portaudio19-dev python3-pyaudio
   pip install pyaudio
   ```

4. **Verify installation** by running:
   ```bash
   python main.py --help
   ```

## Usage

### GUI Mode (Recommended)

Launch the application with the graphical interface:

```bash
python main.py
```

**GUI Features:**
- **Start Service**: Click to start the global keyboard listener
- **Manual Record**: Record directly through the GUI
- **Model Selection**: Choose your preferred Whisper model
- **Search**: Search through your transcriptions
- **View Full Text**: See complete transcriptions
- **Export**: Save all transcriptions to a text file
- **Delete**: Remove unwanted transcriptions

### Headless Mode

Run without GUI for background operation:

```bash
python main.py --headless
```

### Keyboard Shortcuts

- **macOS**: `Cmd + R` - Toggle recording
- **Windows/Linux**: `Ctrl + R` - Toggle recording

### Command Line Options

```bash
python main.py [options]

Options:
  --headless          Run without GUI (service mode only)
  --model MODEL       Specify Whisper model (tiny, base, small, medium, large)
  --help             Show help message
  --version          Show version information
```

### Whisper Models

Choose the model that best fits your needs:

- **tiny**: Fastest, least accurate (~1GB VRAM)
- **base**: Balanced speed/accuracy (~1GB VRAM) - **Default**
- **small**: Good accuracy (~2GB VRAM)
- **medium**: Better accuracy (~5GB VRAM)
- **large**: Best accuracy (~10GB VRAM)

Example with different model:
```bash
python main.py --model small
```

## File Structure

```
speech-to-text-recorder/
├── main.py                 # Main application entry point
├── speech_recorder.py      # Core speech recording coordinator
├── audio_recorder.py       # Audio recording functionality
├── speech_to_text.py       # Whisper integration
├── database.py             # SQLite database management
├── keyboard_handler.py     # Global keyboard shortcuts
├── ui.py                   # GUI interface
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── transcriptions.db      # SQLite database (created on first run)
└── audio_files/           # Recorded audio files (created on first run)
```

## Database

The application creates a local SQLite database (`transcriptions.db`) that stores:

- Transcription text
- Timestamp
- Recording duration
- Audio file path
- Confidence score

## Troubleshooting

### Common Issues

1. **"No microphone available"**
   - Check your microphone permissions
   - Verify your microphone is connected and working
   - On macOS, grant microphone access to Terminal/your Python app

2. **"Whisper model failed to load"**
   - Ensure you have enough disk space for the model
   - Try a smaller model (e.g., `--model tiny`)
   - Check your internet connection for initial model download

3. **"Failed to start keyboard listener"**
   - On macOS, grant Accessibility permissions to Terminal
   - Run as administrator on Windows if needed
   - Try running with `sudo` on Linux

4. **PyAudio installation issues**
   - macOS: `brew install portaudio`
   - Ubuntu: `sudo apt-get install portaudio19-dev`
   - Windows: Use pre-compiled wheel or Visual Studio Build Tools

### Permissions

#### macOS
Grant the following permissions in System Preferences > Security & Privacy:
- **Microphone** access for Terminal/Python
- **Accessibility** access for Terminal (for global shortcuts)

#### Windows
- May need to run as Administrator for global shortcuts
- Ensure microphone access is enabled for Python applications

#### Linux
- Add your user to the `audio` group: `sudo usermod -a -G audio $USER`
- For global shortcuts, you may need to run with elevated privileges

## Performance Tips

1. **Model Selection**: Start with the `base` model and upgrade if needed
2. **Storage**: Clean up old audio files periodically to save space
3. **Memory**: Close other applications when using larger Whisper models
4. **Recording Quality**: Use a quiet environment for better transcription accuracy

## Privacy & Security

- All processing is done **locally** - no data is sent to external servers
- Audio files are stored locally in the `audio_files/` directory
- Database is stored locally as `transcriptions.db`
- You can delete audio files after transcription if desired

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is open source. See the license file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech-to-text
- [pynput](https://github.com/moses-palmer/pynput) for global keyboard shortcuts
- [sounddevice](https://github.com/spatialaudio/python-sounddevice) for audio recording

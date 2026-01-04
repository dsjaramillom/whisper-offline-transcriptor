🎙️ Offline AI Audio/Video Transcriber
A high-privacy, local transcription tool built with Python and OpenAI's Whisper model. This project was developed to process sensitive recordings (such as legal hearings) completely offline, ensuring data security and high performance through hardware optimization.

🌟 Key Features

100% Offline Privacy: Processes all data locally; no data ever leaves your machine.


Hardware Acceleration: Optimized to use NVIDIA GPU (CUDA), reducing processing time from hours to minutes.


User-Friendly Interface: Built with tkinter, featuring real-time progress bars for audio extraction, model loading, and transcription.

Robust Error Handling: Includes custom logging systems and automated environment checks.

🛠️ Technical Stack

Core: Python 3.10+.


AI Model: faster-whisper (optimized version of OpenAI Whisper).


Media Engine: FFmpeg for high-speed audio extraction and manipulation.


Computation: PyTorch with CUDA 11.8 support.


🚀 Installation & Setup
Follow these steps to set up the environment on Windows:


Python & PATH: Install Python 3.10+ and ensure 'Add Python to PATH' is checked.

FFmpeg Configuration:

Download FFmpeg and extract it to C:\ffmpeg.

Add C:\ffmpeg\bin to your System Environment Variables (PATH).

GPU Acceleration (Optional):

Bash

pip install torch --index-url https://download.pytorch.org/whl/cu118
Dependencies:

Bash

pip install git+https://github.com/guillaumekln/faster-whisper tqdm
🧠 Engineering Journey: Trial & Error
This project showcases my ability to adapt advanced technology to specific needs. During development, I overcame several technical challenges:

UI Responsiveness: Implemented multi-threading to prevent the interface from freezing during heavy AI processing tasks.

Real-time Feedback: Designed a custom audio-chunking logic to provide users with an accurate progress percentage, a feature not natively available in the standard Whisper implementation.

Dependency Resolution: Identified and documented solutions for critical library errors (e.g., cublas64_12.dll) by managing specific CUDA Runtime versions.


📋 Usage
Run the script: python Whisper_Final.py.

Select your transcription level (Tiny to Medium).

Choose your file (.mp4, .mp3, .wav, etc.).

The transcript will be automatically saved as a .txt file in the source folder.
For detailed setup instructions, please refer to the [Installation Guide](INSTALLATION.md).

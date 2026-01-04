🛠️ Installation Guide - Offline Whisper Transcriptor
This guide provides step-by-step instructions to set up the environment and run the transcription tool on Windows.

1. Install Python
Download the latest version of Python (3.10 or higher) from python.org.


Important: Check the box "Add Python to PATH" during installation.

Verify the installation by opening CMD and running: python --version.

2. Install FFmpeg
Download the "Release full build" ZIP from gyan.dev.

Extract the contents and copy the folder to C:\ffmpeg.

Add FFmpeg to the system PATH:

Open Control Panel > System > Advanced System Settings > Environment Variables.

Under 'System variables', select 'Path' and click 'Edit'.

Add a new entry: C:\ffmpeg\bin.

Restart CMD and verify with: ffmpeg -version.

3. Install PyTorch with GPU Support (Optional)
If you have an NVIDIA GPU, follow these steps to enable hardware acceleration:

Uninstall any previous torch versions: pip uninstall torch -y.

Install the CUDA-enabled version: pip install torch --index-url https://download.pytorch.org/whl/cu118.

Verify compatibility by running:


python -c "import torch; print(torch.cuda.is_available())".


Expected result: True.

4. Install Dependencies
Run the following commands in your terminal:


pip install git+https://github.com/guillaumekln/faster-whisper.


pip install tqdm.


pip install playsound (optional for sound alerts).

5. Install CUDA Runtime (Only for GPU users)
If you encounter errors like cublas64_12.dll not found:

Go to NVIDIA CUDA Downloads.

Select Windows / x86_64 / Version 11.8 / exe (local).

Download, install, and restart your computer.

6. Running the Program
Save the script (e.g., Whisper_Final.py) in a fixed folder like C:\Transcriptor.

Run it using: python Whisper_Final.py.

Select your file and monitor the three progress bars: Extracting Audio, Loading Model, and Transcribing.

7. Troubleshooting

'pip' is not recognized: Python was not added to the PATH.


No module named torch: Installation failed or environment error.


cublas64_12.dll missing: Install CUDA Runtime 11.8.


CMD window closes immediately: Run the script manually from the console to see the error message: python Whisper_Final.py.

"""
Main launcher for MinBot system:
1. Runs alloy.py to transcribe and diarize audio.
2. Runs agent_minute.py to generate meeting minutes from transcript.
"""

import threading
import subprocess
import sys
import time


def run_alloy():
    """Run audio transcription and diarization module."""
    print("🎙️ Starting transcription engine...")
    subprocess.run([sys.executable, "alloy.py"])


def run_agent_minute():
    """Run meeting minute generation module."""
    print("🧠 Starting meeting summarization agent...")
    subprocess.run([sys.executable, "agent_minute.py"])


if __name__ == "__main__":
    print("🚀 Launching MinBot system...")

    # Start both modules in separate threads
    t1 = threading.Thread(target=run_alloy, daemon=True)
    t2 = threading.Thread(target=run_agent_minute, daemon=True)

    t1.start()
    t2.start()

    # Keep main thread alive to let daemon threads run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down MinBot system...")

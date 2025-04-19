import os
import json
import time
from typing import List, Dict
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openai import OpenAI

# 🔐 Load API keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# 📁 File paths
TRANSCRIPT_FILE = "transcription_output.json"
SPEAKER_MAP_FILE = "speaker_mapping.json"
MINUTES_FILE = "live_meeting_minutes.txt"

# 🧠 State memory of discussed items
discussed_topics: List[Dict[str, str]] = []


def load_transcript() -> List[Dict[str, str]]:
    """Loads the transcript JSON file."""
    try:
        with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load transcript: {e}")
        return []


def load_speaker_mapping() -> Dict[str, str]:
    """Loads the speaker mapping JSON file."""
    try:
        with open(SPEAKER_MAP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load speaker mapping: {e}")
        return {}


def format_transcript(raw: List[Dict], mapping: Dict[str, str]) -> str:
    """Replaces speaker IDs with names and formats lines."""
    for entry in raw:
        speaker_key = entry["speaker"].replace("_", "")
        entry["speaker"] = mapping.get(speaker_key, speaker_key)
    return "\n".join(f"{entry['speaker']}: {entry['text']}" for entry in raw)


def generate_minutes(transcript_text: str) -> str:
    """
    Generates structured meeting minutes from a full transcript string.

    This tool takes the cleaned and speaker-resolved transcript and sends it to OpenAI’s API
    to produce structured minutes with summaries, action items, and key decisions.

    Returns:
        str: A Markdown-formatted meeting summary, suitable for documentation or sharing.
    """
    SYSTEM_PROMPT = """
    You are a professional meeting assistant.
    Your job is to read the full transcript of a meeting and generate clear, structured meeting minutes.
    The minutes should include:
    - A brief summary of what the meeting was about
    - Action items (who will do what)
    - Key decisions that were made
    - Any follow-up points or deadlines
    - A bullet-point section for the topics discussed
    Format the output in Markdown.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript_text},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating minutes: {e}"


def update_minutes(minutes: str):
    """Writes the minutes to a file."""
    with open(MINUTES_FILE, "w", encoding="utf-8") as f:
        f.write(minutes)
    print("✅ Minutes updated.")


def summarize_and_store_topics():
    """Generates minutes, stores them in memory, and writes to disk."""
    transcript = load_transcript()
    speaker_map = load_speaker_mapping()
    if not transcript:
        return

    transcript_text = format_transcript(transcript, speaker_map)
    minutes = generate_minutes(transcript_text)
    update_minutes(minutes)

    # Store summary in memory for future manipulation
    discussed_topics.append(
        {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "text": transcript_text,
            "summary": minutes,
        }
    )


class TranscriptWatcher(FileSystemEventHandler):
    """Watches the transcript file and re-summarizes on changes."""

    def on_modified(self, event):
        if event.src_path.endswith(TRANSCRIPT_FILE):
            print("📄 Transcript updated. Re-summarizing...")
            summarize_and_store_topics()


def start_watchdog():
    """Starts monitoring the transcript file for updates."""
    print("📡 Watching for transcript updates...")
    event_handler = TranscriptWatcher()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def remove_last_topic_from_memory():
    """Removes the most recently stored topic from memory."""
    if not discussed_topics:
        print("⚠️ No topics to remove.")
        return
    discussed_topics.pop()
    print("🗑️ Last topic removed from memory.")


# ==========================
# ▶️ Entry Point
# ==========================
if __name__ == "__main__":
    summarize_and_store_topics()  # Initial run
    start_watchdog()

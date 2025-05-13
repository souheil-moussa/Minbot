import os
import json
import time
from typing import List, Dict
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent
from langchain.tools import tool

# Load API keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# File paths
TRANSCRIPT_FILE = "transcription_output.json"
SPEAKER_MAP_FILE = "speaker_mapping.json"
MINUTES_FILE = "live_meeting_minutes.txt"

# State memory of discussed items
discussed_topics: List[Dict[str, str]] = []


# =============================
# 🔧 Tool Definition
# =============================
@tool
def generate_meeting_minutes(transcript_text: str) -> str:
    """
    Reads a full transcript and generates structured meeting minutes in Markdown format.
    Includes: summary, action items, key decisions, and follow-up points.
    """
    prompt = f"""
You are a professional meeting assistant.
Read the following meeting transcript and generate clear, structured meeting minutes.
Include:
- A brief summary
- Action items (who will do what)
- Key decisions made
- Follow-up points or deadlines
- Bullet-pointed discussion topics
Format the output in Markdown.

Transcript:
{transcript_text}
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    result = llm.invoke(prompt)
    return result.content


# =============================
# 📄 Data Functions
# =============================
def load_transcript() -> List[Dict[str, str]]:
    try:
        with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load transcript: {e}")
        return []


def load_speaker_mapping() -> Dict[str, str]:
    try:
        with open(SPEAKER_MAP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load speaker mapping: {e}")
        return {}


def format_transcript(raw: List[Dict], mapping: Dict[str, str]) -> str:
    for entry in raw:
        speaker_key = entry["speaker"].replace("_", "")
        entry["speaker"] = mapping.get(speaker_key, speaker_key)
    return "\n".join(f"{entry['speaker']}: {entry['text']}" for entry in raw)


# =============================
# 🧠 Agent Setup
# =============================
llm = ChatOpenAI(model="gpt-4o", temperature=0)
agent = create_react_agent(llm, tools=[generate_meeting_minutes])
messages = []  # Conversation history


def summarize_and_store_topics():
    transcript = load_transcript()
    speaker_map = load_speaker_mapping()
    if not transcript:
        return

    transcript_text = format_transcript(transcript, speaker_map)

    # Add user request
    messages.append(
        HumanMessage(content=f"Summarize the following meeting:\n{transcript_text}")
    )

    # Agent responds (may call a tool)
    new_msgs = agent.invoke({"messages": messages})["messages"]
    messages.extend(new_msgs)

    # Handle and log messages
    for msg in new_msgs:
        if isinstance(msg, AIMessage) and not msg.content:
            tool_name = msg.tool_calls[0]["name"]
            tool_args = msg.tool_calls[0]["args"]
            print(f"🧠 Agent called tool: {tool_name} with args: {tool_args}")
        elif isinstance(msg, ToolMessage):
            print(f"🔧 Tool result:\n{msg.content}")
            update_minutes(msg.content)
            discussed_topics.append(
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "text": transcript_text,
                    "summary": msg.content,
                }
            )
        elif isinstance(msg, AIMessage) and msg.content:
            print(f"💬 AI response:\n{msg.content}")


def update_minutes(minutes: str):
    with open(MINUTES_FILE, "w", encoding="utf-8") as f:
        f.write(minutes)
    print("✅ Minutes updated.")


class TranscriptWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(TRANSCRIPT_FILE):
            print("📄 Transcript updated. Re-summarizing...")
            summarize_and_store_topics()


def start_watchdog():
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
    if not discussed_topics:
        print("⚠️ No topics to remove.")
        return
    discussed_topics.pop()
    print("🗑️ Last topic removed from memory.")


if __name__ == "__main__":
    summarize_and_store_topics()
    start_watchdog()

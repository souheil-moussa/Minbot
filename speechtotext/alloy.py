import os
import gc
import json
import time
import whisperx
import alloy_id  # Import the new speaker identification module
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

token = os.getenv("WHISPERX_TOKEN")

# Configuration
device = "cuda"
audio_dir = "C:\\Users\\Emmanuel\\Desktop\\Alloy\\audiosegments"
json_output = "transcription_output.json"
speaker_mapping_output = "speaker_mapping.json"  # Stores speaker labels
speaker_fixed_mapping_file = "speaker_fixed_mapping.json"  # Ensures speaker consistency
batch_size = 16  # Lower for better diarization accuracy
compute_type = "float16"
model_size = "medium"  # Change to "large-v2" for better accuracy

# Load WhisperX models once
model = whisperx.load_model(model_size, device, compute_type=compute_type)
diarize_model = whisperx.DiarizationPipeline(use_auth_token=token, device=device)

# Queue to process new files
audio_queue = deque()


# Load JSON files safely
def load_json(file_path, default_value):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️ Warning: {file_path} is corrupted. Resetting file.")
                return default_value
    return default_value


transcription_data = load_json(json_output, [])
speaker_fixed_mapping = load_json(speaker_fixed_mapping_file, {})


# File watcher to detect new audio files
class AudioHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".mp3"):
            print(f"🎤 New file detected: {event.src_path}")
            audio_queue.append(event.src_path)


# Start watchdog observer
observer = Observer()
observer.schedule(AudioHandler(), path=audio_dir, recursive=False)
observer.start()

print("🔍 Watching for new audio segments...")

# Process audio queue in real-time
try:
    while True:
        if audio_queue:
            audio_file = audio_queue.popleft()
            print(f"🎙️ Processing: {audio_file}")

            # Load and transcribe audio
            audio = whisperx.load_audio(audio_file)
            result = model.transcribe(
                audio, batch_size=batch_size, language="en", task="translate"
            )

            # result = model.transcribe(audio, batch_size=batch_size)

            # Align timestamps
            # model_a, metadata = whisperx.load_align_model(
            #     language_code=result["language"], device=device
            # )
            model_a, metadata = whisperx.load_align_model(
                language_code="en", device=device
            )

            result = whisperx.align(
                result["segments"],
                model_a,
                metadata,
                audio,
                device,
                return_char_alignments=False,
            )

            # Run speaker diarization
            diarize_segments = diarize_model(audio)
            result = whisperx.assign_word_speakers(diarize_segments, result)

            # Extract results
            for segment in result["segments"]:
                new_entry = {
                    "start": segment["start"],
                    "end": segment["end"],
                    "speaker": segment.get("speaker", "unknown"),
                    "text": segment["text"],
                }
                transcription_data.append(new_entry)

            # Save transcription JSON
            with open(json_output, "w", encoding="utf-8") as f:
                json.dump(transcription_data, f, indent=4, ensure_ascii=False)

            print(f"✅ Transcribed & saved: {audio_file}")

            # Call speaker identification module
            new_speaker_labels = alloy_id.process_new_speakers(
                json_output, audio_file, speaker_fixed_mapping
            )

            # Save updated fixed mapping
            with open(speaker_fixed_mapping_file, "w", encoding="utf-8") as f:
                json.dump(speaker_fixed_mapping, f, indent=4, ensure_ascii=False)

            # Save speaker mappings to separate file
            with open(speaker_mapping_output, "w", encoding="utf-8") as f:
                json.dump(new_speaker_labels, f, indent=4, ensure_ascii=False)

            print(f"🎭 Updated speaker mapping saved to: {speaker_mapping_output}")

            # Free memory
            gc.collect()

        time.sleep(0.2)  # Fast polling

except KeyboardInterrupt:
    print("\n🛑 Stopping observer...")
    observer.stop()

observer.join()

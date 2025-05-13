import os
import json
import glob
from pydub import AudioSegment
from pyannote.audio import Model, Inference
from scipy.spatial.distance import pdist
from dotenv import load_dotenv

# Load .env file for Pyannote authentication
load_dotenv()
pyannote_token = os.getenv("PYANNOTE_TOKEN")

# Configuration
speaker_samples_dir = "speaker_samples"
audioprints_dir = "audioprints"
speaker_mapping_file = "speaker_mapping.json"

# Load Pyannote model
speaker_model = Model.from_pretrained(
    "pyannote/embedding", use_auth_token=pyannote_token
)


# Function to get embeddings
def get_embedding(file_path):
    inference = Inference(speaker_model, window="whole")
    return inference(file_path)


# Load known speaker database
def load_speaker_database(audioprints_dir):
    speaker_database = {}
    for file_path in glob.glob(os.path.join(audioprints_dir, "*.mp3")):
        speaker_name = os.path.splitext(os.path.basename(file_path))[0]
        speaker_database[speaker_name] = get_embedding(file_path)
    return speaker_database


# Identify speakers while ensuring fixed assignments
def identify_speaker(unknown_embedding, speaker_database, speaker_id, fixed_mapping):
    if speaker_id in fixed_mapping:
        return fixed_mapping[speaker_id]  # Use previously assigned speaker

    min_distance = float("inf")
    closest_speaker = "unknown"

    for speaker_name, reference_embedding in speaker_database.items():
        distance = pdist([unknown_embedding, reference_embedding], metric="cosine")[0]
        if distance < min_distance and speaker_name not in fixed_mapping.values():
            min_distance = distance
            closest_speaker = speaker_name

    fixed_mapping[speaker_id] = closest_speaker  # Save mapping
    return closest_speaker


# Merge all segments for each speaker
def merge_speaker_segments(transcription_data, audio_file):
    if not os.path.exists(speaker_samples_dir):
        os.makedirs(speaker_samples_dir)

    audio = AudioSegment.from_mp3(audio_file)
    speaker_audio_segments = {}

    for segment in transcription_data:
        speaker_id = segment["speaker"]
        speaker_id = speaker_id.replace("SPEAKER_", "speaker")

        start_ms = int(segment["start"] * 1000)
        end_ms = int(segment["end"] * 1000)

        if speaker_id not in speaker_audio_segments:
            speaker_audio_segments[speaker_id] = AudioSegment.silent(duration=500)
        speaker_audio_segments[speaker_id] += audio[
            start_ms:end_ms
        ] + AudioSegment.silent(duration=500)

    merged_speaker_files = {}
    for speaker_id, merged_audio in speaker_audio_segments.items():
        speaker_sample_file = os.path.join(speaker_samples_dir, f"{speaker_id}.mp3")
        merged_audio.export(speaker_sample_file, format="mp3")
        merged_speaker_files[speaker_id] = speaker_sample_file

    return merged_speaker_files


# Process new speakers while keeping mapping fixed
def process_new_speakers(json_file, audio_file, speaker_fixed_mapping):
    with open(json_file, "r", encoding="utf-8") as f:
        transcription_data = json.load(f)

    speaker_database = load_speaker_database(audioprints_dir)
    merged_speaker_files = merge_speaker_segments(transcription_data, audio_file)

    speaker_labels = {}

    for speaker_id, speaker_sample_file in merged_speaker_files.items():
        speaker_embedding = get_embedding(speaker_sample_file)
        identified_speaker = identify_speaker(
            speaker_embedding, speaker_database, speaker_id, speaker_fixed_mapping
        )
        speaker_labels[speaker_id] = identified_speaker

    return speaker_labels

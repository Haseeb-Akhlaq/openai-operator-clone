# src/voice_assistant/config.py
import json
import os

import pyaudio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
PREFIX_PADDING_MS = 300
SILENCE_THRESHOLD = 0.5
SILENCE_DURATION_MS = 400
RUN_TIME_TABLE_LOG_JSON = "runtime_time_table.jsonl"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000


SESSION_INSTRUCTIONS = "You are an AI voice assistant with access to a web browser. Your role is to follow user commands by utilizing the browser_use tool. You have full permissions to execute any browsing-related tasks as instructed. If a command is unclear, ask follow-up questions for clarification. When using the browser_use tool, provide a detailed and precise description to ensure accurate results."

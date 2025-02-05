# src/voice_assistant/microphone.py
import logging
import queue
from typing import Optional

import pyaudio

from config import CHANNELS, CHUNK, FORMAT, RATE

logger = logging.getLogger(__name__)


class AsyncMicrophone:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self.callback,
        )
        self.queue = queue.Queue()
        self.is_recording = False
        self.is_receiving = False
        logger.info("AsyncMicrophone initialized")

    def callback(self, in_data, frame_count, time_info, status):
        if self.is_recording and not self.is_receiving:
            self.queue.put(in_data)
        return (None, pyaudio.paContinue)

    def start_recording(self):
        self.is_recording = True
        logger.info("Started recording")

    def stop_recording(self):
        self.is_recording = False
        logger.info("Stopped recording")

    def start_receiving(self):
        self.is_receiving = True
        self.is_recording = False
        logger.info("Started receiving assistant response")

    def stop_receiving(self):
        self.is_receiving = False
        logger.info("Stopped receiving assistant response")

    def get_audio_data(self) -> Optional[bytes]:
        data = b""
        while not self.queue.empty():
            data += self.queue.get()
        return data if data else None

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        logger.info("AsyncMicrophone closed")

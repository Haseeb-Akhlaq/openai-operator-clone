# src/voice_assistant/main.py
import asyncio
import json
import logging
import os

import pygame
import websockets
from websockets.exceptions import ConnectionClosedError

from config import (
    PREFIX_PADDING_MS,
    SESSION_INSTRUCTIONS,
    SILENCE_DURATION_MS,
    SILENCE_THRESHOLD,
)
from assistant_modules.microphone import AsyncMicrophone
from assistant_modules.utils import base64_encode_audio
from assistant_modules.log_utils import log_ws_event
from assistant_modules.visual_interface import (
    VisualInterface,
    run_visual_interface,
)
from assistant_modules.websocket_handler import process_ws_messages

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


async def realtime_api():
    while True:
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("Please set the OPENAI_API_KEY in your .env file.")
                return

            exit_event = asyncio.Event()

            url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "OpenAI-Beta": "realtime=v1",
            }

            mic = AsyncMicrophone()
            visual_interface = VisualInterface()

            async with websockets.connect(url, extra_headers=headers) as websocket:
                logger.info("Connected to the server.")
                # Initialize the session with voice capabilities and tools
                session_update = {
                    "type": "session.update",
                    "session": {
                        "modalities": ["text", "audio"],
                        "instructions": SESSION_INSTRUCTIONS,
                        "voice": "shimmer",
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16",
                        "turn_detection": {
                            "type": "server_vad",
                            "threshold": SILENCE_THRESHOLD,
                            "prefix_padding_ms": PREFIX_PADDING_MS,
                            "silence_duration_ms": SILENCE_DURATION_MS,
                        },
                        "tools": [
                            {
                                "type": "function",
                                "name": "use_browser",
                                "description": "Runs a browser-based task using an AI agent",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "task": {
                                            "type": "string",
                                            "description": "The task description for the AI agent to execute",
                                        }
                                    },
                                    "required": ["task"],
                                },
                            }
                        ],
                    },
                }
                log_ws_event("outgoing", session_update)
                await websocket.send(json.dumps(session_update))

                ws_task = asyncio.create_task(
                    process_ws_messages(websocket, mic, visual_interface)
                )
                visual_task = asyncio.create_task(
                    run_visual_interface(visual_interface)
                )

                logger.info(
                    "Conversation started. Speak freely, and the assistant will respond."
                )
                mic.start_recording()
                logger.info("Recording started. Listening for speech...")

                try:
                    while not exit_event.is_set():
                        await asyncio.sleep(0.01)  # Small delay to reduce CPU usage
                        if not mic.is_receiving:
                            audio_data = mic.get_audio_data()
                            if audio_data:
                                base64_audio = base64_encode_audio(audio_data)
                                if base64_audio:
                                    audio_event = {
                                        "type": "input_audio_buffer.append",
                                        "audio": base64_audio,
                                    }
                                    log_ws_event("outgoing", audio_event)
                                    await websocket.send(json.dumps(audio_event))
                                    # Update energy for visualization
                                    visual_interface.process_audio_data(audio_data)
                                else:
                                    logger.debug("No audio data to send")
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt received. Closing the connection.")
                except Exception as e:
                    logger.exception(
                        f"An unexpected error occurred in the main loop: {e}"
                    )
                finally:
                    exit_event.set()
                    mic.stop_recording()
                    mic.close()
                    await websocket.close()
                    visual_interface.set_active(False)

                # Wait for the WebSocket processing task to complete
                try:
                    await ws_task
                    await visual_task
                except Exception as e:
                    logging.exception(f"Error in WebSocket processing task: {e}")

            # If execution reaches here without exceptions, exit the loop
            break
        except ConnectionClosedError as e:
            if "keepalive ping timeout" in str(e):
                logging.warning(
                    "WebSocket connection lost due to keepalive ping timeout. Reconnecting..."
                )
                await asyncio.sleep(1)  # Wait before reconnecting
                continue  # Retry the connection
            logging.exception("WebSocket connection closed unexpectedly.")
            break  # Exit the loop on other connection errors
        except Exception as e:
            logging.exception(f"An unexpected error occurred: {e}")
            break  # Exit the loop on unexpected exceptions
        finally:
            if "mic" in locals():
                mic.stop_recording()
                mic.close()
            if "websocket" in locals():
                await websocket.close()
            pygame.quit()


async def main_async():
    await realtime_api()


def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    print("Press Ctrl+C to exit the program.")
    main()

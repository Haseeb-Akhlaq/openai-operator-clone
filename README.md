# OpenAI Operator Clone with Real-time Voice Interaction

This project is a clone of OpenAI’s browser agent **Operator**. It utilizes the open-source library **browser_use** to enable voice-controlled web browsing. The project is integrated with OpenAI’s real-time API, allowing seamless interaction with the browser using voice commands.

To ensure proper functionality, **browser_use** requires a multi-modal LLM. For this, I am using **Google Gemini 2.0 Flash**, which is a cost-effective alternative to GPT-4o.

## Overview Diagram

*(Add your overview diagram here)*

## Features

- **Real-time voice interaction** using WebSockets.
- **Integration with OpenAI's GPT-4** for natural language understanding.
- **Automated web browsing** via the `browser_use` tool.
- **Visual interface** to display the assistant's state.
- **Logging** of runtime and WebSocket events.

## Setup

### Prerequisites
- Ensure you have **Python 3.11 or later** (browser_use does not work with older versions).
- Install **Playwright** if any errors occur (`playwright install`).

### Installation Steps
1. **Clone the repository** to your local machine:
   ```sh
   git clone https://github.com/your-repo/openai-operator-clone.git
   cd openai-operator-clone
   ```
2. **Create a virtual environment:**
   ```sh
   python3 -m venv venv
   ```
3. **Activate the virtual environment:**
   - **Linux/macOS:**
     ```sh
     source venv/bin/activate
     ```
   - **Windows:**
     ```sh
     venv\Scripts\activate
     ```
4. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
5. **Set up environment variables:**
   - Create a `.env` file based on `.env.sample`.
6. **Run the application:**
   ```sh
   python main.py
   ```

## Project Structure

```
voice-assistant/
├── assistant_modules/
│   ├── audio.py
│   ├── log_utils.py
│   ├── microphone.py
│   ├── utils.py
│   ├── visual_interface.py
│   └── websocket_handler.py
├── browser_tool/
│   └── agent.py
├── __pycache__/
├── .env
├── .env.sample
├── .gitignore
├── config.py
├── main.py
├── requirements.txt
├── runtime_time_table.jsonl
└── venv/
```

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

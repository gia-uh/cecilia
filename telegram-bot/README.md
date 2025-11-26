# Telegram Bot with LMStudio Integration

A cross-platform Python script that polls a Telegram bot for messages and forwards them to a local LMStudio model for AI-generated responses.

## Features

- ✅ Polls Telegram bot every 2 seconds for new messages
- ✅ Forwards messages to local LMStudio model
- ✅ Sends AI responses back to users
- ✅ Cross-platform (macOS and Windows)
- ✅ Environment-based configuration
- ✅ Optional RAG with BeaverDB vectors (LMStudio embeddings) seeded from `data/cuban_data_v2.json`
- ✅ Stores the last 5 messages per chat using BeaverDB for contextual replies
- ✅ Comprehensive error handling and logging

## Prerequisites

1. **Python 3.7+** installed on your system
2. **LMStudio** installed and running with:
   - A model loaded
   - Local server enabled (default port: 1234)
3. **Telegram Bot Token** from [@BotFather](https://t.me/botfather)

## Installation

1. **Clone or download this repository**

2. **Set up Python environment (choose one method):**

   **Option A: Using Conda (Recommended)**
   
   ```bash
   conda env create -f environment.yaml
   conda activate telegram-lmstudio-bot
   ```

   **Option B: Using pip**
   
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Telegram bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   LMSTUDIO_API_URL=http://localhost:1234/v1
   LMSTUDIO_MODEL=cecilia-2b-instruct-v1
   BEAVER_DB_PATH=beaver.db
   EMBEDDING_MODEL=text-embedding-nomic-embed-text-v1.5
   RAG_BEAVER_DB_PATH=rag.db
   RAG_COLLECTION_NAME=cuban_rag
   RAG_TOP_K=3
   RAG_MIN_SCORE=0.6
   RAG_BATCH_SIZE=32
   ENABLE_RAG=true
   RAG_DATA_PATH=data/cuban_data_v2.json
   ```

## RAG Setup (BeaverDB + LMStudio)

1) Ensure LMStudio is running an embedding-capable model (`EMBEDDING_MODEL`), and the chat model (`LMSTUDIO_MODEL`) is loaded.
2) Seed the vector collection with the Cuban data:
   ```bash
   python seed_rag.py
   ```
   This reads `RAG_DATA_PATH` (default `data/cuban_data_v2.json`), calls LMStudio `/embeddings`, and indexes into the BeaverDB collection `RAG_COLLECTION_NAME` stored in `RAG_BEAVER_DB_PATH` (separate from chat/messages DB).
3) Run the bot as usual:
   ```bash
   python bot.py
   ```
   When `ENABLE_RAG=true`, user queries fetch the top `RAG_TOP_K` vectors and prepend them as system context for better answers.

## Getting a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts to name your bot
4. Copy the bot token provided by BotFather
5. Paste it into your `.env` file

## Setting Up LMStudio

1. Open LMStudio
2. Download and load a model (e.g., Llama, Mistral, etc.)
3. Go to the **Local Server** tab
4. Click **Start Server**
5. Ensure the server is running on port 1234 (default)

## Usage

Run the bot:

```bash
python bot.py
```

You should see output like:
```
2025-11-25 13:18:00 - INFO - Starting Telegram Bot with LMStudio integration...
2025-11-25 13:18:00 - INFO - Configuration validated successfully
2025-11-25 13:18:00 - INFO - LMStudio connection verified
2025-11-25 13:18:00 - INFO - Bot is running. Polling every 2 seconds...
2025-11-25 13:18:00 - INFO - Press Ctrl+C to stop
```

Now send a message to your bot on Telegram, and it will respond with AI-generated content!

## Stopping the Bot

Press `Ctrl+C` to gracefully stop the bot.

## Troubleshooting

### "TELEGRAM_BOT_TOKEN not found in .env file"
- Make sure you created a `.env` file (not `.env.example`)
- Verify your bot token is correctly set in the `.env` file

### "Unable to connect to LMStudio"
- Ensure LMStudio is running
- Verify a model is loaded in LMStudio
- Check that the local server is started in LMStudio
- Confirm the port matches (default: 1234)

### Bot doesn't respond to messages
- Check the console logs for errors
- Verify your bot token is correct
- Ensure LMStudio server is running and responding
- Try sending `/start` to your bot first

### Windows-specific issues
- Use `python` instead of `python3` if needed
- Ensure Python is added to your PATH
- Use Command Prompt or PowerShell

## How It Works

1. The script polls Telegram's `getUpdates` API every 2 seconds
2. When a new message is received, it's logged and forwarded to LMStudio
3. Up to the last 5 chat messages for that user are loaded from BeaverDB and sent as context
4. LMStudio processes the message using the loaded model
5. The AI response is sent back to the user via Telegram's `sendMessage` API
6. The script tracks the last update ID to avoid processing duplicates

## Configuration Options

Edit `.env` to customize:

- `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather (required)
- `LMSTUDIO_API_URL`: LMStudio API endpoint (default: `http://localhost:1234/v1`)
- `LMSTUDIO_MODEL`: Model ID currently loaded in LMStudio (default: `cecilia-2b-instruct-v1`)
- `BEAVER_DB_PATH`: Location of the BeaverDB file for chat history (default: `beaver.db`)
- `EMBEDDING_MODEL`: Model used for embeddings via LMStudio `/embeddings` (default: `text-embedding-nomic-embed-text-v1.5`)
- `RAG_BEAVER_DB_PATH`: Location of the BeaverDB file for RAG vectors (separate from chat/messages)
- `RAG_COLLECTION_NAME`: BeaverDB collection name for vector search
- `RAG_TOP_K`: Number of neighbors to fetch for context
- `RAG_MIN_SCORE`: Minimum similarity score to accept a retrieved doc
- `RAG_BATCH_SIZE`: Batch size for embedding requests when seeding
- `ENABLE_RAG`: Toggle to enable/disable retrieval-augmented replies
- `RAG_DATA_PATH`: Path to the JSON data for seeding the RAG collection

## License

MIT License - feel free to use and modify as needed.

#!/usr/bin/env python3
"""
Telegram Bot with LMStudio Integration
Polls Telegram bot for messages and forwards them to local LMStudio model.
"""

import os
import sys
import time
import logging
import requests
import atexit
import uuid
from dotenv import load_dotenv
from beaver import BeaverDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
LMSTUDIO_API_URL = os.getenv('LMSTUDIO_API_URL', 'http://localhost:1234/v1')
LMSTUDIO_MODEL = os.getenv('LMSTUDIO_MODEL', 'cecilia-2b-instruct-v1')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-nomic-embed-text-v1.5')
RAG_COLLECTION_NAME = os.getenv('RAG_COLLECTION_NAME', 'cuban_rag')
RAG_TOP_K = int(os.getenv('RAG_TOP_K', '3'))
ENABLE_RAG = os.getenv('ENABLE_RAG', 'true').lower() == 'true'
RAG_MIN_SCORE = float(os.getenv('RAG_MIN_SCORE', '0.6'))
BEAVER_DB_PATH = os.getenv('BEAVER_DB_PATH', 'beaver.db')
RAG_BEAVER_DB_PATH = os.getenv('RAG_BEAVER_DB_PATH', 'rag.db')
MAX_HISTORY_MESSAGES = 6
POLL_INTERVAL = 2  # seconds

# Telegram API endpoints
TELEGRAM_API_BASE = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'
GET_UPDATES_URL = f'{TELEGRAM_API_BASE}/getUpdates'
SEND_MESSAGE_URL = f'{TELEGRAM_API_BASE}/sendMessage'

# Persistent chat history (per chat_id) using BeaverDB
db_dir = os.path.dirname(os.path.abspath(BEAVER_DB_PATH))
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

beaver_db = BeaverDB(BEAVER_DB_PATH)
atexit.register(beaver_db.close)

# Separate RAG vector store to isolate from chat/message DB
rag_db_dir = os.path.dirname(os.path.abspath(RAG_BEAVER_DB_PATH))
if rag_db_dir and not os.path.exists(rag_db_dir):
    os.makedirs(rag_db_dir, exist_ok=True)
rag_db = BeaverDB(RAG_BEAVER_DB_PATH)
atexit.register(rag_db.close)
rag_collection = rag_db.collection(RAG_COLLECTION_NAME)


def _user_key(user_id):
    """Normalize user_id to string for consistent key usage."""
    return str(user_id)


def _chat_key(chat_id):
    """Normalize chat_id to string for consistent key usage."""
    return str(chat_id)


def get_embedding(text):
    """Get embedding vector from LMStudio /embeddings endpoint."""
    try:
        url = f"{LMSTUDIO_API_URL}/embeddings"
        payload = {
            "model": EMBEDDING_MODEL,
            "input": text,
        }
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        emb = data.get('data', [{}])[0].get('embedding')
        if not emb:
            logger.error(f"Unexpected embedding response format: {data}")
            return None
        # L2 normalize to turn dot product into cosine similarity
        norm = sum((x * x for x in emb)) ** 0.5
        if norm == 0:
            logger.error("Zero-norm embedding received")
            return None
        return [x / norm for x in emb]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching embedding: {e}")
        return None


def _history_list(user_id):
    """Get the BeaverDB list that stores short-term chat history for a user."""
    return beaver_db.list(f'user_{_user_key(user_id)}_history')


def get_recent_history(user_id):
    """Return the last MAX_HISTORY_MESSAGES for this user."""
    history = list(_history_list(user_id))
    return history[-MAX_HISTORY_MESSAGES:]


def append_to_history(user_id, role, content, msg_id=None):
    """Append a message with a UUID and trim history to the configured limit."""
    history_list = _history_list(user_id)
    msg_id = msg_id or str(uuid.uuid4())
    history_list.push({'id': msg_id, 'role': role, 'content': content})
    while len(history_list) > MAX_HISTORY_MESSAGES:
        # Remove oldest entry; Beaver list pop() has no index support
        del history_list[0]
    return msg_id


def clear_history(user_id):
    """Clear stored chat history for a user (short-term only)."""
    history_list = _history_list(user_id)
    while len(history_list):
        del history_list[0]


def global_messages_list():
    """Persistent message archive across all chats (not cleared on /clear)."""
    return beaver_db.list('global_messages')


def global_messages_map():
    """Dictionary keyed by message id for quick lookup."""
    return beaver_db.dict('global_messages_map')


def log_global_message(chat_id, user_id, username, role, content, msg_id):
    """Store full message log without trimming."""
    msg_record = {
        'id': msg_id,
        'chat_id': chat_id,
        'user_id': user_id,
        'username': username,
        'role': role,
        'content': content,
        'timestamp': time.time()
    }
    messages = global_messages_list()
    messages.push(msg_record)
    msg_map = global_messages_map()
    msg_map[msg_id] = msg_record


def feedback_dict(chat_id):
    """Dictionary where feedback keyed by message UUID is stored (per chat)."""
    return beaver_db.dict(f'chat_{_chat_key(chat_id)}_feedback')


def global_feedback_dict():
    """Global feedback keyed by message UUID."""
    return beaver_db.dict('global_feedback')


def build_rag_context(user_text):
    """Retrieve relevant docs for the user query and return system message + sources."""
    if not ENABLE_RAG:
        return None, []

    embedding = get_embedding(user_text)
    if embedding is None:
        return None, []

    try:
        results = rag_collection.search(embedding, top_k=RAG_TOP_K)
    except Exception as e:
        logger.error(f"Error during vector search: {e}")
        return None, []

    if not results:
        return None, []

    contexts = []
    sources = []
    for doc, score in results:
        if score < RAG_MIN_SCORE:
            continue
        body = getattr(doc, 'body', None)
        if not body and hasattr(doc, 'metadata'):
            body = doc.metadata.get('text')
        if not body:
            body = str(doc)
        contexts.append(f"- {body}")
        sources.append({'id': doc.id, 'score': score})
        if len(contexts) >= RAG_TOP_K:
            break

    logger.info(
        "RAG retrieved %d docs (min_score=%.2f): %s",
        len(sources),
        RAG_MIN_SCORE,
        "; ".join(f"{s['id']} (score={s['score']:.4f})" for s in sources),
    )

    system_content = (
        "Usa exclusivamente el siguiente contexto cubano para responder con precisión. "
        "Si el contexto no ayuda, indica que no tienes datos suficientes.\n\n"
        + "\n".join(contexts)
    )
    return {'role': 'system', 'content': system_content}, sources


def validate_config():
    """Validate required configuration."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in .env file")
        sys.exit(1)
    logger.info("Configuration validated successfully")


def get_telegram_updates(offset=None):
    """
    Poll Telegram for new updates.
    
    Args:
        offset: Update ID to start from (for avoiding duplicates)
    
    Returns:
        List of updates or None on error
    """
    try:
        params = {
            'timeout': POLL_INTERVAL,
            'offset': offset
        }
        response = requests.get(GET_UPDATES_URL, params=params, timeout=POLL_INTERVAL + 5)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('ok'):
            logger.error(f"Telegram API error: {data}")
            return None
        
        return data.get('result', [])
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Telegram updates: {e}")
        return None


def send_telegram_message(chat_id, text, reply_markup=None):
    """
    Send a message to a Telegram chat.
    
    Args:
        chat_id: Telegram chat ID
        text: Message text to send
        reply_markup: Optional Telegram reply markup (e.g., inline keyboard)
    
    Returns:
        True on success, False on error
    """
    try:
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        if reply_markup is not None:
            payload['reply_markup'] = reply_markup
        response = requests.post(SEND_MESSAGE_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('ok'):
            logger.error(f"Failed to send message: {data}")
            return False
        
        logger.info(f"Message sent to chat {chat_id}")
        return True
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Telegram message: {e}")
        return False


def answer_callback_query(callback_id, text=None):
    """Acknowledge Telegram callback queries to remove the loading state."""
    try:
        payload = {'callback_query_id': callback_id}
        if text:
            payload['text'] = text
        response = requests.post(f'{TELEGRAM_API_BASE}/answerCallbackQuery', json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error answering callback query: {e}")


def get_lmstudio_response(messages):
    """
    Get response from LMStudio model using the provided chat messages.
    
    Args:
        messages: List of message dicts with roles and content
    
    Returns:
        AI response text or error message
    """
    try:
        url = f'{LMSTUDIO_API_URL}/chat/completions'
        payload = {
            'model': LMSTUDIO_MODEL,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': -1,
            'stream': False
        }
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # Extract the response text
        if 'choices' in data and len(data['choices']) > 0:
            ai_response = data['choices'][0]['message']['content']
            logger.info(f"LMStudio response received ({len(ai_response)} chars) with {len(messages)} context messages")
            return ai_response
        else:
            logger.error(f"Unexpected LMStudio response format: {data}")
            return "Sorry, I couldn't generate a response."
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with LMStudio: {e}")
        return f"Error: Unable to connect to LMStudio. Please ensure it's running on {LMSTUDIO_API_URL}"


def process_callback(update):
    """Handle callback queries (e.g., feedback buttons)."""
    callback = update.get('callback_query', {})
    data = callback.get('data', '')
    callback_id = callback.get('id')

    # Acknowledge callbacks even if unrecognized to clear Telegram loading state
    if not data or not data.startswith('fb|'):
        if callback_id:
            answer_callback_query(callback_id)
        return

    parts = data.split('|')
    if len(parts) != 4:
        if callback_id:
            answer_callback_query(callback_id, "Feedback inválido")
        return

    _, chat_id_str, msg_id, value = parts
    chat_id = chat_id_str
    user_id = callback.get('from', {}).get('id')
    username = callback.get('from', {}).get('username')

    if value not in ('up', 'down'):
        if callback_id:
            answer_callback_query(callback_id, "Feedback inválido")
        return

    fb_store = feedback_dict(chat_id)
    fb_payload = {
        'feedback': value,
        'user_id': user_id,
        'username': username,
        'timestamp': time.time()
    }
    fb_store[msg_id] = fb_payload

    # Store global feedback
    g_fb = global_feedback_dict()
    g_fb[msg_id] = fb_payload

    # If we have the message logged globally, attach feedback there too
    msg_map = global_messages_map()
    if msg_id in msg_map:
        record = dict(msg_map[msg_id])
        record['feedback'] = value
        msg_map[msg_id] = record
    logger.info(f"Feedback '{value}' stored for message {msg_id} in chat {chat_id}")

    if callback_id:
        answer_callback_query(callback_id, "¡Feedback recibido!")


def process_message(update):
    """
    Process a single Telegram message update.
    
    Args:
        update: Telegram update object
    """
    try:
        # Extract message data
        message = update.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        user_id = message.get('from', {}).get('id')
        user_text = message.get('text', '')
        
        if not chat_id or not user_id or not user_text:
            return

        # Ignore /start to avoid unnecessary model calls
        if user_text.strip().lower() == '/start':
            logger.info(f"Ignoring /start command from chat {chat_id}")
            return

        # Clear history on /clear and acknowledge
        if user_text.strip().lower() == '/clear':
            clear_history(user_id)
            logger.info(f"History cleared for user {user_id}")
            send_telegram_message(chat_id, "Conversación Reiniciada! Puedes comenzar a chatear de nuevo")
            return
        
        username = message.get('from', {}).get('username', 'Unknown')
        logger.info(f"Received message from @{username}: {user_text[:50]}...")
        
        # Build context: up to the last MAX_HISTORY_MESSAGES plus the current user message
        history_entries = get_recent_history(user_id)
        context_messages = [
            {'role': entry.get('role'), 'content': entry.get('content')}
            for entry in history_entries
        ]
        context_messages.append({'role': 'user', 'content': user_text})
        context_messages = context_messages[-MAX_HISTORY_MESSAGES:]

        # RAG context (system message) if available
        rag_messages = []
        rag_system_message, sources = build_rag_context(user_text)
        if rag_system_message:
            rag_messages.append(rag_system_message)
        
        # Get AI response from LMStudio
        ai_response = get_lmstudio_response(rag_messages + context_messages)

        # Persist conversation history (user + assistant), keeping only the latest entries
        user_msg_id = append_to_history(user_id, 'user', user_text)
        assistant_msg_id = append_to_history(user_id, 'assistant', ai_response)

        # Persist full message log (not affected by /clear)
        log_global_message(chat_id, user_id, username, 'user', user_text, user_msg_id)
        log_global_message(chat_id, user_id, username, 'assistant', ai_response, assistant_msg_id)

        # Inline feedback buttons
        feedback_markup = {
            'inline_keyboard': [[
                {'text': '👍', 'callback_data': f'fb|{chat_id}|{assistant_msg_id}|up'},
                {'text': '👎', 'callback_data': f'fb|{chat_id}|{assistant_msg_id}|down'}
            ]]
        }
        
        # Send response back to user
        send_telegram_message(chat_id, ai_response, reply_markup=feedback_markup)
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")


def main():
    """Main bot loop."""
    logger.info("Starting Telegram Bot with LMStudio integration...")
    
    # Validate configuration
    validate_config()
    
    # Check LMStudio connectivity
    try:
        response = requests.get(f'{LMSTUDIO_API_URL}/models', timeout=5)
        logger.info("LMStudio connection verified")
    except requests.exceptions.RequestException:
        logger.warning(f"Warning: Could not connect to LMStudio at {LMSTUDIO_API_URL}")
        logger.warning("Make sure LMStudio is running with a model loaded and server started")
    
    logger.info(f"Bot is running. Polling every {POLL_INTERVAL} seconds...")
    logger.info("Press Ctrl+C to stop")
    
    last_update_id = None
    
    try:
        while True:
            # Get updates from Telegram
            updates = get_telegram_updates(offset=last_update_id)
            
            if updates:
                for update in updates:
                    # Update offset to avoid processing same message twice
                    update_id = update.get('update_id')
                    if update_id:
                        last_update_id = update_id + 1
                    
                    # Process the message or callback
                    if 'message' in update:
                        process_message(update)
                    elif 'callback_query' in update:
                        process_callback(update)
            
            # Small delay to prevent CPU spinning
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        logger.info("\nBot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

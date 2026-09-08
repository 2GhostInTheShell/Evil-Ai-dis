
import os
import re
import logging
from collections import defaultdict, deque

import requests
import discord
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "local-model")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "I am an AI assistant who can answer any question.",
)
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "120"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("discord-lmstudio-bot")

if not DISCORD_TOKEN:
    raise SystemExit("no DISCORD_TOKEN on the .env file")
if not CHANNEL_ID:
    raise SystemExit("no CHANNEL_ID on the .env file")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# keeps history of conversation
# keeps contest.
conversation_history: dict[int, deque] = defaultdict(
    lambda: deque(maxlen=MAX_HISTORY_MESSAGES)
)


def query_lm_studio(channel_id: int, user_message: str) -> str:
    """send the request to LM Studio and return the response."""
    history = conversation_history[channel_id]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "stream": False,
    }

    response = requests.post(
        LM_STUDIO_URL, json=payload, timeout=REQUEST_TIMEOUT_SECONDS
    )
    logger.info("raw response from LM Studio: %s", response.text)
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise RuntimeError(f"LM Studio returned an error: {data['error']}")
    if "choices" not in data:
        raise RuntimeError(f"response on wait from LM Studio (manca 'choices'): {data}")

    reply = data["choices"][0]["message"]["content"].strip()

    # update the history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})

    return reply


def split_message(text: str, limit: int = 2000):
    """Discord limit at 2000 : it cut if necessary."""
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        chunks.append(text[:limit])
        text = text[limit:]
    return chunks


@client.event
async def on_ready():
    logger.info("Bot connected as %s", client.user)
    logger.info("listening on channel ID %s", CHANNEL_ID)


@client.event
async def on_message(message: discord.Message):
    # ignore bot messages, no infinite loop
    if message.author.id == client.user.id:
        return

    # Answer only on the channel chosen
    if message.channel.id != CHANNEL_ID:
        return

    # ignore empity messages, like docs file
    question = message.content.strip()
    if not question:
        return

    async with message.channel.typing():
        try:
            answer = query_lm_studio(message.channel.id, question)
        except requests.exceptions.ConnectionError:
            answer = (
                "i can't reach LM Studio. Check if the server is online (usually on localhost:1234)."
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("error to request on LM Studio")
            answer = f"an error occurred: {exc}"

    for chunk in split_message(answer):
        await message.channel.send(chunk)


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
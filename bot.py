import logging
import logging.config
from pyrogram import Client, __version__, types
from typing import Union, Optional, AsyncGenerator
from datetime import datetime
import pytz

# Configure logging
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# Configuration
SESSION = "your_session_name"
API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
LOG_CHANNEL = "your_log_channel_id"

# Link editing rules
LINK_RULES = {
    "hubcloud": {"prefix": "", "suffix": "club"},
    "gdtot": {"prefix": "new6", "suffix": "dad"},
    "gdflix": {"prefix": "new4", "suffix": "cfd"},
    "appdrive": {"prefix": "", "suffix": "fit"},
    "filepress": {"prefix": "new1", "suffix": "shop"}
}

# Queue sequence
QUEUE_SEQUENCE = [
    "gdflix", "hubcloud", "gdtot", "hubcloud", 
    "appdrive", "hubcloud", "filepress", "hubcloud"
]

def edit_link(url: str) -> str:
    for key, value in LINK_RULES.items():
        if key in url:
            base_url = url.split('/')[2]
            new_prefix = value['prefix']
            new_suffix = value['suffix']
            
            if key == "hubcloud":
                return url.replace(base_url, f"{new_prefix}.{key}.{new_suffix}")
            elif key == "gdtot":
                return url.replace(base_url, f"{new_prefix}.{key}.{new_suffix}")
            elif key == "gdflix":
                return url.replace(base_url, f"{new_prefix}.{key}.{new_suffix}")
            elif key == "appdrive":
                return url.replace(base_url, f"{key}.{new_suffix}")
            elif key == "filepress":
                if "?usid=" in url:
                    url = url.split("?")[0]
                return url.replace(base_url, f"{new_prefix}.{key}.{new_suffix}")
    return url

class Bot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            sleep_threshold=10,
        )

    async def start(self):
        await super().start()
        logging.info("Bot started.")
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz).strftime("%H:%M:%S %p")
        await self.send_message(chat_id=LOG_CHANNEL, text=f"Bot started at {now}")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped.")

    async def iter_messages(self, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator[types.Message, None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff + 1)))
            for message in messages:
                yield message
                current += 1

    async def process_messages(self, chat_id: Union[int, str]):
        queue = []
        for message in self.iter_messages(chat_id, limit=1000):
            if message.text:
                edited_message = message.text
                urls = [url for url in edited_message.split() if any(link in url for link in LINK_RULES.keys())]
                for url in urls:
                    edited_url = edit_link(url)
                    edited_message = edited_message.replace(url, edited_url)
                queue.append(edited_message)
        
        # Send messages in the specified queue order
        sequence_index = 0
        for message in queue:
            # Find the next link type to send
            for link_type in QUEUE_SEQUENCE:
                if link_type in message:
                    await self.send_message(chat_id, message)
                    sequence_index = (sequence_index + 1) % len(QUEUE_SEQUENCE)
                    break

app = Bot()
app.run()

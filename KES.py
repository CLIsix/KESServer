#!/usr/bin/env python
# pylint: disable=unused-argument

import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey

version = "1.0.0"

logo = f"""
 __ _  ____  ____ 
(  / )(  __)/ ___)  KEY EXCHANGE SWARM
 )  (  ) _) \___ \\  {version}
(__\_)(____)(____/  With 💙 by CliSix
"""

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Keys aren't saved locally.
key_memory = {}

async def check_key(public_key_str: str) -> bool:
    """
    Checks if the provided string is a valid public key in PEM format.

    Args:
        public_key_str (str): The string containing the public key.

    Returns:
        bool: True if the string is a valid public key, False otherwise.
    """
    try:
        # Try to load the public key
        public_key = serialization.load_pem_public_key(
            public_key_str.encode('utf-8'),
            backend=default_backend()
        )
        # If no exception is raised, the key is valid
        return True
    except (ValueError, InvalidKey):
        # If a ValueError or InvalidKey exception is raised, the key is invalid
        return False

# Process incoming commands
async def process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg_in = update.message.text
    query_id = update.message.from_user.id
    # if len(msg_in.split("\n")) >= 2:
    #     # KESgram user is dumping local directory
    #     pass
    # else:
    #     # User is sharing their public key, or requesting a public key.
    key_infer = await check_key(msg_in)
    if key_infer:
        await context
        # KESgram sent a public key, do not reply, just save.
        key_memory[str(query_id)] = msg_in
    else:
        try:
            await update.message.reply_text(key_memory[msg_in])
        except Exception as e:
            print(e)

def main() -> None:
    """Start the bot."""

    with open("./API_KEYS","r") as f:
        TOKEN = f.read()
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
# src/common.py
import logging

import dotenv

from config import init_logging_config

dotenv.load_dotenv()
init_logging_config()

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "emoji": "🇺🇸🇬🇧",
        "description": "to translate to English",
    },
    "jp": {
        "name": "Japanese",
        "emoji": "🇯🇵",
        "description": "to translate to Japanese",
    },
}

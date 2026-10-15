import asyncio
import logging
import os
import random
import sys
import string
from typing import List, Dict

from aiogram import Bot, Dispatcher, F, types
from aiogram.types import FSInputFile
from dotenv import load_dotenv

try:
    import file_search
    HAS_C_MODULE = True
except ImportError:
    HAS_C_MODULE = False
    logging.warning("C-модуль 'file_search' не найден. Будет использована только Python-логика.")

from spellchecker import SpellChecker

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_FILENAME = os.getenv("DICT_FILENAME", "my_dict.txt")
GIFS_DIRNAME = os.getenv("GIFS_DIRNAME", "gifs")
GIF_EXTENSION = ".gif"

GIFS_DIR = os.path.join(BASE_DIR, GIFS_DIRNAME)
DICT_PATH = os.path.join(BASE_DIR, DICT_FILENAME)

logger.info("Загрузка словарей...")
spell_ru = SpellChecker(language='ru')
if not HAS_C_MODULE:
    spell_en = SpellChecker(language='en')
logger.info("Словари загружены.")

BOT_TOKEN = os.getenv("BOT_TOKEN")

ENG_LAYOUT = "qwertyuiop[]asdfghjkl;'zxcvbnm,.`QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>~"
RUS_LAYOUT = "йцукенгшщзхъфывапролджэячсмитьбюёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ"
LAYOUT_TRANSLATION_TABLE = str.maketrans(ENG_LAYOUT, RUS_LAYOUT)

RUSSIAN_LETTERS = set("йцукенгшщзхъфывапролджэячсмитьбюёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ")

GIF_FILES: List[str] = []
GIF_FILE_IDS: Dict[str, str] = {}

def preload_gifs():
    global GIF_FILES
    if os.path.exists(GIFS_DIR):
        GIF_FILES = [f for f in os.listdir(GIFS_DIR) if f.lower().endswith(GIF_EXTENSION)]
        logger.info(f"В кэш загружено {len(GIF_FILES)} GIF-файлов.")
    else:
        logger.warning(f"Папка {GIFS_DIR} не найдена!")

def clean_and_tokenize(text: str) -> List[str]:
    raw_tokens = text.split()
    filtered_tokens = [t for t in raw_tokens if not t.startswith('@')]
    filtered_text = " ".join(filtered_tokens)

    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text_clean = filtered_text.translate(translator)
    
    words = [w for w in text_clean.split() if len(w) > 1 and not w.isdigit()]
    return words

def is_english_word_c(word: str) -> bool:
    if not HAS_C_MODULE:
        return word in spell_en.known([word])
    try:
        return file_search.contains_word(DICT_PATH, word.lower())
    except Exception as e:
        logger.error(f"Ошибка в C-модуле: {e}")
        return False

def check_structure(original_text: str) -> bool:
    if not original_text or len(original_text) < 2:
        return False
        
    if any(char in RUSSIAN_LETTERS for char in original_text):
        return False

    words = clean_and_tokenize(original_text)
    if not words:
        return False 

    english_words_count = 0
    for word in words:
        if is_english_word_c(word):
            english_words_count += 1
            
    if len(words) > 0 and (english_words_count / len(words) > 0.4):
        return False

    translated_text = original_text.translate(LAYOUT_TRANSLATION_TABLE)
    trans_words = clean_and_tokenize(translated_text)
    
    if not trans_words:
        return True

    known_ru = spell_ru.known(trans_words)
    if len(known_ru) / len(trans_words) > 0.2:
        return True
    
    return True

async def main():
    if not BOT_TOKEN:
        logger.error("Токен бота не найден. Убедитесь, что он указан в .env")
        sys.exit(1)

    preload_gifs()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    logger.info("Бот запускается...")

    @dp.message(F.text)
    async def handle_message(message: types.Message):
        if not check_structure(message.text):
            return

        if not GIF_FILES:
            return

        gif_filename = random.choice(GIF_FILES)
        file_id = GIF_FILE_IDS.get(gif_filename)
        
        try:
            if file_id:
                logger.info(f"Отправка кэшированного GIF: {gif_filename}")
                await message.bot.send_animation(
                    chat_id=message.chat.id,
                    animation=file_id,
                    reply_to_message_id=message.message_id
                )
            else:
                logger.info(f"Загрузка и отправка GIF: {gif_filename}")
                gif_path = os.path.join(GIFS_DIR, gif_filename)
                gif_file = FSInputFile(gif_path)
                
                sent_msg = await message.bot.send_animation(
                    chat_id=message.chat.id,
                    animation=gif_file,
                    reply_to_message_id=message.message_id
                )
                
                if sent_msg.animation and sent_msg.animation.file_id:
                    GIF_FILE_IDS[gif_filename] = sent_msg.animation.file_id

        except Exception as e:
            logger.error(f"Ошибка при отправке GIF: {e}")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")

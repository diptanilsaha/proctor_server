import os
import secrets
import datetime
from flask import current_app
from wonderwords import RandomWord

r = RandomWord()

def generate_clientname():
    clientname = ".".join(r.random_words(3, word_max_length=10))
    return clientname

def calculate_duration(
    start_time: datetime.datetime,
    end_time: datetime.datetime
) -> int:
    diff = end_time - start_time
    diff_minute = diff.total_seconds() // 60
    return int(diff_minute)

def remove_assessment_media(filename: str) -> bool:
    try:
        os.remove(
            os.path.join(current_app.config['ASSESSMENT_MEDIA'], filename)
        )
    except OSError:
        return False
    return True

def generate_media_name(media_file_name: str):
    media_ext = media_file_name.split('.')[-1]
    media_name = f"{secrets.token_hex(16)}.{media_ext}"
    return media_name

import os
import secrets
import datetime
import ipaddress
import jwt
from flask import current_app
from wonderwords import RandomWord
from .models import Client
from .database import db

r = RandomWord()

def generate_clientname():
    """Generate clientName using 'wonderwords' library."""
    clientname = ".".join(r.random_words(3, word_max_length=10))
    return clientname

def calculate_duration(
    start_time: datetime.datetime,
    end_time: datetime.datetime
) -> int:
    """Calculate Duration from Start Time and End Time."""
    diff = end_time - start_time
    diff_minute = diff.total_seconds() // 60
    return int(diff_minute)

def remove_assessment_media(filename: str) -> bool:
    """Remove Assessment Media on deletion."""
    try:
        os.remove(
            os.path.join(current_app.config['ASSESSMENT_MEDIA'], filename)
        )
    except OSError:
        return False
    return True

def generate_media_name(media_file_name: str) -> str:
    """Generate Media Name."""
    media_ext = media_file_name.split('.')[-1]
    media_name = f"{secrets.token_hex(16)}.{media_ext}"
    return media_name

def get_client_from_token(token: str) -> Client | None:
    """Get client from Token."""
    client_from_token = jwt.decode(
        token,
        key=current_app.config['SECRET_KEY'],
        algorithms=["HS256",]
    )
    client = db.session.get(Client, client_from_token['client_id'])
    return client

def validate_ip_address(ip_address: str) -> bool:
    """Validate IP Address."""
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False

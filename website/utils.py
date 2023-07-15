from django.conf import settings
from .models import ShortLink
import string, random

SHORT_CODE_LENGTH = settings.SHORT_CODE_LENGTH if settings.SHORT_CODE_LENGTH else 6

def generate_short_code():
    symbols = ""
    try:
        if settings.USE_UPPERCASE_ALPHABETS: symbols += string.ascii_uppercase
    except: pass
    try:
        if settings.USE_LOWERCASE_ALPHABETS: symbols += string.ascii_lowercase
    except: pass
    try:
        if settings.USE_DIGITS: symbols += string.digits
    except: pass

    symbols = symbols if symbols else string.ascii_lowercase
    
    return ''.join(random.choices(symbols, k=SHORT_CODE_LENGTH))

def get_short_code( short_code=None):
    short_code = short_code if short_code else generate_short_code()
    while(ShortLink.objects.check(code=short_code)):
        short_code = generate_short_code()
    return short_code

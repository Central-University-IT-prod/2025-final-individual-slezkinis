from django.core.cache import cache

import logging

def is_bad(text: str):
    bad_words = cache.get("bad_words", [])
    logging.error(bad_words)
    if text is not None:
        return False
    lower_text = text.lower()
    for word in bad_words:
        if word.lower() in lower_text:
            return True
    return False
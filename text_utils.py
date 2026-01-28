"""
Text utilities for TTS normalization.
Fixes pronunciation for brand names and expands acronyms.
"""
import re

# Custom dictionary for brand name corrections or specific pronunciations
# Key: The word as it appears in text
# Value: How it should be written for better TTS pronunciation
PRONUNCIATION_MAP = {
    "BandhanNova": "Bandhan Nova",
    "BandhaNova": "Bandha Nova",
}

def expand_acronyms(text):
    """
    Finds uppercase acronyms (2-4 chars) and inserts spaces between letters
    to force letter-by-letter pronunciation.
    Example: ROI -> R O I, IIR -> I I R
    """
    def spacing_replacer(match):
        acronym = match.group(0)
        # Only space out if it's all caps and length 2-4
        if acronym.isupper() and 2 <= len(acronym) <= 4:
            return " ".join(list(acronym))
        return acronym

    # Regex matches words consisting only of uppercase letters A-Z
    # We use word boundaries \b to ensure we don't match parts of longer words
    return re.sub(r'\b[A-Z]{2,4}\b', spacing_replacer, text)

def normalize_text(text, language='en'):
    """
    Normalize text for better TTS output.
    """
    if not text:
        return text

    # 1. Apply custom pronunciation map (case-insensitive search)
    # We use a case-insensitive regex for each key in PRONUNCIATION_MAP
    for original, correction in PRONUNCIATION_MAP.items():
        pattern = re.compile(re.escape(original), re.IGNORECASE)
        text = pattern.sub(correction, text)

    # 2. Expand acronyms for English words
    # Even in Bengali text, English abbreviations might appear
    text = expand_acronyms(text)

    # 3. Handle double spaces that might have been introduced
    text = re.sub(r'\s+', ' ', text).strip()

    return text

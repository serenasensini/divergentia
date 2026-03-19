"""
Application-wide constants and configuration values
"""

# Part-of-Speech tags (spaCy universal POS tags)
POS_NOUN = "NOUN"
POS_PROPER_NOUN = "PROPN"
POS_VERB = "VERB"
POS_ADJECTIVE = "ADJ"
POS_ADVERB = "ADV"

# POS tag groups
POS_NOUNS = [POS_NOUN, POS_PROPER_NOUN]
POS_VERBS = [POS_VERB]
POS_ADJECTIVES = [POS_ADJECTIVE]
POS_ADVERBS = [POS_ADVERB]

# File format constants
SUPPORTED_DOCUMENT_FORMATS = ['pdf', 'docx', 'txt', 'rtf']
SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'bmp']

# File size limits (in bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_TEXT_LENGTH = 1000000  # 1 million characters

# API rate limiting
DEFAULT_RATE_LIMIT = "10 per minute"
UPLOAD_RATE_LIMIT = "5 per minute"

# Ollama configuration
OLLAMA_DEFAULT_MODEL = "llama2"
OLLAMA_REQUEST_TIMEOUT = 120  # seconds
OLLAMA_MAX_RETRIES = 3
OLLAMA_RETRY_DELAY = 1.0  # seconds

# Text processing
MIN_KEYWORD_LENGTH = 3
DEFAULT_MAX_KEYWORDS = 5
DEFAULT_CHUNK_SIZE = 2000
DEFAULT_CHUNK_OVERLAP = 200

# Formatting defaults
DEFAULT_FONT_NAME = "Arial"
DEFAULT_FONT_SIZE = 11
DEFAULT_LINE_SPACING = 1.15

# Colors (hex format)
COLOR_BLACK = "#000000"
COLOR_WHITE = "#FFFFFF"
COLOR_RED = "#FF0000"
COLOR_GREEN = "#00FF00"
COLOR_BLUE = "#0000FF"
COLOR_ORANGE = "#cc5500"

# Keywords marker text
KEYWORDS_MARKER = "Parole chiave:"


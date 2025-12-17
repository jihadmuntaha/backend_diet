def is_valid_message(message: str) -> bool:
    """
    Simple validation for chatbot input
    """
    return isinstance(message, str) and len(message.strip()) > 3

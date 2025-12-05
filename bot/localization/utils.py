"""
Translation utility function
"""
from .translations import translations


def t(key: str, lang: str = "en", **kwargs) -> str:
    """
    Get translated text by key.

    Args:
        key: Translation key
        lang: Language code ('en' or 'ru')
        **kwargs: Variables to format into the string

    Returns:
        Translated text
    """
    translation = translations.get(key, {})
    text = translation.get(lang, translation.get("en", key))

    # Format with variables if provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass

    return text
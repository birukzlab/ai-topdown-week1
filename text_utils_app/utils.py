def get_stats(text: str):
    words = text.split()
    return {
        "chars": len(text),
        "words": len(words),
        "reading_time_min": len(words) / 200.0,  # naive 200 wpm
    }

def transform_text(text: str, mode:str):
    if mode == "UPPERCASE":
        return text.upper()
    if mode == "lowercase":
        return text.lower()
    if mode == "Title Case":
        return text.title()
    return text


def get_stats(text: str):
    words = text.split()
    return {
        "chars": len(text),
        "words": len(words),
        "reading_time_min": len(words) / 200.0,  # naive 200 wpm
    }

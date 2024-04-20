import re


def remove_urls(text):
    pattern = re.compile(r"http\S+|www\S+")
    return pattern.sub("", text)


def remove_special_characters(text):
    pattern = re.compile(r"[^a-zA-Z0-9\s]")
    return pattern.sub("", text)


def remove_hashtags(text):
    pattern = re.compile(r"#\w+")
    return pattern.sub("", text)


def remove_emojis(text):
    regrex_pattern = re.compile(
        pattern="["
        "\U0001F600-\U0001F64F"  # emojiicons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+",
        flags=re.UNICODE,
    )
    return regrex_pattern.sub(r"", text)


def preprocess_text(text):
    text = remove_urls(text)
    text = remove_special_characters(text)
    text = remove_hashtags(text)
    text = remove_emojis(text)
    return text

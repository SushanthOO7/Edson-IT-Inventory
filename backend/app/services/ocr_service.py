from app.utils.regex_extractors import extract_asset_tag, extract_model, extract_serial_number

SKIP_TOKENS = {
    "ASSET",
    "TAG",
    "SERIAL",
    "NUMBER",
    "SERVICE",
    "MODEL",
    "DEVICE",
}


def extract_scan_signals(text: str) -> dict[str, str | None]:
    return {
        "asset_tag": extract_asset_tag(text),
        "serial_number": extract_serial_number(text),
        "model": extract_model(text),
    }


def extract_candidate_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for raw_token in text.replace(":", " ").replace("#", " ").split():
        token = "".join(character for character in raw_token.upper() if character.isalnum() or character == "-")
        if len(token) < 3 or token in SKIP_TOKENS or token in tokens:
            continue
        tokens.append(token)
    return tokens[:20]

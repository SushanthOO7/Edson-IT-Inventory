from app.utils.regex_extractors import extract_asset_tag, extract_model, extract_serial_number


def extract_scan_signals(text: str) -> dict[str, str | None]:
    return {
        "asset_tag": extract_asset_tag(text),
        "serial_number": extract_serial_number(text),
        "model": extract_model(text),
    }

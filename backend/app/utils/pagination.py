def clamp_page_size(page_size: int, maximum: int = 100) -> int:
    return max(1, min(page_size, maximum))

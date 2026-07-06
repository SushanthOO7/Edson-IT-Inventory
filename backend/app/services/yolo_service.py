import cv2
import numpy as np


def detect_regions(image_bytes: bytes) -> list[dict[str, int | float | str]]:
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        return []

    height, width = image.shape[:2]
    if width == 0 or height == 0:
        return []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 60, 160)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions: list[dict[str, int | float | str]] = []
    image_area = float(width * height)
    for contour in contours:
        x, y, box_width, box_height = cv2.boundingRect(contour)
        area = float(box_width * box_height)
        if area < image_area * 0.002 or area > image_area * 0.45:
            continue
        aspect_ratio = box_width / max(box_height, 1)
        if aspect_ratio < 1.2 or aspect_ratio > 12:
            continue

        confidence = min(0.95, max(0.25, area / image_area * 8))
        regions.append(
            {
                "x": int(x),
                "y": int(y),
                "width": int(box_width),
                "height": int(box_height),
                "confidence": round(confidence, 3),
                "label": "possible_label_region",
            }
        )

    regions.sort(key=lambda region: float(region["confidence"]), reverse=True)
    return regions[:10]

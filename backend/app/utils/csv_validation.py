import csv
from io import StringIO


def validate_required_columns(csv_text: str, required_columns: list[str]) -> list[str]:
    reader = csv.DictReader(StringIO(csv_text))
    missing = [column for column in required_columns if column not in (reader.fieldnames or [])]
    return missing

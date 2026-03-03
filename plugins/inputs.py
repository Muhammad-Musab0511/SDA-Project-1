from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import pandas as pd


from core.contracts import PipelineService


class CSVReader:
    def __init__(self, path: str, service: PipelineService):
        self.path = Path(path)
        self.service = service
    def run(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.path}")
        frame = pd.read_csv(self.path)
        raw_records = frame.to_dict(orient="records")
        records: list[dict[str, Any]] = [
            {str(key): value for key, value in row.items()} for row in raw_records
        ]
        self.service.execute(records)

class JSONReader:
    def __init__(self, path: str, service: PipelineService):
        self.path = Path(path)
        self.service = service
    def run(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(f"JSON file not found: {self.path}")

        with self.path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if isinstance(payload, dict) and "records" in payload:
            records = payload["records"]
        elif isinstance(payload, list):
            records = payload
        else:
            raise ValueError("JSON input must be a list of records or an object containing a 'records' list")

        if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
            raise ValueError("JSON records must be a list of objects")

        normalized_records: list[dict[str, Any]] = [
            {str(key): value for key, value in item.items()} for item in records
        ]

        self.service.execute(normalized_records)
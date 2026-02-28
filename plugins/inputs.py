from __future__ import annotations
import json
from pathlib import Path
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
        self.service.execute(frame.to_dict(orient="records"))

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

        self.service.execute(records)
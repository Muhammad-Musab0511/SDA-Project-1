from __future__ import annotations
from typing import Any, Protocol


class DataSink(Protocol):
    def write(self, records: dict[str, Any]) -> None:
        ...
class PipelineService(Protocol):
    def execute(self, raw_data: list[dict[str, Any]]) -> None:
        ...

    
class TransformationEngine(PipelineService):
    def __init__(self, sink: DataSink, settings: dict[str, Any]):
        self.sink = sink
        self.settings = settings

    def execute(self, raw_data: list[dict[str, Any]]) -> None:
        ...



class CSVReader:
    def __init__(self, path: str, service: PipelineService):
        self.path = path
        self.service = service

    def run(self) -> None:
        ...
class JSONReader:
    def __init__(self, path: str, service: PipelineService):
        self.path = path
        self.service = service

    def run(self) -> None:
        ...



class ConsoleWriter:
    def write(self, records: dict[str, Any]) -> None:
        ...
class GraphicsChartWriter:
    def write(self, records: dict[str, Any]) -> None:
        ...
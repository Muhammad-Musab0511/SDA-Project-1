from typing import Any, Protocol, runtime_checkable

@runtime_checkable
class DataSink(Protocol):
    def write(self, records: dict[str, Any]) -> None:
        ...
@runtime_checkable
class PipelineService(Protocol):
    def execute(self, raw_data: list[dict[str, Any]]) -> None:
        ...
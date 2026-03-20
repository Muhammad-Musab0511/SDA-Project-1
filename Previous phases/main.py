from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.contracts import DataSink
from core.engine import TransformationEngine
from plugins.inputs import CSVReader, JSONReader
from plugins.outputs import ConsoleWriter, GraphicsChartWriter


class MultiSink:
    def __init__(self, sinks: list[Any]):
        self.sinks = sinks

    def write(self, records: dict[str, Any]) -> None:
        list(map(lambda sink: sink.write(records), self.sinks))


def _is_data_sink(instance: Any) -> bool:
    return isinstance(instance, DataSink)


INPUT_DRIVERS = {
    "csv": CSVReader,
    "json": JSONReader,
}

OUTPUT_DRIVERS = {
    "console": ConsoleWriter,
    "chart": GraphicsChartWriter,
}


def _load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _validate_config(config: dict[str, Any]) -> None:
    required_sections = ["input", "output", "analysis"]
    missing_sections = list(filter(lambda key: key not in config, required_sections))
    if missing_sections:
        raise ValueError(f"Missing config sections: {missing_sections}")

    input_driver = config["input"].get("driver")
    if input_driver not in INPUT_DRIVERS:
        raise ValueError(f"Unsupported input driver: {input_driver}")

    output_drivers = config["output"].get("drivers", [])
    invalid_outputs = list(filter(lambda item: item not in OUTPUT_DRIVERS, output_drivers))
    if invalid_outputs:
        raise ValueError(f"Unsupported output drivers: {invalid_outputs}")

    required_analysis = ["region", "year", "start_year", "end_year", "decline_years"]
    missing_analysis = list(filter(lambda key: key not in config["analysis"], required_analysis))
    if missing_analysis:
        raise ValueError(f"Missing analysis fields: {missing_analysis}")


def bootstrap(config_file: str = "config.json") -> None:
    project_root = Path(__file__).resolve().parent
    config = _load_config(project_root / config_file)
    _validate_config(config)

    sink_instances = list(map(lambda name: OUTPUT_DRIVERS[name](), config["output"]["drivers"]))
    invalid_sinks = list(filter(lambda item: not _is_data_sink(item), sink_instances))
    if invalid_sinks:
        sink_names = list(map(lambda item: item.__class__.__name__, invalid_sinks))
        raise TypeError(f"Output drivers do not satisfy DataSink protocol: {sink_names}")

    sink = sink_instances[0] if len(sink_instances) == 1 else MultiSink(sink_instances)
    # dependency injection of the sink into the transformation engine
    engine = TransformationEngine(sink=sink, settings=config["analysis"])

    input_driver_name = config["input"]["driver"]
    input_driver = INPUT_DRIVERS[input_driver_name]
    input_path = str((project_root / config["input"]["path"]).resolve())

    source = input_driver(path=input_path, service=engine)
    source.run()


if __name__ == "__main__":
    bootstrap()

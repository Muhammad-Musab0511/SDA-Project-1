
import csv
import time


class InputModule:
    def __init__(self, config: dict, raw_queue):
        self._config = config
        self._raw_queue = raw_queue

        dynamics = config["pipeline_dynamics"]
        self._delay: float = dynamics["input_delay_seconds"]
        self._parallelism: int = dynamics["core_parallelism"]
        self._dataset_path: str = config["dataset_path"]

        # Build a quick lookup so CSV column names map to internal field names and types.
        self._column_map: dict = {}
        for col in config["schema_mapping"]["columns"]:
            self._column_map[col["source_name"]] = (
                col["internal_mapping"],
                col["data_type"],
            )
    @staticmethod
    def _cast(value: str, data_type: str):
        if data_type == "string":
            return str(value)
        if data_type == "integer":
            return int(value)
        if data_type == "float":
            return float(value)
        return value

    def run(self) -> None:
        sequence = 0
        with open(self._dataset_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                packet: dict = {"_sequence": sequence}
                for source_name, raw_value in row.items():
                    if source_name in self._column_map:
                        internal_name, data_type = self._column_map[source_name]
                        packet[internal_name] = self._cast(raw_value, data_type)
                self._raw_queue.put(packet)
                sequence += 1
                time.sleep(self._delay)

        # Send one sentinel per worker so each worker can shut down cleanly.
        for _ in range(self._parallelism):
            self._raw_queue.put(None)

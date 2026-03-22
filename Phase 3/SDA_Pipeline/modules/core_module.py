import hashlib

def verify_signature(metric_value: float, security_hash: str, secret_key: str, iterations: int) -> bool:
    raw_value_str: str = f"{metric_value:.2f}"
    computed: str = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=secret_key.encode("utf-8"),
        salt=raw_value_str.encode("utf-8"),
        iterations=iterations,
    ).hex()
    return computed == security_hash


def compute_running_average(window: list, new_value: float, window_size: int) -> tuple:
    """
    Return a new sliding window plus its average.
    The input list is left unchanged.
    """
    new_window: list = (window + [new_value])[-window_size:]
    average: float = sum(new_window) / len(new_window)
    return new_window, average

class CoreWorker:
    """
    One scatter-stage worker.
    It verifies each packet signature, forwards valid packets, and drops invalid ones.
    """

    def __init__(self, config: dict, raw_queue, intermediate_queue, worker_id: int = 0):
        self._raw_queue = raw_queue
        self._intermediate_queue = intermediate_queue
        self._worker_id = worker_id
        stateless = config["processing"]["stateless_tasks"]

        op = stateless.get("operation", "verify_signature")
        if op != "verify_signature":
            raise ValueError(f"Unsupported stateless operation: {op}")

        algorithm = stateless.get("algorithm", "pbkdf2_hmac")
        if algorithm != "pbkdf2_hmac":
            raise ValueError(f"Unsupported signature algorithm: {algorithm}")

        self._secret_key: str = stateless["secret_key"]
        self._iterations: int = int(stateless["iterations"])
        self._value_field: str = stateless.get("value_field", "metric_value")
        self._signature_field: str = stateless.get("signature_field", "security_hash")

    def run(self) -> None:
        verified = dropped = 0
        while True:
            packet = self._raw_queue.get()
            if packet is None:
                self._intermediate_queue.put(None)
                print(f"[CoreWorker-{self._worker_id}] Done. "
                      f"Verified={verified}, Dropped={dropped}")
                return
            if verify_signature(
                packet[self._value_field],
                packet[self._signature_field],
                self._secret_key,
                self._iterations,
            ):
                self._intermediate_queue.put(packet)
                verified += 1
            else:
                dropped += 1

class Aggregator:
    """
    Gather-stage node that restores packet order and computes running averages.
    """

    def __init__(self, config: dict, intermediate_queue, processed_queue, num_workers: int):
        self._intermediate_queue = intermediate_queue
        self._processed_queue = processed_queue
        self._num_workers = num_workers
        stateful = config["processing"]["stateful_tasks"]
        stateless = config["processing"]["stateless_tasks"]
        self._window_size: int = int(stateful["running_average_window_size"])
        self._entity_field: str = stateful.get("group_by_field", "entity_name")
        self._value_field: str = stateful.get(
            "value_field", stateless.get("value_field", "metric_value")
        )
        self._computed_field: str = stateful.get("output_field", "computed_metric")

    def run(self) -> None:
        # Mutable shell state for packet ordering and per-entity windows.
        windows: dict = {}          # Maps each entity to its current averaging window.
        reseq_buffer: dict = {}     # Holds out-of-order packets by sequence number.
        next_expected: int = 0
        sentinels: int = 0
        total: int = 0

        while True:
            packet = self._intermediate_queue.get()

            if packet is None:
                sentinels += 1
                if sentinels == self._num_workers:
                    # All workers finished; emit any buffered packets still in order.
                    while next_expected in reseq_buffer:
                        p = reseq_buffer.pop(next_expected)
                        total += self._emit(p, windows)
                        next_expected += 1
                    self._processed_queue.put(None)
                    print(f"[Aggregator] Done. Emitted={total}")
                    return
                continue

            seq: int = packet["_sequence"]
            if seq == next_expected:
                total += self._emit(packet, windows)
                next_expected += 1
                while next_expected in reseq_buffer:
                    p = reseq_buffer.pop(next_expected)
                    total += self._emit(p, windows)
                    next_expected += 1
            else:
                reseq_buffer[seq] = packet

    def _emit(self, packet: dict, windows: dict) -> int:
        entity = packet.get(self._entity_field, "__global__")
        if entity not in windows:
            windows[entity] = []
        # Compute the updated window and average without mutating the old list.
        new_window, avg = compute_running_average(
            windows[entity], packet[self._value_field], self._window_size
        )
        windows[entity] = new_window
        out = dict(packet)
        out[self._computed_field] = avg
        self._processed_queue.put(out)
        return 1

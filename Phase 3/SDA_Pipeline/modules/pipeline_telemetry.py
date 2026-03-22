class PipelineTelemetry:
    def __init__(self, raw_queue, intermediate_queue, processed_queue, max_size: int):
        self._raw_queue = raw_queue
        self._intermediate_queue = intermediate_queue
        self._processed_queue = processed_queue
        self._max_size = max_size
        self._observers: list = []

    def subscribe(self, observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer) -> None:
        self._observers.remove(observer)

    def _safe_qsize(self, q) -> int:
        try:
            return q.qsize()
        except NotImplementedError:
            return 0

    def poll_and_notify(self) -> dict:
        state = {
            "raw_queue_size": self._safe_qsize(self._raw_queue),
            "intermediate_queue_size": self._safe_qsize(self._intermediate_queue),
            "processed_queue_size": self._safe_qsize(self._processed_queue),
            "max_size": self._max_size,
        }
        for observer in self._observers:
            observer.update(state)
        return state

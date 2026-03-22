"""
Entry point that wires the full pipeline together.

This module loads config, creates queues and worker processes, connects
telemetry to the dashboard, then keeps the dashboard running in the main
process until shutdown.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import sys
import os


def main() -> None:
    # Import here so multiprocessing startup stays safe across platforms.
    from modules.input_module import InputModule
    from modules.core_module import CoreWorker, Aggregator
    from modules.output_module import Dashboard
    from modules.pipeline_telemetry import PipelineTelemetry

    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, encoding="utf-8") as fh:
            config: dict = json.load(fh)
    except FileNotFoundError:
        print(f"[Main] ERROR: config.json not found at '{config_path}'", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"[Main] ERROR: Malformed config.json — {exc}", file=sys.stderr)
        sys.exit(1)

    dynamics     = config["pipeline_dynamics"]
    parallelism  = int(dynamics["core_parallelism"])
    max_size     = int(dynamics["stream_queue_max_size"])

    print("=" * 60)
    print("  Generic Concurrent Real-Time Pipeline")
    print("=" * 60)
    print(f"  Dataset         : {config['dataset_path']}")
    print(f"  Core parallelism: {parallelism} workers")
    print(f"  Queue max size  : {max_size}")
    print(f"  Input delay     : {dynamics['input_delay_seconds']} s/packet")
    print("=" * 60)

    raw_queue          = mp.Queue(maxsize=max_size)
    intermediate_queue = mp.Queue(maxsize=max_size)
    processed_queue    = mp.Queue(maxsize=max_size)

    input_proc = InputModule(config, raw_queue)

    core_workers = [
        CoreWorker(config, raw_queue, intermediate_queue, worker_id=i)
        for i in range(parallelism)
    ]

    aggregator   = Aggregator(
        config, intermediate_queue, processed_queue, num_workers=parallelism
    )

    telemetry = PipelineTelemetry(
        raw_queue,
        intermediate_queue,
        processed_queue,
        max_size,
    )

    # Dashboard subscribes to telemetry inside its constructor.
    dashboard = Dashboard(config, processed_queue, telemetry)

    worker_procs = []

    input_process = mp.Process(
        target=input_proc.run,
        name="InputProcess",
        daemon=True,
    )
    worker_procs.append(input_process)

    for worker in core_workers:
        p = mp.Process(
            target=worker.run,
            name=f"CoreWorker-{worker._worker_id}",
            daemon=True,
        )
        worker_procs.append(p)

    agg_process = mp.Process(
        target=aggregator.run,
        name="Aggregator",
        daemon=True,
    )
    worker_procs.append(agg_process)

    for proc in worker_procs:
        proc.start()
        print(f"[Main] Started: {proc.name}  (pid={proc.pid})")

    print("[Main] All workers running — launching dashboard ...")

    # Matplotlib UI must run on the main thread.
    try:
        dashboard.run()
    except KeyboardInterrupt:
        print("\n[Main] Interrupted by user.")

    print("[Main] Shutting down worker processes ...")
    for proc in worker_procs:
        proc.terminate()
        proc.join(timeout=3)

    print("[Main] Pipeline shutdown complete.")


if __name__ == "__main__":
    main()

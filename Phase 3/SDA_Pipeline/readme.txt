Generic Concurrent Real-Time Pipeline - Phase 3

Main entry file
- main.py

How to run
1. Open a terminal in the project root.
2. Install dependency (if needed): pip install matplotlib
3. Run: python main.py

Project structure (actual)
- main.py
- config.json
- readme.txt
- data/
  - sample_sensor_data.csv
- modules/
  - input_module.py
  - core_module.py
  - output_module.py
  - pipeline_telemetry.py
- diagrams/
  - class_diagram.puml
  - sequence_diagram.puml

How to use with unseen datasets
1. Put the unseen CSV into data/.
2. Update config.json:
   - dataset_path
   - schema_mapping.columns (source_name, internal_mapping, data_type)
   - processing.stateless_tasks (secret_key, iterations, optional value_field/signature_field)
   - processing.stateful_tasks (running_average_window_size, optional group_by_field/value_field/output_field)
   - visualizations (telemetry switches and chart axes/titles)
3. Run python main.py without changing module source files.

Pipeline architecture
- Producer-Consumer with multiprocessing.Queue:
  - Input -> raw_queue -> Core workers
  - Core workers -> intermediate_queue -> Aggregator
  - Aggregator -> processed_queue -> Dashboard
- Scatter-Gather:
  - Multiple CoreWorker processes verify signatures in parallel.
- Functional Core, Imperative Shell:
  - Pure functions in core_module.py:
    - verify_signature(...)
    - compute_running_average(...)
  - Aggregator manages mutable stream state (resequencing and windows).
- Observer pattern:
  - PipelineTelemetry is the Subject.
  - Dashboard subscribes as the Observer and updates telemetry bars.

Backpressure behavior
- All stream queues are bounded by pipeline_dynamics.stream_queue_max_size.
- If input is faster than processing, queue put() calls block automatically.
- Dashboard telemetry colors:
  - Green: queue usage < 50%
  - Yellow: queue usage >= 50% and < 80%
  - Red: queue usage >= 80%

Cryptographic signature compatibility (required)
- Secret key source: processing.stateless_tasks.secret_key
- Iterations source: processing.stateless_tasks.iterations
- Algorithm: hashlib.pbkdf2_hmac with hash_name='sha256'
- Rule:
  - raw_value_str = metric value rounded/formatted to two decimals (for example f"{value:.2f}")
  - password = secret key bytes
  - salt = raw_value_str bytes
  - signature = pbkdf2_hmac(...).hex()

Equivalent reference function:

def generate_signature(raw_value_str: str, key: str, iterations: int) -> str:
    """
    Generates a PBKDF2 HMAC SHA-256 signature for the given value.
    Treats the secret key as the password and the raw value as the salt.
    """
    password_bytes = key.encode('utf-8')
    salt_bytes = raw_value_str.encode('utf-8')

    hash_bytes = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=password_bytes,
        salt=salt_bytes,
        iterations=iterations
    )
    return hash_bytes.hex()

Notes
- On Windows, multiprocessing requires the if __name__ == '__main__' guard, which is already in main.py.
- If your unseen dataset uses different column names, only schema_mapping needs updating as long as internal_mapping values match the fields used by processing/visualization settings.

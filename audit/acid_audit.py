import threading
import time

from pyiceberg.catalog import load_catalog

NUM_READERS = 3
DURATION_SECONDS = 60
POLL_INTERVAL = 2

catalog = load_catalog(
    "rest",
    **{
        "uri": "http://localhost:8181",
        "s3.endpoint": "http://localhost:4566",
        "s3.access-key-id": "test",
        "s3.secret-access-key": "test",
        "s3.region": "us-east-1",
        "s3.path-style-access": "true",
    },
)

results = []
errors = []
stop = threading.Event()


def reader(name):
    last_count = 0
    while not stop.is_set():
        try:
            table = catalog.load_table("lake.checkout_events")
            snapshot = table.current_snapshot()
            if snapshot is None:
                time.sleep(POLL_INTERVAL)
                continue

            # Pin to this snapshot explicitly: proves isolation, not a moving target
            count = table.scan(snapshot_id=snapshot.snapshot_id).to_arrow().num_rows
            monotonic = count >= last_count  # append-only: count should never drop
            results.append((name, snapshot.snapshot_id, count, monotonic))
            last_count = count
        except Exception as e:
            errors.append((name, str(e)))
        time.sleep(POLL_INTERVAL)


print(f"Starting {NUM_READERS} concurrent readers for {DURATION_SECONDS}s "
      f"while Flink writes to lake.checkout_events...\n")

threads = [threading.Thread(target=reader, args=(f"reader-{i}",)) for i in range(NUM_READERS)]
for t in threads:
    t.start()

time.sleep(DURATION_SECONDS)
stop.set()
for t in threads:
    t.join()

violations = [r for r in results if not r[3]]

print(f"Total reads: {len(results)}")
print(f"Errors during concurrent access: {len(errors)}")
print(f"Monotonicity violations (row count decreased): {len(violations)}")

if results:
    counts = [r[2] for r in results]
    print(f"Row count observed: min={min(counts)}, max={max(counts)}")

if errors:
    print("\nErrors:")
    for name, err in errors[:5]:
        print(f"  {name}: {err}")

if violations:
    print("\nViolations:")
    for v in violations[:5]:
        print(f"  {v}")

if not errors and not violations:
    print("\nPASS: all concurrent reads succeeded, row counts only increased, no corruption observed.")
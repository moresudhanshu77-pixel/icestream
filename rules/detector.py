import json
import time

from confluent_kafka import Consumer

from suites import checkout_suite, ERROR_THRESHOLD

WINDOW_SECONDS = 5

consumer = Consumer({
    "bootstrap.servers": "localhost:29092",
    "group.id": "icestream-detector",
    "auto.offset.reset": "latest",
})
consumer.subscribe(["checkout.events"])

print(f"Watching checkout.events (window={WINDOW_SECONDS}s, threshold={ERROR_THRESHOLD:.0%})")
print("Ctrl+C to stop\n")

batch = []
window_start = time.time()

try:
    while True:
        msg = consumer.poll(0.2)
        if msg is not None and not msg.error():
            try:
                batch.append(json.loads(msg.value()))
            except json.JSONDecodeError:
                batch.append({})  # unparseable record fails every expectation

        if time.time() - window_start >= WINDOW_SECONDS and batch:
            report = checkout_suite.run(batch)
            rate = report["record_error_rate"]
            state = "ANOMALY" if rate > ERROR_THRESHOLD else "ok"

            print(f"[{time.strftime('%X')}] n={len(batch):5d} error_rate={rate:6.2%}  {state}")
            if rate > ERROR_THRESHOLD:
                for r in report["results"]:
                    if r["failed"]:
                        print(f"   -> {r['expectation']}({r['column']}): {r['failure_rate']:.1%} failing")

            batch = []
            window_start = time.time()

except KeyboardInterrupt:
    print("\nStopping detector...")
finally:
    consumer.close()
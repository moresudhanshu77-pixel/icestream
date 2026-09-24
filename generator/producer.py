import argparse
import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

from confluent_kafka import Producer

CURRENCIES = ["USD", "EUR", "INR", "GBP"]
PAYMENTS = ["card", "upi", "paypal", "cod"]
COUNTRIES = ["US", "IN", "DE", "GB", "BR"]

# Counts what Kafka actually confirmed, not just what we queued
stats = {"ok": 0, "failed": 0}


def on_delivery(err, msg):
    if err:
        stats["failed"] += 1
    else:
        stats["ok"] += 1


def make_event():
    subtotal = round(random.uniform(5, 500), 2)
    tax = round(subtotal * random.choice([0.05, 0.08, 0.18]), 2)
    return {
        "event_id": str(uuid.uuid4()),
        "order_id": random.randint(10**8, 10**9),
        "user_id": random.randint(1, 500_000),
        "event_ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
        "currency": random.choice(CURRENCIES),
        "subtotal": subtotal,
        "tax_amount": tax,
        "total": round(subtotal + tax, 2),
        "country": random.choice(COUNTRIES),
        "payment_method": random.choice(PAYMENTS),
    }


def load_chaos(path):
    """Re-read the chaos file every second so faults can be flipped live."""
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}   # missing or half-written file: fall back to defaults


def inject_faults(event, chaos):
    # Fault 1: NULL tax_amount
    if random.random() < chaos.get("null_rate", 0.005):
        event["tax_amount"] = None

    # Fault 2: schema drift (applied to a fraction of events)
    drift = chaos.get("drift", "none")
    if drift != "none" and random.random() < chaos.get("drift_rate", 1.0):
        if drift == "rename":            # tax_amount -> tax_amt
            event["tax_amt"] = event.pop("tax_amount")
        elif drift == "retype":          # number -> string
            event["subtotal"] = str(event["subtotal"])
        elif drift == "new_column":      # unexpected extra field
            event["loyalty_tier"] = random.choice(["bronze", "silver", "gold"])
    return event


def send(producer, topic, event):
    payload = json.dumps(event)
    while True:
        try:
            producer.produce(topic, key=str(event["user_id"]), value=payload,
                             callback=on_delivery)
            return
        except BufferError:
            producer.poll(0.1)  # local queue full: let delivery catch up, then retry


def main():
    ap = argparse.ArgumentParser(description="IceStream checkout event generator")
    ap.add_argument("--rate", type=int, default=2000, help="events per second")
    ap.add_argument("--bootstrap", default="localhost:29092")
    ap.add_argument("--topic", default="checkout.events")
    ap.add_argument("--chaos", default=os.path.join(os.path.dirname(__file__), "chaos.json"))
    args = ap.parse_args()

    producer = Producer({
        "bootstrap.servers": args.bootstrap,
        "linger.ms": 20,                       # batch messages for up to 20 ms
        "compression.type": "lz4",
        "queue.buffering.max.messages": 500000,
    })

    print(f"Producing {args.rate} events/sec to '{args.topic}' (Ctrl+C to stop)")
    sent = 0
    try:
        while True:
            tick = time.time()
            chaos = load_chaos(args.chaos)
            for _ in range(args.rate):
                send(producer, args.topic, inject_faults(make_event(), chaos))
                producer.poll(0)
            sent += args.rate
            elapsed = time.time() - tick
            print(f"sent={sent} delivered={stats['ok']} failed={stats['failed']} "
                  f"batch_time={elapsed:.2f}s chaos={chaos}", flush=True)
            time.sleep(max(0, 1 - elapsed))   # hold the 1-second cadence
    except KeyboardInterrupt:
        print("\nStopping, waiting for remaining messages to be delivered...")
    finally:
        producer.flush(60)                     # wait up to 60s for the queue to empty
        print(f"Final: delivered={stats['ok']} failed={stats['failed']}")


if __name__ == "__main__":
    main()
import json
import random
import time
import uuid
from datetime import datetime, timezone

from confluent_kafka import Producer

BOOTSTRAP = "localhost:29092"
TOPIC = "checkout.events"

CURRENCIES = ["USD", "EUR", "INR", "GBP"]
PAYMENTS = ["card", "upi", "paypal", "cod"]
COUNTRIES = ["US", "IN", "DE", "GB", "BR"]


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


def main():
    producer = Producer({"bootstrap.servers": BOOTSTRAP})
    sent = 0
    while True:
        for _ in range(5):  # low fixed rate for now; commit 4 makes it configurable
            e = make_event()
            producer.produce(TOPIC, key=str(e["user_id"]), value=json.dumps(e))
            producer.poll(0)
            sent += 1
        print(f"sent={sent}", flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main()
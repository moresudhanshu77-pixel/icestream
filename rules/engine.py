from dataclasses import dataclass
from typing import Callable


@dataclass
class Expectation:
    name: str
    column: str
    check: Callable[[dict], bool]   # returns True if a record passes

    def evaluate(self, batch: list[dict]) -> dict:
        failed = sum(1 for r in batch if not self.check(r))
        return {
            "expectation": self.name,
            "column": self.column,
            "failed": failed,
            "total": len(batch),
            "failure_rate": failed / len(batch) if batch else 0.0,
        }


def expect_column_values_to_not_be_null(col):
    return Expectation(
        "expect_column_values_to_not_be_null", col,
        lambda r: r.get(col) is not None,
    )


def expect_column_values_to_be_between(col, lo, hi):
    def ok(r):
        v = r.get(col)
        return isinstance(v, (int, float)) and not isinstance(v, bool) and lo <= v <= hi
    return Expectation("expect_column_values_to_be_between", col, ok)


def expect_column_values_to_be_of_type(col, typ):
    def ok(r):
        v = r.get(col)
        return isinstance(v, typ) and not isinstance(v, bool)
    return Expectation("expect_column_values_to_be_of_type", col, ok)


def expect_column_to_exist(col):
    return Expectation("expect_column_to_exist", col, lambda r: col in r)


class Suite:
    def __init__(self, expectations: list[Expectation]):
        self.expectations = expectations

    def run(self, batch: list[dict]) -> dict:
        results = [e.evaluate(batch) for e in self.expectations]
        bad_records = sum(
            1 for r in batch if any(not e.check(r) for e in self.expectations)
        )
        return {
            "results": results,
            "record_error_rate": bad_records / len(batch) if batch else 0.0,
        }
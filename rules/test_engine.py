from engine import (
    Expectation,
    Suite,
    expect_column_to_exist,
    expect_column_values_to_not_be_null,
    expect_column_values_to_be_of_type,
    expect_column_values_to_be_between,
)


def test_null_rate_detected():
    batch = [{"tax_amount": None}] * 5 + [{"tax_amount": 1.0}] * 5
    result = expect_column_values_to_not_be_null("tax_amount").evaluate(batch)
    assert result["failed"] == 5
    assert result["failure_rate"] == 0.5


def test_no_nulls_passes_clean():
    batch = [{"tax_amount": 1.0}] * 10
    result = expect_column_values_to_not_be_null("tax_amount").evaluate(batch)
    assert result["failed"] == 0
    assert result["failure_rate"] == 0.0


def test_rename_drift_detected():
    batch = [{"tax_amt": 1.0}] * 10  # renamed, tax_amount is missing
    result = expect_column_to_exist("tax_amount").evaluate(batch)
    assert result["failed"] == 10
    assert result["failure_rate"] == 1.0


def test_retype_drift_detected():
    batch = [{"subtotal": "100.0"}] * 10  # string instead of number
    result = expect_column_values_to_be_of_type("subtotal", (int, float)).evaluate(batch)
    assert result["failed"] == 10


def test_correct_type_passes():
    batch = [{"subtotal": 100.0}] * 10
    result = expect_column_values_to_be_of_type("subtotal", (int, float)).evaluate(batch)
    assert result["failed"] == 0


def test_range_check_flags_out_of_bounds():
    batch = [{"total": -5.0}, {"total": 50.0}, {"total": 200_000.0}]
    result = expect_column_values_to_be_between("total", 0, 100_000).evaluate(batch)
    assert result["failed"] == 2  # -5.0 and 200_000.0 are out of range


def test_empty_batch_does_not_error():
    result = expect_column_values_to_not_be_null("tax_amount").evaluate([])
    assert result["total"] == 0
    assert result["failure_rate"] == 0.0


def test_suite_record_error_rate_single_expectation():
    suite = Suite([expect_column_values_to_not_be_null("a")])
    report = suite.run([{"a": 1}, {"a": None}, {"a": 3}, {"a": None}])
    assert report["record_error_rate"] == 0.5


def test_suite_record_error_rate_multiple_expectations():
    # a record failing ANY expectation counts once, not once per expectation
    suite = Suite([
        expect_column_values_to_not_be_null("a"),
        expect_column_values_to_not_be_null("b"),
    ])
    batch = [
        {"a": None, "b": None},  # fails both, counts as 1 bad record
        {"a": 1, "b": None},     # fails one
        {"a": 1, "b": 2},        # passes
    ]
    report = suite.run(batch)
    assert report["record_error_rate"] == 2 / 3


def test_custom_expectation():
    is_even = Expectation("is_even", "n", lambda r: r.get("n", 0) % 2 == 0)
    batch = [{"n": 2}, {"n": 3}, {"n": 4}, {"n": 5}]
    result = is_even.evaluate(batch)
    assert result["failed"] == 2
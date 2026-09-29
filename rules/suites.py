from engine import (
    expect_column_to_exist,
    expect_column_values_to_not_be_null,
    expect_column_values_to_be_of_type,
    expect_column_values_to_be_between,
    Suite,
)

checkout_suite = Suite([
    expect_column_to_exist("tax_amount"),
    expect_column_values_to_not_be_null("tax_amount"),
    expect_column_values_to_not_be_null("subtotal"),
    expect_column_values_to_be_of_type("subtotal", (int, float)),
    expect_column_values_to_be_between("total", 0, 100_000),
    expect_column_values_to_not_be_null("event_id"),
])

# 2% is the circuit-breaker threshold used later in Week 3
ERROR_THRESHOLD = 0.02
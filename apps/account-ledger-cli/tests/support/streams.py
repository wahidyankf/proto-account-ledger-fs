"""Builders for the short streams the rule tests replay."""

HEADER = ("event", "booked", "type", "account", "amount", "value_date", "reference", "instalments")


def csv_text(rows: list[dict[str, str]]) -> str:
    """The stream file for these rows under the current header; a column a row omits is empty."""
    lines = [",".join(HEADER), *(",".join(row.get(column, "") for column in HEADER) for row in rows)]
    return "\n".join(lines) + "\n"

"""Parse labels rather than row offsets, and reconcile before accepting data.

Balances are integer thousandths of a troy ounce internally. Pledged is a
subset of Registered in the supported CME layout, never an additional stock.
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from io import BytesIO
import re

SOURCE_URL = "https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls"
SOURCE_PAGE = "https://www.cmegroup.com/solutions/clearing/operations-and-deliveries/nymex-delivery-notices.html"
FIELDS = {
    "PREV TOTAL": "previous",
    "RECEIVED": "received",
    "WITHDRAWN": "withdrawn",
    "NET CHANGE": "net_change",
    "ADJUSTMENT": "adjustment",
    "TOTAL TODAY": "today",
}
LABELS = {
    "TOTAL REGISTERED": "registered",
    "TOTAL ELIGIBLE": "eligible",
    "TOTAL PLEDGED": "pledged",
    "COMBINED TOTAL": "total",
}


class ReportError(ValueError):
    pass


def normalize(value):
    return re.sub(r"\s+", " ", str(value or "")).strip().upper()


def milli_oz(value):
    if value is None or str(value).strip() == "" or isinstance(value, bool):
        raise ReportError("Missing/non-numeric stock cell; blanks are not zero")
    raw = str(value).strip().replace(",", "")
    if raw.startswith("(") and raw.endswith(")"):
        raw = "-" + raw[1:-1]
    try:
        number = Decimal(raw)
        if not number.is_finite():
            raise ReportError("Non-finite stock cell")
        rounded = number.quantize(Decimal("0.001"), rounding=ROUND_HALF_EVEN)
        # Accept floating point noise, reject a changed unit/precision silently rounded.
        if abs(number - rounded) > Decimal("0.00001"):
            raise ReportError("Stock precision exceeds supported 0.001 troy oz")
        return int(rounded * 1000)
    except (InvalidOperation, ValueError) as exc:
        raise ReportError(f"Invalid stock cell: {value!r}") from exc


def read_workbook(blob):
    if blob.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
        import xlrd
        try:
            book = xlrd.open_workbook(file_contents=blob)
            return [(s.name, [s.row_values(i) for i in range(s.nrows)]) for s in book.sheets()], "xls"
        except xlrd.XLRDError as exc:
            raise ReportError(f"Invalid XLS: {exc}") from exc
    if blob.startswith(b"PK\x03\x04"):
        import openpyxl
        try:
            book = openpyxl.load_workbook(BytesIO(blob), read_only=True, data_only=True)
            try:
                return [(s.title, [list(r) for r in s.iter_rows(values_only=True)]) for s in book], "xlsx"
            finally:
                book.close()
        except Exception as exc:
            raise ReportError(f"Invalid XLSX: {exc}") from exc
    raise ReportError("Not an XLS/XLSX workbook (possible HTML error or access challenge)")


def parse_report(blob):
    sheets, kind = read_workbook(blob)
    candidates = [(name, rows) for name, rows in sheets
                  if any(normalize(c) == "METAL DEPOSITORY STATISTICS" for r in rows for c in r)]
    if len(candidates) != 1:
        raise ReportError("Expected exactly one Metal Depository Statistics sheet")
    name, rows = candidates[0]
    result = parse_rows(rows)
    result.update(sheet=name, file_type=kind)
    return result


def parse_rows(rows):
    cells = [normalize(c) for r in rows for c in r]
    if "GOLD" not in cells or not any(c in {"TROY OUNCE", "TROY OUNCES"} for c in cells):
        raise ReportError("Expected GOLD in Troy Ounce units")
    dates = {}
    for label, key in [("Report", "report_date"), ("Activity", "date")]:
        matches = [m.group(1) for r in rows for c in r
                   if (m := re.search(rf"{label}\s+Date\s*:\s*(\d{{1,2}}/\d{{1,2}}/\d{{4}})", str(c), re.I))]
        if len(matches) != 1:
            raise ReportError(f"Expected one {label} Date")
        try:
            dates[key] = datetime.strptime(matches[0], "%m/%d/%Y").date().isoformat()
        except ValueError as exc:
            raise ReportError(f"Invalid {label} Date") from exc
    if dates["date"] > dates["report_date"]:
        raise ReportError("Activity Date after Report Date")
    headers = [(i, r) for i, r in enumerate(rows)
               if set(FIELDS).issubset({normalize(c) for c in r}) and "DEPOSITORY" in {normalize(c) for c in r}]
    if len(headers) != 1:
        raise ReportError("Missing/ambiguous stock headers")
    header_i, header = headers[0]
    columns = {}
    for heading, field in FIELDS.items():
        indices = [i for i, v in enumerate(header) if normalize(v) == heading]
        if len(indices) != 1:
            raise ReportError(f"Duplicate header {heading}")
        columns[field] = indices[0]
    label_col = next(i for i, v in enumerate(header) if normalize(v) == "DEPOSITORY")

    def values(row, pledged=False):
        out = {}
        for field, col in columns.items():
            if col >= len(row):
                raise ReportError("Short stock row")
            if pledged and field not in {"previous", "today"}:
                out[field] = None  # CME leaves Pledged movement cells blank.
            else:
                out[field] = milli_oz(row[col])
        return out

    totals, locations, current = {}, [], None
    for i in range(header_i + 1, len(rows)):
        row = rows[i]
        label = normalize(row[label_col]) if label_col < len(row) else ""
        if label in LABELS:
            key = LABELS[label]
            if key in totals:
                raise ReportError(f"Duplicate summary row {label}")
            totals[key] = {"row": i + 1, "balances": values(row, key == "pledged")}
            current = None
        elif label in {"REGISTERED", "ELIGIBLE", "PLEDGED", "TOTAL"}:
            if current is None:
                raise ReportError("Stock category without a depository")
            key = label.lower()
            if key in current["categories"]:
                raise ReportError(f"Duplicate {label} for {current['name']}")
            current["categories"][key] = {"row": i + 1, "balances": values(row, key == "pledged")}
        elif label and not totals and all(not str(row[c] or "").strip() for c in columns.values() if c < len(row)):
            current = {"name": str(row[label_col]).strip(), "row": i + 1,
                       "enhanced_delivery": "ENHANCED DELIVERY" in label or "400 OZ" in label,
                       "categories": {}}
            locations.append(current)
    if not {"registered", "eligible", "total"}.issubset(totals) or not locations:
        raise ReportError("Missing summary rows or warehouse detail")
    if any(not {"registered", "eligible", "total"}.issubset(d["categories"]) for d in locations):
        raise ReportError("Incomplete depository detail")

    checks = []

    def equal(a, b, context):
        if a != b:
            raise ReportError(f"Reconciliation failed: {context}: {a / 1000:.3f} != {b / 1000:.3f}")
        checks.append(context)

    def reconcile(categories, context):
        for key, item in categories.items():
            v = item["balances"]
            if v["today"] < 0 or v["previous"] < 0:
                raise ReportError("Negative inventory")
            if key != "pledged":
                if v["received"] < 0 or v["withdrawn"] < 0:
                    raise ReportError("Negative receipt/withdrawal")
                equal(v["net_change"], v["received"] - v["withdrawn"], f"{context}/{key}: net movement")
                equal(v["today"], v["previous"] + v["net_change"] + v["adjustment"], f"{context}/{key}: balance bridge")
        for field in FIELDS.values():
            equal(categories["total"]["balances"][field],
                  categories["registered"]["balances"][field] + categories["eligible"]["balances"][field],
                  f"{context}: registered + eligible / {field}")
        if "pledged" in categories:
            for field in ("previous", "today"):
                if categories["pledged"]["balances"][field] > categories["registered"]["balances"][field]:
                    raise ReportError("Pledged exceeds Registered; unsupported accounting layout")
    reconcile(totals, "summary")
    for d in locations:
        reconcile(d["categories"], d["name"])
    for key, item in totals.items():
        for field, value in item["balances"].items():
            if value is None:
                continue
            detail_sum = sum(d["categories"].get(key, {"balances": {field: 0}})["balances"][field] for d in locations)
            equal(value, detail_sum, f"all depositories = summary / {key}/{field}")
    return {**dates, "unit": "troy_oz", "scope": "CME Gold Stocks official combined report (GC and 4GC)",
            "pledged_accounting": "subset_of_registered_verified_by_reconciliation",
            "summary": totals, "depositories": locations,
            "checks": checks, "parser_version": "0.1.0"}

from typing import Any, Dict, List


DEFAULT_TOLERANCE = 0.01


def compare_values(
    expected: float,
    actual: float,
    tolerance: float
) -> bool:

    return abs(expected - actual) <= tolerance


def validation_result(
    rule: str,
    expected,
    actual,
    tolerance: float,
    message_pass: str,
    message_fail: str
):

    difference = None

    if expected is not None and actual is not None:
        difference = round(
            abs(expected - actual),
            2
        )

        status = (
            "PASS"
            if difference <= tolerance
            else "FAIL"
        )

    else:

        status = "NOT_APPLICABLE"

    if status == "PASS":
        message = message_pass

    elif status == "FAIL":
        message = message_fail

    else:
        message = "Required values are missing."

    return {
        "rule": rule,
        "expected_value": expected,
        "actual_value": actual,
        "difference": difference,
        "status": status,
        "message": message
    }


def validate_invoice(
    fields: Dict[str, Any],
    tolerance: float = DEFAULT_TOLERANCE
):

    validations = []

    subtotal = fields.get("subtotal")
    discount = fields.get("discount")
    tax = fields.get("tax")
    total = fields.get("total")

    if (
        subtotal is not None
        and tax is not None
        and total is not None
    ):

        discount_value = discount or 0

        expected = (
            subtotal
            - discount_value
            + tax
        )

        validations.append(
            validation_result(
                "invoice_total_calculation",
                expected,
                total,
                tolerance,
                "Invoice total calculation is correct.",
                "Invoice total does not match subtotal - discount + tax."
            )
        )

    else:

        validations.append({
            "rule": "invoice_total_calculation",
            "expected_value": None,
            "actual_value": total,
            "difference": None,
            "status": "NOT_APPLICABLE",
            "message": "Required invoice fields are missing."
        })

    return validations


def validate_balance_sheet(
    fields: Dict[str, Any],
    tolerance: float = DEFAULT_TOLERANCE
):

    assets = fields.get("total_assets")
    liabilities = fields.get("total_liabilities")
    equity = fields.get("total_equity")

    if (
        assets is None
        or liabilities is None
        or equity is None
    ):

        return [{
            "rule": "balance_sheet_equation",
            "expected_value": None,
            "actual_value": assets,
            "difference": None,
            "status": "NOT_APPLICABLE",
            "message": "Required balance sheet fields are missing."
        }]

    expected = liabilities + equity

    return [
        validation_result(
            "balance_sheet_equation",
            expected,
            assets,
            tolerance,
            "Assets equal liabilities plus equity.",
            "Assets do not equal liabilities plus equity."
        )
    ]


def validate_profit_loss(
    fields: Dict[str, Any],
    tolerance: float = DEFAULT_TOLERANCE
):

    validations = []

    revenue = fields.get("revenue")
    cogs = fields.get("cost_of_goods_sold")
    gross_profit = fields.get("gross_profit")

    if (
        revenue is not None
        and cogs is not None
        and gross_profit is not None
    ):

        expected = revenue - cogs

        validations.append(
            validation_result(
                "gross_profit_calculation",
                expected,
                gross_profit,
                tolerance,
                "Gross profit calculation is correct.",
                "Gross profit does not equal revenue minus COGS."
            )
        )
    else:

        validations.append({
            "rule": "gross_profit_calculation",
            "expected_value": None,
            "actual_value": gross_profit,
            "difference": None,
            "status": "NOT_APPLICABLE",
            "message": "Required gross profit fields are missing."
        })

    total_income = fields.get("total_income")
    total_expenses = fields.get("total_expenses")
    net_profit = fields.get("net_profit")

    if (
        total_income is not None
        and total_expenses is not None
        and net_profit is not None
    ):

        expected = total_income - total_expenses

        validations.append(
            validation_result(
                "net_profit_calculation",
                expected,
                net_profit,
                tolerance,
                "Net profit calculation is correct.",
                "Net profit does not equal total income minus total expenses."
            )
        )
    else:

        validations.append({
            "rule": "net_profit_calculation",
            "expected_value": None,
            "actual_value": net_profit,
            "difference": None,
            "status": "NOT_APPLICABLE",
            "message": "Required net profit fields are missing."
        })

    return validations


def validate_cash_flow(
    fields: Dict[str, Any],
    tolerance: float = DEFAULT_TOLERANCE
):

    validations = []

    operating = fields.get("operating_cash_flow")
    investing = fields.get("investing_cash_flow")
    financing = fields.get("financing_cash_flow")
    net = fields.get("net_cash_flow")

    if (
        operating is not None
        and investing is not None
        and financing is not None
        and net is not None
    ):

        expected = operating + investing + financing

        validations.append(
            validation_result(
                "net_cash_flow_calculation",
                expected,
                net,
                tolerance,
                "Net cash flow calculation is correct.",
                "Net cash flow does not match operating + investing + financing."
            )
        )

    else:

        validations.append({
            "rule": "net_cash_flow_calculation",
            "expected_value": None,
            "actual_value": net,
            "difference": None,
            "status": "NOT_APPLICABLE",
            "message": "Required cash flow fields are missing."
        })

    opening = fields.get("opening_cash")
    closing = fields.get("closing_cash")

    if (
        opening is not None
        and net is not None
        and closing is not None
    ):

        expected = opening + net

        validations.append(
            validation_result(
                "closing_cash_calculation",
                expected,
                closing,
                tolerance,
                "Closing cash calculation is correct.",
                "Closing cash does not equal opening cash plus net cash flow."
            )
        )

    else:

        validations.append({
            "rule": "closing_cash_calculation",
            "expected_value": None,
            "actual_value": closing,
            "difference": None,
            "status": "NOT_APPLICABLE",
            "message": "Required opening/closing cash fields are missing."
        })

    return validations


def calculate_overall_status(
    validations: List[Dict[str, Any]]
):

    applicable = [
        item
        for item in validations
        if item["status"] != "NOT_APPLICABLE"
    ]

    if not applicable:
        return "NOT_APPLICABLE"

    if any(
        item["status"] == "FAIL"
        for item in applicable
    ):
        return "FAIL"

    return "PASS"


def validate_financial_data(
    document_type: str,
    fields: Dict[str, Any],
    tolerance: float = DEFAULT_TOLERANCE
):

    document_type = document_type.lower()

    if document_type == "invoice":
        validations = validate_invoice(
            fields,
            tolerance
        )

    elif document_type in ["balance_sheet", "balance sheet"]:
        validations = validate_balance_sheet(
            fields,
            tolerance
        )

    elif document_type in [
        "profit_loss",
        "profit and loss",
        "profit & loss"
    ]:
        validations = validate_profit_loss(
            fields,
            tolerance
        )

    elif document_type in [
        "cash_flow",
        "cash flow",
        "cash flow statement"
    ]:
        validations = validate_cash_flow(
            fields,
            tolerance
        )

    else:
        raise ValueError(
            f"Unsupported document type: {document_type}"
        )

    return {
        "document_type": document_type,
        "overall_status": calculate_overall_status(
            validations
        ),
        "tolerance": tolerance,
        "validations": validations
    }
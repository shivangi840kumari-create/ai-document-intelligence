import re
from typing import Any


# ---------------------------------------------------------
# BASIC HELPERS
# ---------------------------------------------------------

def clean_number(value: str):
    if value is None:
        return None

    value = str(value).strip()

    negative = False

    # Example: (150.00) -> -150.00
    if value.startswith("(") and value.endswith(")"):
        negative = True
        value = value[1:-1]

    value = (
        value.replace(",", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
        .strip()
    )

    try:
        number = float(value)

        if negative:
            number = -number

        return number

    except ValueError:
        return None


def find_amount(text: str, keywords):
    """
    Find an amount on a line containing one of the keywords.

    If no matching amount is found, return None.
    """

    lines = text.splitlines()

    # Check more specific keywords first
    keywords = sorted(keywords, key=len, reverse=True)

    amount_pattern = (
        r"[-(]?\s*"
        r"[₹$€£]?\s*"
        r"\d[\d,]*(?:\.\d+)?"
        r"\s*\)?"
    )

    for keyword in keywords:
        keyword_lower = keyword.lower()

        for line in lines:
            lower = line.lower()

            if keyword_lower in lower:
                matches = re.findall(
                    amount_pattern,
                    line
                )

                if matches:
                    number = clean_number(matches[-1])

                    if number is not None:
                        return number

    return None


def find_labeled_value(text: str, labels):
    """
    Extract text appearing after labels such as:

    Client: XYZ Corporation
    Customer: ABC Ltd
    Invoice Number: INV-001

    Returns None if the label/value is not present.
    """

    lines = text.splitlines()

    labels = sorted(labels, key=len, reverse=True)

    for label in labels:

        pattern = re.compile(
            rf"^\s*{re.escape(label)}\s*[:\-]\s*(.+?)\s*$",
            re.IGNORECASE
        )

        for line in lines:

            match = pattern.match(line)

            if match:
                value = match.group(1).strip()

                if value:
                    return value

    return None


def find_date(text: str):
    """
    Extract a date only when a date is explicitly present.

    Supported examples:
    2025-04-01
    01/04/2025
    01-04-2025
    2025/04/01
    """

    lines = text.splitlines()

    date_pattern = (
        r"\b("
        r"\d{4}[-/]\d{2}[-/]\d{2}"
        r"|"
        r"\d{2}[-/]\d{2}[-/]\d{4}"
        r")\b"
    )

    for line in lines:

        if re.search(
            r"invoice\s*date|date",
            line,
            re.IGNORECASE
        ):
            match = re.search(
                date_pattern,
                line
            )

            if match:
                return match.group(1)

    return None


def find_currency(text: str):
    """
    Detect currency from an explicit symbol.

    $ -> USD
    ₹ -> INR
    € -> EUR
    £ -> GBP

    If no currency is visible, return None.
    """

    if "₹" in text:
        return "INR"

    if "$" in text:
        return "USD"

    if "€" in text:
        return "EUR"

    if "£" in text:
        return "GBP"

    # Also support explicit currency names/codes
    currency_patterns = [
        (r"\bUSD\b|\bUS\s*DOLLARS?\b", "USD"),
        (r"\bINR\b|\bINDIAN\s*RUPEES?\b", "INR"),
        (r"\bEUR\b|\bEUROS?\b", "EUR"),
        (r"\bGBP\b|\bPOUNDS?\b", "GBP"),
    ]

    for pattern, currency in currency_patterns:

        if re.search(pattern, text, re.IGNORECASE):
            return currency

    return None


def find_invoice_number(text: str):
    """
    Extract invoice number only when an explicit invoice-number
    label exists.

    Example:
    Invoice Number: INV-1001
    Invoice No: INV-1001
    Invoice #: INV-1001
    """

    lines = text.splitlines()

    pattern = re.compile(
        r"^\s*invoice\s*"
        r"(?:number|no\.?|#)"
        r"\s*[:\-]?\s*(.+?)\s*$",
        re.IGNORECASE
    )

    for line in lines:

        match = pattern.match(line)

        if match:
            value = match.group(1).strip()

            if value:
                return value

    return None


# ---------------------------------------------------------
# INVOICE EXTRACTION
# ---------------------------------------------------------

def extract_invoice(text: str):

    return {
        "invoice_number": find_invoice_number(text),

        "invoice_date": find_date(text),

        "vendor": find_labeled_value(
            text,
            [
                "Vendor",
                "Seller",
                "Supplier",
                "From"
            ]
        ),

        "customer": find_labeled_value(
            text,
            [
                "Customer",
                "Client",
                "Buyer",
                "Bill To"
            ]
        ),

        "currency": find_currency(text),

        "subtotal": find_amount(
            text,
            [
                "subtotal",
                "sub total"
            ]
        ),

        "discount": find_amount(
            text,
            [
                "discount"
            ]
        ),

        "tax": find_amount(
            text,
            [
                "tax",
                "gst",
                "vat"
            ]
        ),

        "total": find_amount(
            text,
            [
                "grand total",
                "total amount",
                "total"
            ]
        )
    }


# ---------------------------------------------------------
# BALANCE SHEET
# ---------------------------------------------------------

def extract_balance_sheet(text: str):

    return {
        "total_assets": find_amount(
            text,
            ["total assets"]
        ),

        "total_liabilities": find_amount(
            text,
            ["total liabilities"]
        ),

        "total_equity": find_amount(
            text,
            [
                "total equity",
                "shareholders equity"
            ]
        )
    }


# ---------------------------------------------------------
# PROFIT & LOSS
# ---------------------------------------------------------

def extract_profit_loss(text: str):

    return {
        "revenue": find_amount(
            text,
            [
                "revenue",
                "sales"
            ]
        ),

        "cost_of_goods_sold": find_amount(
            text,
            [
                "cost of goods sold",
                "cogs"
            ]
        ),

        "gross_profit": find_amount(
            text,
            [
                "gross profit"
            ]
        ),

        "total_income": find_amount(
            text,
            [
                "total income"
            ]
        ),

        "total_expenses": find_amount(
            text,
            [
                "total expenses"
            ]
        ),

        "net_profit": find_amount(
            text,
            [
                "net profit",
                "net income"
            ]
        )
    }


# ---------------------------------------------------------
# CASH FLOW
# ---------------------------------------------------------

def extract_cash_flow(text: str):

    return {
        "opening_cash": find_amount(
            text,
            [
                "opening cash",
                "cash at beginning"
            ]
        ),

        "operating_cash_flow": find_amount(
            text,
            [
                "operating cash flow"
            ]
        ),

        "investing_cash_flow": find_amount(
            text,
            [
                "investing cash flow"
            ]
        ),

        "financing_cash_flow": find_amount(
            text,
            [
                "financing cash flow"
            ]
        ),

        "net_cash_flow": find_amount(
            text,
            [
                "net cash flow"
            ]
        ),

        "closing_cash": find_amount(
            text,
            [
                "closing cash",
                "cash at end"
            ]
        )
    }


# ---------------------------------------------------------
# MAIN EXTRACTION FUNCTION
# ---------------------------------------------------------

def extract_document(
    document_type: str,
    text: str
):

    document_type = document_type.lower().strip()

    if document_type == "invoice":

        fields = extract_invoice(text)

    elif document_type in [
        "balance_sheet",
        "balance sheet"
    ]:

        fields = extract_balance_sheet(text)

    elif document_type in [
        "profit_loss",
        "profit and loss",
        "profit & loss"
    ]:

        fields = extract_profit_loss(text)

    elif document_type in [
        "cash_flow",
        "cash flow",
        "cash flow statement"
    ]:

        fields = extract_cash_flow(text)

    else:

        raise ValueError(
            f"Unsupported document type: {document_type}"
        )

    return {
        "document_type": document_type,
        "fields": fields
    }
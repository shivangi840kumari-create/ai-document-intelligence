from app.services.extraction_service import extract_document


def test_invoice_extraction():
    text = """
    Invoice Number: INV-1001
    Invoice Date: 01/04/2025
    Vendor: ABC Ltd
    Customer: XYZ Corporation
    Subtotal: $100.00
    Tax: $10.00
    Total: $110.00
    """

    result = extract_document(
        document_type="invoice",
        text=text
    )

    assert result["document_type"] == "invoice"
    assert result["fields"]["invoice_number"] == "INV-1001"
    assert result["fields"]["vendor"] == "ABC Ltd"


def test_balance_sheet_extraction():
    text = """
    Balance Sheet
    Total Assets: $1000
    Total Liabilities: $400
    Total Equity: $600
    """

    result = extract_document(
        document_type="balance_sheet",
        text=text
    )

    assert result["document_type"] == "balance_sheet"
    assert result["fields"]["total_assets"] == 1000
    assert result["fields"]["total_liabilities"] == 400
    assert result["fields"]["total_equity"] == 600


def test_profit_loss_extraction():
    text = """
    Revenue: $1000
    Cost of Goods Sold: $400
    Gross Profit: $600
    Total Income: $1000
    Total Expenses: $700
    Net Profit: $300
    """

    result = extract_document(
        document_type="profit_loss",
        text=text
    )

    assert result["document_type"] == "profit_loss"
    assert result["fields"]["revenue"] == 1000
    assert result["fields"]["net_profit"] == 300


def test_cash_flow_extraction():
    text = """
    Operating Cash Flow: $500
    Investing Cash Flow: -$100
    Financing Cash Flow: $100
    Net Cash Flow: $500
    Opening Cash: $1000
    Closing Cash: $1500
    """

    result = extract_document(
        document_type="cash_flow",
        text=text
    )

    assert result["document_type"] == "cash_flow"
    assert result["fields"]["net_cash_flow"] == 500
    assert result["fields"]["closing_cash"] == 1500
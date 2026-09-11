from app.services.financial_validation_service import validate_financial_data


def test_invoice_pass():
    data = {
        "subtotal": 100,
        "discount": 10,
        "tax": 9,
        "total": 99
    }

    result = validate_financial_data("invoice", data)

    assert result["overall_status"] == "PASS"


def test_invoice_fail():
    data = {
        "subtotal": 100,
        "discount": 10,
        "tax": 9,
        "total": 150
    }

    result = validate_financial_data("invoice", data)

    assert result["overall_status"] == "FAIL"


def test_balance_sheet_pass():
    data = {
        "total_assets": 1000,
        "total_liabilities": 400,
        "total_equity": 600
    }

    result = validate_financial_data("balance_sheet", data)

    assert result["overall_status"] == "PASS"


def test_profit_loss_pass():
    data = {
        "revenue": 1000,
        "cost_of_goods_sold": 400,
        "gross_profit": 600,
        "total_income": 1000,
        "total_expenses": 700,
        "net_profit": 300
    }

    result = validate_financial_data("profit_loss", data)

    assert result["overall_status"] == "PASS"


def test_cash_flow_pass():
    data = {
        "operating_cash_flow": 500,
        "investing_cash_flow": -100,
        "financing_cash_flow": 100,
        "net_cash_flow": 500,
        "opening_cash": 1000,
        "closing_cash": 1500
    }

    result = validate_financial_data("cash_flow", data)

    assert result["overall_status"] == "PASS"
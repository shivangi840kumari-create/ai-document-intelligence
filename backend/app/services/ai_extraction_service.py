import json
import logging
from typing import Any, Dict

from google import genai

from app.core.config import settings

logger = logging.getLogger(__name__)


def _extract_json_from_response(text: str) -> Dict[str, Any]:
    text = text.strip()

    # Remove markdown code fences if Gemini returns them
    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.lower().startswith("json"):
            text = text[4:].strip()

    return json.loads(text)


def extract_with_gemini(
    document_type: str,
    pages: list
) -> Dict[str, Any]:

    if not settings.GEMINI_API_KEY:
        raise RuntimeError("Gemini API key is not configured.")

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )

    page_text = []

    for page in pages:
        page_text.append(
            f"--- PAGE {page['page_number']} ---\n"
            f"{page['text']}"
        )

    document_text = "\n\n".join(page_text)

    prompt = f"""
You are a financial document extraction system.

Extract information from this {document_type} document.

STRICT RULES:

1. Extract ONLY information visibly present in the supplied document text.
2. Never invent, estimate, calculate, or infer missing values.
3. If a value is missing or unreadable, return null.
4. Preserve the original meaning of the document.
5. Preserve negative values and financial signs.
6. Include evidence/source text for important extracted fields whenever possible.
7. Include the page number where the value was found.
8. Currency must be returned as a standard ISO 4217 currency code whenever identifiable.
Examples: "$" or "US$" → "USD", "€" → "EUR", "£" → "GBP", "₹" → "INR".
If the currency cannot be determined reliably, return null.
9. Numeric financial values must be JSON numbers, not strings.
10. Do not perform financial validation.
11. Return ONLY valid JSON.
12. Do not return markdown or explanations.
DOCUMENT TYPE:
{document_type}

Return exactly this structure:

{{
  "document_type": "{document_type}",
  "fields": {{}},
  "tables": []
}}

For every important field use:

{{
  "value": null,
  "confidence": 0.0,
  "evidence": null,
  "page_number": null
}}

Confidence must be between 0 and 1.

FOR INVOICE EXTRACT:

invoice_number
invoice_date
vendor
customer
currency
subtotal
discount
tax
total

FOR BALANCE SHEET EXTRACT:

company_name
statement_date
currency
total_assets
total_liabilities
total_equity

FOR PROFIT AND LOSS EXTRACT:

company_name
statement_period
currency
revenue
cogs
gross_profit
total_income
total_expenses
net_profit

FOR CASH FLOW STATEMENT EXTRACT:

company_name
statement_period
currency
operating_cash_flow
investing_cash_flow
financing_cash_flow
net_cash_flow
opening_cash
closing_cash

Also extract meaningful visible line items and comparative periods.

TABLE FORMAT:

{{
  "name": "table name",
  "columns": ["column1", "column2"],
  "rows": [
    {{
      "column1": "value",
      "column2": "value"
    }}
  ],
  "page_number": 1
}}

DOCUMENT TEXT:

{document_text}
"""

    try:

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt
        )

        response_text = response.text or ""

        if not response_text.strip():
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return _extract_json_from_response(
            response_text
        )

    except Exception as exc:

        logger.exception(
            "Gemini extraction failed: %s",
            exc
        )

        raise
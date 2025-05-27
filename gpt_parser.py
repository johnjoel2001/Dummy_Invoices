from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_order_info(message):
    prompt = f"""
Extract the company name and all order lines from this message:
"{message}"

Each order line should include:
- quantity (number of pairs)
- rate (price per pair)
- item description (e.g., "60 Gms Grey")

Return JSON like this:
{{
  "company": "Deivamani Ambathur",
  "orders": [
    {{"description": "60 Gms Grey", "quantity": 70, "rate": 6.8}},
    {{"description": "80 Gms Grey", "quantity": 70, "rate": 8.5}},
    {{"description": "Coated Gloves Red and Black", "quantity": 2, "rate": 26}}
  ]
}}
Only return valid JSON.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    try:
        return eval(response.choices[0].message.content)
    except:
        return None

def extract_payment_info(message):
    prompt = f"""
Extract the company name and amount from this message:
"{message}"
Return JSON like:
{{"company": "XYZ", "amount": 1234}}
Only return valid JSON.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    try:
        return eval(response.choices[0].message.content)
    except:
        return None

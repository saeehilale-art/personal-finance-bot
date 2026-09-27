import os
from dotenv import load_dotenv

load_dotenv()

# Try Gemini if available
try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except Exception:
    client = None


def generate_budget(income, expense):

    savings = income - expense

    # ----- Gemini -----
    if client:
        try:
            prompt = f"""
You are a personal finance advisor.

Income: ₹{income}
Expense: ₹{expense}
Savings: ₹{savings}

Give:
1. Financial Health
2. Overspending Analysis
3. Savings Tips
4. Budget Plan
5. Emergency Fund Advice

Keep it under 150 words.
"""
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            return response.text

        except Exception:
            pass

    # ----- Offline AI Fallback -----
    spent = (expense / income * 100) if income else 0

    if spent > 80:
        health = "Poor"
        tip = "Reduce non-essential spending and review entertainment expenses."
    elif spent > 60:
        health = "Moderate"
        tip = "Increase savings by setting a monthly budget limit."
    else:
        health = "Excellent"
        tip = "Great discipline! Continue building an emergency fund."

    return f"""
1. Financial Health
{health}

2. Overspending Analysis
You have spent {spent:.1f}% of your monthly income.

3. Savings Recommendation
Current Savings: ₹{savings}

4. Budget Plan
Needs: 50%
Wants: 30%
Savings: 20%

5. Emergency Fund Advice
Maintain at least 3–6 months of essential expenses.
"""
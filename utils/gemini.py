import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()  # if you’re using a .env file

api_key = os.getenv("GEMINI_API_KEY")
print("Gemini API Key:", api_key)        # <-- no keyword arg here
genai.configure(api_key=api_key)        # <-- configure takes api_key=…

model = genai.GenerativeModel("gemini-2.0-flash-001")

def get_remedies(disease, deficiency):
    prompt = f"""
    Suggest remedies and solutions for the following issues in coffee plants , also add any checmial substance they can use without harming the environment much:

    - Disease: {disease}
    - Nutrient Deficiency: {deficiency}

    Use simple bullet points. No special characters.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Gemini API error: {e}"

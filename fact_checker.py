import os

from dotenv import load_dotenv

import google.generativeai as genai



# =========================
# LOAD ENVIRONMENT
# =========================

load_dotenv()


api_key = os.getenv(
    "GEMINI_API_KEY"
)



# =========================
# GEMINI SETUP
# =========================

gemini_model = None


try:


    if api_key:


        genai.configure(
            api_key=api_key
        )


        gemini_model = genai.GenerativeModel(
            "gemini-1.5-flash"
        )


        print(
            "Gemini AI loaded successfully"
        )


    else:


        print(
            "Gemini API key not found"
        )



except Exception as e:


    print(
        "Gemini loading error:",
        e
    )








# =========================
# VERIFY NEWS
# =========================

def verify_news(news):



    if gemini_model is None:


        return """

STATUS: ERROR

CONFIDENCE: 0%

CATEGORY:
Gemini Configuration


EXPLANATION:
Gemini AI is not available.
Using local ML backup.


CORRECT INFORMATION:
Unavailable.


LATEST VERIFIED INFORMATION:
Unavailable.

"""






    prompt = f"""


You are FactShield AI.

You are a real-time fact verification system.


Check whether the user claim is:

REAL

FAKE

UNCERTAIN



Verify:

- Politics
- Government
- Health
- Science
- Technology
- Sports
- Education
- Viral social media claims



Rules:

Do not check grammar.

Verify only facts.


USER CLAIM:


\"\"\"

{news}

\"\"\"


Reply exactly:


STATUS:


CONFIDENCE:


CATEGORY:


EXPLANATION:


CORRECT INFORMATION:


LATEST VERIFIED INFORMATION:


"""





    try:



        response = gemini_model.generate_content(


            prompt,


            generation_config={


                "temperature": 0.0


            }


        )



        return response.text








    except Exception as error:



        error_text = str(error)





        if (

            "429" in error_text

            or

            "RESOURCE_EXHAUSTED" in error_text

            or

            "quota" in error_text.lower()

        ):



            return """

STATUS: API LIMIT REACHED

CONFIDENCE: 0%

CATEGORY:
Gemini API Limit


EXPLANATION:
Gemini request limit finished.
FactShield will continue using ML backup.


CORRECT INFORMATION:
Unable to verify using Gemini now.


LATEST VERIFIED INFORMATION:
Try again after quota reset.

"""






        return f"""

STATUS: ERROR

CONFIDENCE: 0%

CATEGORY:
Gemini Error


EXPLANATION:

{error_text}


CORRECT INFORMATION:
Unavailable.


LATEST VERIFIED INFORMATION:
Unavailable.

"""

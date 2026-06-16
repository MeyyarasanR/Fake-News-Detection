import os

from dotenv import load_dotenv

from google import genai

from google.genai import types



# =========================
# Load Environment
# =========================

load_dotenv()


api_key = os.getenv(
    "GEMINI_API_KEY"
)


if not api_key:

    raise Exception(
        "GEMINI_API_KEY missing"
    )



# =========================
# Gemini Client
# =========================

client = genai.Client(

    api_key=api_key

)





# =========================
# Verify News Function
# =========================

def verify_news(news):


    prompt = f"""


You are FactShield AI.

You are an advanced real-time
fact verification system.


Your job:

Check whether the user information
is REAL or FAKE using latest facts.


You must verify:

1. Tamil Nadu
- Chief Minister
- Ministers
- Political parties
- Elections
- Government orders
- Holidays
- Local announcements


2. India
- Prime Minister
- Government
- Parliament
- Supreme Court
- RBI
- ISRO


3. World
- Leaders
- Countries
- International events


4. Health
- Diseases
- Medicines
- Treatments
- Medical claims


5. Science
- Space
- NASA
- ISRO
- Research


6. Technology
- AI
- Cyber security
- Companies


7. Sports
- Cricket
- Olympics
- Records


8. Education
- Exams
- Universities


9. Viral Messages
- WhatsApp forwards
- Social media rumours



IMPORTANT:

Never check grammar.

Never judge by writing style.

Only verify the FACT.

Always check:
- person names
- dates
- positions
- numbers
- events



Rules:

Correct information:

STATUS: REAL


Wrong information:

STATUS: FAKE


Not enough proof:

STATUS: UNCERTAIN




USER CLAIM:


\"\"\"

{news}

\"\"\"




Reply only:


STATUS:


CONFIDENCE:


CATEGORY:


EXPLANATION:


CORRECT INFORMATION:


LATEST VERIFIED INFORMATION:


"""


    try:


        response = client.models.generate_content(


            model=

            "gemini-2.0-flash-lite",


            contents=

            prompt,


            config=types.GenerateContentConfig(


                tools=[


                    types.Tool(


                        google_search=

                        types.GoogleSearch()


                    )


                ],


                temperature=0.0


            )


        )


        return response.text




    except Exception as error:


        error_text = str(error)



        # =====================
        # Quota limit handling
        # =====================

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:


            return """

STATUS: API LIMIT REACHED

CONFIDENCE: 0%

CATEGORY:
Gemini API Limit


EXPLANATION:
Your Gemini free API request limit is finished.
FactShield AI is working correctly.
Try again after quota reset.


CORRECT INFORMATION:
Unable to verify now because API quota ended.


LATEST VERIFIED INFORMATION:
Gemini verification temporarily unavailable.

"""



        # =====================
        # Other errors
        # =====================


        return f"""

STATUS: ERROR

CONFIDENCE: 0%

CATEGORY:
System Error


EXPLANATION:

{error_text}


CORRECT INFORMATION:
Unable to check.


LATEST VERIFIED INFORMATION:
Unavailable.

"""
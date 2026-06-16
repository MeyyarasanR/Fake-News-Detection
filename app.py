import os
import re
import pickle

from flask import Flask, render_template, request, jsonify

from fact_checker import verify_news
from fact_database import local_fact_check


app = Flask(__name__)


# =========================
# GLOBAL OBJECTS
# =========================

model = None
vectorizer = None



# =========================
# CLEAN TEXT
# =========================

def clean_text(text):

    if not isinstance(text, str):
        return ""


    text = text.lower()


    text = re.sub(
        r"[^a-zA-Z\s]",
        " ",
        text
    )


    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()


    return text







# =========================
# LOAD ML MODEL
# =========================

def load_ml_assets():

    global model
    global vectorizer


    try:


        print(
            "Loading ML model..."
        )


        with open(
            "model.pkl",
            "rb"
        ) as f:

            model = pickle.load(f)



        with open(
            "vector.pkl",
            "rb"
        ) as f:

            vectorizer = pickle.load(f)



        print(
            "ML model loaded successfully"
        )



    except Exception as error:


        print(
            "ML loading error:",
            error
        )









# =========================
# HOME
# =========================

@app.route("/")
def index():


    return render_template(
        "index.html"
    )









# =========================
# PREDICT API
# =========================

@app.route(
    "/predict",
    methods=["POST"]
)

def predict():


    try:


        data = request.get_json()


        text_content = data.get(
            "text",
            ""
        ).strip()



        if not text_content:


            return jsonify({

                "status":
                "error",

                "message":
                "Please enter news"

            })







        # =====================
        # LOCAL FACT DATABASE
        # =====================


        local_result = local_fact_check(
            text_content
        )



        if local_result:


            upper = local_result.upper()



            if "STATUS: FAKE" in upper:

                prediction = "Fake"


            elif "STATUS: REAL" in upper:

                prediction = "Real"


            else:

                prediction = "Uncertain"




            return jsonify({


                "status":
                "success",


                "prediction":
                prediction,


                "confidence":
                100,


                "verification_mode":
                "Local Fact Database",


                "ai_verification":
                local_result

            })









        # =====================
        # GEMINI CHECK
        # =====================


        ai_result = verify_news(
            text_content
        )


        upper_ai = ai_result.upper()






        if "STATUS: FAKE" in upper_ai:


            return jsonify({

                "status":
                "success",

                "prediction":
                "Fake",

                "confidence":
                95,

                "verification_mode":
                "Gemini Live Verification",

                "ai_verification":
                ai_result

            })






        elif "STATUS: REAL" in upper_ai:


            return jsonify({

                "status":
                "success",

                "prediction":
                "Real",

                "confidence":
                95,

                "verification_mode":
                "Gemini Live Verification",

                "ai_verification":
                ai_result

            })






        elif "STATUS: UNCERTAIN" in upper_ai:


            return jsonify({

                "status":
                "success",

                "prediction":
                "Uncertain",

                "confidence":
                50,

                "verification_mode":
                "Gemini Live Verification",

                "ai_verification":
                ai_result

            })











        # =====================
        # ML BACKUP
        # =====================


        if model is None or vectorizer is None:


            return jsonify({

                "status":
                "error",

                "message":
                "ML model unavailable"

            })





        cleaned = clean_text(
            text_content
        )


        vector = vectorizer.transform(
            [cleaned]
        )



        output = model.predict(
            vector
        )[0]



        probability = model.predict_proba(
            vector
        )[0]



        confidence = (
            probability[output]
            *
            100
        )



        if confidence > 90:

            confidence = 90




        if output == 1:

            prediction = "Fake"


        else:

            prediction = "Real"






        report = f"""

STATUS: {prediction.upper()}

CONFIDENCE: {round(confidence,2)}%

CATEGORY:
Offline Machine Learning

EXPLANATION:
Live AI verification unavailable.

FactShield used backup detection system.

SYSTEM:
TF-IDF + Logistic Regression

"""





        return jsonify({


            "status":
            "success",


            "prediction":
            prediction,


            "confidence":
            round(
                confidence,
                2
            ),


            "verification_mode":
            "Offline ML Backup",


            "ai_verification":
            report


        })










    except Exception as error:


        return jsonify({

            "status":
            "error",

            "message":
            str(error)

        })










# =========================
# START
# =========================

load_ml_assets()



if __name__ == "__main__":


    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    app.run(

        host="0.0.0.0",

        port=port

    )
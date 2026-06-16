def local_fact_check(news):

    text = news.lower()


    # =====================
    # INDIA PRIME MINISTER
    # =====================

    if "prime minister of india" in text:

        if (
            "narendra modi" in text
            or
            "modi" in text
        ):

            return """

STATUS: REAL

CONFIDENCE: 100%

CATEGORY:
Indian Politics

EXPLANATION:
The claim is correct.

CORRECT INFORMATION:
Narendra Modi is the Prime Minister of India.

"""

        else:

            return """

STATUS: FAKE

CONFIDENCE: 100%

CATEGORY:
Indian Politics

EXPLANATION:
The mentioned person is not the Prime Minister of India.

CORRECT INFORMATION:
Narendra Modi is the current Prime Minister of India.

"""




    # =====================
    # SEEMAN
    # =====================

    if "seeman" in text:

        if (
            "naam tamilar" in text
            or
            "ntk" in text
        ):

            return """

STATUS: REAL

CONFIDENCE: 100%

CATEGORY:
Tamil Nadu Politics

EXPLANATION:
Seeman is associated with Naam Tamilar Katchi.

CORRECT INFORMATION:
Seeman is the chief coordinator of Naam Tamilar Katchi.

"""

        else:

            return None





    # =====================
    # UNKNOWN
    # =====================

    return None
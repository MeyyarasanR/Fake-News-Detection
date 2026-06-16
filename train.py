import os
import sys
import re
import pickle
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


def clean_text(text):

    if not isinstance(text, str):
        return ""

    text = text.lower()

    text = re.sub(
        r'^.*?\b(reuters)\b\s*[-—–]+\s*',
        '',
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r'[^a-zA-Z\s]',
        ' ',
        text
    )

    text = re.sub(
        r'\s+',
        ' ',
        text
    ).strip()

    return text



def main():

    print("=== Fake News Detection Training ===")


    fake_path = os.path.join(
        "dataset",
        "Fake.csv"
    )

    true_path = os.path.join(
        "dataset",
        "True.csv"
    )

    custom_path = "custom_data.csv"


    if (
        not os.path.exists(fake_path)
        or not os.path.exists(true_path)
    ):
        print("Dataset files missing")
        sys.exit(1)


    print("Loading datasets...")


    df_fake = pd.read_csv(fake_path)

    df_true = pd.read_csv(true_path)


    df_fake["label"] = 1

    df_true["label"] = 0



    if os.path.exists(custom_path):

        df_custom = pd.read_csv(custom_path)

        print(
            "Custom news loaded:",
            len(df_custom)
        )

    else:

        df_custom = pd.DataFrame(
            columns=[
                "text",
                "label"
            ]
        )



    print(
        "Fake:",
        len(df_fake)
    )

    print(
        "Real:",
        len(df_true)
    )


    if "title" not in df_custom.columns:

        df_custom["title"] = ""


    df = pd.concat(
        [
            df_fake,
            df_true,
            df_custom
        ],
        ignore_index=True
    )


    df = df.dropna(
        subset=[
            "text",
            "label"
        ]
    )


    df["full_text"] = (

        df.get(
            "title",
            ""
        ).astype(str)

        + " "

        + df["text"].astype(str)

    )


    print("Cleaning text...")


    df["cleaned_text"] = (

        df["full_text"]
        .apply(clean_text)

    )


    X_train, X_test, y_train, y_test = train_test_split(

        df["cleaned_text"],

        df["label"],

        test_size=0.2,

        random_state=42,

        stratify=df["label"]

    )


    print(
        "Training data:",
        len(X_train)
    )


    print("Creating TF-IDF...")


    vectorizer = TfidfVectorizer(

        stop_words="english",

        max_df=0.9,

        min_df=2,

        ngram_range=(1,3),

        max_features=50000

    )


    X_train_vec = vectorizer.fit_transform(
        X_train
    )


    X_test_vec = vectorizer.transform(
        X_test
    )


    print("Training Logistic Regression...")


    model = LogisticRegression(

        max_iter=2000,

        C=2,

        random_state=42

    )


    model.fit(
        X_train_vec,
        y_train
    )


    prediction = model.predict(
        X_test_vec
    )


    accuracy = accuracy_score(
        y_test,
        prediction
    )


    print(
        "Accuracy:",
        round(
            accuracy * 100,
            2
        ),
        "%"
    )


    print(
        classification_report(
            y_test,
            prediction,
            target_names=[
                "Real News",
                "Fake News"
            ]
        )
    )


    pickle.dump(
        model,
        open(
            "model.pkl",
            "wb"
        )
    )


    pickle.dump(
        vectorizer,
        open(
            "vector.pkl",
            "wb"
        )
    )


    print(
        "SUCCESS: Updated model.pkl and vector.pkl"
    )



if __name__ == "__main__":

    main()

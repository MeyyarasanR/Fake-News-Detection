import os
import sys
import re
import pickle
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


def clean_text(text):

    if not isinstance(text, str):
        return ""

    text = text.lower()

    # remove Reuters/source patterns
    text = re.sub(
        r'^.*?\b(reuters)\b\s*[-—–]+\s*',
        '',
        text,
        flags=re.IGNORECASE
    )

    # remove location prefixes
    text = re.sub(
        r'^[a-z\s]{3,20}\s*[-—–]+\s*',
        '',
        text
    )

    # keep alphabets only
    text = re.sub(
        r'[^a-zA-Z\s]',
        ' ',
        text
    )

    # remove extra spaces
    text = re.sub(
        r'\s+',
        ' ',
        text
    ).strip()

    return text



def main():

    print("=== Upgraded Fake News Detection Training ===")


    # Dataset paths
    fake_path = os.path.join(
        "dataset",
        "Fake.csv"
    )

    true_path = os.path.join(
        "dataset",
        "True.csv"
    )

    custom_path = "custom_data.csv"



    # check files

    if (
        not os.path.exists(fake_path)
        or not os.path.exists(true_path)
    ):
        print("Dataset missing")
        sys.exit(1)



    print("Loading datasets...")


    df_fake = pd.read_csv(fake_path)

    df_true = pd.read_csv(true_path)



    # Your Indian updated news file

    if os.path.exists(custom_path):

        df_custom = pd.read_csv(custom_path)

        print(
            f"Loaded custom Indian news: {len(df_custom)}"
        )

    else:

        df_custom = pd.DataFrame(
            columns=[
                "title",
                "text",
                "label"
            ]
        )



    print(
        f"Fake news: {len(df_fake)}"
    )

    print(
        f"True news: {len(df_true)}"
    )



    # labels

    df_fake["label"] = 1

    df_true["label"] = 0



    # add empty title if missing

    df_custom["title"] = ""



    # combine all data

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
        df["title"].astype(str)
        + " "
        + df["text"].astype(str)
    )



    print("Cleaning text...")


    df["cleaned_text"] = (
        df["full_text"]
        .apply(clean_text)
    )


    df = df[
        df["cleaned_text"] != ""
    ]



    print("Splitting data...")


    X_train, X_val, y_train, y_val = train_test_split(

        df["cleaned_text"],

        df["label"],

        test_size=0.2,

        random_state=42,

        stratify=df["label"]

    )



    print(
        "Training size:",
        len(X_train)
    )


    vectorizer = TfidfVectorizer(

        stop_words="english",

        max_df=0.7,

        ngram_range=(1,2),

        max_features=25000

    )


    X_train_vec = vectorizer.fit_transform(
        X_train
    )


    X_val_vec = vectorizer.transform(
        X_val
    )



    models = {


        "Logistic Regression":
        LogisticRegression(
            max_iter=1000,
            random_state=42
        ),


        "Naive Bayes":
        MultinomialNB(),


        "Random Forest":
        RandomForestClassifier(

            n_estimators=50,

            max_depth=30,

            random_state=42,

            n_jobs=-1

        )

    }



    best_model = None

    best_name = ""

    best_accuracy = 0



    print("\nTraining models...\n")



    for name, model in models.items():

        print(
            "Training",
            name
        )


        model.fit(
            X_train_vec,
            y_train
        )


        prediction = model.predict(
            X_val_vec
        )


        accuracy = accuracy_score(
            y_val,
            prediction
        )


        print(
            name,
            ":",
            round(
                accuracy*100,
                2
            ),
            "%"
        )


        if accuracy > best_accuracy:

            best_accuracy = accuracy

            best_model = model

            best_name = name



    print(
        "\nWinner:",
        best_name
    )


    print(
        classification_report(
            y_val,
            best_model.predict(X_val_vec),
            target_names=[
                "Real News",
                "Fake News"
            ]
        )
    )



    # save model

    pickle.dump(
        best_model,
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
        "\nSUCCESS: model.pkl and vector.pkl updated"
    )



if __name__ == "__main__":

    main()

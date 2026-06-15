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
    """
    Cleans raw news text by:
    - Lowercasing the content.
    - Stripping Reuters location/source prefixes to remove source bias.
    - Removing special characters, punctuation, and digits.
    - Normalizing whitespace.
    """
    if not isinstance(text, str):
        return ""
        
    # 1. Lowercase text
    text = text.lower()
    
    # 2. Strip standard Reuters source prefixes (e.g., "WASHINGTON (Reuters) - ")
    # This prevents the model from relying purely on source citations for classification.
    text = re.sub(r'^.*?\b(reuters)\b\s*[-—–]+\s*', '', text, flags=re.IGNORECASE)
    
    # Strip other common capitalized location prefixes (e.g., "LONDON - ")
    text = re.sub(r'^[a-z\s]{3,20}\s*[-—–]+\s*', '', text)
    
    # 3. Keep only alphabetic characters and spaces (removes punctuation, digits, special characters)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # 4. Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def main():
    print("=== Upgraded Fake News Detection Model Training ===")
    
    # Check if dataset files exist
    fake_path = os.path.join("dataset", "Fake.csv")
    true_path = os.path.join("dataset", "True.csv")
    
    if not os.path.exists(fake_path) or not os.path.exists(true_path):
        print("[ERROR] Dataset files not found. Please run download_dataset.py first.")
        sys.exit(1)
        
    # 1. Load datasets
    print("Loading datasets...")
    df_fake = pd.read_csv(fake_path)
    df_true = pd.read_csv(true_path)
    
    print(f"Loaded {len(df_fake)} fake news articles.")
    print(f"Loaded {len(df_true)} true news articles.")
    
    # 2. Label data (1 = Fake, 0 = Real)
    df_fake['label'] = 1
    df_true['label'] = 0
    
    # 3. Concatenate and drop missing entries
    df = pd.concat([df_fake, df_true], ignore_index=True)
    df = df.dropna(subset=['title', 'text'])
    
    # 4. Combine title and text
    df['full_text'] = df['title'] + " " + df['text']
    
    # 5. Apply advanced preprocessing
    print("Applying text preprocessing (lowercasing, source artifact removal, cleaning)...")
    # Using pandas map/apply for cleaning
    df['cleaned_text'] = df['full_text'].apply(clean_text)
    
    # Drop rows that became empty after cleaning
    df = df[df['cleaned_text'] != '']
    
    # 6. Train/Test Split (80% train, 20% validation)
    print("Splitting data into training and validation sets...")
    X_train, X_val, y_train, y_val = train_test_split(
        df['cleaned_text'], 
        df['label'], 
        test_size=0.2, 
        random_state=42, 
        stratify=df['label']
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Validation set size: {len(X_val)}")
    
    # 7. TF-IDF Vectorization
    print("Vectorizing text using TF-IDF (removing English stop words, max_df=0.7, ngrams 1-2)...")
    # Setting max_features to 25,000 to keep model lightweight and prevent memory errors with Random Forest
    vectorizer = TfidfVectorizer(
        stop_words='english', 
        max_df=0.7, 
        ngram_range=(1, 2), 
        max_features=25000
    )
    
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_val_vectorized = vectorizer.transform(X_val)
    
    # 8. Train and evaluate 3 algorithms
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Multinomial Naive Bayes": MultinomialNB(),
        "Random Forest": RandomForestClassifier(n_estimators=50, max_depth=30, random_state=42, n_jobs=-1)
    }
    
    best_model_name = None
    best_model = None
    best_accuracy = -1
    model_accuracies = {}
    
    print("\n=== Training & Evaluating Models ===")
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train_vectorized, y_train)
        
        # Evaluate
        y_pred = model.predict(X_val_vectorized)
        acc = accuracy_score(y_val, y_pred)
        model_accuracies[name] = acc
        print(f"{name} Validation Accuracy: {acc * 100:.2f}%")
        
        # Track best model
        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name
            best_model = model
            
    # 9. Print comparison summary
    print("\n=== Model Comparison Summary ===")
    for name, acc in model_accuracies.items():
        print(f"- {name}: {acc * 100:.2f}%")
        
    print(f"\nWinner: {best_model_name} with {best_accuracy * 100:.2f}% accuracy!")
    
    # Print detailed classification report for the winning model
    y_pred_best = best_model.predict(X_val_vectorized)
    print(f"\nClassification Report for Best Model ({best_model_name}):")
    print(classification_report(y_val, y_pred_best, target_names=["Real News (0)", "Fake News (1)"]))
    
    # 10. Save the winning model and vectorizer
    print("Saving the best model and vectorizer...")
    with open("model.pkl", "wb") as f_model:
        pickle.dump(best_model, f_model)
    with open("vector.pkl", "wb") as f_vector:
        pickle.dump(vectorizer, f_vector)
        
    print(f"[SUCCESS] Saved {best_model_name} as model.pkl and TF-IDF as vector.pkl!")

if __name__ == "__main__":
    main()

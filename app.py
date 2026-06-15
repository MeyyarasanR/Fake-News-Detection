import os
import sys
import re
import pickle
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global variables for model and vectorizer
model = None
vectorizer = None

def clean_text(text):
    """
    Mirrors the preprocessing pipeline used during training:
    - Lowercase the text.
    - Strip Reuters/location source prefixes to remove source bias.
    - Remove special characters, punctuation, and digits.
    - Normalize whitespace.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'^.*?\b(reuters)\b\s*[-\u2014\u2013]+\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^[a-z\s]{3,20}\s*[-\u2014\u2013]+\s*', '', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_ml_assets():
    global model, vectorizer
    model_path = "model.pkl"
    vector_path = "vector.pkl"
    
    if not os.path.exists(model_path) or not os.path.exists(vector_path):
        print("[CRITICAL] Saved model.pkl or vector.pkl not found! Please run train.py first.")
        return False
        
    try:
        print("Loading serialized model and vectorizer...")
        with open(model_path, "rb") as f_model:
            model = pickle.load(f_model)
        with open(vector_path, "rb") as f_vector:
            vectorizer = pickle.load(f_vector)
        print("Model and vectorizer loaded successfully.")
        return True
    except Exception as e:
        print(f"[CRITICAL] Error loading ML assets: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None or vectorizer is None:
        return jsonify({
            'status': 'error',
            'message': 'Model is not loaded on the server.'
        }), 500
        
    try:
        # Support both JSON payload and standard form data
        if request.is_json:
            data = request.get_json()
            text_content = data.get('text', '').strip()
        else:
            text_content = request.form.get('text', '').strip()
            
        if not text_content:
            return jsonify({
                'status': 'error',
                'message': 'Please enter some text to analyze.'
            }), 400
            
        # 1. Apply the same preprocessing used during training
        cleaned_text = clean_text(text_content)
        
        if not cleaned_text:
            return jsonify({
                'status': 'error',
                'message': 'Text could not be processed after cleaning. Please provide more content.'
            }), 400
        
        # 2. Transform the cleaned text using the loaded TF-IDF vectorizer
        vectorized_text = vectorizer.transform([cleaned_text])
        
        # 3. Perform prediction
        prediction_val = model.predict(vectorized_text)[0]
        
        # 4. Calculate probability/confidence score
        probabilities = model.predict_proba(vectorized_text)[0]
        confidence = probabilities[prediction_val]  # Probability of the predicted class
        
        # Determine label (1 = Fake, 0 = Real)
        label = "Fake" if prediction_val == 1 else "Real"
        
        return jsonify({
            'status': 'success',
            'prediction': label,
            'confidence': round(float(confidence) * 100, 2),
            'text_preview': text_content[:100] + '...' if len(text_content) > 100 else text_content
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Prediction failed: {str(e)}'
        }), 500

# Load model when application starts
load_ml_assets()

if __name__ == '__main__':
    app.run()

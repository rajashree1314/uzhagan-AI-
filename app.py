from flask import Flask, render_template, request
import mysql.connector
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Load embedding model
embedding_model = SentenceTransformer("intfloat/multilingual-e5-large")
translator = GoogleTranslator(source='en', target='ta')

# Load FAISS index and scheme mapping
faiss_index = faiss.read_index("faiss_index.bin")
with open("scheme_id_mapping.pkl", "rb") as f:
    scheme_ids = pickle.load(f)

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YJnov@06",
        database="farmer_schemes_db"
    )

# Fetch scheme details from database
def fetch_scheme_details(scheme_ids):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    format_strings = ','.join(['%s'] * len(scheme_ids))
    cursor.execute(f"SELECT * FROM schemes WHERE id IN ({format_strings})", tuple(scheme_ids))
    schemes = cursor.fetchall()
    cursor.close()
    conn.close()
    return schemes

# Route to render form page
@app.route('/')
def index():
    return render_template('index.html')

# Route to process user input and recommend schemes
@app.route('/recommend', methods=['POST'])
def recommend_schemes():
    user_input = f"{request.form['land_size']} hectares, {request.form['category']}, {request.form['location']}, {request.form['farming_type']}"
    user_embedding = embedding_model.encode([user_input])

    _, indices = faiss_index.search(np.array(user_embedding, dtype=np.float32), 5)
    recommended_scheme_ids = [scheme_ids[idx] for idx in indices[0]]
    recommended_schemes = fetch_scheme_details(recommended_scheme_ids)

    # Translate schemes to Tamil
    for scheme in recommended_schemes:
        scheme['scheme_name'] = translator.translate(scheme['scheme_name'])
        scheme['eligibility'] = translator.translate(scheme['eligibility'])
        scheme['benefits'] = translator.translate(scheme['benefits'])
        scheme['apply_process'] = translator.translate(scheme['apply_process'])
        scheme['department'] = translator.translate(scheme['department'])

    return render_template('recommendations.html', schemes=recommended_schemes)

if __name__ == '__main__':
    app.run(debug=True)

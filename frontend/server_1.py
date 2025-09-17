from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from sentence_transformers import SentenceTransformer
import contextlib  # <-- for suppressing stdout

app = Flask(__name__)
CORS(app)

# Load model and label encoder
loaded_best_model = joblib.load("frontend/complaint_agency_bert_classifier.joblib")
loaded_le = joblib.load("frontend/label_encoder_bert.joblib")

embedder = SentenceTransformer('all-MiniLM-L6-v2')

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        text = data.get("description", "").strip()
        if not text:
            return jsonify({"error": "Empty description"}), 400

        # ---------------------------
        # Step 2: Suppress stray logs
        # ---------------------------
        # This ensures only JSON is returned, no TF / ST logs appear
        with contextlib.redirect_stdout(None):
            embedding = embedder.encode([text])
            pred = loaded_best_model.predict(embedding)

        dept = loaded_le.inverse_transform(pred)[0]
        return jsonify({"department": dept})

    except Exception as e:
        # Log exception on server for debugging
        print("Error during prediction:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Model and label encoder loaded successfully.")
    print("SentenceTransformer loaded successfully.")
    print("Starting server on http://127.0.0.1:5000")
    app.run(debug=True)

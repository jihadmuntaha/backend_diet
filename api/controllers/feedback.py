from flask import jsonify, request
from config import db
from models.user_reviews import UserReview as Feedback
from flask_jwt_extended import get_jwt_identity
import pickle
import datetime

# LOAD MODEL FEEDBACK
model_sentimen_rf = pickle.load(open('dataset/models/model_sentimen_rf.pkl', 'rb'))
vectorizer_sentimen = pickle.load(open('dataset/models/vectorizer.pkl', 'rb'))

def feedback():
    user_id = get_jwt_identity()
    data = request.get_json()
    ulasan_user = data.get('comment')

    if not ulasan_user:
        return jsonify({"msg": "Ulasan kosong"}), 400

    # 1. PROSES PREDIKSI AI
    teks_tfidf = vectorizer_sentimen.transform([ulasan_user])
    prediksi = model_sentimen_rf.predict(teks_tfidf)[0] 

    if prediksi >= 4:
        label_sentimen = "Positif"
    elif prediksi <= 2:
        label_sentimen = "Negatif"
    else:
        label_sentimen = "Netral"

    new_feedback = Feedback(
        user_id=user_id,
        comment=ulasan_user,
        rating=int(prediksi),  
        sentiment=label_sentimen,
        created_at=datetime.datetime.utcnow()
    )
    
    try:
        db.session.add(new_feedback)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Terima kasih atas feedback Anda!",
            "data": {
                "rating_ai": int(prediksi),
                "sentimen": label_sentimen
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Gagal simpan ke DB", "error": str(e)}), 500
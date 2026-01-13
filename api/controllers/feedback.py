from flask import jsonify
from requests import request
from config import db
from models.user_reviews import UserReview as Feedback


def post_feedback():
    try:
        data = request.get_json() 
        
        if not data:
            return jsonify({"error": "Data tidak ditemukan"}), 400
            
        rating = data.get('rating')
        message = data.get('message')
        
        new_feedback = Feedback(
            rating=rating,
            message=message
        )
        db.session.add(new_feedback)
        db.session.commit()

        return jsonify({"message": "Feedback berhasil disimpan!"}), 201
        
    except Exception as e:
        print(f"Error pada Controller: {e}")
        return jsonify({"error": str(e)}), 500
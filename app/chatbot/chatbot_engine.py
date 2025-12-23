import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .preprocessing import preprocess

THRESHOLD = 0.35

class ChatbotPSC:
    def __init__(self, kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            self.knowledge = json.load(f)

        self.questions = [
            preprocess(item["question_representative"])
            for item in self.knowledge
        ]

        self.vectorizer = TfidfVectorizer()
        self.kb_vectors = self.vectorizer.fit_transform(self.questions)

    def get_response(self, user_input):
        user_input = preprocess(user_input)
        user_vector = self.vectorizer.transform([user_input])

        similarities = cosine_similarity(user_vector, self.kb_vectors)[0]
        best_index = similarities.argmax()
        best_score = similarities[best_index]

        if best_score >= THRESHOLD:
            return {
                "answer": self.knowledge[best_index]["answer"],
                "score": float(best_score),
                "source": self.knowledge[best_index]["source"]
            }

        return {
            "answer": "Maaf, saya belum menemukan jawaban yang relevan.",
            "score": float(best_score),
            "source": None
        }

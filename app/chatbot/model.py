import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.chatbot.preprocessing import clean_text


class ChatbotModel:
    """
    Retrieval-based Chatbot Model using TF-IDF
    """

    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)

        if "review_text" not in self.df.columns:
            raise ValueError("CSV must contain 'review_text' column")

        self.df["clean_text"] = self.df["review_text"].astype(str).apply(clean_text)

        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df["clean_text"])

    def get_response(self, user_input: str) -> str:
        """
        Return most relevant review based on cosine similarity
        """
        user_input_clean = clean_text(user_input)

        if not user_input_clean:
            return "Pertanyaan tidak valid."

        user_vector = self.vectorizer.transform([user_input_clean])
        similarities = cosine_similarity(user_vector, self.tfidf_matrix)

        best_index = similarities.argmax()
        best_score = similarities[0][best_index]

        if best_score < 0.1:
            return "Maaf, saya belum menemukan jawaban yang relevan."

        return self.df.iloc[best_index]["review_text"]

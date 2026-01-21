from flask import jsonify, request
from api.controllers.chatbot_setup import chatbot_setup

# def chatbot_logic(question: str):
#     answer = chatbot_setup.ask(question)

#     return {
#         "question": question,
#         "answer": answer
#     }

def chat():
    data = request.json
    user_query = data.get("question")
    
    if not user_query:
        return jsonify({"error": "Pertanyaan tidak boleh kosong"}), 400
    
    # Memanggil RAG Service yang sudah kita buat tadi
    response = chatbot_setup.ask(user_query)
    # response = chatbot_no_langchain.ask(user_query)
    
    return jsonify({
        "status": "success",
        "question": user_query,
        "answer": response
    })
import os
import pickle
import faiss
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import SentenceTransformer

load_dotenv()

class ChatbotSetup:
    def __init__(self):
        print("🚀 Initializing RAG Service...")

        self.embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        self.vectorstore = FAISS.load_local(
            "dataset/models/chatbot",
            self.embedding,
            allow_dangerous_deserialization=True
        )

        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )

    # 🔥 GEMINI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.2
        )

        self.prompt = PromptTemplate.from_template("""
            Anda adalah chatbot kesehatan yang cerdas dan praktis. 
            Jawablah pertanyaan pengguna dengan gaya bicara langsung (Direct) namun tetap sopan. 
            Hindari pembukaan yang terlalu panjang seperti 'Berdasarkan informasi yang diberikan...'. 
            Langsung saja berikan solusi atau saran yang bisa dipraktekkan pengguna sehari-hari berdasarkan konteks yang ada.

            Konteks:
            {context}

            Pertanyaan:
            {question}

            Jawaban:
            """)

        self.chain = (
            {
            "context": lambda x: "\n".join(d.page_content for d in self.retriever.invoke(x["question"])),"question": lambda x: x["question"]
                }
                | self.prompt
                | self.llm
                | StrOutputParser()
            )

        print("✅ RAG Gemini ready")

    def ask(self, question: str) -> str:
        return self.chain.invoke({"question": question})


chatbot_setup = ChatbotSetup()

# class ChatbotNoLangchain:
#     def __init__(self):
#         print("🚀 Initializing Manual RAG Service (No Langchain)...")
        
#         # 1. Load model embedding (Backend untuk cari kemiripan teks)
#         self.model_embed = SentenceTransformer("all-MiniLM-L6-v2")
        
#         # 2. Load Index FAISS asli
#         # Pastikan di folder chatbot2 ada file index.faiss
#         self.index = faiss.read_index("dataset/models/chatbot2/index.faiss")
        
#         # 3. Load Dokumen Teks asli (.pkl hasil dump pickle biasa)
#         with open("dataset/models/chatbot2/index.pkl", "rb") as f:
#             self.documents = pickle.load(f)

#         api_key = os.getenv("GOOGLE_API_KEY")
#         genai.configure(api_key = api_key)
#         self.llm = genai.GenerativeModel("gemini-2.5-flash")

#     def ask(self, question):
#         # 5. Cari konteks secara manual menggunakan FAISS
#         query_embedding = self.model_embed.encode([question])
#         # FAISS butuh input float32
#         distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k=5)
        
#         # Mengambil teks berdasarkan index yang ditemukan
#         contexts = [self.documents[i] for i in indices[0]]
#         context_text = "\n".join(contexts)

#         # 6. Buat prompt manual untuk Gemini
#         prompt = f"""
#         Anda adalah asisten ahli diet. Jawablah pertanyaan berikut berdasarkan konteks yang disediakan.
        
#         Konteks:
#         {context_text}

#         Pertanyaan: {question}
#         Jawaban:
#         """

#         # 7. Panggil Gemini untuk generate jawaban
#         response = self.llm.generate_content(prompt)
        
#         return response.text

# # Inisialisasi objek agar bisa dipanggil di routes.py
# chatbot_no_langchain = ChatbotNoLangchain()  
        
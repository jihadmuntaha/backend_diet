---

# Diet & Posture Backend API

Backend service untuk aplikasi **Diet & Posture Management** yang menyediakan autentikasi pengguna, manajemen profil kesehatan, perhitungan BMI, rekomendasi diet, analisis postur, visualisasi data, serta chatbot berbasis dataset. Backend ini dibangun menggunakan **Flask** dengan pendekatan modular dan scalable.

---

## 🔧 Tech Stack

* **Python 3.x**
* **Flask**
* **Flask SQLAlchemy**
* **Flask Blueprint**
* **SQLite / MySQL**
* **JWT & Session-based Authentication**
* **Google OAuth 2.0**
* **Scikit-learn (Chatbot & NLP)**
* **RESTful API Architecture**

---

## 📐 Arsitektur & Pendekatan

Backend ini menggunakan **layered architecture** dengan pemisahan tanggung jawab yang jelas:

```
app/
├── routes/        # Routing & HTTP handling (Blueprint)
├── services/      # Business logic & processing
├── models/        # Database models (ORM)
├── chatbot/       # NLP & chatbot training/inference
├── utils/         # Helper & utilities
├── templates/     # Server-side rendering (admin)
├── static/        # Static assets
└── app.py         # Application entry point
```

### Alasan menggunakan Service Layer

* Menghindari *fat controller*
* Memisahkan HTTP logic dan business logic
* Memudahkan testing dan pengembangan fitur lanjutan
* Menyiapkan backend untuk konsumsi API mobile/web

---

## 🔐 Authentication & Authorization

Fitur autentikasi yang diimplementasikan:

* Login & Register manual
* Login menggunakan **Google OAuth**
* Session management
* Role-based access (`admin` & `user`)
* Proteksi endpoint menggunakan middleware

Flow autentikasi:

1. User login / OAuth
2. Validasi kredensial
3. Session / token disimpan
4. Role dicek sebelum akses fitur tertentu

---

## 🧠 Core Features

### 👤 User & Health Profile

* Manajemen data tinggi, berat badan, target berat
* Perhitungan **BMI otomatis**
* Klasifikasi postur (normal, kyphosis, lordosis, dll.)
* Activity level & diet goal

### 🥗 Diet Recommendation

* Penyesuaian jenis diet (cutting, bulking, maintenance)
* Integrasi dengan profil kesehatan pengguna

### 📊 Visualization & Chart

* Penyediaan data statistik untuk chart (berat badan, BMI, progres)
* Endpoint khusus untuk visualisasi frontend

### 🤖 Chatbot (NLP)

* Dataset berbasis teks hasil preprocessing
* TF-IDF / text vectorization
* Intent-based response
* Model dilatih terpisah dan di-load saat runtime

> Jika dataset diperbarui, model perlu di-training ulang.

---

## 🌐 API Design

* Mengikuti prinsip **REST**
* Format response menggunakan **JSON**
* HTTP Method sesuai semantik (`GET`, `POST`, `PUT`, `DELETE`)
* Endpoint terpisah antara:

  * Auth
  * User
  * Diet
  * Posture
  * Chatbot
  * Chart

Contoh response standar:

```json
{
  "status": "success",
  "message": "Data retrieved successfully",
  "data": {}
}
```

---

## 🧪 Testing & Readability

* Struktur kode dibuat untuk **mudah dibaca (reading the code)**
* Fungsi kecil, spesifik, dan bertanggung jawab tunggal
* Cocok untuk:

  * Ujian membaca kode
  * Presentasi akademik
  * Pengembangan lanjutan (mobile app)

---

## 🚀 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Pastikan environment variable (OAuth client, secret key, dsb.) sudah dikonfigurasi.

---

## 📌 Notes

* Backend ini **siap dikonsumsi oleh aplikasi mobile (Flutter)** maupun frontend web
* Struktur modular memudahkan scaling dan penambahan fitur
* Fokus pada *fundamental framework programming*, bukan sekadar CRUD

---

## 📄 License

This project is intended for **academic and learning purposes**.

---

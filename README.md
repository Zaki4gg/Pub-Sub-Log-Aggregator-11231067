# UTS Sistem Terdistribusi
# Pub-Sub-Log-Aggregator-11231067

## 📘 Deskripsi Singkat
Proyek ini merupakan implementasi layanan **Pub-Sub Log Aggregator** yang menerima event/log dari publisher, memprosesnya melalui consumer idempotent (tidak memproses ulang event duplikat), dan menyimpan data unik secara **persisten di SQLite** agar tahan terhadap restart.  
Sistem berjalan lokal dalam container **Docker**, tanpa koneksi eksternal publik.

---

## ⚙️ Cara Build dan Run

### 1. Build Docker Image
pada terminal vs code jalankan:

docker build -t uts-aggregator .

### 2. Run Docker container
setelah berhasil build lanjutkan run docker dengan:

docker run -p 8080:8080 uts-aggregator

akan muncul:

INFO:     Application startup complete.

INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)

Buka browser ke http://localhost:8080/docs

Kamu akan lihat Swagger UI dengan endpoint:

POST /publish

GET /events

GET /stats


. 

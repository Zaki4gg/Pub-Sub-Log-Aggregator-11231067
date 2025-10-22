# UTS Sistem Terdistribusi
# Pub-Sub-Log-Aggregator-11231067

## 📘 Deskripsi Singkat
Proyek ini merupakan implementasi layanan **Pub-Sub Log Aggregator** yang menerima event/log dari publisher, memprosesnya melalui consumer idempotent (tidak memproses ulang event duplikat), dan menyimpan data unik secara **persisten di SQLite** agar tahan terhadap restart.  
Sistem berjalan lokal dalam container **Docker**, tanpa koneksi eksternal publik.

---

## Fitur Utama
- **Publish Event (POST /publish)**  
  Menerima event JSON single/batch dan memprosesnya ke queue internal.
- **Deduplication & Idempotency**  
  Event unik disimpan di SQLite, duplikat diabaikan.
- **Persistence**  
  Dedup store tetap mencegah reprocessing setelah container di-restart.
- **Observability**  
  Endpoint `/stats` menampilkan statistik sistem.
- **Swagger UI**  
  Dokumentasi otomatis tersedia di `http://localhost:8080/docs`.

---

## Cara Build dan Run

### 1. Build Docker Image
pada terminal vs code jalankan:
<br>docker build -t uts-aggregator .

### 2. Run Docker container
setelah berhasil build lanjutkan run docker dengan:
<br>docker run -p 8080:8080 uts-aggregator
<br>akan muncul:
<br>INFO:     Application startup complete.
<br>INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)

---

## Asumsi Sistem
Event yang dikirim memiliki kombinasi unik (topic, event_id). Digunakan untuk deteksi duplikat
<br>Semua komponen berjalan lokal dalam satu jaringan internal. Tidak ada layanan eksternal publik
<br>Delivery bersifat at-least-once. Simulasi pengiriman ulang (retry) oleh publisher
<br>Total ordering tidak diterapkan.	Cukup dengan partial ordering via timestamp
<br>Dedup store menggunakan SQLite lokal. Menjamin persistensi dan idempotency

---
## Endpoint API
Buka browser ke http://localhost:8080/docs
<br>Kamu akan lihat Swagger UI dengan endpoint:

### POST /publish
<br> Menerima satu atau batch event dalam format JSON

### GET /events
<br> Mengembalikan daftar event unik (bisa filter topic)

### GET /stats
<br> Menampilkan statistik agregator: total, duplikat, uptime


. 

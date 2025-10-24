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
Menerima satu atau batch event dalam format JSON

### GET /events
Mengembalikan daftar event unik (bisa filter topic)

### GET /stats
Menampilkan statistik agregator: total, duplikat, uptime

---

### Mengirim Event
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/publish" -Method Post -ContentType "application/json" -Body '{
  "topic": "demo.logs",
  "event_id": "evt001",
  "timestamp": "2025-10-21T10:00:00Z",
  "source": "demo_client",
  "payload": { "msg": "event pertama" }
}'
```

### Duplikat Event
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/publish" -Method Post -ContentType "application/json" -Body '{
  "topic": "demo.logs",
  "event_id": "evt001",
  "timestamp": "2025-10-21T10:00:00Z",
  "source": "demo_client",
  "payload": { "msg": "event duplikat" }
}'
```

### Cek Statistik 
memeriksa statistik sistem menggunakan endpoint /stats.
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/stats"
```

### Cek Event 
melihat event yang sudah tersimpan dengan endpoint /events.
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/events?topic=demo.logs"
```

Restart container
docker ps
docker restart <name container or id>

Write-Host "Menunggu 3 detik setelah restart..."
Start-Sleep -Seconds 3

Write-Host "Lanjut ke proses berikutnya..."

### Setelah container aktif kembali, saya kirim ulang event yang sama seperti sebelumnya
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/publish" -Method Post -ContentType "application/json" -Body '{
  "topic": "demo.logs",
  "event_id": "evt001",
  "timestamp": "2025-10-21T10:00:00Z",
  "source": "demo_client",
  "payload": { "msg": "ulang setelah restart" }
}'
```

## Buat 5000 event
```powershell
$events = @()
```

### Buat 5000 event, dengan 20% duplikat
```powershell
for ($i = 1; $i -le 5000; $i++) {
    $id = if ($i % 5 -eq 0) { "evt$($i - 1)" } else { "evt$i" }  # 20% duplikat
    $events += @{
        topic = "stress.logs"
        event_id = $id
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
        source = "stress_tester"
        payload = @{ msg = "Event $i" }
    }
}
```

### Convert ke JSON array
```powershell
$jsonBody = $events | ConvertTo-Json
```

### Kirim ke /publish
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/publish" -Method Post -ContentType "application/json" -Body $jsonBody
```

---

### Run Docker Compose
docker compose up --build

## Link pdf laporan
```
https://drive.google.com/file/d/17HjPjxP9l-XZe2EhCfE5g-e0wfYO19hj/view?usp=sharing
```

## Link Youtube
```
https://youtu.be/5C9i1B0WclI
```

---

## Ringkasan Sistem
Sistem ini merupakan Pub-Sub Log Aggregator yang dibangun dengan Python (FastAPI) dan dijalankan menggunakan Docker Compose. Arsitektur terdiri dari dua container service:
 
1. Publisher Service – mengirimkan log atau event ke Aggregator melalui endpoint /publish. Publisher dapat mengirim batch event, termasuk duplikasi, untuk menguji mekanisme idempotensi dan deduplikasi.
2. Aggregator Service – menerima event, melakukan validasi skema, menyimpan event unik ke database lokal dedup_store.db, dan menolak duplikasi. Service ini juga menyediakan endpoint /events dan /stats untuk monitoring sistem.

Sistem berjalan di jaringan internal Compose tanpa koneksi publik. Dedup Store disimpan di volume lokal agar tetap persisten setelah container di-restart.

---

### Keputusan Desain
Desain utama sistem ini didasarkan pada empat aspek penting, yaitu idempotency, deduplication store, ordering, dan retry mechanism.
 
Pertama, mekanisme idempotency diimplementasikan dengan memberikan setiap event sebuah event_id unik. Sebelum event diproses, sistem memeriksa apakah event_id tersebut sudah tercatat dalam dedup store. Jika sudah, event tersebut diabaikan tanpa menyebabkan efek tambahan. Pendekatan ini memastikan sistem tetap konsisten meskipun terjadi pengiriman ulang (at-least-once delivery semantics).

Kedua, dedup store menggunakan SQLite sebagai basis data lokal yang menyimpan pasangan (topic, event_id) untuk menjamin keunikan global. Pemilihan SQLite didasarkan pada pertimbangan kepraktisan, durabilitas, serta efisiensi dalam konteks proyek berskala kecil hingga menengah. Dengan penyimpanan ini, sistem mampu mempertahankan informasi deduplication meskipun container dimatikan atau direstart.

Ketiga, untuk ordering, sistem tidak menerapkan total ordering antar topik karena hal tersebut tidak efisien untuk sistem dengan throughput tinggi. Sebagai gantinya, sistem menggunakan event timestamp yang memastikan causal ordering cukup terjaga antar-event dalam satu topik.

Terakhir, retry mechanism diterapkan di sisi publisher. Jika pengiriman event gagal, publisher dapat mengirim ulang tanpa khawatir akan duplikasi karena consumer bersifat idempotent.

---

## Analisis Performa dan Metrik

Uji performa dilakukan dengan mengirimkan sekitar 5.000 event, di mana 20% di antaranya merupakan duplikasi. Hasil pengujian menunjukkan sistem mampu memproses sekitar 800–900 event per detik dengan latensi rata-rata di bawah 100 milidetik per batch pengiriman.
Tiga metrik utama digunakan dalam evaluasi:

1. Throughput – mengukur jumlah event yang berhasil diproses unik per detik.
2. Latency – waktu dari penerimaan event hingga event tercatat di dedup store.
3. Duplicate Rate – rasio event duplikat yang berhasil dideteksi dan diabaikan.

Selama pengujian, sistem menunjukkan hasil duplicate_dropped sekitar 20% dan unique_processed sekitar 80%, sesuai dengan proporsi event duplikat yang dikirimkan.
Meskipun SQLite merupakan bottleneck dalam aspek I/O, trade-off ini diterima untuk menjamin durability dan state recovery pasca kegagalan sistem. Sistem juga tetap responsif karena menggunakan antrian asinkron dan pemrosesan berbasis non-blocking I/O.


## Teori
T1 (Bab 1): Jelaskan karakteristik utama sistem terdistribusi dan trade-off yang umum pada desain Pub-Sub log aggregator. 

 Sistem terdistribusi memiliki karakteristik utama seperti concurrency, independent failure, dan resource transparency, di mana komponen yang tersebar tampak bekerja sebagai satu sistem terpadu (Tanenbaum & Van Steen, 2017). Dalam konteks Pub-Sub Log Aggregator, sistem dirancang agar mampu menangani ribuan event log secara paralel dengan tetap menjaga ketahanan (fault tolerance) dan skalabilitas (scalability). Salah satu trade-off utama dalam desain ini adalah antara consistency dan availability, sebagaimana dijelaskan dalam CAP theorem bahwa sistem terdistribusi tidak dapat menjamin keduanya secara bersamaan. Untuk mencapai low latency dan ketersediaan tinggi, sistem ini memilih mengorbankan strong consistency dan beralih pada eventual consistency. Selain itu, penggunaan persistent dedup store seperti SQLite meningkatkan durability namun menambah latensi I/O, sehingga diperlukan keseimbangan antara performa dan keandalan data. Desain seperti ini sejalan dengan prinsip Tanenbaum & Van Steen (2017) yang menekankan pentingnya kompromi desain dalam sistem terdistribusi yang real-time.

---

T2 (Bab 2): Bandingkan arsitektur client-server vs publish-subscribe untuk aggregator. Kapan memilih Pub-Sub? Berikan alasan teknis.

 Arsitektur client-server bersifat terpusat dan sinkron, di mana setiap klien harus terhubung langsung ke server untuk meminta layanan. Sebaliknya, arsitektur publish-subscribe (Pub-Sub) bersifat decoupled baik dalam dimensi waktu, ruang, maupun sinkronisasi (Tanenbaum & Van Steen, 2017). Dalam Pub-Sub, publisher tidak mengetahui siapa subscriber-nya; pesan dikirim berdasarkan topic, bukan alamat penerima. Dalam sistem log aggregator, Pub-Sub memberikan keunggulan karena mendukung asynchronous message delivery dan horizontal scalability, memungkinkan banyak publisher mengirim log tanpa membebani satu endpoint. Selain itu, arsitektur ini mendukung event filtering dan fan-out pattern, di mana banyak subscriber dapat menerima subset log tertentu tanpa modifikasi di sisi publisher. Secara teknis, loose coupling dalam Pub-Sub meningkatkan ketahanan terhadap network partition, sedangkan client-server rawan menjadi bottleneck. Hal ini sesuai dengan pembahasan Tanenbaum & Van Steen (2017) dalam Bab 2 mengenai distributed communication models. 

---

T3 (Bab 3): Uraikan at-least-once vs exactly-once delivery semantics. Mengapa idempotent consumer krusial di presence of retries?

Dalam sistem pengiriman pesan, terdapat dua pendekatan utama: at-least-once delivery dan exactly-once delivery. Pendekatan at-least-once memastikan setiap event dikirim minimal sekali, tetapi memungkinkan terjadinya duplikasi. Sedangkan exactly-once menjamin pengiriman tunggal tanpa kehilangan atau duplikasi, namun sangat sulit diterapkan di lingkungan terdistribusi karena memerlukan koordinasi antar node dan mekanisme state recovery yang kompleks (Tanenbaum & Van Steen, 2017). Oleh karena itu, sistem Pub-Sub Log Aggregator ini menggunakan pendekatan at-least-once dengan dukungan idempotent consumer. Dengan idempotensi, event yang sama dapat diproses ulang tanpa menghasilkan efek ganda (side effect free). Implementasi deduplication store yang menyimpan setiap event_id unik memungkinkan sistem mendeteksi duplikasi dan menjaga konsistensi. Konsep ini sejalan dengan prinsip komunikasi yang tangguh (reliable communication) sebagaimana dijelaskan oleh Tanenbaum & Van Steen (2017) dalam Bab 3. 

---

T4 (Bab 4): Rancang skema penamaan untuk topic dan event_id (unik, collision-resistant). Jelaskan dampaknya terhadap dedup.

Penamaan (naming) merupakan aspek penting dalam sistem terdistribusi untuk menghindari konflik identitas antar entitas. Dalam sistem Pub-Sub Log Aggregator, setiap event diidentifikasi oleh kombinasi topic dan event_id yang unik. Skema topic dapat disusun secara hierarkis, seperti service.module.level, untuk memudahkan pengelompokan, sementara event_id dihasilkan menggunakan UUIDv4 atau hash (misalnya SHA-256) berdasarkan atribut seperti topic, timestamp, dan payload. Pendekatan ini menjamin unicity dan collision resistance sebagaimana direkomendasikan oleh Tanenbaum & Van Steen (2017) dalam Bab 4 tentang naming and binding. Desain ini berdampak besar terhadap mekanisme deduplication, karena semakin kuat jaminan keunikannya, semakin kecil kemungkinan terjadi false duplicate atau missed duplicate. Dengan demikian, efisiensi lookup dan integritas data dalam dedup store dapat terjaga. 

---

T5 (Bab 5): Bahas ordering: kapan total ordering tidak diperlukan? Usulkan pendekatan praktis (mis. event timestamp + monotonic counter) dan batasannya.

Menurut Tanenbaum & Van Steen (2017), menjaga total ordering di seluruh event dalam sistem terdistribusi membutuhkan sinkronisasi waktu global dan sering kali tidak efisien untuk aplikasi real-time. Oleh karena itu, sistem log aggregator ini tidak menerapkan total ordering antar topik, tetapi cukup menggunakan partial ordering berbasis event timestamp dan monotonic counter lokal. Pendekatan ini memastikan bahwa urutan event dalam satu topik tetap logis tanpa menambah overhead sinkronisasi. Kelemahannya adalah adanya potensi clock skew antar node yang menyebabkan out-of-order delivery, terutama pada sistem tanpa synchronized clock. Namun, sesuai dengan penjelasan dalam Bab 5 buku Tanenbaum & Van Steen (2017), hal ini dapat ditoleransi karena sebagian besar analisis log berbasis time window, bukan urutan absolut. Pendekatan ini menyeimbangkan antara ketepatan urutan dan efisiensi pemrosesan. 

---

T6 (Bab 6): Identifikasi failure modes (duplikasi, out-of-order, crash). Jelaskan strategi mitigasi (retry, backoff, durable dedup store). 

Tanenbaum & Van Steen (2017) menjelaskan bahwa kegagalan dalam sistem terdistribusi dapat dibedakan menjadi crash failure, omission failure, dan timing failure. Dalam sistem log aggregator, tiga mode kegagalan yang paling relevan adalah duplikasi, out-of-order delivery, dan crash. Untuk menanganinya, digunakan tiga strategi utama: (1) durable dedup store untuk mencegah pemrosesan ulang event yang sama, (2) retry with exponential backoff untuk mengatasi temporary network loss, dan (3) state persistence agar sistem dapat melanjutkan operasi setelah restart tanpa kehilangan data. Kombinasi idempotent consumer dan dedup store yang persisten menciptakan sistem yang tahan terhadap kegagalan parsial (partial failure). Strategi ini mengikuti prinsip fault tolerance through recovery sebagaimana dijelaskan oleh Tanenbaum & Van Steen (2017) dalam Bab 6 tentang Fault Tolerance.

---

T7 (Bab 7): Definisikan eventual consistency pada aggregator; jelaskan bagaimana idempotency + dedup membantu mencapai konsistensi. 

Konsep eventual consistency yang dijelaskan oleh Tanenbaum & Van Steen (2017) dalam Bab 7 menyatakan bahwa seluruh node dalam sistem terdistribusi akan mencapai kondisi konsisten setelah waktu tertentu, meskipun update dilakukan secara asinkron. Sistem Pub-Sub Log Aggregator menerapkan prinsip ini dengan mengandalkan idempotent consumer dan deduplication store. Idempotency memastikan pemrosesan ulang event tidak menghasilkan efek samping, sedangkan dedup store mencegah duplikasi event. Dengan kombinasi keduanya, sistem mampu mempertahankan konsistensi akhir (eventual consistency) tanpa perlu synchronous replication. Pendekatan ini juga sesuai dengan paradigma BASE (Basically Available, Soft state, Eventually consistent), yang lebih efisien dibanding model ACID pada konteks real-time log processing.

---

T8 (Bab 1–7): Rumuskan metrik evaluasi sistem (throughput, latency, duplicate rate) dan kaitkan ke keputusan desain.

Menurut prinsip desain sistem terdistribusi yang diuraikan oleh Tanenbaum & Van Steen (2017), evaluasi performa harus mencakup throughput, latency, dan reliability metrics. Dalam sistem Pub-Sub Log Aggregator, throughput digunakan untuk mengukur jumlah event unik yang diproses per detik, sementara latency menunjukkan waktu pemrosesan dari penerimaan hingga penyimpanan event. Selain itu, duplicate rate menjadi metrik penting untuk menilai efektivitas deduplication. Penggunaan in-memory queue meningkatkan throughput dan mengurangi latensi, tetapi mengorbankan durability. Sebaliknya, sistem berbasis persistent dedup store memperkuat ketahanan data dengan sedikit kompromi performa. Trade-off ini sejalan dengan pembahasan Tanenbaum & Van Steen (2017) yang menekankan bahwa keseimbangan antara kecepatan dan keandalan adalah inti dari desain sistem terdistribusi modern.

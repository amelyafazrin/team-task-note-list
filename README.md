# TeamFlow --- Team Task & Note List

Aplikasi web sederhana untuk mencatat dan membagi tugas antaranggota
kelompok. Proyek ini dibuat untuk UTS mata kuliah **Cloud Computing**
dengan menerapkan Python REST API, HTML + Vanilla JavaScript, Docker,
Docker Named Volume, Custom Bridge Network, Docker Compose, Jenkins
CI/CD, dan GitHub Webhook.

## 1. Identitas Kelompok

  No.   Nama Anggota       NIM
  ----- ------------------ --------------
  1     Liony Syafitri     101012330035
  2     Amelya Fazrin      101012330146
  3     Hanif Rafsanjani   101012330044
  4     Ziya Bahjatulloh   101012300364

**Mata Kuliah:** Cloud Computing\
**Studi Kasus:** 6 --- Papan Catatan Tugas Kelompok (*Team Task & Note
List*)\
**Repository:** https://github.com/amelyafazrin/team-task-note-list

## 2. Deskripsi Aplikasi

TeamFlow merupakan aplikasi *task list* untuk membantu anggota kelompok
mencatat tugas, menentukan penanggung jawab (*person in charge/PIC*),
dan menambahkan catatan. Frontend berkomunikasi dengan backend melalui
REST API secara asynchronous menggunakan `fetch()`.

### Fitur

-   Menampilkan daftar tugas.
-   Menambahkan tugas, PIC, dan catatan.
-   Menghapus tugas berdasarkan indeks.
-   Mencari tugas berdasarkan informasi yang ditampilkan pada aplikasi.
-   Menyimpan data dalam file JSON pada Docker Named Volume agar data
    tetap tersedia ketika container backend dihapus dan dibuat ulang.

## 3. Teknologi yang Digunakan

-   **Backend:** Python dan Flask REST API.
-   **Frontend:** HTML, CSS, dan Vanilla JavaScript.
-   **Web server:** Nginx.
-   **Containerization:** Docker.
-   **Orchestration:** Docker Compose.
-   **Networking:** Custom Bridge Network (`app-net`).
-   **Persistent storage:** Docker Named Volume (`team-task-data`).
-   **CI/CD:** Jenkins Declarative Pipeline.
-   **Source control & trigger:** GitHub dan GitHub Webhook.
-   **Tunneling untuk Jenkins lokal:** ngrok.

## 4. Struktur Direktori

``` text
team-task-note-list/
├── backend/
│   ├── app.py
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── docker-compose.jenkins.yml
├── Jenkinsfile
├── .dockerignore
├── .gitignore
└── README.md
```

## 5. Arsitektur Sistem

``` mermaid
flowchart TD
    U[User / Browser] -->|HTTP :8080| N[Nginx Frontend]
    N -->|Proxy / API| B[Backend Python Flask :5000]
    B -->|Read / Write tasks.json| V[(Docker Named Volume<br/>team-task-data)]
    N --- NET[Custom Bridge Network<br/>app-net]
    B --- NET

    G[Developer: git push main] --> GH[GitHub Repository]
    GH -->|Push Webhook HTTPS| NG[ngrok Tunnel]
    NG -->|Forward to Jenkins :8082| J[Jenkins]
    J --> C[Checkout]
    C --> S[Syntax Check]
    S --> I[Build Image]
    I --> D[Automated Deployment]
    D --> H[Health Check]
    H -->|Docker Compose| B
    H -->|Docker Compose| N
```

### Penjelasan komponen

1.  Browser mengakses frontend melalui port `8080`.
2.  Nginx menyajikan halaman web dan meneruskan request `/api/` ke
    service backend melalui nama service Docker `backend`.
3.  Backend berjalan pada port container `5000` dan menyimpan data ke
    `/app/data/tasks.json`.
4.  Direktori `/app/data` dipasang ke Named Volume `team-task-data`,
    sehingga data tidak ikut terhapus ketika container backend dihapus.
5.  Frontend dan backend terhubung melalui Custom Bridge Network
    `app-net`.
6.  Push ke branch `main` pada GitHub mengirim webhook ke Jenkins
    melalui URL publik ngrok.
7.  Jenkins menjalankan pipeline untuk checkout source, memeriksa syntax
    Python, membangun image, melakukan deployment, dan memeriksa
    kesehatan backend.

## 6. REST API

Backend menyediakan endpoint berikut:

  Method   Endpoint           Fungsi
  -------- ------------------ ------------------------------------
  GET      `/tasks`           Mengambil seluruh daftar tugas
  POST     `/tasks`           Menambahkan tugas baru
  DELETE   `/tasks?index=X`   Menghapus tugas berdasarkan indeks
  GET      `/health`          Memeriksa status backend

Contoh body untuk menambahkan tugas:

``` json
{
  "task": "Menyelesaikan laporan",
  "responsible": "Nama PIC",
  "notes": "Catatan tugas"
}
```

Contoh pengujian melalui browser:

-   Frontend: http://localhost:8080
-   Backend API: http://localhost:8081/tasks
-   Backend health: http://localhost:8081/health

## 7. Instalasi dan Menjalankan Secara Lokal

### Prasyarat

Pastikan aplikasi berikut sudah terpasang dan berjalan:

-   Docker Desktop
-   Git

### Langkah menjalankan

Clone repository dan masuk ke direktori proyek:

``` bash
git clone https://github.com/amelyafazrin/team-task-note-list.git
cd team-task-note-list
```

Bangun image dan jalankan seluruh service:

``` bash
docker compose up -d --build
```

Periksa status container:

``` bash
docker compose ps
```

Buka aplikasi pada:

``` text
http://localhost:8080
```

Endpoint backend:

``` text
http://localhost:8081/tasks
http://localhost:8081/health
```

### Konfigurasi Docker lokal

File `docker-compose.yml` digunakan untuk menjalankan aplikasi secara
lokal. Konfigurasi ini memasang:

-   Named Volume `team-task-data` ke `/app/data` pada backend.
-   Bind Mount `frontend/index.html` dan `frontend/nginx.conf` ke
    container Nginx agar perubahan file frontend di komputer lokal dapat
    langsung terlihat tanpa membangun ulang image frontend.
-   Custom Bridge Network `app-net` untuk komunikasi antarkontainer.

### Menghentikan aplikasi

``` bash
docker compose down
```

Perintah tersebut tidak menghapus Named Volume. **Jangan gunakan
`docker compose down -v`** jika data tugas masih ingin dipertahankan.

## 8. Pengujian Data Persistence (Data Immunity)

Pengujian ini membuktikan bahwa data tetap tersimpan meskipun container
backend dihapus.

1.  Tambahkan beberapa tugas melalui aplikasi.
2.  Pastikan data tampil pada `http://localhost:8081/tasks`.
3.  Hapus container backend:

``` bash
docker rm -f team-task-backend
```

4.  Buat kembali backend menggunakan konfigurasi deployment Jenkins:

``` bash
docker compose -p team-task-note-list -f docker-compose.jenkins.yml up -d backend
```

5.  Periksa kembali data:

``` text
http://localhost:8081/tasks
```

Data yang sebelumnya dimasukkan harus tetap tersedia karena file
`tasks.json` disimpan pada Docker Named Volume, bukan hanya di
filesystem container.

## 9. Konfigurasi Jenkins CI/CD

Jenkins digunakan untuk menjalankan proses CI/CD secara otomatis ketika
ada push ke branch `main`.

### Konfigurasi job

1.  Buat item Jenkins bertipe **Pipeline**.
2.  Pada bagian Pipeline, pilih **Pipeline script from SCM**.
3.  Pilih SCM **Git**.
4.  Masukkan repository:

``` text
https://github.com/amelyafazrin/team-task-note-list.git
```

5.  Atur branch menjadi:

``` text
*/main
```

6.  Atur Script Path menjadi:

``` text
Jenkinsfile
```

7.  Aktifkan trigger **GitHub hook trigger for GITScm polling**.

### Lima stage Jenkinsfile

  -----------------------------------------------------------------------
  Stage                               Fungsi
  ----------------------------------- -----------------------------------
  Checkout                            Mengambil source code dari
                                      repository

  Syntax Check                        Memeriksa syntax Python pada
                                      `backend/app.py`

  Build Image                         Membangun Docker image backend dan
                                      frontend

  Automated Deployment                Menjalankan atau memperbarui
                                      service menggunakan Docker Compose

  Health Check                        Memastikan endpoint health backend
                                      merespons
  -----------------------------------------------------------------------

### Konfigurasi deployment Jenkins

Jenkins menggunakan file `docker-compose.jenkins.yml`. File ini tidak
memasang Bind Mount frontend dari workspace Jenkins karena Docker Engine
yang digunakan berada pada Docker Desktop host dan path workspace
container Jenkins tidak tersedia sebagai path host yang sama.

Sebagai gantinya, frontend dibangun ke dalam Docker image pada proses
Build Image. Konfigurasi lokal tetap menggunakan Bind Mount seperti yang
disyaratkan untuk pengembangan frontend.

### GitHub Webhook dan ngrok

Jika Jenkins berjalan lokal, GitHub tidak dapat mengakses alamat
`localhost` secara langsung. ngrok digunakan untuk menyediakan URL HTTPS
publik sementara yang meneruskan request ke Jenkins lokal.

Jalankan tunnel pada komputer yang menjalankan Jenkins:

``` bash
ngrok http 8082
```

Gunakan URL HTTPS yang ditampilkan ngrok sebagai Payload URL GitHub
dengan path:

``` text
https://URL-NGROK-ANDA/github-webhook/
```

Pengaturan webhook:

-   Content type: `application/json`
-   Event: **Just the push event**
-   Active: dicentang

Pastikan tunnel ngrok tetap aktif saat pengujian webhook. URL ngrok
dapat berubah atau menjadi offline ketika tunnel dihentikan.

### Pengujian CI/CD otomatis

Setelah konfigurasi selesai, lakukan perubahan pada source code lalu
jalankan:

``` bash
git add .
git commit -m "Update application"
git push origin main
```

GitHub akan mengirim event push ke webhook. Jenkins kemudian menjalankan
pipeline secara otomatis. Periksa halaman job Jenkins dan pastikan build
berakhir dengan status **SUCCESS**.

**Hasil pengujian proyek:** Build Jenkins #7 berhasil dipicu oleh GitHub
push dan berakhir dengan status SUCCESS. Pengujian tersebut membuktikan
webhook dan pipeline otomatis berjalan.

## 10. Catatan Keamanan

-   Jangan memasukkan GitHub Personal Access Token (PAT), password
    Jenkins, ngrok authtoken, atau secret ke repository maupun README.
-   Jika repository privat atau konfigurasi Jenkins membutuhkan
    autentikasi Git, simpan credential melalui Jenkins Credentials,
    bukan langsung di Jenkinsfile.
-   URL ngrok merupakan endpoint publik sementara. Hentikan tunnel jika
    tidak digunakan.
-   Jangan menghapus Named Volume dengan opsi `-v` ketika data masih
    dibutuhkan.

## 11. Video Demo

Video demo kelompok berdurasi **5--8 menit** dan memperlihatkan:

1.  Tampilan aplikasi TeamFlow serta proses menambah dan menghapus
    tugas.
2.  Pengujian REST API backend.
3.  Konfigurasi Docker Compose, Custom Bridge Network, Bind Mount, dan
    Named Volume.
4.  Simulasi Data Immunity dengan menghapus container backend dan
    membuktikan data tetap ada setelah container dibuat kembali.
5.  Proses `git push` ke branch `main`.
6.  GitHub Webhook memicu Jenkins secara otomatis dan pipeline
    menyelesaikan seluruh stage hingga status **SUCCESS**.

**Tautan video demo:** *(isi setelah video diunggah)*

------------------------------------------------------------------------

**Catatan:** Pastikan seluruh anggota kelompok memeriksa isi README,
konfigurasi, dan hasil demo sebelum pengumpulan melalui LMS.

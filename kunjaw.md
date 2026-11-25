# KUNCI JAWABAN — EVCONN LINUX WARGAME
## Level 0–10

> **KHUSUS OPERATOR / MENTOR. Jangan bagikan dokumen ini kepada peserta sebelum kegiatan selesai.**

Dokumen ini berisi alur penyelesaian, command utama, lokasi file target, dan hubungan password antarlevel.

**Catatan:** Password akun ditentukan sendiri oleh operator ketika menjalankan `main.py`. Karena itu, dokumen ini tidak mencantumkan password tetap. Password yang ditemukan pada setiap level akan menjadi password akun level berikutnya.

---

## Level 0 — The Beginning

**Materi:** membaca file menggunakan `cat`.

### Langkah penyelesaian

Login ke akun awal:

```bash
su - player
```

Baca petunjuk:

```bash
cat README.md
```

Baca password Level 1:

```bash
cat pw-evconn.md
```

**Jawaban:** isi `pw-evconn.md` merupakan password untuk login ke akun `level1`.

**Alur password:** Level 0 → Level 1.

---

## Level 1 — The Dash File

**Materi:** membaca file yang namanya berupa tanda minus (`-`).

**Lokasi file target:** `/home/level1/-`

### Langkah penyelesaian

```bash
ls -la
cat ./-
```

**Jawaban:** isi file `-` merupakan password untuk akun `level2`.

**Mengapa menggunakan `./-`?**

Tanda minus dapat dibaca sebagai opsi oleh command. Dengan menuliskan `./-`, kita menyebut file bernama `-` yang berada di direktori saat ini.

**Alur password:** Level 1 → Level 2.

---

## Level 2 — The Invisible Secret

**Materi:** hidden files atau file tersembunyi.

**Lokasi file target:** `/home/level2/.secret`

### Langkah penyelesaian

```bash
ls -la
cat .secret
```

**Jawaban:** isi file `.secret` merupakan password untuk akun `level3`.

**Penjelasan:** nama file yang diawali tanda titik (`.`) termasuk hidden file. Opsi `-a` pada `ls` menampilkan file tersembunyi.

**Alur password:** Level 2 → Level 3.

---

## Level 3 — The Cloud Audit Log

**Materi:** mencari teks di dalam file menggunakan `grep`.

**Lokasi file target:** `/home/level3/cloud-audit.log`

### Langkah penyelesaian

```bash
grep -in "credential_ready" cloud-audit.log
```

Baris target memiliki pola seperti berikut:

```text
account=level4 status=credential_ready password=<PASSWORD_LEVEL4>
```

**Jawaban:** ambil nilai setelah `password=`. Nilai tersebut merupakan password untuk akun `level4`.

**Penjelasan opsi:**
- `-i`: pencarian tidak membedakan huruf besar dan kecil.
- `-n`: menampilkan nomor baris hasil pencarian.

**Alur password:** Level 3 → Level 4.

---

## Level 4 — The Lost Snapshot

**Materi:** mencari file berdasarkan nama menggunakan `find`.

**Lokasi file target:**

```text
cloud/regions/ap-southeast-1/backups/snapshot-002/recovery-token.txt
```

### Langkah penyelesaian

```bash
find . -name "recovery-token.txt"
```

Setelah lokasi ditemukan, baca file:

```bash
cat ./cloud/regions/ap-southeast-1/backups/snapshot-002/recovery-token.txt
```

**Jawaban:** isi `recovery-token.txt` merupakan password untuk akun `level5`.

**Penjelasan command:**
- `find`: mencari file atau direktori.
- `.`: memulai pencarian dari direktori saat ini.
- `-name`: mencari berdasarkan nama.

**Alur password:** Level 4 → Level 5.

---

## Level 5 — The Oversized Cloud Log

**Materi:** mencari file berdasarkan karakteristik menggunakan `find`.

**Karakteristik file target:**
1. File biasa.
2. Memiliki ekstensi `.log`.
3. Ukurannya lebih dari 1 KiB.

**Lokasi file target:**

```text
cloud/regions/ap-southeast-1/backups/logs/17.log
```

### Langkah penyelesaian

```bash
find . -type f -name "*.log" -size +1k
```

Setelah file ditemukan, baca isinya:

```bash
cat ./cloud/regions/ap-southeast-1/backups/logs/17.log
```

**Jawaban:** ambil nilai setelah `password=` pada baris akun `level6`. Nilai tersebut merupakan password untuk akun `level6`.

**Penjelasan opsi:**
- `-type f`: hanya mencari file biasa.
- `-name "*.log"`: mencari file dengan ekstensi `.log`.
- `-size +1k`: mencari file yang ukurannya lebih dari 1 KiB.

**Alur password:** Level 5 → Level 6.

---

## Level 6 — The Last Deployment

**Materi:** membaca bagian awal dan akhir file menggunakan `head` dan `tail`.

**Lokasi file target:** `/home/level6/deployment.log`

### Langkah penyelesaian

```bash
head -n 5 deployment.log
tail -n 5 deployment.log
```

**Jawaban:** perhatikan baris terakhir yang memuat informasi akun `level7` dan nilai `password=`. Nilai tersebut merupakan password untuk akun `level7`.

**Penjelasan command:**
- `head -n 5`: menampilkan lima baris pertama.
- `tail -n 5`: menampilkan lima baris terakhir.

**Alur password:** Level 6 → Level 7.

---

## Level 7 — The Missing Report

**Materi:** menghitung jumlah baris menggunakan `wc -l`.

**Lokasi direktori target:** `/home/level7/cloud/reports/`

### Langkah penyelesaian

Masuk ke direktori laporan:

```bash
cd cloud/reports
```

Hitung jumlah baris seluruh file log:

```bash
wc -l *.log
```

Pilih file yang memiliki tepat 15 baris, yaitu `daily-03.log`.

Baca file tersebut:

```bash
cat daily-03.log
```

**Jawaban:** ambil nilai setelah `password=` pada baris akun `level8`. Nilai tersebut merupakan password untuk akun `level8`.

**Penjelasan command:**
- `wc`: menghitung jumlah kata, baris, dan karakter.
- `-l`: menampilkan jumlah baris.
- `*.log`: memilih semua file dengan ekstensi `.log`.

**Alur password:** Level 7 → Level 8.

---

## Level 8 — Permission Denied

**Materi:** mengubah permission file menggunakan `chmod`.

**Lokasi file target:** `/home/level8/cloud/credentials.txt`

### Langkah penyelesaian

Masuk ke direktori cloud:

```bash
cd cloud
```

Periksa permission:

```bash
ls -l
```

Tambahkan izin baca untuk pemilik file:

```bash
chmod u+r credentials.txt
```

Baca file:

```bash
cat credentials.txt
```

**Jawaban:** ambil nilai setelah `password=`. Nilai tersebut merupakan password untuk akun `level9`.

**Penjelasan command:**
- `chmod`: mengubah permission.
- `u`: pemilik file (user).
- `+r`: menambahkan izin baca (read).

File awalnya memiliki permission `000`, sehingga pemilik perlu menambahkan izin baca terlebih dahulu.

**Alur password:** Level 8 → Level 9.

---

## Level 9 — The Stuck Worker

**Materi:** melihat dan menghentikan proses menggunakan `ps` dan `kill`.

### Langkah penyelesaian

Lihat daftar proses:

```bash
ps aux
```

Cari proses dengan nama `backup-worker.py`. Catat PID yang berada pada kolom kedua.

Hentikan proses tersebut:

```bash
kill PID
```

Ganti `PID` dengan nomor proses yang ditemukan. Tunggu worker berhenti, kemudian baca laporan:

```bash
cat cloud/recovery-report.txt
```

**Jawaban:** ambil nilai setelah `password=` pada laporan. Nilai tersebut merupakan password untuk akun `level10`.

**Penjelasan command:**
- `ps aux`: menampilkan daftar proses yang sedang berjalan.
- `kill PID`: mengirim sinyal untuk menghentikan proses berdasarkan PID. Secara default, `kill` mengirim SIGTERM.

**Catatan:** peserta hanya boleh menghentikan proses `backup-worker.py` milik challenge, bukan proses sistem Ubuntu.

**Alur password:** Level 9 → Level 10.

---

## Level 10 — The Hidden Endpoint

**Materi:** memeriksa port listening dan mengakses layanan HTTP menggunakan `ss` dan `curl`.

### Langkah penyelesaian

Baca informasi layanan:

```bash
cat cloud/service-status.txt
```

Periksa port yang sedang listening:

```bash
ss -tuln
```

Cari layanan yang menggunakan alamat lokal `127.0.0.1`. Catat nomor port yang ditemukan.

Akses endpoint:

```bash
curl http://127.0.0.1:PORT
```

Ganti `PORT` dengan nomor port yang ditemukan dari output `ss`.

**Jawaban:** respons HTTP akan menampilkan Final Flag EVCONN.

**Penjelasan command:**
- `ss -tuln`: menampilkan socket TCP/UDP yang sedang listening tanpa menerjemahkan alamat dan nomor port ke nama layanan.
- `curl`: mengirim request ke URL dan menampilkan respons dari layanan.

**Alur:** Level 10 merupakan tantangan terakhir. Tidak ada akun lanjutan.

---

## Rekap password flow

| Level yang diselesaikan | Lokasi password berikutnya | Akun tujuan |
|---|---|---|
| Level 0 | `pw-evconn.md` | `player` → `level1` |
| Level 1 | `-` | `level2` |
| Level 2 | `.secret` | `level3` |
| Level 3 | `cloud-audit.log` | `level4` |
| Level 4 | `recovery-token.txt` | `level5` |
| Level 5 | `17.log` | `level6` |
| Level 6 | `deployment.log` | `level7` |
| Level 7 | `daily-03.log` | `level8` |
| Level 8 | `credentials.txt` | `level9` |
| Level 9 | `recovery-report.txt` | `level10` |
| Level 10 | Endpoint HTTP | Final Flag |

---

## Catatan penting untuk operator

1. Password akun ditentukan oleh operator melalui `main.py`. Gunakan password yang berbeda untuk setiap akun.
2. Password yang ditanam sebagai jawaban pada suatu level harus sama dengan password akun tujuan pada level berikutnya.
3. Password akun `player` dibagikan kepada peserta secara terpisah. Password akun `level1` diperoleh dari `pw-evconn.md`.
4. Jalankan pengujian menggunakan `su - player`, kemudian ikuti alur sampai Level 10.
5. Generator dirancang untuk tidak menimpa akun atau direktori yang sudah ada. Untuk pengujian ulang, gunakan VM bersih atau pulihkan snapshot.
6. Jangan membagikan `kunjaw.md` dan Final Flag kepada peserta.
7. Sebelum membuat OVA, uji seluruh level setelah VM dinyalakan ulang. Perhatikan bahwa worker Level 9 pada versi generator saat ini belum dibuat sebagai service persisten, sehingga perlu penyesuaian sebelum OVA final didistribusikan.

---

**EVCONN STUDY GROUP — Cloud & Linux Fundamentals Lab**

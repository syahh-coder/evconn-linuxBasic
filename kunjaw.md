# KUNCI JAWABAN — EVCONN CLOUD WARGAME
## Level 0–5

> **Khusus operator/mentor. Jangan dibagikan kepada peserta sebelum challenge selesai.**

Dokumen ini berisi alur penyelesaian, command yang diharapkan, lokasi file target, dan hubungan password antarlevel. Password sebenarnya ditentukan oleh operator saat menjalankan generator, jadi tidak ada password tetap yang ditulis di dokumen ini.

---

## Level 0 — The Beginning

**Materi:** membaca file menggunakan `cat`.

### Langkah penyelesaian

```bash
cat README.md
cat pw-evconn.md
```

**Jawaban:** password untuk login ke akun `level1` terdapat di dalam `pw-evconn.md`.

**Alur password:** Level 0 → Level 1.

---

## Level 1 — The Dash File

**Materi:** membaca file yang namanya berupa tanda minus (`-`).

**Lokasi file target:**

```text
/home/level1/-
```

### Langkah penyelesaian

```bash
ls
cat ./-
```

**Jawaban:** isi file `-` merupakan password untuk akun `level2`.

**Mengapa menggunakan `./-`?**

Tanda minus dapat dibaca sebagai opsi oleh command. Dengan menuliskan `./-`, kita menyebut file bernama `-` yang berada di direktori saat ini.

**Alur password:** Level 1 → Level 2.

---

## Level 2 — The Invisible Secret

**Materi:** hidden files atau file tersembunyi.

**Lokasi file target:**

```text
/home/level2/.secret
```

### Langkah penyelesaian

```bash
ls -la
cat .secret
```

**Jawaban:** isi file `.secret` merupakan password untuk akun `level3`.

**Penjelasan:** file yang namanya diawali tanda titik (`.`) termasuk hidden file. Opsi `-a` pada `ls` menampilkan file tersembunyi.

**Alur password:** Level 2 → Level 3.

---

## Level 3 — The Cloud Audit Log

**Materi:** mencari teks di dalam file menggunakan `grep`.

**Lokasi file target:**

```text
/home/level3/cloud-audit.log
```

### Langkah penyelesaian

```bash
grep -in "credential_ready" cloud-audit.log
```

Baris target memiliki pola seperti berikut:

```text
[IAM-CREDENTIAL-EXPORT] account=level4 status=credential_ready password=<PASSWORD_LEVEL4>
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

**Materi:** mencari file berdasarkan beberapa karakteristik menggunakan `find`.

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

## Rekap password flow

| Level yang diselesaikan | Lokasi password berikutnya | Akun tujuan |
|---|---|---|
| Level 0 | `pw-evconn.md` | `level1` |
| Level 1 | `-` | `level2` |
| Level 2 | `.secret` | `level3` |
| Level 3 | `cloud-audit.log` | `level4` |
| Level 4 | `recovery-token.txt` | `level5` |
| Level 5 | `17.log` | `level6` |

## Catatan untuk operator

1. Password tidak ditentukan secara permanen di dokumen ini. Gunakan password yang dimasukkan saat menjalankan generator.
2. Password yang ditanam sebagai jawaban pada suatu level harus sama dengan password akun tujuan pada level berikutnya.
3. Saat menguji, login menggunakan akun level terkait dengan `su - levelN`.
4. Jika generator menolak berjalan karena akun sudah ada, periksa VM atau gunakan VM pengujian bersih. Generator dirancang untuk tidak menimpa akun yang sudah tersedia.
5. Kunci jawaban ini mengikuti versi Level 4 **The Lost Snapshot** yang mencari `recovery-token.txt`, dan Level 5 **The Oversized Cloud Log** yang mencari file `.log` berukuran lebih dari 1 KiB.

---

**EVCONN STUDY GROUP — Cloud & Linux Fundamentals Lab**

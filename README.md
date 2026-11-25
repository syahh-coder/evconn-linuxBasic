# EVCONN Linux Wargame

Lab pengenalan Linux untuk Study Group EVCONN dengan pendekatan mini CTF bertema Cloud Operations.

Panduan ini dimulai dari **Ubuntu Server yang baru selesai diinstal**, belum memiliki Git, dan belum dipasang dependency EVCONN.

## 1. Gambaran alur instalasi

Urutan dari Ubuntu Server kosong sampai lab siap dimainkan:

1. Login ke Ubuntu Server menggunakan akun yang memiliki akses `sudo`.
2. Update daftar paket Ubuntu.
3. Install Git agar bisa clone repository.
4. Clone repository EVCONN dari GitHub.
5. Jalankan `script.sh` untuk memasang Python dan dependency challenge.
6. Jalankan `main.py` untuk membuat `password.txt` jika belum ada.
7. Isi password operator di `password.txt`.
8. Jalankan kembali `main.py` untuk membuat akun dan challenge Level 0–10.

**Catatan:** seluruh proses dijalankan di dalam Ubuntu Server VM, bukan di terminal Windows/host.

## 2. Persyaratan VM

Rekomendasi untuk lab Study Group:

- Ubuntu Server 22.04 LTS atau lebih baru.
- RAM minimal 2 GB (disarankan 4 GB).
- CPU minimal 2 core.
- Disk minimal 20 GB.
- Network VM aktif dan dapat mengakses internet saat instalasi.
- Akun Ubuntu yang memiliki akses `sudo`.
- systemd aktif sebagai init system.

Gunakan VM khusus untuk EVCONN. Jangan jalankan generator ini pada server produksi atau server yang menyimpan data penting.

## 3. Tahap pertama — Siapkan Ubuntu Server kosong

Setelah Ubuntu Server selesai diinstal:

1. Login menggunakan username dan password Ubuntu yang dibuat saat instalasi.
2. Pastikan akun tersebut memiliki akses `sudo`.
3. Pastikan jaringan VM aktif agar Ubuntu dapat mengunduh paket dan mengakses GitHub.

Cek user yang sedang login:

```bash
whoami
```

Cek akses sudo:

```bash
sudo -v
```

Jika perintah tersebut berhasil tanpa error, lanjutkan.

### Update daftar paket Ubuntu

```bash
sudo apt update
```

Opsional, jika ingin memasang pembaruan sistem terlebih dahulu:

```bash
sudo apt upgrade -y
```

### Install Git

Ubuntu yang baru diinstal belum tentu memiliki Git. Pasang Git dan sertifikat HTTPS terlebih dahulu:

```bash
sudo apt install -y git ca-certificates
```

Periksa instalasi Git:

```bash
git --version
```

Jika versi Git muncul, berarti Git sudah siap digunakan.

> Jika `sudo` tidak tersedia, login sebagai root atau siapkan akun administrator Ubuntu terlebih dahulu. Perintah instalasi paket kemudian dijalankan dari shell root tanpa awalan `sudo`.

## 4. Tahap kedua — Clone repository EVCONN

Clone repository dari GitHub:

```bash
git clone <URL-REPOSITORY>
```

Masuk ke direktori repository:

```bash
cd evconn-linux-wargame
```

Jika nama folder hasil clone berbeda, sesuaikan nama folder pada perintah `cd`.

Periksa isi repository:

```bash
ls -la
```

Pastikan file berikut tersedia:

```text
main.py
script.sh
level-0.py
level-1.py
level-2.py
level-3.py
level-4.py
level-5.py
level-6.py
level-7.py
level-8.py
level-9.py
level-10.py
password.example.txt
README.md
.gitignore
```

File `password.txt` dan file kunci jawaban operator memang tidak disertakan di repository publik.

## 5. Tahap ketiga — Jalankan script.sh

`script.sh` adalah installer dependency EVCONN. Script ini memasang Python 3, Git, dan command Linux yang dibutuhkan untuk challenge.

Berikan izin eksekusi:

```bash
chmod +x script.sh
```

Jalankan installer:

```bash
sudo ./script.sh
```

Tunggu sampai proses selesai dan muncul pesan:

```text
EVCONN LINUX WARGAME - SETUP SELESAI
```

Script akan memeriksa:

- Sistem operasi harus Ubuntu.
- Python minimal versi 3.10.
- Command Linux untuk Level 0–10 tersedia.
- systemd aktif sebagai init system.

### Paket yang dipasang

| Paket | Kegunaan |
|---|---|
| `python3` | Menjalankan generator EVCONN |
| `git` | Clone dan mengambil repository |
| `ca-certificates` | Sertifikat koneksi HTTPS |
| `nano` | Mengedit file konfigurasi password |
| `iproute2` | Command `ss` untuk Level 10 |
| `curl` | Mengakses endpoint Level 10 |
| `procps` | Command `ps` untuk Level 9 |
| `findutils` | Command `find` |
| `grep` | Command `grep` untuk Level 3 |
| `coreutils` | `cat`, `ls`, `head`, `tail`, `wc`, `chmod`, dan lainnya |
| `passwd` | `useradd`, `userdel`, dan `chpasswd` |
| `systemd` | Menjalankan service Level 9 dan Level 10 |

Tidak perlu memasang package Python menggunakan `pip`. Generator EVCONN menggunakan standard library Python dan command Ubuntu.

## 6. Tahap keempat — Siapkan password.txt

Semua password akun dan Final Flag dikelola melalui satu file `password.txt`.

Pada eksekusi pertama, jika `password.txt` belum ada, `main.py` akan membuat file tersebut dari `password.example.txt`, mengatur permission menjadi `600`, lalu berhenti agar operator dapat mengisi nilainya.

Jalankan:

```bash
sudo python3 main.py
```

Setelah file dibuat, edit:

```bash
sudo nano password.txt
```

Isi seluruh nilai placeholder dengan password pilihan operator:

```ini
password0=PASSWORD_AKUN_PLAYER
password1=PASSWORD_AKUN_LEVEL1
password2=PASSWORD_AKUN_LEVEL2
password3=PASSWORD_AKUN_LEVEL3
password4=PASSWORD_AKUN_LEVEL4
password5=PASSWORD_AKUN_LEVEL5
password6=PASSWORD_AKUN_LEVEL6
password7=PASSWORD_AKUN_LEVEL7
password8=PASSWORD_AKUN_LEVEL8
password9=PASSWORD_AKUN_LEVEL9
password10=PASSWORD_AKUN_LEVEL10

final_flag=EVCONN{FINAL_FLAG}
```

Arti setiap key:

| Key | Password untuk akun | Ditemukan peserta pada |
|---|---|---|
| `password0` | `player` | Diberikan operator kepada peserta |
| `password1` | `level1` | Level 0 |
| `password2` | `level2` | Level 1 |
| `password3` | `level3` | Level 2 |
| `password4` | `level4` | Level 3 |
| `password5` | `level5` | Level 4 |
| `password6` | `level6` | Level 5 |
| `password7` | `level7` | Level 6 |
| `password8` | `level8` | Level 7 |
| `password9` | `level9` | Level 8 |
| `password10` | `level10` | Level 9 |
| `final_flag` | Tidak digunakan sebagai password akun | Level 10 |

**Penting:**
- Jangan biarkan nilai `GANTI_` atau placeholder lain.
- Gunakan password berbeda untuk setiap akun.
- Password tidak boleh mengandung tanda titik dua (`:`) atau baris baru.
- Jangan menambahkan spasi di awal atau akhir nilai.
- `password.txt` berisi password plaintext, jadi hanya operator yang boleh mengaksesnya.

Simpan file, lalu batasi permission:

```bash
sudo chmod 600 password.txt
```

## 7. Tahap kelima — Buat seluruh challenge

Setelah `password.txt` selesai diisi, jalankan kembali:

```bash
sudo python3 main.py
```

Jika Ubuntu VM masih bersih, `main.py` akan:

1. Memeriksa seluruh file generator.
2. Membaca konfigurasi password.
3. Membuat akun `player` dan `level1` sampai `level10`.
4. Membuat seluruh direktori dan file challenge.
5. Mengaktifkan service Level 9 dan Level 10.
6. Menampilkan pesan bahwa lab berhasil dibuat.

Jika berhasil, akan muncul informasi bahwa akun awal peserta adalah `player`.

Peserta tidak perlu menjalankan file `level-0.py` sampai `level-10.py` secara manual. Seluruh challenge dibuat oleh `main.py`.

## 8. Tahap keenam — Mulai permainan

Berikan password akun `player` (`password0`) kepada peserta melalui jalur terpisah.

Untuk menguji permainan sebagai peserta:

```bash
su - player
```

Masukkan password `player`, kemudian:

```bash
cat README.md
```

Ikuti instruksi Level 0. Password untuk masuk ke level berikutnya ditemukan dengan menyelesaikan challenge sebelumnya.

Untuk keluar dari akun peserta:

```bash
exit
```

## 9. Mengubah password setelah lab dibuat

Jika operator ingin mengganti password, edit file:

```bash
sudo nano password.txt
```

Ubah nilai password yang diperlukan, simpan, lalu jalankan:

```bash
sudo python3 main.py
```

Jika lab sudah terpasang, `main.py` akan mendeteksi instalasi dan meminta konfirmasi:

```text
Instalasi EVCONN sudah ditemukan.
Mode: UPDATE PASSWORD.

Lanjutkan update? [y/N]:
```

Ketik `y` untuk melanjutkan.

Mode update akan memperbarui password akun Linux dan password yang tertanam pada file challenge, termasuk worker Level 9 dan Final Flag Level 10. Service Level 9 dan Level 10 akan direstart.

**Jangan menjalankan mode update ketika peserta sedang mengerjakan challenge**, karena password jawaban dan proses challenge dapat berubah.

Jika instalasi terdeteksi tidak lengkap, jangan memaksa menjalankan ulang generator. Periksa error atau pulihkan snapshot VM yang bersih.

## 10. Pemeriksaan service

Level 9 dan Level 10 menggunakan systemd service.

Periksa statusnya:

```bash
sudo systemctl status evconn-level9.service
sudo systemctl status evconn-level10.service
```

Keduanya seharusnya berstatus `active (running)` ketika challenge siap digunakan.

Setelah reboot, periksa kembali kedua service tersebut sebelum peserta mulai bermain.

## 11. Keamanan dan persiapan distribusi

- `password.txt` berisi password plaintext. Jangan upload ke GitHub.
- `kunjaw.md` dan `kunjaw_toThePoint.md` adalah dokumen operator. Jangan bagikan kepada peserta.
- `.gitignore` mengecualikan file password dan kunci jawaban.
- `password.example.txt` hanya berisi placeholder dan boleh dimasukkan ke repository.
- Jangan menjalankan lab pada server produksi.
- Uji semua level dari Level 0 sampai Level 10.
- Uji reboot Ubuntu dan pastikan service Level 9 serta Level 10 aktif kembali.
- Buat snapshot VM setelah seluruh pengujian berhasil.
- Sebelum mengekspor OVA, pastikan tidak ada password operator atau catatan kunci jawaban yang ikut dibagikan.

---

**EVCONN STUDY GROUP — Cloud & Linux Fundamentals Lab**

#!/usr/bin/env python3
"""Generator challenge Level 3 - EVCONN Linux Wargame.

Challenge: The Noisy Logs

Fungsi utama:
    create_level3(password_level3, password_level4, home_root="/home")

Fungsi ini dirancang agar nantinya dapat dipanggil oleh main.py.
Script membuat akun Linux level3, README.md, hint.md, dan satu file
system.log yang berisi banyak baris log. Password untuk akun level4
disisipkan di antara baris-baris log tersebut.

Jalankan secara mandiri di Ubuntu Server:
    sudo python3 level-3.py

Catatan: mode mandiri meminta operator memasukkan password secara interaktif.
Password Level 3 harus sama dengan password yang ditemukan peserta pada Level 2.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import subprocess
from pathlib import Path

USERNAME = "level3"
DEFAULT_HOME_ROOT = Path("/home")

README_CONTENT = """# EVCONN LINUX WARGAME
## LEVEL 3 — THE NOISY LOGS

### CERITA

Akun level3 terbuka, dan kali ini kamu nggak sedang berada di sebuah
server fisik di ruangan dingin. Kamu ada di dalam sebuah instance yang
berjalan di awan, salah satu dari sekian banyak mesin virtual yang
menyala dan padam tanpa pernah ada yang memperhatikan.

Di direktori ini ada satu file: `system.log`.

Setiap instance cloud punya kebiasaan yang sama, yaitu mencatat segalanya.
Layanan yang hidup lalu mati, health check yang lolos, autoscaling yang
naik dan turun, percobaan login yang gagal, snapshot backup yang jalan
tengah malam. Ratusan baris, semuanya terdengar penting, nyaris semuanya
cuma bising.

Admin yang terburu-buru itu ternyata pernah ada di sini. Dalam
kesibukannya menyalakan dan mematikan resource, ada satu hal yang ikut
tercatat tanpa dia sadari: kunci menuju akun berikutnya, terselip di
antara kebisingan yang dia ciptakan sendiri.

Kamu bisa membaca semuanya dari atas sampai bawah. Tapi di cloud, waktu
adalah tagihan.

### TUJUAN

Temukan password yang digunakan untuk masuk ke akun `level4`.

### PETUNJUK

1. Periksa file yang tersedia di direktori saat ini.
2. File log yang panjang jarang dibaca dari baris pertama sampai terakhir.
3. Tidak semua baris yang terdengar meyakinkan membawa jawaban yang benar.
4. Butuh bantuan? Baca file `hint.md`.

Selamat mencoba!

**EVCONN STUDY GROUP — Linux Fundamentals Lab**
"""

HINT_CONTENT = """# HINT — LEVEL 3

Command yang mungkin kamu butuhkan:

- ls
- cat
- less
- grep
- man
"""
HINT_CONTENT = """# HINT — LEVEL 3

Command yang mungkin kamu butuhkan:

- ls
- cat
- less
- grep
- grep -i
- grep -n

Petunjuk tambahan:

- `grep` digunakan untuk mencari teks tertentu di dalam file.
- Gunakan `-i` agar pencarian tidak membedakan huruf besar dan kecil.
- Gunakan `-n` untuk menampilkan nomor baris hasil pencarian.
- Coba cari kata yang berkaitan dengan password atau kredensial
  di dalam file `cloud-audit.log`.
- Periksa konteks setiap hasil karena beberapa baris merupakan
  catatan dan percakapan pengecoh dari tim Cloud Operations.

Contoh pola perintah:

    grep -in "kata_kunci" cloud-audit.log
"""


def _require_root() -> None:
    """Pastikan generator dijalankan dengan hak akses root."""
    if os.geteuid() != 0:
        raise PermissionError(
            "Script harus dijalankan sebagai root. Gunakan: sudo python3 level-3.py"
        )


def _validate_password(password: str, label: str) -> None:
    """Validasi agar format input aman untuk chpasswd dan file teks."""
    if not isinstance(password, str) or not password:
        raise ValueError(f"{label} tidak boleh kosong.")
    if any(char in password for char in ("\n", "\r", ":")):
        raise ValueError(
            f"{label} tidak boleh mengandung baris baru atau tanda titik dua (:)."
        )


def _set_linux_password(username: str, password: str) -> None:
    """Atur password akun tanpa menaruh password pada argumen command line."""
    subprocess.run(
        ["chpasswd"],
        input=f"{username}:{password}\n",
        text=True,
        check=True,
    )


def _build_system_log(password_level4: str) -> str:
    """Buat log audit cloud dengan aktivitas infrastruktur, jokes, dan satu kredensial target."""
    entries = [
        "[COMPUTE] Instance vm-web-01 berhasil dijalankan.",
        "[COMPUTE] Instance vm-db-02 berhasil dihentikan.",
        "[NETWORK] Virtual network evconn-vnet berhasil diperiksa.",
        "[NETWORK] Pemeriksaan konektivitas antar-subnet selesai.",
        "[STORAGE] Object storage berhasil merespons permintaan.",
        "[STORAGE] Bucket evconn-backup berhasil disinkronkan.",
        "[IAM] Pemeriksaan kebijakan akses pengguna selesai.",
        "[SECURITY] Pemeriksaan konfigurasi firewall cloud selesai.",
        "[MONITORING] Penggunaan CPU instance berada dalam batas normal.",
        "[MONITORING] Penggunaan memori berhasil direkam.",
        "[BACKUP] Snapshot instance berhasil dibuat.",
        "[AUTOSCALING] Jumlah instance tetap sesuai kebutuhan beban kerja.",
        "[CLOUD-BILLING] Perhitungan biaya layanan cloud berhasil diperbarui.",
        "[CHAT] Admin: Tagihan cloud naik lagi. Siapa yang lupa mematikan VM?",
        "[CHAT] Operator: Sepertinya ada 12 instance yang masih menyala sejak Jumat.",
        "[CHAT] Admin: Itu bukan autoscaling, itu auto-boros.",
        "[STORAGE] Ijazah admin belum ditemukan. Kemungkinan tersimpan di bucket yang salah.",
        "[CHAT] Operator: Sudah coba cari di object storage, Pak?",
        "[CHAT] Admin: Sudah, yang ketemu malah foto kucing di folder backup.",
        "[NETWORK] Latency meningkat selama proses pengujian jaringan.",
        "[CHAT] Admin: Kenapa koneksi lambat?",
        "[CHAT] Operator: Mungkin admin sedang mengunduh game dari instance produksi.",
        "[SECURITY] Bucket evconn-public ditemukan memiliki akses publik.",
        "[CHAT] Admin: Bucket public itu disengaja, kan?",
        "[CHAT] Operator: Tidak, Pak. Itu salah konfigurasi.",
        "[BACKUP] Snapshot berhasil dibuat. Kenangan mantan tidak termasuk dalam backup.",
        "[CHAT] Admin: Siapa yang menghapus snapshot terakhir?",
        "[CHAT] Operator: Saya kira itu file duplikat, Pak.",
        "[IAM] Pengguna cloud meminta reset password.",
        "[CHAT] Admin: Password yang kuat itu penting.",
        "[CHAT] Operator: Password admin masih nama kucing, Pak.",
        "[COMPUTE] Instance berhasil berjalan. Admin belum berhasil move on.",
        "[MONITORING] Dashboard cloud menampilkan seluruh layanan dalam kondisi aktif.",
        "[CHAT] Admin: Kalau semua layanan hijau, kenapa dompet saya merah?",
        "[CLOUD-BILLING] Biaya penyimpanan meningkat karena file log lama belum dihapus.",
        "[CHAT] Operator: Log tahun lalu masih disimpan semua.",
        "[CHAT] Admin: Hapus yang tidak diperlukan, jangan hapus kenangan.",
        "[NETWORK] Load balancer berhasil mendistribusikan trafik.",
        "[CHAT] Admin: Load balancer bisa membagi beban kerja, bisa membagi beban pikiran?",
        "[STORAGE] Replikasi data antar-zone berhasil.",
        "[SECURITY] Percobaan autentikasi pengguna guest ditolak.",
        "[CHAT] Operator: Ada yang tahu password Wi-Fi ruang cloud?",
        "[CHAT] Admin: Tanya access point, jangan tanya saya.",
        "[AUTOSCALING] Skala layanan tidak berubah karena trafik stabil.",
        "[CHAT] Admin: Instance bertambah terus.",
        "[CHAT] Operator: Itu bukan instance, Pak. Itu tab browser Bapak.",
        "[BACKUP] Retensi backup berhasil diperiksa.",
        "[CHAT] Admin: Backup sudah aman?",
        "[CHAT] Operator: Aman, Pak. Yang belum aman cuma deadline laporan.",
        "[SECURITY] Pemeriksaan akses bucket selesai.",
        "[CHAT] Admin: Jangan simpan kredensial di file catatan biasa.",
        "[CHAT] Operator: Siap, Pak. Saya simpan di sticky note digital.",
        "[MONITORING] Alarm penggunaan CPU berhasil dikirim.",
        "[CHAT] Admin: Server panas sekali.",
        "[CHAT] Operator: Coba matikan instance yang tidak dipakai, Pak.",
        "[CLOUD-BILLING] Tagihan layanan komputasi berhasil dihitung.",
        "[CHAT] Admin: Tolong cari cara supaya cloud gratis selamanya.",
        "[CHAT] Operator: Kalau ketemu, kabari seluruh dunia, Pak.",
        "[STORAGE] Object storage menerima permintaan unggah berkas.",
        "[CHAT] Admin: File final yang mana?",
        "[CHAT] Operator: final_fix_baru_beneran_terakhir_v7.zip.",
        "[NETWORK] Pemeriksaan DNS cloud selesai.",
        "[CHAT] Admin: DNS itu singkatan dari 'Duh, Network Saya'?",
        "[IAM] Peran pengguna berhasil diperbarui.",
        "[CHAT] Operator: Akses admin sudah diberikan.",
        "[CHAT] Admin: Jangan sampai diberikan ke semua orang, ya.",
        "[SECURITY] Audit konfigurasi keamanan cloud sedang berlangsung.",
        "[INFO] Seluruh layanan utama EVCONN Cloud terpantau aktif.",
    ]

    lines: list[str] = []

    # Buat 200 baris aktivitas cloud dengan waktu dan nomor kejadian berbeda.
    for index in range(1, 201):
        hour = 8 + ((index - 1) // 3600)
        minute = ((index - 1) // 60) % 60
        second = (index - 1) % 60
        timestamp = f"2026-11-24 {hour:02d}:{minute:02d}:{second:02d}"
        message = entries[(index * 7 + index // 3) % len(entries)]
        lines.append(f"{timestamp} [EVENT-{index:04d}] {message}")

    # Satu baris kredensial target di antara catatan audit cloud.
    target_line = (
        "2026-11-24 08:02:17 [EVENT-0118] [IAM-CREDENTIAL-EXPORT] "
        f"account=level4 status=credential_ready password={password_level4}"
    )
    lines.insert(117, target_line)

    return "\n".join(lines) + "\n"

def create_level3(
    password_level3: str,
    password_level4: str,
    home_root: str | Path = DEFAULT_HOME_ROOT,
) -> Path:
    """Buat akun dan challenge Level 3.

    Args:
        password_level3: Password untuk login ke akun Linux `level3`.
                         Password ini berasal dari Level 2.
        password_level4: Password yang harus ditemukan peserta di Level 3.
                         Password ini akan menjadi password akun `level4`.
        home_root: Direktori induk home akun. Default: `/home`.

    Returns:
        Path menuju home directory akun `level3`.

    Raises:
        PermissionError: Jika script tidak dijalankan sebagai root.
        ValueError: Jika password tidak valid.
        RuntimeError: Jika akun atau direktori tujuan sudah tersedia.
        subprocess.CalledProcessError: Jika perintah Linux gagal.
    """
    _require_root()
    _validate_password(password_level3, "Password Level 3")
    _validate_password(password_level4, "Password Level 4")

    home_root = Path(home_root).expanduser().resolve()
    home_root.mkdir(parents=True, exist_ok=True)
    home_dir = home_root / USERNAME

    try:
        pwd.getpwnam(USERNAME)
    except KeyError:
        pass
    else:
        raise RuntimeError(
            f"Akun '{USERNAME}' sudah ada. Hentikan proses dan periksa VM terlebih dahulu."
        )

    if home_dir.exists():
        raise RuntimeError(
            f"Direktori '{home_dir}' sudah ada. Tidak ada file yang ditimpa."
        )

    user_created = False

    try:
        # Buat akun Linux dengan home directory dan shell Bash.
        subprocess.run(
            [
                "useradd",
                "--create-home",
                "--home-dir",
                str(home_dir),
                "--shell",
                "/bin/bash",
                USERNAME,
            ],
            check=True,
        )
        user_created = True

        # Atur password akun level3.
        _set_linux_password(USERNAME, password_level3)

        account = pwd.getpwnam(USERNAME)

        # Buat README untuk peserta.
        readme_path = home_dir / "README.md"
        readme_path.write_text(README_CONTENT, encoding="utf-8")

        # Buat hint berisi daftar command yang mungkin dibutuhkan.
        hint_path = home_dir / "hint.md"
        hint_path.write_text(HINT_CONTENT, encoding="utf-8")

        # Satu file utama berisi 201 baris log, termasuk satu baris password.
        log_path = home_dir / "cloud-audit.log"
        log_path.write_text(
            _build_system_log(password_level4),
            encoding="utf-8",
        )

        # Atur kepemilikan seluruh file kepada akun level3.
        for path in (home_dir, readme_path, hint_path, log_path):
            os.chown(path, account.pw_uid, account.pw_gid)

        # Home hanya dapat diakses pemiliknya.
        os.chmod(home_dir, 0o700)

        # File dapat dibaca pemilik, tetapi tidak dapat diubah peserta.
        os.chmod(readme_path, 0o400)
        os.chmod(hint_path, 0o400)
        os.chmod(log_path, 0o400)

        return home_dir

    except Exception:
        # Jika pembuatan gagal di tengah jalan, bersihkan akun yang baru dibuat.
        if user_created:
            subprocess.run(
                ["userdel", "--remove", USERNAME],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if home_dir.exists():
                shutil.rmtree(home_dir, ignore_errors=True)
        raise


def main() -> None:
    """Mode mandiri untuk menguji generator Level 3."""
    _require_root()

    print("=== EVCONN LINUX WARGAME: GENERATOR LEVEL 3 ===")
    print("Challenge: The Noisy Logs\n")

    print("Masukkan password yang akan digunakan peserta untuk login ke level3.")
    password_level3 = getpass.getpass("Password Level 3: ")
    password_level3_confirm = getpass.getpass("Ulangi Password Level 3: ")

    if password_level3 != password_level3_confirm:
        raise SystemExit("Password Level 3 tidak cocok. Tidak ada akun yang dibuat.")

    print("\nMasukkan password yang harus ditemukan peserta untuk Level 4.")
    password_level4 = getpass.getpass("Password Level 4: ")
    password_level4_confirm = getpass.getpass("Ulangi Password Level 4: ")

    if password_level4 != password_level4_confirm:
        raise SystemExit("Password Level 4 tidak cocok. Tidak ada akun yang dibuat.")

    created_home = create_level3(password_level3, password_level4)

    print("\n[BERHASIL] Challenge Level 3 berhasil dibuat.")
    print(f"Akun Linux : {USERNAME}")
    print(f"Home       : {created_home}")
    print("\nUntuk menguji login, jalankan:")
    print("  su - level3")
    print("\nDi dalam akun level3, baca petunjuk dengan:")
    print("  cat README.md")
    print("  cat hint.md")
    print("\nPeriksa panjang file log dengan:")
    print("  wc -l cloud-audit.log")
    print("\nCari informasi password dengan grep, misalnya:")
    print('  grep -in "password" cloud-audit.log')
    print("\nPassword Level 3 yang kamu masukkan tadi harus sama dengan")
    print("password yang ditemukan peserta pada Level 2.")


if __name__ == "__main__":
    main()

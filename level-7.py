#!/usr/bin/env python3
"""Generator challenge Level 7 - EVCONN Cloud Wargame.

Challenge: The Missing Report

Fungsi utama:
    create_level7(password_level7, password_level8, home_root="/home")

Script membuat akun Linux level7, README.md, hint.md, dan beberapa file
laporan cloud. Salah satu laporan memiliki tepat 15 baris dan berisi
password untuk akun level8.

Jalankan secara mandiri di Ubuntu Server:
    sudo python3 level-7.py

Password Level 7 harus sama dengan password yang ditemukan peserta
pada Level 6.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import subprocess
from pathlib import Path

USERNAME = "level7"
DEFAULT_HOME_ROOT = Path("/home")

README_CONTENT = """# EVCONN CLOUD WARGAME
## LEVEL 7 — THE MISSING REPORT

### CERITA

Tim Cloud Operations EVCONN sedang memeriksa laporan aktivitas beberapa
virtual machine setelah pekerjaan maintenance selesai.

Ada beberapa file laporan di direktori `cloud/reports`. Nama file-nya
hampir sama karena semuanya dibuat otomatis oleh sistem monitoring.

Administrator meninggalkan pesan:

"Saya butuh satu laporan untuk melanjutkan pemeriksaan. Seingat saya,
laporan itu punya tepat 15 baris. Yang lain bukan. Tolong cari, ya.
Saya sudah terlalu lama menatap dashboard sampai angka tagihan cloud
terlihat seperti nomor telepon."

Kamu tidak perlu membuka semua laporan satu per satu. Linux memiliki
command sederhana untuk menghitung jumlah baris dalam file.

### TUJUAN

Temukan file laporan yang memiliki tepat 15 baris.

Baca file tersebut untuk mendapatkan password akun `level8`.

### PETUNJUK

1. Masuk ke direktori `cloud/reports`.
2. Periksa jumlah baris setiap file laporan.
3. Pilih laporan yang memiliki tepat 15 baris.
4. Baca laporan tersebut untuk menemukan password berikutnya.

Selamat mencoba!

**EVCONN STUDY GROUP — Cloud & Linux Fundamentals Lab**
"""

HINT_CONTENT = """# HINT — LEVEL 7
## THE MISSING REPORT

Command yang mungkin kamu butuhkan:

- `pwd`    : melihat lokasi direktori saat ini.
- `ls`     : melihat isi direktori.
- `wc -l`  : menghitung jumlah baris dalam file.
- `cat`    : membaca isi file.

Petunjuk:

Masuk ke direktori laporan, lalu hitung jumlah baris semua file log.

Contoh:

    wc -l *.log

Cari file yang memiliki tepat 15 baris, lalu baca dengan `cat`.
"""


def _require_root() -> None:
    """Pastikan generator dijalankan dengan hak akses root."""
    if os.geteuid() != 0:
        raise PermissionError(
            "Script harus dijalankan sebagai root. Gunakan: sudo python3 level-7.py"
        )


def _validate_password(password: str, label: str) -> None:
    """Validasi password untuk chpasswd dan file teks."""
    if not isinstance(password, str) or not password:
        raise ValueError(f"{label} tidak boleh kosong.")
    if any(char in password for char in ("\n", "\r", ":")):
        raise ValueError(
            f"{label} tidak boleh mengandung baris baru atau tanda titik dua (:)."
        )


def _set_linux_password(username: str, password: str) -> None:
    """Atur password akun melalui stdin."""
    subprocess.run(
        ["chpasswd"],
        input=f"{username}:{password}\n",
        text=True,
        check=True,
    )


def _write_report(path: Path, lines: list[str]) -> None:
    """Tulis laporan dengan satu baris teks untuk setiap item."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_reports(home_dir: Path, password_level8: str) -> None:
    """Buat beberapa laporan dengan jumlah baris berbeda."""
    report_dir = home_dir / "cloud" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    reports = {
        "daily-01.log": [
            "[INFO] Report date: 2026-11-24",
            "[INFO] Region: ap-southeast-1",
            "[INFO] Instance: web-01",
            "[INFO] CPU status: normal",
            "[INFO] Memory status: normal",
            "[INFO] Disk status: normal",
            "[INFO] Report status: completed",
        ],
        "daily-02.log": [
            "[INFO] Report date: 2026-11-24",
            "[INFO] Region: ap-southeast-1",
            "[INFO] Instance: db-01",
            "[INFO] Database status: healthy",
            "[INFO] Connection pool: normal",
            "[INFO] Backup status: completed",
            "[INFO] Storage status: normal",
            "[INFO] Replication status: healthy",
            "[INFO] Monitoring status: active",
            "[INFO] No critical alerts detected",
            "[INFO] Report status: completed",
        ],
        "daily-03.log": [
            "[INFO] EVCONN Cloud Operations Report",
            "[INFO] Report date: 2026-11-24",
            "[INFO] Region: ap-southeast-1",
            "[INFO] Instance: app-03",
            "[INFO] Deployment status: completed",
            "[INFO] CPU usage: normal",
            "[INFO] Memory usage: normal",
            "[INFO] Disk usage: normal",
            "[INFO] Network status: connected",
            "[INFO] Health check: passed",
            "[INFO] Backup status: completed",
            "[INFO] Monitoring agent: active",
            "[INFO] Access audit: completed",
            f"[IAM] account=level8 password={password_level8}",
            "[INFO] Report status: completed",
        ],
        "daily-04.log": [
            "[INFO] Report date: 2026-11-24",
            "[INFO] Region: eu-west-1",
            "[INFO] Instance: app-04",
            "[INFO] Deployment status: completed",
            "[INFO] CPU usage: normal",
            "[INFO] Memory usage: normal",
            "[INFO] Disk usage: normal",
            "[INFO] Network status: connected",
            "[INFO] Health check: passed",
            "[INFO] Backup status: completed",
            "[INFO] Monitoring agent: active",
            "[INFO] Access audit: completed",
            "[INFO] No critical alerts detected",
            "[INFO] Load balancer: healthy",
            "[INFO] Storage volume: attached",
            "[INFO] Snapshot status: available",
            "[INFO] Report status: completed",
            "[INFO] Operator note: routine maintenance",
            "[INFO] Next check: scheduled",
        ],
        "daily-05.log": [
            "[INFO] Report date: 2026-11-24",
            "[INFO] Instance: test-05",
            "[INFO] Instance state: stopped",
            "[INFO] Report status: completed",
        ],
    }

    for filename, lines in reports.items():
        _write_report(report_dir / filename, lines)

    # File tambahan bukan laporan .log, sebagai bagian dari direktori cloud.
    (home_dir / "cloud" / "README.txt").write_text(
        "EVCONN Cloud Reports\nLaporan operasional disimpan di direktori reports.\n",
        encoding="utf-8",
    )


def create_level7(
    password_level7: str,
    password_level8: str,
    home_root: str | Path = DEFAULT_HOME_ROOT,
) -> Path:
    """Buat akun dan challenge Level 7.

    Args:
        password_level7: Password untuk login ke akun Linux `level7`.
                         Password ini berasal dari Level 6.
        password_level8: Password yang harus ditemukan peserta di Level 7.
                         Password ini akan menjadi password akun `level8`.
        home_root: Direktori induk home akun. Default: `/home`.

    Returns:
        Path menuju home directory akun `level7`.
    """
    _require_root()
    _validate_password(password_level7, "Password Level 7")
    _validate_password(password_level8, "Password Level 8")

    home_root = Path(home_root).expanduser().resolve()
    home_root.mkdir(parents=True, exist_ok=True)
    home_dir = home_root / USERNAME

    try:
        pwd.getpwnam(USERNAME)
    except KeyError:
        pass
    else:
        raise RuntimeError(
            f"Akun '{USERNAME}' sudah ada. Periksa VM terlebih dahulu."
        )

    if home_dir.exists():
        raise RuntimeError(
            f"Direktori '{home_dir}' sudah ada. Tidak ada file yang ditimpa."
        )

    user_created = False

    try:
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

        _set_linux_password(USERNAME, password_level7)
        account = pwd.getpwnam(USERNAME)

        (home_dir / "README.md").write_text(README_CONTENT, encoding="utf-8")
        (home_dir / "hint.md").write_text(HINT_CONTENT, encoding="utf-8")
        _build_reports(home_dir, password_level8)

        # Atur kepemilikan seluruh isi home kepada akun level7.
        os.chown(home_dir, account.pw_uid, account.pw_gid)
        for item in home_dir.rglob("*"):
            os.chown(item, account.pw_uid, account.pw_gid)

        # Direktori hanya dapat diakses pemilik akun.
        directories = [home_dir, *[p for p in home_dir.rglob("*") if p.is_dir()]]
        for directory in directories:
            os.chmod(directory, 0o700)

        # File hanya dapat dibaca pemilik akun.
        for file_path in [p for p in home_dir.rglob("*") if p.is_file()]:
            os.chmod(file_path, 0o400)

        return home_dir

    except Exception:
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
    """Mode mandiri untuk menguji generator Level 7."""
    _require_root()

    print("=== EVCONN CLOUD WARGAME: GENERATOR LEVEL 7 ===")
    print("Challenge: The Missing Report\n")

    print("Masukkan password untuk login ke akun level7.")
    password_level7 = getpass.getpass("Password Level 7: ")
    password_level7_confirm = getpass.getpass("Ulangi Password Level 7: ")

    if password_level7 != password_level7_confirm:
        raise SystemExit("Password Level 7 tidak cocok. Tidak ada akun yang dibuat.")

    print("\nMasukkan password yang harus ditemukan peserta untuk Level 8.")
    password_level8 = getpass.getpass("Password Level 8: ")
    password_level8_confirm = getpass.getpass("Ulangi Password Level 8: ")

    if password_level8 != password_level8_confirm:
        raise SystemExit("Password Level 8 tidak cocok. Tidak ada akun yang dibuat.")

    created_home = create_level7(password_level7, password_level8)

    print("\n[BERHASIL] Challenge Level 7 berhasil dibuat.")
    print(f"Akun Linux : {USERNAME}")
    print(f"Home       : {created_home}")
    print("\nUntuk menguji login, jalankan:")
    print("  su - level7")
    print("  cat README.md")
    print("  cat hint.md")
    print("  cd cloud/reports")
    print("  wc -l *.log")
    print("  cat daily-03.log")
    print("\nPassword Level 7 harus sama dengan password yang ditemukan")
    print("peserta pada Level 6.")


if __name__ == "__main__":
    main()

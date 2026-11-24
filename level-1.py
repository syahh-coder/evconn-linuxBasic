#!/usr/bin/env python3
"""Generator challenge Level 1 - EVCONN Linux Wargame.

Challenge: The Dash File

Fungsi utama:
    create_level1(password_level1, password_level2, home_root="/home")

Fungsi ini dirancang agar nantinya dapat dipanggil oleh main.py.
Script ini membuat akun Linux level1, README.md, hint.md, dan file
bernama '-' (yang berisi password untuk akun level2).

Jalankan secara mandiri di Ubuntu Server:
    sudo python3 level-1.py

Catatan: mode mandiri meminta operator memasukkan password secara interaktif.
Password Level 1 yang dimasukkan operator harus dicantumkan oleh main.py
ke file pw-evconn.md pada direktori Level 0.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import subprocess
from pathlib import Path

USERNAME = "level1"
DEFAULT_HOME_ROOT = Path("/home")

README_CONTENT = """# EVCONN LINUX WARGAME
## LEVEL 1 — THE DASH FILE

### CERITA

Pintu pertama terbuka tanpa suara.

Kamu masuk ke server EVCONN sebagai level1. Nggak ada alarm, nggak ada
yang menyapa. Cuma prompt yang berkedip pelan, seolah menunggu kamu salah
ketik.

Dari jejak di Level 0, kelihatan ada satu admin yang kerjanya terburu-buru.
Orang seperti itu hampir selalu meninggalkan sesuatu. Kali ini bukan sticky
note di pinggir monitor, tapi sebuah file yang tergeletak di home directory
ini. Isinya kunci menuju akun berikutnya.

Anehnya, nama file itu cuma satu karakter. Mungkin iseng. Mungkin nggak
sengaja. Atau mungkin dia tahu persis apa yang dia lakukan.

Kuncinya ada di depan mata. Kamu cuma perlu cari cara buat membukanya.

### TUJUAN

Temukan password yang digunakan untuk masuk ke akun `level2`.

### PETUNJUK

1. Periksa isi direktori tempat kamu berada.
2. Perhatikan apakah ada yang janggal.
3. Butuh bantuan? Baca file `hint.md`.

Selamat mencoba!

**EVCONN STUDY GROUP — Linux Fundamentals Lab**
"""

HINT_CONTENT = """# HINT — LEVEL 1

Command yang mungkin kamu butuhkan:

- ls
- cat
"""


def _require_root() -> None:
    """Pastikan generator dijalankan dengan hak akses root."""
    if os.geteuid() != 0:
        raise PermissionError(
            "Script harus dijalankan sebagai root. Gunakan: sudo python3 level-1.py"
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


def create_level1(
    password_level1: str,
    password_level2: str,
    home_root: str | Path = DEFAULT_HOME_ROOT,
) -> Path:
    """Buat akun dan challenge Level 1.

    Args:
        password_level1: Password untuk login ke akun Linux `level1`.
                        Password ini berasal dari Level 0.
        password_level2: Password yang harus ditemukan peserta di Level 1.
                        Password ini akan menjadi password akun `level2`.
        home_root: Direktori induk home akun. Default: `/home`.

    Returns:
        Path menuju home directory akun `level1`.

    Raises:
        PermissionError: Jika script tidak dijalankan sebagai root.
        ValueError: Jika password tidak valid.
        RuntimeError: Jika akun atau direktori tujuan sudah tersedia.
        subprocess.CalledProcessError: Jika perintah Linux gagal.
    """
    _require_root()
    _validate_password(password_level1, "Password Level 1")
    _validate_password(password_level2, "Password Level 2")

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

        # Password dikirim melalui stdin, bukan sebagai argumen command line.
        _set_linux_password(USERNAME, password_level1)

        account = pwd.getpwnam(USERNAME)

        # Buat README untuk peserta.
        readme_path = home_dir / "README.md"
        readme_path.write_text(README_CONTENT, encoding="utf-8")

        # Buat file hint berisi daftar command yang mungkin dibutuhkan.
        hint_path = home_dir / "hint.md"
        hint_path.write_text(HINT_CONTENT, encoding="utf-8")

        # File bernama '-' adalah inti challenge.
        # Peserta perlu membaca file ini dengan: cat ./-
        challenge_path = home_dir / "-"
        challenge_path.write_text(password_level2 + "\n", encoding="utf-8")

        # Atur kepemilikan seluruh konten kepada akun level1.
        os.chown(home_dir, account.pw_uid, account.pw_gid)
        os.chown(readme_path, account.pw_uid, account.pw_gid)
        os.chown(hint_path, account.pw_uid, account.pw_gid)
        os.chown(challenge_path, account.pw_uid, account.pw_gid)

        # Home hanya dapat diakses pemiliknya.
        # README dan hint dapat dibaca pemilik; file jawaban hanya dapat dibaca pemilik.
        os.chmod(readme_path, 0o400)
        os.chmod(hint_path, 0o400)
        os.chmod(challenge_path, 0o400)
        os.chmod(home_dir, 0o700)

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
    """Mode mandiri untuk menguji generator Level 1."""
    _require_root()

    print("=== EVCONN LINUX WARGAME: GENERATOR LEVEL 1 ===")
    print("Challenge: The Dash File\n")
    print("Masukkan password yang akan digunakan peserta untuk login ke level1.")
    password_level1 = getpass.getpass("Password Level 1: ")
    password_level1_confirm = getpass.getpass("Ulangi Password Level 1: ")
    if password_level1 != password_level1_confirm:
        raise SystemExit("Password Level 1 tidak cocok. Tidak ada akun yang dibuat.")

    print("\nMasukkan password yang harus ditemukan peserta untuk Level 2.")
    password_level2 = getpass.getpass("Password Level 2: ")
    password_level2_confirm = getpass.getpass("Ulangi Password Level 2: ")
    if password_level2 != password_level2_confirm:
        raise SystemExit("Password Level 2 tidak cocok. Tidak ada akun yang dibuat.")

    created_home = create_level1(password_level1, password_level2)

    print("\n[BERHASIL] Challenge Level 1 berhasil dibuat.")
    print(f"Akun Linux : {USERNAME}")
    print(f"Home       : {created_home}")
    print("\nUntuk menguji login, jalankan:")
    print("  su - level1")
    print("\nDi dalam akun level1, baca petunjuk dengan:")
    print("  cat README.md")
    print("  cat hint.md")
    print("\nPassword Level 1 yang kamu masukkan tadi perlu dicantumkan")
    print("oleh main.py pada file pw-evconn.md di Level 0.")
    print("Setelah challenge diselesaikan, peserta akan menemukan password Level 2 dengan:")
    print("  cat ./-")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Generator challenge Level 2 - EVCONN Linux Wargame.

Challenge: The Invisible Secret

Fungsi utama:
    create_level2(password_level2, password_level3, home_root="/home")

Fungsi ini dirancang agar nantinya dapat dipanggil oleh main.py.
Script ini membuat akun Linux level2, README.md, hint.md, dan file
tersembunyi bernama .secret yang berisi password untuk akun level3.

Jalankan secara mandiri di Ubuntu Server:
    sudo python3 level-2.py

Catatan: mode mandiri meminta operator memasukkan password secara interaktif.
Password Level 2 yang dimasukkan operator harus sama dengan password yang
ditemukan peserta pada Level 1.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import subprocess
from pathlib import Path

USERNAME = "level2"
DEFAULT_HOME_ROOT = Path("/home")

README_CONTENT = """# EVCONN LINUX WARGAME
## LEVEL 2 — THE INVISIBLE SECRET

### CERITA

Akun level2 menyambutmu dengan sunyi.

Kamu menjalankan perintah pertama dan hasilnya hampir kosong. Cuma
satu-dua file biasa, tanpa apa pun yang kelihatan berharga. Kalau kamu
berhenti di sini, kamu mungkin akan menyimpulkan bahwa admin sudah
membersihkan semuanya sebelum pergi.

Tapi admin yang ceroboh di Level 1 tidak mungkin tiba-tiba serapi itu.

Di sudut layar, tersisa satu catatan pendek yang ditulis dengan tergesa:

    "Jangan langsung percaya pada apa yang terlihat."

Mungkin itu peringatan. Mungkin juga itu pengakuan.

Ada sesuatu di direktori ini. Ia tidak bersembunyi dengan cara yang rumit,
hanya dengan cara yang sering dilewatkan orang yang terlalu cepat merasa
sudah melihat semuanya.

### TUJUAN

Temukan password yang digunakan untuk masuk ke akun `level3`.

### PETUNJUK

1. Direktori yang kelihatan kosong belum tentu benar-benar kosong.
2. Terkadang yang kamu butuhkan bukan perintah baru, melainkan cara
   lain memakai perintah yang sudah kamu kenal.
3. Butuh bantuan? Baca file `hint.md`.

Selamat mencoba!

**EVCONN STUDY GROUP — Linux Fundamentals Lab**
"""

HINT_CONTENT = """# HINT — LEVEL 2

Command yang mungkin kamu butuhkan:

- pwd
- ls
- ls -la
- cat

Petunjuk tambahan:
Gunakan opsi yang dapat menampilkan file tersembunyi,
termasuk file yang namanya diawali dengan tanda titik (.).
"""


def _require_root() -> None:
    """Pastikan generator dijalankan dengan hak akses root."""
    if os.geteuid() != 0:
        raise PermissionError(
            "Script harus dijalankan sebagai root. Gunakan: sudo python3 level-2.py"
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


def create_level2(
    password_level2: str,
    password_level3: str,
    home_root: str | Path = DEFAULT_HOME_ROOT,
) -> Path:
    """Buat akun dan challenge Level 2.

    Args:
        password_level2: Password untuk login ke akun Linux `level2`.
                         Password ini berasal dari Level 1.
        password_level3: Password yang harus ditemukan peserta di Level 2.
                         Password ini akan menjadi password akun `level3`.
        home_root: Direktori induk home akun. Default: `/home`.

    Returns:
        Path menuju home directory akun `level2`.

    Raises:
        PermissionError: Jika script tidak dijalankan sebagai root.
        ValueError: Jika password tidak valid.
        RuntimeError: Jika akun atau direktori tujuan sudah tersedia.
        subprocess.CalledProcessError: Jika perintah Linux gagal.
    """
    _require_root()
    _validate_password(password_level2, "Password Level 2")
    _validate_password(password_level3, "Password Level 3")

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
        _set_linux_password(USERNAME, password_level2)

        account = pwd.getpwnam(USERNAME)

        # Buat README untuk peserta.
        readme_path = home_dir / "README.md"
        readme_path.write_text(README_CONTENT, encoding="utf-8")

        # Buat hint berisi daftar command yang mungkin dibutuhkan.
        hint_path = home_dir / "hint.md"
        hint_path.write_text(HINT_CONTENT, encoding="utf-8")

        # File tersembunyi adalah inti challenge.
        # Peserta dapat menemukannya dengan ls -la, lalu membacanya dengan cat.
        challenge_path = home_dir / ".secret"
        challenge_path.write_text(password_level3 + "\n", encoding="utf-8")

        # Atur kepemilikan seluruh konten kepada akun level2.
        os.chown(home_dir, account.pw_uid, account.pw_gid)
        os.chown(readme_path, account.pw_uid, account.pw_gid)
        os.chown(hint_path, account.pw_uid, account.pw_gid)
        os.chown(challenge_path, account.pw_uid, account.pw_gid)

        # Home hanya dapat diakses pemiliknya.
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
    """Mode mandiri untuk menguji generator Level 2."""
    _require_root()

    print("=== EVCONN LINUX WARGAME: GENERATOR LEVEL 2 ===")
    print("Challenge: The Invisible Secret\n")

    print("Masukkan password yang akan digunakan peserta untuk login ke level2.")
    password_level2 = getpass.getpass("Password Level 2: ")
    password_level2_confirm = getpass.getpass("Ulangi Password Level 2: ")

    if password_level2 != password_level2_confirm:
        raise SystemExit("Password Level 2 tidak cocok. Tidak ada akun yang dibuat.")

    print("\nMasukkan password yang harus ditemukan peserta untuk Level 3.")
    password_level3 = getpass.getpass("Password Level 3: ")
    password_level3_confirm = getpass.getpass("Ulangi Password Level 3: ")

    if password_level3 != password_level3_confirm:
        raise SystemExit("Password Level 3 tidak cocok. Tidak ada akun yang dibuat.")

    created_home = create_level2(password_level2, password_level3)

    print("\n[BERHASIL] Challenge Level 2 berhasil dibuat.")
    print(f"Akun Linux : {USERNAME}")
    print(f"Home       : {created_home}")
    print("\nUntuk menguji login, jalankan:")
    print("  su - level2")
    print("\nDi dalam akun level2, baca petunjuk dengan:")
    print("  cat README.md")
    print("  cat hint.md")
    print("\nUntuk menemukan file tersembunyi, peserta perlu memeriksa:")
    print("  ls -la")
    print("\nSetelah ditemukan, password Level 3 dapat dibaca dengan:")
    print("  cat .secret")
    print("\nPassword Level 2 yang kamu masukkan tadi harus sama dengan")
    print("password yang ditemukan peserta pada Level 1.")


if __name__ == "__main__":
    main()

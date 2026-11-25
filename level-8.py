#!/usr/bin/env python3
"""Generator challenge Level 8 - EVCONN Cloud Wargame.

Challenge: Permission Denied

Fungsi utama:
    create_level8(password_level8, password_level9, home_root="/home")

Script membuat akun Linux level8, README.md, hint.md, dan file
cloud/credentials.txt. File target dimiliki akun level8 tetapi permission
awalnya 000, sehingga peserta perlu memberi izin baca kepada pemiliknya
dengan chmod u+r.

Jalankan secara mandiri di Ubuntu Server:
    sudo python3 level-8.py

Password Level 8 harus sama dengan password yang ditemukan peserta
pada Level 7.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import subprocess
from pathlib import Path

USERNAME = "level8"
DEFAULT_HOME_ROOT = Path("/home")

README_CONTENT = """# EVCONN CLOUD WARGAME
## LEVEL 8 — PERMISSION DENIED

### CERITA

Laporan di Level 7 sudah ketemu. Sekarang Tim Cloud Operations EVCONN
harus memeriksa konfigurasi salah satu cloud instance.

Catatan aksesnya disimpan admin di `credentials.txt`. Tapi begitu file
itu dibuka, terminal langsung membalas:

    Permission denied

Admin yang sama meninggalkan pesan:

    "File-nya benar kok, jangan cari file lain. Kemarin saya atur
    permission-nya biar aman, eh malah saya sendiri yang nggak bisa
    baca. Maklum, kebanyakan kopi."

File itu ada di depan matamu, dan kamu pemiliknya. Tinggal cari tahu
kenapa kamu sendiri nggak boleh membukanya.
### TUJUAN

Buka file `cloud/credentials.txt` dengan memperbaiki permission-nya.

Di dalam file tersebut terdapat password untuk masuk ke akun `level9`.

### PETUNJUK

1. Masuk ke direktori `cloud`.
2. Periksa permission file `credentials.txt`.
3. Tambahkan izin baca untuk pemilik file.
4. Baca file tersebut untuk mendapatkan password berikutnya.

Selamat mencoba!

**EVCONN STUDY GROUP — Cloud & Linux Fundamentals Lab**
"""

HINT_CONTENT = """# HINT — LEVEL 8
## PERMISSION DENIED

Command yang mungkin kamu butuhkan:

- `pwd`     : melihat lokasi direktori saat ini.
- `ls -l`   : melihat file beserta permission-nya.
- `cd`      : berpindah direktori.
- `chmod`   : mengubah permission file.
- `cat`     : membaca isi file.

Petunjuk:

Masuk ke direktori `cloud`, lalu periksa permission file.

Gunakan perintah berikut untuk menambahkan izin baca bagi pemilik file:

    chmod u+r credentials.txt

Setelah itu, baca file dengan `cat`.
"""


def _require_root() -> None:
    """Pastikan generator dijalankan dengan hak akses root."""
    if os.geteuid() != 0:
        raise PermissionError(
            "Script harus dijalankan sebagai root. Gunakan: sudo python3 level-8.py"
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


def create_level8(
    password_level8: str,
    password_level9: str,
    home_root: str | Path = DEFAULT_HOME_ROOT,
) -> Path:
    """Buat akun dan challenge Level 8.

    Args:
        password_level8: Password untuk login ke akun Linux `level8`.
                         Password ini berasal dari Level 7.
        password_level9: Password yang harus ditemukan peserta di Level 8.
                         Password ini akan menjadi password akun `level9`.
        home_root: Direktori induk home akun. Default: `/home`.

    Returns:
        Path menuju home directory akun `level8`.
    """
    _require_root()
    _validate_password(password_level8, "Password Level 8")
    _validate_password(password_level9, "Password Level 9")

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

        _set_linux_password(USERNAME, password_level8)
        account = pwd.getpwnam(USERNAME)

        cloud_dir = home_dir / "cloud"
        cloud_dir.mkdir(parents=True, exist_ok=True)

        (home_dir / "README.md").write_text(README_CONTENT, encoding="utf-8")
        (home_dir / "hint.md").write_text(HINT_CONTENT, encoding="utf-8")

        credentials_path = cloud_dir / "credentials.txt"
        credentials_path.write_text(
            f"EVCONN CLOUD ACCESS\naccount=level9\npassword={password_level9}\n",
            encoding="utf-8",
        )

        # Seluruh isi home dimiliki oleh akun level8.
        os.chown(home_dir, account.pw_uid, account.pw_gid)
        os.chown(cloud_dir, account.pw_uid, account.pw_gid)
        os.chown(home_dir / "README.md", account.pw_uid, account.pw_gid)
        os.chown(home_dir / "hint.md", account.pw_uid, account.pw_gid)
        os.chown(credentials_path, account.pw_uid, account.pw_gid)

        # Direktori dapat diakses pemilik akun.
        os.chmod(home_dir, 0o700)
        os.chmod(cloud_dir, 0o700)

        # README dan hint dapat dibaca pemilik.
        os.chmod(home_dir / "README.md", 0o400)
        os.chmod(home_dir / "hint.md", 0o400)

        # File target sengaja tidak memberi izin apa pun.
        # Pemilik tetap dapat mengubah permission dengan chmod.
        os.chmod(credentials_path, 0o000)

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
    """Mode mandiri untuk menguji generator Level 8."""
    _require_root()

    print("=== EVCONN CLOUD WARGAME: GENERATOR LEVEL 8 ===")
    print("Challenge: Permission Denied\n")

    print("Masukkan password untuk login ke akun level8.")
    password_level8 = getpass.getpass("Password Level 8: ")
    password_level8_confirm = getpass.getpass("Ulangi Password Level 8: ")

    if password_level8 != password_level8_confirm:
        raise SystemExit("Password Level 8 tidak cocok. Tidak ada akun yang dibuat.")

    print("\nMasukkan password yang harus ditemukan peserta untuk Level 9.")
    password_level9 = getpass.getpass("Password Level 9: ")
    password_level9_confirm = getpass.getpass("Ulangi Password Level 9: ")

    if password_level9 != password_level9_confirm:
        raise SystemExit("Password Level 9 tidak cocok. Tidak ada akun yang dibuat.")

    created_home = create_level8(password_level8, password_level9)

    print("\n[BERHASIL] Challenge Level 8 berhasil dibuat.")
    print(f"Akun Linux : {USERNAME}")
    print(f"Home       : {created_home}")
    print("\nUntuk menguji login, jalankan:")
    print("  su - level8")
    print("  cat README.md")
    print("  cat hint.md")
    print("  cd cloud")
    print("  ls -l")
    print("  chmod u+r credentials.txt")
    print("  cat credentials.txt")
    print("\nPassword Level 8 harus sama dengan password yang ditemukan")
    print("peserta pada Level 7.")


if __name__ == "__main__":
    main()

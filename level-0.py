#!/usr/bin/env python3
"""Generator Level 0 - EVCONN Linux Wargame.

Level 0 adalah titik awal peserta. Script ini membuat akun `player`,
README.md, dan pw-evconn.md yang berisi password untuk masuk ke level1.

Fungsi utama:
    create_level0(player_password, password_level1, home_root="/home")

Jalankan secara mandiri di Ubuntu Server:
    sudo python3 level-0.py

Script ini dirancang agar nantinya dapat dipanggil oleh main.py.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import subprocess
from pathlib import Path

USERNAME = "player"
DEFAULT_HOME_ROOT = Path("/home")

README_CONTENT = """# EVCONN LINUX WARGAME
## SELAMAT DATANG DI LEVEL 0!

Selamat datang di EVCONN Linux Wargame!

Dalam lab ini, kamu akan mempelajari dasar-dasar Linux
melalui serangkaian tantangan yang harus diselesaikan
secara bertahap menggunakan terminal.

Setiap level memiliki tantangan yang berbeda. Untuk
melanjutkan ke level berikutnya, kamu harus menemukan
password yang disediakan di dalam tantangan tersebut.

Password yang ditemukan digunakan untuk masuk ke akun
Linux pada level selanjutnya.

### TUJUAN PEMBELAJARAN

Setelah menyelesaikan seluruh tantangan, kamu diharapkan mampu:

1. Mengenal lingkungan Linux dan penggunaan terminal.
2. Menavigasi direktori dan mengelola file.
3. Menggunakan perintah-perintah dasar Linux.
4. Memahami file, direktori, permission, dan ownership.
5. Menggabungkan beberapa perintah untuk menyelesaikan masalah.

### ATURAN PERMAINAN

1. Mulai permainan dari Level 0 dan lanjutkan secara berurutan.
2. Setiap level memiliki password untuk masuk ke level berikutnya.
3. Baca README.md pada setiap level sebelum mengerjakan tantangan.
4. Gunakan perintah Linux yang tersedia untuk menyelesaikan misi.
5. Jangan melewati level. Cobalah menyelesaikan setiap tantangan sendiri.

### MEMULAI PERMAINAN

Saat ini kamu berada di Level 0.

Level 0 merupakan tahap pengenalan. Belum ada tantangan
yang perlu diselesaikan.

Untuk mendapatkan password masuk ke Level 1, baca file
yang telah disediakan menggunakan perintah berikut:

    cat pw-evconn.md

Simpan password tersebut. Password itu digunakan untuk
masuk ke akun Linux `level1`.

### MASUK KE LEVEL 1

Setelah mendapatkan password, jalankan perintah:

    su - level1

Masukkan password yang telah kamu temukan ketika diminta.

Jika berhasil, kamu akan masuk ke lingkungan Level 1.
Baca petunjuk tantangan dengan perintah:

    cat README.md

### SELAMAT BERMAIN!

Explore, Learn, and Hack Responsibly.

EVCONN STUDY GROUP
Linux Fundamentals Lab
"""

PASSWORD_FILE_HEADER = """# EVCONN - PASSWORD LEVEL 1

Selamat! Kamu telah menyelesaikan tahap pengenalan.

Gunakan password berikut untuk masuk ke akun Linux `level1`:

"""


def _require_root() -> None:
    """Pastikan generator dijalankan dengan hak akses root."""
    if os.geteuid() != 0:
        raise PermissionError(
            "Script harus dijalankan sebagai root. "
            "Gunakan: sudo python3 level-0.py"
        )


def _validate_password(password: str, label: str) -> None:
    """Validasi format password sebelum digunakan."""
    if not isinstance(password, str) or not password:
        raise ValueError(f"{label} tidak boleh kosong.")
    if any(char in password for char in ("\n", "\r", ":")):
        raise ValueError(
            f"{label} tidak boleh mengandung baris baru atau tanda titik dua (:)."
        )


def _set_linux_password(username: str, password: str) -> None:
    """Atur password akun melalui stdin, bukan argumen command line."""
    subprocess.run(
        ["chpasswd"],
        input=f"{username}:{password}\n",
        text=True,
        check=True,
    )


def create_level0(
    player_password: str,
    password_level1: str,
    home_root: str | Path = DEFAULT_HOME_ROOT,
) -> Path:
    """Buat akun peserta dan file pengenalan Level 0.

    Args:
        player_password: Password awal untuk login sebagai `player`.
        password_level1: Password yang akan ditemukan peserta di
                         `pw-evconn.md` dan digunakan untuk login ke `level1`.
        home_root: Direktori induk home akun. Default: `/home`.

    Returns:
        Path menuju home directory akun `player`.

    Raises:
        PermissionError: Jika script tidak dijalankan sebagai root.
        ValueError: Jika password tidak valid.
        RuntimeError: Jika akun atau direktori tujuan sudah tersedia.
        subprocess.CalledProcessError: Jika perintah Linux gagal.
    """
    _require_root()
    _validate_password(player_password, "Password player")
    _validate_password(password_level1, "Password Level 1")

    home_root = Path(home_root).expanduser().resolve()
    home_root.mkdir(parents=True, exist_ok=True)
    home_dir = home_root / USERNAME

    try:
        pwd.getpwnam(USERNAME)
    except KeyError:
        pass
    else:
        raise RuntimeError(
            f"Akun '{USERNAME}' sudah ada. "
            "Periksa VM terlebih dahulu; script tidak akan mengubah akun yang ada."
        )

    if home_dir.exists():
        raise RuntimeError(
            f"Direktori '{home_dir}' sudah ada. Tidak ada file yang ditimpa."
        )

    user_created = False

    try:
        # Buat akun awal peserta tanpa memberikan akses sudo.
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

        _set_linux_password(USERNAME, player_password)

        account = pwd.getpwnam(USERNAME)

        # README berisi pengenalan dan instruksi Level 0.
        readme_path = home_dir / "README.md"
        readme_path.write_text(README_CONTENT, encoding="utf-8")

        # Password Level 1 diberikan secara sengaja pada tahap awal.
        password_path = home_dir / "pw-evconn.md"
        password_path.write_text(
            PASSWORD_FILE_HEADER + password_level1 + "\n",
            encoding="utf-8",
        )

        # Atur kepemilikan dan permission.
        os.chown(home_dir, account.pw_uid, account.pw_gid)
        os.chown(readme_path, account.pw_uid, account.pw_gid)
        os.chown(password_path, account.pw_uid, account.pw_gid)

        # Hanya akun player yang dapat masuk ke home Level 0.
        os.chmod(home_dir, 0o700)
        os.chmod(readme_path, 0o400)
        os.chmod(password_path, 0o400)

        return home_dir

    except Exception:
        # Bersihkan akun yang dibuat script jika proses gagal.
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
    """Mode mandiri untuk menguji generator Level 0."""
    _require_root()

    print("=== EVCONN LINUX WARGAME: GENERATOR LEVEL 0 ===\n")

    print("Buat password untuk akun awal peserta (player).")
    player_password = getpass.getpass("Password player: ")
    player_password_confirm = getpass.getpass("Ulangi password player: ")

    if player_password != player_password_confirm:
        raise SystemExit("Password player tidak cocok. Tidak ada akun yang dibuat.")

    print("\nMasukkan password yang akan digunakan untuk login ke level1.")
    password_level1 = getpass.getpass("Password Level 1: ")
    password_level1_confirm = getpass.getpass("Ulangi Password Level 1: ")

    if password_level1 != password_level1_confirm:
        raise SystemExit("Password Level 1 tidak cocok. Tidak ada akun yang dibuat.")

    created_home = create_level0(player_password, password_level1)

    print("\n[BERHASIL] Level 0 berhasil dibuat.")
    print(f"Akun       : {USERNAME}")
    print(f"Home       : {created_home}")
    print("\nBagikan kredensial awal berikut kepada peserta:")
    print(f"Username   : {USERNAME}")
    print("Password   : sesuai password player yang dibuat operator")
    print("\nPeserta dapat memulai dengan:")
    print("  cat README.md")
    print("  cat pw-evconn.md")
    print("  su - level1")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generator challenge Level 4 - EVCONN Cloud Wargame.

Challenge: The Lost Snapshot

Fungsi utama:
    create_level4(password_level4, password_level5, home_root="/home")

Script ini membuat akun Linux level4, README.md, hint.md, dan struktur
direktori cloud sederhana. Peserta harus mencari file recovery-token.txt
menggunakan perintah find, lalu membaca password untuk akun level5.

Jalankan secara mandiri di Ubuntu Server:
    sudo python3 level-4.py

Catatan:
- Password Level 4 harus sama dengan password yang ditemukan peserta
  pada Level 3.
- Mode mandiri meminta operator memasukkan kedua password secara interaktif.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import subprocess
from pathlib import Path

USERNAME = "level4"
DEFAULT_HOME_ROOT = Path("/home")

README_CONTENT = """# EVCONN CLOUD WARGAME
## LEVEL 4 — THE LOST SNAPSHOT

### CERITA

Di Level 3, kuncinya tersembunyi di tengah kebisingan. Di Level 4,
kuncinya bukan bersembunyi. Ia cuma tersesat.

Semalam, deployment di EVCONN Cloud gagal. Rollback berhasil, snapshot
terakhir selesai dibuat dengan rapi, dan satu-satunya yang tersisa
tinggal memulihkan virtual machine-nya. Hanya ada satu penghalang:
recovery token. Tanpa token itu, snapshot cuma tumpukan data yang
menunggu di gudang tanpa pemilik.

Masalahnya, gudang itu sudah jauh lebih besar dari yang diingat siapa
pun. Ada tiga region, beberapa instance, konfigurasi jaringan, backup
harian dan mingguan, arsip yang tidak jelas milik siapa, dan beberapa
catatan yang sepertinya ditulis hanya untuk menghibur diri sendiri.

Admin yang bertugas meninggalkan pesan. Nadanya terdengar sudah sangat
lelah:

    "File-nya masih ada. Saya yakin tidak terhapus. Saya cuma lupa
    menaruhnya di mana. Tolong jangan tanya saya, saya juga lagi cari
    file ijazah yang katanya sudah di-backup."

Di cloud, mesin yang menunggu tetap menghitung biaya. Kamu bisa saja
membuka folder satu per satu dan berharap beruntung. Tapi coba hitung
dulu, ada berapa banyak folder di sana.
### TUJUAN

Temukan file bernama `recovery-token.txt`, kemudian baca isinya.

Password di dalam file tersebut digunakan untuk masuk ke akun `level5`.

### PETUNJUK

1. Kamu sedang berada di home directory akun `level4`.
2. File yang dicari berada di salah satu subdirektori.
3. Gunakan perintah Linux untuk mencari file berdasarkan namanya.
4. Jika sudah ditemukan, baca file tersebut.

Selamat mencoba!

**EVCONN STUDY GROUP — Cloud & Linux Fundamentals Lab**
"""

HINT_CONTENT = """# HINT — LEVEL 4
## THE LOST SNAPSHOT

### COMMAND YANG DIBUTUHKAN

- `pwd`  : melihat lokasi direktori saat ini.
- `ls`   : melihat isi direktori.
- `find` : mencari file atau direktori.
- `cat`  : membaca isi file.

### PETUNJUK

Gunakan `find` untuk mencari file berdasarkan nama.

Contoh:

    find . -name "recovery-token.txt"

Keterangan:
- `.` berarti mulai mencari dari direktori saat ini.
- `-name` digunakan untuk mencari berdasarkan nama file.

Setelah lokasi file ditemukan, gunakan `cat` untuk membaca isinya.

Tidak perlu menggunakan command lain untuk menyelesaikan tantangan ini.
"""


def _require_root() -> None:
    """Pastikan generator dijalankan dengan hak akses root."""
    if os.geteuid() != 0:
        raise PermissionError(
            "Script harus dijalankan sebagai root. Gunakan: sudo python3 level-4.py"
        )


def _validate_password(password: str, label: str) -> None:
    """Validasi format password untuk chpasswd dan file teks."""
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


def _write_text(path: Path, content: str) -> None:
    """Buat direktori induk dan tulis file teks."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_cloud_directories(home_dir: Path, password_level5: str) -> None:
    """Buat struktur cloud sederhana dengan beberapa file pengecoh."""
    files = {
        "cloud/README.txt":
            "EVCONN Cloud Storage\nDirektori penyimpanan data operasional.\n",
        "cloud/regions/ap-southeast-1/region-info.txt":
            "Region: ap-southeast-1\nStatus: available\n",
        "cloud/regions/ap-southeast-1/backups/backup-report.txt":
            "Backup harian berhasil diselesaikan.\n",
        "cloud/regions/ap-southeast-1/backups/snapshot-001/snapshot-info.txt":
            "Snapshot ID: evconn-snapshot-001\nStatus: completed\n",
        "cloud/regions/ap-southeast-1/backups/snapshot-001/notes.txt":
            "Catatan admin: jangan lupa mematikan VM pengujian.\n",
        "cloud/regions/ap-southeast-1/backups/snapshot-002/snapshot-info.txt":
            "Snapshot ID: evconn-snapshot-002\nStatus: completed\n",
        "cloud/regions/ap-southeast-1/backups/snapshot-002/recovery-token.txt":
            f"{password_level5}\n",
        "cloud/regions/ap-southeast-1/instances/web-01/instance.conf":
            "instance_id=evconn-web-01\nstate=running\n",
        "cloud/regions/ap-southeast-1/instances/db-01/instance.conf":
            "instance_id=evconn-db-01\nstate=running\n",
        "cloud/shared/monitoring/status.log":
            "[INFO] Seluruh layanan cloud berjalan normal.\n",
    }

    for relative_path, text in files.items():
        _write_text(home_dir / relative_path, text)


def create_level4(
    password_level4: str,
    password_level5: str,
    home_root: str | Path = DEFAULT_HOME_ROOT,
) -> Path:
    """Buat akun dan challenge Level 4.

    Args:
        password_level4: Password untuk login ke akun Linux `level4`.
                         Password ini berasal dari Level 3.
        password_level5: Password yang harus ditemukan peserta di Level 4.
                         Password ini akan menjadi password akun `level5`.
        home_root: Direktori induk home akun. Default: `/home`.

    Returns:
        Path menuju home directory akun `level4`.

    Raises:
        PermissionError: Jika generator tidak dijalankan sebagai root.
        ValueError: Jika password tidak valid.
        RuntimeError: Jika akun atau direktori tujuan sudah tersedia.
        subprocess.CalledProcessError: Jika perintah Linux gagal.
    """
    _require_root()
    _validate_password(password_level4, "Password Level 4")
    _validate_password(password_level5, "Password Level 5")

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

        _set_linux_password(USERNAME, password_level4)
        account = pwd.getpwnam(USERNAME)

        (home_dir / "README.md").write_text(README_CONTENT, encoding="utf-8")
        (home_dir / "hint.md").write_text(HINT_CONTENT, encoding="utf-8")
        _build_cloud_directories(home_dir, password_level5)

        # Seluruh isi home dimiliki oleh akun level4.
        os.chown(home_dir, account.pw_uid, account.pw_gid)
        for item in home_dir.rglob("*"):
            os.chown(item, account.pw_uid, account.pw_gid)

        # Hanya pemilik akun yang dapat mengakses direktori dan membaca file.
        for directory in [home_dir, *[p for p in home_dir.rglob("*") if p.is_dir()]]:
            os.chmod(directory, 0o700)

        for file_path in [p for p in home_dir.rglob("*") if p.is_file()]:
            os.chmod(file_path, 0o400)

        return home_dir

    except Exception:
        # Bersihkan akun dan home directory jika proses gagal.
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
    """Mode mandiri untuk menguji generator Level 4."""
    _require_root()

    print("=== EVCONN CLOUD WARGAME: GENERATOR LEVEL 4 ===")
    print("Challenge: The Lost Snapshot\n")

    print("Masukkan password untuk login ke akun level4.")
    password_level4 = getpass.getpass("Password Level 4: ")
    password_level4_confirm = getpass.getpass("Ulangi Password Level 4: ")

    if password_level4 != password_level4_confirm:
        raise SystemExit("Password Level 4 tidak cocok. Tidak ada akun yang dibuat.")

    print("\nMasukkan password yang harus ditemukan peserta untuk Level 5.")
    password_level5 = getpass.getpass("Password Level 5: ")
    password_level5_confirm = getpass.getpass("Ulangi Password Level 5: ")

    if password_level5 != password_level5_confirm:
        raise SystemExit("Password Level 5 tidak cocok. Tidak ada akun yang dibuat.")

    created_home = create_level4(password_level4, password_level5)

    print("\n[BERHASIL] Challenge Level 4 berhasil dibuat.")
    print(f"Akun Linux : {USERNAME}")
    print(f"Home       : {created_home}")
    print("\nUntuk menguji login, jalankan:")
    print("  su - level4")
    print("\nBaca petunjuk:")
    print("  cat README.md")
    print("  cat hint.md")
    print("\nCari dan baca file recovery token:")
    print('  find . -name "recovery-token.txt"')
    print("  cat ./cloud/regions/ap-southeast-1/backups/snapshot-002/recovery-token.txt")
    print("\nPassword Level 4 harus sama dengan password yang ditemukan")
    print("peserta pada Level 3.")


if __name__ == "__main__":
    main()

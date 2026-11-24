#!/usr/bin/env python3
"""Generator challenge Level 5 - EVCONN Cloud Wargame.

Challenge: The Oversized Cloud Log

Fungsi utama:
    create_level5(password_level5, password_level6, home_root="/home")

Script ini membuat akun Linux level5, README.md, hint.md, dan beberapa
file log bernomor di direktori cloud. Salah satu file log berukuran
lebih dari 1 KiB dan berisi password untuk akun level6.

Jalankan secara mandiri di Ubuntu Server:
    sudo python3 level-5.py

Password Level 5 harus sama dengan password yang ditemukan peserta
pada Level 4.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import subprocess
from pathlib import Path

USERNAME = "level5"
DEFAULT_HOME_ROOT = Path("/home")

README_CONTENT = """# EVCONN CLOUD WARGAME
## LEVEL 5 — THE OVERSIZED CLOUD LOG

### CERITA

Recovery token ketemu, dan virtual machine yang tumbang semalam akhirnya
menyala lagi. Tim Cloud Operations EVCONN menarik napas lega. Tapi di
dunia infrastruktur, lega biasanya cuma jeda sebelum pekerjaan berikutnya.

Sekarang giliran audit. Sebelum insiden ditutup, setiap instance harus
diperiksa catatannya, dan setiap instance meninggalkan jejak dengan cara
yang sama: file log dengan nama paling sederhana yang bisa dibayangkan.
`1.log`, `2.log`, `3.log`, dan seterusnya, tersebar di beberapa
direktori. Tidak ada yang punya judul. Tidak ada yang punya penjelasan.

Satu di antara mereka mencatat sesuatu yang lain dari biasanya. Hasil
audit yang terlalu panjang untuk dianggap rutin, termasuk di dalamnya
kredensial yang seharusnya tidak pernah ikut tertulis.

Admin yang bertugas, orang yang sama yang kemarin masih mencari ijazahnya
di folder backup, hanya sempat meninggalkan pesan singkat:

    "Log yang kamu cari itu file biasa berekstensi .log, dan ukurannya
    lebih dari 1 KiB. Log yang lain kecil-kecil semua. Sisanya saya
    lupa. Jangan suruh saya buka satu-satu, nanti saya malah
    ketiduran."

Membuka dua puluhan file satu per satu memang bisa. Tapi kamu sudah
tahu ciri-cirinya, jadi mungkin ada cara yang lebih cerdas untuk
menemukannya.

### TUJUAN

Temukan file dengan karakteristik berikut:

1. File biasa dengan ekstensi `.log`.
2. Ukurannya lebih dari 1 KiB.

Baca file tersebut untuk mendapatkan password akun `level6`.

### PETUNJUK

1. Periksa direktori cloud yang tersedia.
2. Ada banyak file log dengan nama berupa angka.
3. Gunakan `find` untuk mencari file berdasarkan nama dan ukuran.
4. Jika sudah menemukan file yang sesuai, baca menggunakan `cat`.

Selamat mencoba!

**EVCONN STUDY GROUP — Cloud & Linux Fundamentals Lab**
"""

HINT_CONTENT = """# HINT — LEVEL 5
## THE OVERSIZED CLOUD LOG

Command yang mungkin kamu butuhkan:

- `pwd`       : melihat lokasi direktori saat ini.
- `ls`        : melihat isi direktori.
- `find`      : mencari file berdasarkan kriteria.
- `cat`       : membaca isi file.

Petunjuk:

Gunakan `find` untuk mencari file `.log` yang ukurannya lebih dari 1 KiB.

Contoh pola:

    find . -type f -name "*.log" -size +1k

Setelah menemukan file yang sesuai, gunakan `cat` untuk membaca isinya.
"""


def _require_root() -> None:
    """Pastikan generator dijalankan dengan hak akses root."""
    if os.geteuid() != 0:
        raise PermissionError(
            "Script harus dijalankan sebagai root. Gunakan: sudo python3 level-5.py"
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


def _write_text(path: Path, content: str) -> None:
    """Buat direktori induk dan tulis file teks."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_cloud_logs(home_dir: Path, password_level6: str) -> None:
    """Buat 24 log bernomor; hanya satu berukuran lebih dari 1 KiB."""
    log_directories = [
        "cloud/regions/ap-southeast-1/instances/web-01/logs",
        "cloud/regions/ap-southeast-1/instances/db-01/logs",
        "cloud/regions/ap-southeast-1/backups/logs",
        "cloud/shared/monitoring/logs",
    ]

    for directory in log_directories:
        (home_dir / directory).mkdir(parents=True, exist_ok=True)

    # Buat 24 file log kecil dengan nama bernomor.
    for number in range(1, 25):
        if number == 17:
            continue

        directory = log_directories[(number - 1) % len(log_directories)]
        log_path = home_dir / directory / f"{number}.log"

        log_content = (
            f"2026-11-24T09:{number:02d}:00Z [INFO] "
            f"event_id={number:03d} service=cloud-monitoring status=ok\n"
            f"2026-11-24T09:{number:02d}:10Z [INFO] "
            "instance_health_check=passed\n"
            f"2026-11-24T09:{number:02d}:20Z [INFO] "
            "backup_state=available\n"
        )
        _write_text(log_path, log_content)

    # Buat satu file target bernama angka biasa.
    # Isinya dibuat panjang agar ukurannya lebih dari 1 KiB.
    target_directory = (
        home_dir / "cloud/regions/ap-southeast-1/backups/logs"
    )
    target_path = target_directory / "17.log"

    target_lines = [
        "2026-11-24T10:00:00Z [SNAPSHOT] Cloud backup audit started.",
        "2026-11-24T10:00:05Z [COMPUTE] Instance evconn-prod-web-01 checked.",
        "2026-11-24T10:00:10Z [STORAGE] Snapshot metadata verified.",
        "2026-11-24T10:00:15Z [NETWORK] Recovery network is ready.",
        "2026-11-24T10:00:20Z [MONITORING] Instance health check passed.",
        "2026-11-24T10:00:25Z [BACKUP] Snapshot checksum verified.",
    ]

    # Catatan audit tambahan membuat file target lebih besar dari 1 KiB.
    for step in range(1, 31):
        target_lines.append(
            f"2026-11-24T10:{step:02d}:30Z [AUDIT] "
            f"Backup validation step {step:02d} completed successfully."
        )

    target_lines.extend(
        [
            "2026-11-24T10:59:40Z [IAM] Recovery credential generated.",
            f"2026-11-24T10:59:50Z [IAM] account=level6 password={password_level6}",
            "2026-11-24T10:59:59Z [SNAPSHOT] Cloud backup audit completed.",
        ]
    )

    _write_text(target_path, "\n".join(target_lines) + "\n")

    # File non-log sebagai pengecoh ringan.
    _write_text(
        home_dir / "cloud/README.txt",
        "EVCONN Cloud: direktori log dan catatan operasional.\n",
    )
    _write_text(
        home_dir / "cloud/regions/ap-southeast-1/instances/web-01/instance.conf",
        "instance_id=evconn-web-01\nstate=running\n",
    )


def create_level5(
    password_level5: str,
    password_level6: str,
    home_root: str | Path = DEFAULT_HOME_ROOT,
) -> Path:
    """Buat akun dan challenge Level 5.

    Args:
        password_level5: Password untuk login ke akun Linux `level5`.
                         Password ini berasal dari Level 4.
        password_level6: Password yang harus ditemukan peserta di Level 5.
                         Password ini akan menjadi password akun `level6`.
        home_root: Direktori induk home akun. Default: `/home`.

    Returns:
        Path menuju home directory akun `level5`.
    """
    _require_root()
    _validate_password(password_level5, "Password Level 5")
    _validate_password(password_level6, "Password Level 6")

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

        _set_linux_password(USERNAME, password_level5)
        account = pwd.getpwnam(USERNAME)

        (home_dir / "README.md").write_text(README_CONTENT, encoding="utf-8")
        (home_dir / "hint.md").write_text(HINT_CONTENT, encoding="utf-8")
        _build_cloud_logs(home_dir, password_level6)

        # Atur kepemilikan seluruh isi home kepada akun level5.
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
    """Mode mandiri untuk menguji generator Level 5."""
    _require_root()

    print("=== EVCONN CLOUD WARGAME: GENERATOR LEVEL 5 ===")
    print("Challenge: The Oversized Cloud Log\n")

    print("Masukkan password untuk login ke akun level5.")
    password_level5 = getpass.getpass("Password Level 5: ")
    password_level5_confirm = getpass.getpass("Ulangi Password Level 5: ")

    if password_level5 != password_level5_confirm:
        raise SystemExit("Password Level 5 tidak cocok. Tidak ada akun yang dibuat.")

    print("\nMasukkan password yang harus ditemukan peserta untuk Level 6.")
    password_level6 = getpass.getpass("Password Level 6: ")
    password_level6_confirm = getpass.getpass("Ulangi Password Level 6: ")

    if password_level6 != password_level6_confirm:
        raise SystemExit("Password Level 6 tidak cocok. Tidak ada akun yang dibuat.")

    created_home = create_level5(password_level5, password_level6)

    print("\n[BERHASIL] Challenge Level 5 berhasil dibuat.")
    print(f"Akun Linux : {USERNAME}")
    print(f"Home       : {created_home}")
    print("\nUntuk menguji login, jalankan:")
    print("  su - level5")
    print("\nBaca petunjuk:")
    print("  cat README.md")
    print("  cat hint.md")
    print("\nCari file log berdasarkan ekstensi dan ukuran:")
    print('  find . -type f -name "*.log" -size +1k')
    print("\nPassword Level 5 harus sama dengan password yang ditemukan")
    print("peserta pada Level 4.")


if __name__ == "__main__":
    main()

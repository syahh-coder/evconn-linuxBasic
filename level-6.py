#!/usr/bin/env python3
"""Generator challenge Level 6 - EVCONN Cloud Wargame.

Challenge: The Last Deployment

Fungsi utama:
    create_level6(password_level6, password_level7, home_root="/home")

Script membuat akun level6, README.md, hint.md, dan deployment.log.
Password akun level7 berada pada beberapa baris terakhir log.

Jalankan:
    sudo python3 level-6.py

Password Level 6 harus sama dengan password yang ditemukan peserta pada Level 5.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import subprocess
from pathlib import Path

USERNAME = "level6"
DEFAULT_HOME_ROOT = Path("/home")

README_CONTENT = """# EVCONN CLOUD WARGAME
## LEVEL 6 — THE LAST DEPLOYMENT

### CERITA

Audit log kemarin sudah beres. Malam ini ada deployment baru di salah
satu virtual machine EVCONN, dan semua yang terjadi tercatat di
`deployment.log`: pemeriksaan awal, persiapan instance, aplikasi yang
naik, sampai pengecekan layanan. Isinya ratusan baris.

Admin yang sama meninggalkan pesan, kali ini ditulis sambil buru-buru:

    "Deployment-nya beres. Password buat akses berikutnya sudah saya
    catat di baris-baris paling akhir log. Cek sendiri ya, saya
    dipanggil dulu, tagihan cloud bulan ini membengkak dan semua orang
    menatap saya."

Password itu ada di ujung file. Membaca ratusan baris dari atas memang
bisa, tapi lama.
### TUJUAN

Temukan password yang digunakan untuk masuk ke akun `level7`.

Password tersebut tercatat pada bagian akhir file `deployment.log`.

### PETUNJUK

1. Periksa file yang tersedia.
2. Lihat beberapa baris awal untuk mengenali isi log.
3. Periksa beberapa baris terakhir karena catatan terbaru berada di bagian akhir.
4. Jika masih kesulitan, baca file `hint.md`.

Selamat mencoba!

**EVCONN STUDY GROUP — Cloud & Linux Fundamentals Lab**
"""

HINT_CONTENT = """# HINT — LEVEL 6
## THE LAST DEPLOYMENT

Command yang mungkin kamu butuhkan:

- `pwd`  : melihat lokasi direktori saat ini.
- `ls`   : melihat isi direktori.
- `head` : melihat bagian awal file.
- `tail` : melihat bagian akhir file.
- `cat`  : membaca seluruh isi file.

Petunjuk:

Gunakan `head` untuk melihat beberapa baris awal dan `tail`
untuk melihat beberapa baris terakhir.

Contoh:

    head -n 5 deployment.log
    tail -n 5 deployment.log

Perhatikan catatan deployment paling akhir untuk menemukan
password akun berikutnya.
"""


def _require_root() -> None:
    if os.geteuid() != 0:
        raise PermissionError(
            "Script harus dijalankan sebagai root. Gunakan: sudo python3 level-6.py"
        )


def _validate_password(password: str, label: str) -> None:
    if not isinstance(password, str) or not password:
        raise ValueError(f"{label} tidak boleh kosong.")
    if any(char in password for char in ("\n", "\r", ":")):
        raise ValueError(
            f"{label} tidak boleh mengandung baris baru atau tanda titik dua (:)."
        )


def _set_linux_password(username: str, password: str) -> None:
    subprocess.run(
        ["chpasswd"],
        input=f"{username}:{password}\n",
        text=True,
        check=True,
    )


def _build_deployment_log(password_level7: str) -> str:
    """Buat log deployment panjang dengan password pada bagian akhirnya."""
    events = [
        "[INFO] Cloud instance vm-app-01 berhasil diperiksa.",
        "[INFO] Pemeriksaan kapasitas CPU selesai.",
        "[INFO] Penggunaan memori berada dalam batas normal.",
        "[INFO] Koneksi ke virtual network berhasil.",
        "[INFO] Storage volume berhasil dipasang.",
        "[INFO] Image aplikasi berhasil diunduh.",
        "[INFO] Dependency aplikasi berhasil diperiksa.",
        "[INFO] Konfigurasi environment berhasil dimuat.",
        "[INFO] Deployment package berhasil diekstrak.",
        "[INFO] Pemeriksaan service dependency selesai.",
        "[INFO] Health check endpoint memberikan respons normal.",
        "[INFO] Load balancer berhasil mendeteksi instance.",
        "[INFO] Backup konfigurasi sebelum deployment selesai.",
        "[INFO] Deployment berjalan sesuai jadwal.",
        "[INFO] Monitoring agent berhasil dijalankan.",
        "[INFO] Pemeriksaan log aplikasi selesai.",
        "[INFO] Instance siap menerima trafik.",
        "[CHAT] Admin: Siapa yang menyalakan VM testing semalaman?",
        "[CHAT] Operator: Sepertinya lupa dimatikan, Pak.",
        "[CHAT] Admin: Tagihan cloud tidak bisa ikut tidur, ya.",
        "[CHAT] Operator: Password Wi-Fi ruang server masih sama?",
        "[CHAT] Admin: Coba tanya access point, saya sedang cari kopi.",
        "[WARNING] Admin membuka terlalu banyak dashboard sekaligus.",
        "[INFO] Snapshot sebelum deployment berhasil dibuat.",
        "[INFO] Proses deployment tidak menemukan error.",
    ]

    lines: list[str] = []
    for index in range(1, 101):
        minute = (index - 1) % 60
        second = ((index - 1) * 7) % 60
        timestamp = f"2026-11-24 14:{minute:02d}:{second:02d}"
        event = events[(index * 5 + index // 4) % len(events)]
        lines.append(f"{timestamp} [DEPLOY-{index:03d}] {event}")

    lines.extend(
        [
            "2026-11-24 15:58:10 [DEPLOYMENT] Final health check started.",
            "2026-11-24 15:58:20 [MONITORING] Application status: healthy.",
            "2026-11-24 15:58:30 [LOAD-BALANCER] Instance registered successfully.",
            "2026-11-24 15:58:40 [DEPLOYMENT] Status: completed.",
            f"2026-11-24 15:58:50 [IAM] account=level7 password={password_level7}",
        ]
    )
    return "\n".join(lines) + "\n"


def create_level6(
    password_level6: str,
    password_level7: str,
    home_root: str | Path = DEFAULT_HOME_ROOT,
) -> Path:
    """Buat akun dan challenge Level 6."""
    _require_root()
    _validate_password(password_level6, "Password Level 6")
    _validate_password(password_level7, "Password Level 7")

    home_root = Path(home_root).expanduser().resolve()
    home_root.mkdir(parents=True, exist_ok=True)
    home_dir = home_root / USERNAME

    try:
        pwd.getpwnam(USERNAME)
    except KeyError:
        pass
    else:
        raise RuntimeError(f"Akun '{USERNAME}' sudah ada. Periksa VM terlebih dahulu.")

    if home_dir.exists():
        raise RuntimeError(f"Direktori '{home_dir}' sudah ada. Tidak ada file yang ditimpa.")

    user_created = False
    try:
        subprocess.run(
            [
                "useradd", "--create-home", "--home-dir", str(home_dir),
                "--shell", "/bin/bash", USERNAME,
            ],
            check=True,
        )
        user_created = True

        _set_linux_password(USERNAME, password_level6)
        account = pwd.getpwnam(USERNAME)

        (home_dir / "README.md").write_text(README_CONTENT, encoding="utf-8")
        (home_dir / "hint.md").write_text(HINT_CONTENT, encoding="utf-8")
        (home_dir / "deployment.log").write_text(
            _build_deployment_log(password_level7), encoding="utf-8"
        )

        os.chown(home_dir, account.pw_uid, account.pw_gid)
        for item in home_dir.iterdir():
            os.chown(item, account.pw_uid, account.pw_gid)

        os.chmod(home_dir, 0o700)
        for file_path in home_dir.iterdir():
            if file_path.is_file():
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
    _require_root()
    print("=== EVCONN CLOUD WARGAME: GENERATOR LEVEL 6 ===")
    print("Challenge: The Last Deployment\n")

    password_level6 = getpass.getpass("Password Level 6: ")
    password_level6_confirm = getpass.getpass("Ulangi Password Level 6: ")
    if password_level6 != password_level6_confirm:
        raise SystemExit("Password Level 6 tidak cocok. Tidak ada akun yang dibuat.")

    print("\nMasukkan password yang harus ditemukan peserta untuk Level 7.")
    password_level7 = getpass.getpass("Password Level 7: ")
    password_level7_confirm = getpass.getpass("Ulangi Password Level 7: ")
    if password_level7 != password_level7_confirm:
        raise SystemExit("Password Level 7 tidak cocok. Tidak ada akun yang dibuat.")

    created_home = create_level6(password_level6, password_level7)

    print("\n[BERHASIL] Challenge Level 6 berhasil dibuat.")
    print(f"Akun Linux : {USERNAME}")
    print(f"Home       : {created_home}")
    print("\nUntuk menguji login, jalankan:")
    print("  su - level6")
    print("  cat README.md")
    print("  cat hint.md")
    print("  tail -n 5 deployment.log")
    print("\nPassword Level 6 harus sama dengan password yang ditemukan peserta pada Level 5.")


if __name__ == "__main__":
    main()

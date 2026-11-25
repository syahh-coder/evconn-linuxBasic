#!/usr/bin/env python3
"""Generator challenge Level 9 - EVCONN Cloud Wargame.

Challenge: The Stuck Worker

Fungsi utama:
    create_level9(password_level9, password_level10, home_root="/home")

Script membuat akun Linux level9, README.md, hint.md, dan worker backup
yang dikelola oleh systemd. Peserta mencari proses backup-worker.py
menggunakan `ps aux`, lalu menghentikannya menggunakan `kill PID`.

Ketika menerima SIGTERM, worker membuat cloud/recovery-report.txt yang
berisi password akun level10. Service diaktifkan saat boot. Jika VM
reboot, service berjalan kembali dan laporan penyelesaian sebelumnya
dibersihkan agar challenge dapat dikerjakan ulang.

Jalankan secara mandiri di Ubuntu Server:
    sudo python3 level-9.py

Password Level 9 harus sama dengan password yang ditemukan peserta
pada Level 8.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import subprocess
import sys
import time
from pathlib import Path

USERNAME = "level9"
DEFAULT_HOME_ROOT = Path("/home")
HELPER_BASE = Path("/var/lib/evconn-wargame")
HELPER_DIR_NAME = "level9"
WORKER_FILENAME = "backup-worker.py"
SERVICE_NAME = "evconn-level9.service"
SERVICE_PATH = Path("/etc/systemd/system") / SERVICE_NAME

README_CONTENT = """# EVCONN CLOUD WARGAME
## LEVEL 9 — THE STUCK WORKER

### CERITA

Tim Cloud Operations EVCONN sedang menjalankan proses backup pada
salah satu virtual machine.

Biasanya proses backup selesai dalam beberapa menit. Namun, kali ini
prosesnya terus berjalan dan tidak menunjukkan tanda-tanda selesai.

Administrator meninggalkan pesan:

\"Backup worker-nya kayaknya nge-hang. Tolong cari prosesnya dan
hentikan. Jangan sampai salah menghentikan proses lain, nanti server
malah ikut bermasalah. Kalau worker berhasil dihentikan, sistem akan
membuat laporan pemulihan secara otomatis.\"

Kamu perlu memeriksa proses yang sedang berjalan, menemukan worker
milik EVCONN, lalu menghentikannya.

### TUJUAN

1. Temukan proses `backup-worker.py` yang sedang berjalan.
2. Catat PID proses tersebut.
3. Hentikan proses menggunakan command `kill`.
4. Baca file `cloud/recovery-report.txt` setelah worker berhenti.

Password di dalam laporan digunakan untuk masuk ke akun `level10`.

**PERHATIAN:** Hentikan hanya proses `backup-worker.py` milik lab ini.
Jangan menghentikan proses sistem Ubuntu atau proses lain.

### PETUNJUK

1. Gunakan command untuk melihat daftar proses.
2. Cari baris yang memuat `backup-worker.py`.
3. PID berada pada kolom kedua dari output `ps aux`.
4. Gunakan PID tersebut untuk menghentikan worker.
5. Baca laporan yang dibuat setelah worker berhenti.

Selamat mencoba!

**EVCONN STUDY GROUP — Cloud & Linux Fundamentals Lab**
"""

HINT_CONTENT = """# HINT — LEVEL 9
## THE STUCK WORKER

Command yang mungkin kamu butuhkan:

- `pwd`     : melihat lokasi direktori saat ini.
- `ls`      : melihat isi direktori.
- `ps aux`  : melihat proses yang sedang berjalan.
- `kill`    : menghentikan proses berdasarkan PID.
- `cat`     : membaca isi file.

Petunjuk:

1. Jalankan `ps aux` untuk melihat daftar proses.
2. Cari proses dengan nama `backup-worker.py`.
3. Ambil PID dari kolom kedua.
4. Hentikan proses dengan perintah:

       kill PID

   Ganti `PID` dengan nomor proses yang kamu temukan.

5. Baca laporan hasilnya:

       cat cloud/recovery-report.txt

Gunakan `kill` hanya pada proses worker milik challenge ini.
"""


def _require_root() -> None:
    """Pastikan generator dijalankan sebagai root."""
    if os.geteuid() != 0:
        raise PermissionError(
            "Script harus dijalankan sebagai root. Gunakan: sudo python3 level-9.py"
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


def _build_worker_script(
    password_level10: str,
    target_uid: int,
    target_gid: int,
    home_dir: Path,
) -> str:
    """Buat worker root-only yang menurunkan privilege ke akun level9."""
    report_path = home_dir / "cloud" / "recovery-report.txt"
    ready_path = home_dir / "cloud" / ".worker-ready"

    return f'''#!/usr/bin/env python3
"""EVCONN backup worker. Script hanya dapat dibaca oleh root."""

import os
import signal
import sys
import time
from pathlib import Path

TARGET_UID = {target_uid}
TARGET_GID = {target_gid}
PASSWORD_LEVEL10 = {password_level10!r}
REPORT_PATH = Path({str(report_path)!r})
READY_PATH = Path({str(ready_path)!r})


def finish_worker(signum, frame):
    """Buat laporan pemulihan saat worker menerima SIGTERM."""
    report_text = (
        "EVCONN CLOUD RECOVERY REPORT\\n"
        "backup_worker_status=stopped\\n"
        "account=level10\\n"
        "password=" + PASSWORD_LEVEL10 + "\\n"
    )
    temporary_path = REPORT_PATH.with_name(".recovery-report.tmp")
    temporary_path.write_text(report_text, encoding="utf-8")
    os.chmod(temporary_path, 0o400)
    os.replace(temporary_path, REPORT_PATH)
    os.chmod(REPORT_PATH, 0o400)
    sys.exit(0)


# systemd menjalankan worker sebagai root agar dapat membaca script rahasia.
# Proses kemudian berjalan dengan UID/GID level9 sehingga peserta dapat kill.
os.setgroups([])
os.setgid(TARGET_GID)
os.setuid(TARGET_UID)

signal.signal(signal.SIGTERM, finish_worker)

# Marker ini digunakan generator untuk memastikan worker sudah siap.
READY_PATH.write_text("ready\\n", encoding="utf-8")
os.chmod(READY_PATH, 0o400)

# Simulasi proses backup yang terus berjalan sampai dihentikan peserta.
while True:
    time.sleep(5)
'''


def _build_systemd_unit(worker_script: Path, home_dir: Path) -> str:
    """Buat service yang aktif saat boot dan membersihkan laporan lama."""
    report_path = home_dir / "cloud" / "recovery-report.txt"
    ready_path = home_dir / "cloud" / ".worker-ready"

    return f"""[Unit]
Description=EVCONN Level 9 Stuck Backup Worker
After=network.target

[Service]
Type=simple
User=root
UMask=0077
ExecStartPre=/usr/bin/rm -f {report_path} {ready_path}
ExecStart={sys.executable} {worker_script}
Restart=on-abnormal
RestartSec=2
KillSignal=SIGTERM
TimeoutStopSec=5
StandardOutput=null
StandardError=journal

[Install]
WantedBy=multi-user.target
"""


def _wait_until_worker_ready(home_dir: Path, timeout: float = 10.0) -> None:
    """Tunggu sampai worker aktif dan menulis marker kesiapan."""
    ready_path = home_dir / "cloud" / ".worker-ready"
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if ready_path.is_file():
            ready_path.unlink(missing_ok=True)
            return

        active = subprocess.run(
            ["systemctl", "is-active", "--quiet", SERVICE_NAME],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if active.returncode != 0:
            status = subprocess.run(
                ["systemctl", "status", SERVICE_NAME, "--no-pager", "--full"],
                check=False,
                capture_output=True,
                text=True,
            )
            detail = (status.stdout or status.stderr).strip()
            raise RuntimeError(
                "Service Level 9 tidak aktif. Periksa konfigurasi systemd.\n"
                + detail[-2500:]
            )

        time.sleep(0.1)

    raise RuntimeError(
        "Worker Level 9 tidak memberikan tanda siap dalam 10 detik. "
        f"Periksa dengan: systemctl status {SERVICE_NAME}"
    )


def _stop_and_remove_service() -> None:
    """Hentikan dan nonaktifkan service saat rollback."""
    subprocess.run(
        ["systemctl", "disable", "--now", SERVICE_NAME],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def create_level9(
    password_level9: str,
    password_level10: str,
    home_root: str | Path = DEFAULT_HOME_ROOT,
) -> Path:
    """Buat akun dan challenge Level 9 dengan worker systemd persisten.

    Args:
        password_level9: Password untuk login ke akun Linux `level9`.
                         Password ini berasal dari Level 8.
        password_level10: Password yang harus ditemukan peserta di Level 9.
                          Password ini menjadi password akun `level10`.
        home_root: Direktori induk home akun. Default: `/home`.

    Returns:
        Path menuju home directory akun `level9`.
    """
    _require_root()
    _validate_password(password_level9, "Password Level 9")
    _validate_password(password_level10, "Password Level 10")

    if shutil.which("systemctl") is None:
        raise RuntimeError("systemctl tidak ditemukan. Gunakan Ubuntu Server dengan systemd.")

    home_root = Path(home_root).expanduser().resolve()
    home_root.mkdir(parents=True, exist_ok=True)
    home_dir = home_root / USERNAME
    helper_dir = HELPER_BASE / HELPER_DIR_NAME

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

    if helper_dir.exists():
        raise RuntimeError(
            f"Direktori helper '{helper_dir}' sudah ada. "
            "Periksa sisa instalasi Level 9 sebelum mencoba lagi."
        )

    if SERVICE_PATH.exists():
        raise RuntimeError(
            f"Service '{SERVICE_PATH}' sudah ada. Periksa instalasi sebelumnya."
        )

    user_created = False
    helper_created = False
    unit_created = False
    service_enable_attempted = False

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

        _set_linux_password(USERNAME, password_level9)
        account = pwd.getpwnam(USERNAME)

        cloud_dir = home_dir / "cloud"
        cloud_dir.mkdir(parents=True, exist_ok=True)

        (home_dir / "README.md").write_text(README_CONTENT, encoding="utf-8")
        (home_dir / "hint.md").write_text(HINT_CONTENT, encoding="utf-8")
        (cloud_dir / "backup-status.txt").write_text(
            "EVCONN BACKUP SERVICE\n"
            "service=backup-worker\n"
            "status=running\n"
            "note=Worker belum menyelesaikan proses backup.\n",
            encoding="utf-8",
        )

        # Seluruh file challenge dimiliki akun level9.
        os.chown(home_dir, account.pw_uid, account.pw_gid)
        for item in home_dir.rglob("*"):
            os.chown(item, account.pw_uid, account.pw_gid)

        os.chmod(home_dir, 0o700)
        for directory in [p for p in home_dir.rglob("*") if p.is_dir()]:
            os.chmod(directory, 0o700)
        for file_path in [p for p in home_dir.rglob("*") if p.is_file()]:
            os.chmod(file_path, 0o400)

        # Simpan worker dan password Level 10 di direktori root-only.
        HELPER_BASE.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chown(HELPER_BASE, 0, 0)
        os.chmod(HELPER_BASE, 0o700)

        helper_dir.mkdir(mode=0o700)
        helper_created = True
        os.chown(helper_dir, 0, 0)
        os.chmod(helper_dir, 0o700)

        worker_script = helper_dir / WORKER_FILENAME
        worker_script.write_text(
            _build_worker_script(
                password_level10,
                account.pw_uid,
                account.pw_gid,
                home_dir,
            ),
            encoding="utf-8",
        )
        os.chown(worker_script, 0, 0)
        os.chmod(worker_script, 0o700)

        # Buat unit systemd yang otomatis aktif saat Ubuntu boot.
        SERVICE_PATH.write_text(
            _build_systemd_unit(worker_script, home_dir),
            encoding="utf-8",
        )
        os.chown(SERVICE_PATH, 0, 0)
        os.chmod(SERVICE_PATH, 0o644)
        unit_created = True

        subprocess.run(["systemctl", "daemon-reload"], check=True)

        service_enable_attempted = True
        subprocess.run(
            ["systemctl", "enable", "--now", SERVICE_NAME],
            check=True,
        )

        _wait_until_worker_ready(home_dir)
        return home_dir

    except Exception:
        if service_enable_attempted:
            _stop_and_remove_service()

        if unit_created and SERVICE_PATH.exists():
            SERVICE_PATH.unlink(missing_ok=True)
            subprocess.run(
                ["systemctl", "daemon-reload"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        if helper_created and helper_dir.exists():
            shutil.rmtree(helper_dir, ignore_errors=True)

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
    """Mode mandiri untuk menguji generator Level 9."""
    _require_root()

    print("=== EVCONN CLOUD WARGAME: GENERATOR LEVEL 9 ===")
    print("Challenge: The Stuck Worker\\n")

    print("Masukkan password untuk login ke akun level9.")
    password_level9 = getpass.getpass("Password Level 9: ")
    password_level9_confirm = getpass.getpass("Ulangi Password Level 9: ")

    if password_level9 != password_level9_confirm:
        raise SystemExit("Password Level 9 tidak cocok. Tidak ada akun yang dibuat.")

    print("\\nMasukkan password yang harus ditemukan peserta untuk Level 10.")
    password_level10 = getpass.getpass("Password Level 10: ")
    password_level10_confirm = getpass.getpass("Ulangi Password Level 10: ")

    if password_level10 != password_level10_confirm:
        raise SystemExit("Password Level 10 tidak cocok. Tidak ada akun yang dibuat.")

    created_home = create_level9(password_level9, password_level10)

    print("\\n[BERHASIL] Challenge Level 9 berhasil dibuat.")
    print(f"Akun Linux : {USERNAME}")
    print(f"Home       : {created_home}")
    print(f"Service    : {SERVICE_NAME}")
    print("Worker     : berjalan sebagai akun level9")
    print("Persistence: otomatis aktif kembali setelah VM reboot")
    print("\\nUntuk menguji login, jalankan:")
    print("  su - level9")
    print("  cat README.md")
    print("  cat hint.md")
    print("  ps aux")
    print("\\nCari backup-worker.py, catat PID kolom kedua, lalu jalankan:")
    print("  kill PID")
    print("\\nSetelah worker berhenti, baca:")
    print("  cat cloud/recovery-report.txt")
    print("\\nPassword Level 9 harus sama dengan password yang ditemukan")
    print("peserta pada Level 8.")


if __name__ == "__main__":
    main()

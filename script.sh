#!/usr/bin/env bash
#
# EVCONN Linux Wargame - Ubuntu Server Setup
#
# Fungsi:
# - Memastikan script dijalankan sebagai root.
# - Memastikan sistem operasi adalah Ubuntu.
# - Memasang Python 3, Git, dan command yang dibutuhkan challenge.
# - Memastikan Python minimal versi 3.10.
# - Memastikan systemd aktif.
#
# Jalankan:
#   chmod +x script.sh
#   sudo ./script.sh
#
# Setelah berhasil:
#   sudo python3 main.py
#

set -Eeuo pipefail

readonly MIN_PYTHON_MAJOR=3
readonly MIN_PYTHON_MINOR=10

info() {
    printf '\n[INFO] %s\n' "$1"
}

success() {
    printf '[OK] %s\n' "$1"
}

fail() {
    printf '\n[ERROR] %s\n' "$1" >&2
    exit 1
}

if [[ "${EUID}" -ne 0 ]]; then
    fail "Jalankan script dengan sudo: sudo ./script.sh"
fi

if [[ ! -r /etc/os-release ]]; then
    fail "Tidak dapat membaca /etc/os-release. Script ini ditujukan untuk Ubuntu Server."
fi

# shellcheck disable=SC1091
source /etc/os-release

if [[ "${ID:-}" != "ubuntu" ]]; then
    fail "Sistem operasi terdeteksi '${PRETTY_NAME:-unknown}'. Script ini dibuat untuk Ubuntu."
fi

if ! command -v apt-get >/dev/null 2>&1; then
    fail "apt-get tidak ditemukan. Gunakan Ubuntu Server dengan APT."
fi

info "Memperbarui daftar paket Ubuntu..."
export DEBIAN_FRONTEND=noninteractive
apt-get update

info "Memasang Python, Git, dan dependency EVCONN..."
apt-get install -y --no-install-recommends \
    python3 \
    python3-minimal \
    git \
    ca-certificates \
    nano \
    iproute2 \
    curl \
    procps \
    findutils \
    grep \
    coreutils \
    passwd \
    systemd

success "Paket Ubuntu berhasil dipasang."

if ! command -v python3 >/dev/null 2>&1; then
    fail "Python 3 belum tersedia setelah instalasi."
fi

PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PYTHON_MAJOR="${PYTHON_VERSION%%.*}"
PYTHON_MINOR="${PYTHON_VERSION#*.}"

if (( PYTHON_MAJOR < MIN_PYTHON_MAJOR )) || {
    (( PYTHON_MAJOR == MIN_PYTHON_MAJOR )) &&
    (( PYTHON_MINOR < MIN_PYTHON_MINOR ));
}; then
    fail "Python ${PYTHON_VERSION} terpasang, tetapi EVCONN membutuhkan Python 3.10 atau lebih baru. Gunakan Ubuntu Server 22.04 atau lebih baru."
fi

success "Python ${PYTHON_VERSION} memenuhi persyaratan."

REQUIRED_COMMANDS=(
    git
    useradd
    userdel
    chpasswd
    systemctl
    ss
    curl
    ps
    grep
    find
    head
    tail
    wc
    chmod
    cat
    ls
    pwd
)

MISSING_COMMANDS=()
for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command -v "${cmd}" >/dev/null 2>&1; then
        MISSING_COMMANDS+=("${cmd}")
    fi
done

if (( ${#MISSING_COMMANDS[@]} > 0 )); then
    fail "Command berikut belum tersedia: ${MISSING_COMMANDS[*]}"
fi

success "Seluruh command yang dibutuhkan challenge tersedia."

if [[ ! -d /run/systemd/system ]]; then
    fail "systemd tidak terdeteksi aktif. Jalankan lab pada Ubuntu Server VM dengan systemd sebagai init system."
fi

success "systemd terdeteksi aktif."

printf '\n'
printf '%s\n' "============================================================"
printf '%s\n' "       EVCONN LINUX WARGAME - SETUP SELESAI"
printf '%s\n' "============================================================"
printf 'Ubuntu       : %s\n' "${PRETTY_NAME:-Ubuntu}"
printf 'Python       : %s\n' "${PYTHON_VERSION}"
printf 'Git          : %s\n' "$(git --version)"
printf 'systemd      : aktif\n'
printf '\n'
printf '%s\n' "Langkah berikutnya:"
printf '%s\n' "  1. Pastikan Anda berada di folder repository EVCONN."
printf '%s\n' "  2. Jalankan: sudo python3 main.py"
printf '%s\n' "  3. Jika password.txt belum ada, edit file tersebut sesuai instruksi."
printf '%s\n' "  4. Jalankan kembali: sudo python3 main.py"
printf '\n'

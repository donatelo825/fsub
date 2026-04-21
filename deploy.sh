#!/usr/bin/env bash
# FsubBot deploy script
# Usage:
#   ./deploy.sh          → build + start
#   ./deploy.sh stop     → stop
#   ./deploy.sh restart  → restart
#   ./deploy.sh logs     → log live
#   ./deploy.sh status   → cek container

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERR]${NC}  $*"; exit 1; }

command -v docker >/dev/null 2>&1 || error "Docker tidak ditemukan."
docker compose version >/dev/null 2>&1 || error "Docker Compose plugin tidak ditemukan."

mkdir -p logs

case "${1:-deploy}" in
  stop)
    info "Menghentikan container..."
    docker compose down
    success "Bot dihentikan." ;;

  restart)
    info "Restart..."
    docker compose restart
    success "Restart selesai." ;;

  logs)
    docker compose logs -f --tail=150 ;;

  status)
    docker compose ps ;;

  deploy|*)
    [[ -f ".env" ]] || error ".env tidak ditemukan. Jalankan: cp sample.env .env  lalu isi konfigurasinya."

    # Cek minimal satu bot terisi
    HAS_BOT=false
    for suffix in "" "_1"; do
        tok=$(grep -E "^TG_BOT_TOKEN${suffix}=" .env 2>/dev/null | cut -d= -f2- | xargs)
        ch=$(grep -E "^CHANNEL_ID${suffix}=" .env 2>/dev/null | cut -d= -f2- | xargs)
        [[ -n "$tok" && "$tok" != "0" && -n "$ch" && "$ch" != "0" ]] && HAS_BOT=true
    done
    [[ "$HAS_BOT" == "true" ]] || error "Isi minimal TG_BOT_TOKEN_1 + CHANNEL_ID_1 di .env"

    info "Build image..."
    docker compose build --no-cache

    info "Menjalankan bot..."
    docker compose up -d

    echo ""
    success "Deploy selesai!"
    docker compose ps
    echo ""
    info "Tips:"
    echo "  Log live  : ./deploy.sh logs"
    echo "  Stop      : ./deploy.sh stop"
    echo "  Restart   : ./deploy.sh restart" ;;
esac

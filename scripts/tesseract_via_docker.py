#!/usr/bin/env python3
"""Wrapper: teruskan panggilan `tesseract` dari host ke container Docker.

Docling menjalankan OCR dengan memanggil `tesseract <img> stdout tsv` sebagai
proses lokal (lihat TesseractOcrCliModel). Karena Tesseract ada di container
(bukan terinstall di Windows), skrip ini:

  1. Menerjemahkan path file temp host (mis. E:\\...\\.ocr_tmp\\tmpXXXX.png)
     menjadi path mount di container (/ocr_tmp/tmpXXXX.png).
  2. Menjalankan `docker exec <container> tesseract <args>`.
  3. Meneruskan stdout/stderr dan exit code apa adanya, agar Docling bisa
     membaca hasil TSV dari stdout persis seperti tesseract lokal.

Hanya butuh stdlib — aman dipanggil oleh python mana pun.
"""
import os
import sys
import subprocess

CONTAINER = os.environ.get("TESSERACT_CONTAINER", "doc-parser-tesseract")
DOCKER = os.environ.get("DOCKER_BIN", "docker")

# Prefix folder temp OCR di host -> path mount di container (docker-compose.yml).
# App meng-export OCR_TMP_DIR (absolut) sebelum memanggil wrapper ini.
HOST_TMP = os.path.abspath(os.environ.get("OCR_TMP_DIR", ".ocr_tmp"))
CONT_TMP = "/ocr_tmp"


def translate(arg: str) -> str:
    """Ubah path absolut host di bawah HOST_TMP menjadi path container."""
    try:
        ap = os.path.abspath(arg)
    except (ValueError, OSError):
        return arg
    if ap.lower().startswith(HOST_TMP.lower()):
        rel = ap[len(HOST_TMP):].lstrip("\\/")
        return CONT_TMP + "/" + rel.replace("\\", "/")
    return arg


def main() -> int:
    args = [translate(a) for a in sys.argv[1:]]
    cmd = [DOCKER, "exec", CONTAINER, "tesseract", *args]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        sys.stderr.write(
            "tesseract wrapper: binary 'docker' tidak ditemukan di PATH. "
            "Pastikan Docker Desktop terpasang.\n"
        )
        return 127
    sys.stdout.buffer.write(proc.stdout)
    sys.stderr.buffer.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

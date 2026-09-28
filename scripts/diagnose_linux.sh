#!/usr/bin/env bash
set -u

echo "EdgeSafe Doctor - Linux"
echo "======================="

pass() { printf 'PASS  %s\n' "$1"; }
warn() { printf 'WARN  %s\n' "$1"; }
fail() { printf 'FAIL  %s\n' "$1"; }

command -v python3 >/dev/null 2>&1 && pass "python3 present" || fail "python3 missing"

if command -v curl >/dev/null 2>&1; then
  pass "curl present"
else
  warn "curl missing"
fi

if command -v ffmpeg >/dev/null 2>&1; then
  pass "ffmpeg present"
else
  warn "ffmpeg missing"
fi

df -h . 2>/dev/null || true

if command -v systemctl >/dev/null 2>&1; then
  systemctl --failed --no-pager 2>/dev/null || true
fi

echo
echo "This script is intentionally non-invasive."
echo "Pass service-specific URLs to 'edgesafe-doctor --http ...' for endpoint checks."

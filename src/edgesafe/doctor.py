"""Cross-platform, dependency-free diagnostics for EdgeSafe Vision."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import socket
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Iterable, List, Optional


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str

    @property
    def ok(self) -> bool:
        return self.status == "PASS"


def check_disk(path: str = ".") -> CheckResult:
    usage = shutil.disk_usage(path)
    free_gb = usage.free / (1024 ** 3)
    status = "PASS" if free_gb >= 2 else "WARN"
    return CheckResult("disk", status, f"{free_gb:.1f} GiB free at {path}")


def check_tcp(host: str, port: int, timeout: float = 2.0) -> CheckResult:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return CheckResult(
                f"tcp:{host}:{port}", "PASS", "connection established"
            )
    except OSError as exc:
        return CheckResult(
            f"tcp:{host}:{port}", "FAIL", f"{type(exc).__name__}: {exc}"
        )


def check_http(url: str, timeout: float = 3.0) -> CheckResult:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "EdgeSafe-Doctor/0.1"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            code = getattr(response, "status", 200)
            status = "PASS" if 200 <= code < 500 else "WARN"
            return CheckResult(url, status, f"HTTP {code}")
    except urllib.error.HTTPError as exc:
        status = "PASS" if exc.code in (401, 403) else "WARN"
        return CheckResult(url, status, f"HTTP {exc.code}")
    except Exception as exc:
        return CheckResult(
            url, "FAIL", f"{type(exc).__name__}: {exc}"
        )


def baseline_results() -> List[CheckResult]:
    return [
        CheckResult(
            "python",
            "PASS",
            f"{platform.python_version()} on {platform.system()} "
            f"{platform.release()}",
        ),
        check_disk("."),
    ]


def run_checks(
    *,
    http_urls: Iterable[str] = (),
    tcp_targets: Iterable[tuple[str, int]] = (),
) -> List[CheckResult]:
    results = baseline_results()
    results.extend(check_http(url) for url in http_urls)
    results.extend(check_tcp(host, port) for host, port in tcp_targets)
    return results


def parse_target(value: str) -> tuple[str, int]:
    host, sep, raw_port = value.rpartition(":")
    if not sep or not host:
        raise argparse.ArgumentTypeError("target must be HOST:PORT")
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if not (1 <= port <= 65535):
        raise argparse.ArgumentTypeError("port must be 1..65535")
    return host, port


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edgesafe-doctor",
        description="Run non-invasive EdgeSafe deployment health checks.",
    )
    parser.add_argument(
        "--http",
        action="append",
        default=[],
        help="HTTP/HTTPS health URL; repeat for multiple endpoints.",
    )
    parser.add_argument(
        "--tcp",
        action="append",
        type=parse_target,
        default=[],
        metavar="HOST:PORT",
        help="TCP target to probe; repeat for multiple targets.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of the human-readable table.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    results = run_checks(http_urls=args.http, tcp_targets=args.tcp)

    if args.json:
        print(json.dumps([asdict(x) for x in results], indent=2))
    else:
        width = max(len(x.name) for x in results)
        for item in results:
            print(
                f"{item.status:4}  {item.name:<{width}}  {item.detail}"
            )

    return 1 if any(x.status == "FAIL" for x in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Cross-platform, dependency-free diagnostics for EdgeSafe Vision."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import socket
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urlsplit, urlunsplit


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str

    @property
    def ok(self) -> bool:
        return self.status == "PASS"


@dataclass(frozen=True)
class DoctorConfig:
    http_urls: tuple[str, ...] = ()
    tcp_targets: tuple[tuple[str, int], ...] = ()
    file_paths: tuple[str, ...] = ()


def check_disk(path: str = ".") -> CheckResult:
    usage = shutil.disk_usage(path)
    free_gb = usage.free / (1024 ** 3)
    status = "PASS" if free_gb >= 2 else "WARN"
    return CheckResult("disk", status, f"{free_gb:.1f} GiB free at {path}")


def check_file(path: str) -> CheckResult:
    target = Path(path).expanduser()
    name = f"file:{target}"

    if not target.exists():
        return CheckResult(name, "FAIL", "not found")
    if not target.is_file():
        return CheckResult(name, "WARN", "path exists but is not a regular file")

    try:
        size = target.stat().st_size
        with target.open("rb") as handle:
            handle.read(1)
    except OSError as exc:
        return CheckResult(name, "FAIL", f"{type(exc).__name__}: {exc}")

    return CheckResult(name, "PASS", f"readable, {size} bytes")


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


def _safe_url_label(url: str) -> str:
    """Return a diagnostic label without URL credentials, query, or fragment."""

    try:
        parsed = urlsplit(url)
        host = parsed.hostname or ""
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        if parsed.port is not None:
            host = f"{host}:{parsed.port}"
        return urlunsplit((parsed.scheme, host, parsed.path, "", ""))
    except ValueError:
        return url.split("?", 1)[0].split("#", 1)[0]


def check_http(url: str, timeout: float = 3.0) -> CheckResult:
    label = _safe_url_label(url)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "EdgeSafe-Doctor/0.2"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            code = getattr(response, "status", 200)
            status = "PASS" if 200 <= code < 500 else "WARN"
            return CheckResult(label, status, f"HTTP {code}")
    except urllib.error.HTTPError as exc:
        status = "PASS" if exc.code in (401, 403) else "WARN"
        return CheckResult(label, status, f"HTTP {exc.code}")
    except Exception as exc:
        return CheckResult(
            label, "FAIL", f"{type(exc).__name__}: {exc}"
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
    file_paths: Iterable[str] = (),
) -> List[CheckResult]:
    results = baseline_results()
    results.extend(check_http(url) for url in http_urls)
    results.extend(check_tcp(host, port) for host, port in tcp_targets)
    results.extend(check_file(path) for path in file_paths)
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


def _string_list(data: object, key: str) -> list[str]:
    if data is None:
        return []
    if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
        raise ValueError(f"{key} must be a JSON array of strings")
    return list(data)


def load_check_config(path: str) -> DoctorConfig:
    """Load a small, explicit JSON check plan."""

    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read config: {exc}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("config must contain valid JSON") from exc

    if not isinstance(data, dict):
        raise ValueError("config root must be a JSON object")

    allowed = {"http", "tcp", "files"}
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValueError(f"unknown config keys: {', '.join(unknown)}")

    http_urls = _string_list(data.get("http"), "http")
    raw_tcp = _string_list(data.get("tcp"), "tcp")
    file_paths = _string_list(data.get("files"), "files")

    tcp_targets: list[tuple[str, int]] = []
    for value in raw_tcp:
        try:
            tcp_targets.append(parse_target(value))
        except argparse.ArgumentTypeError as exc:
            raise ValueError(f"invalid tcp target {value!r}: {exc}") from exc

    return DoctorConfig(
        http_urls=tuple(http_urls),
        tcp_targets=tuple(tcp_targets),
        file_paths=tuple(file_paths),
    )


def build_evidence_bundle(results: Iterable[CheckResult]) -> dict:
    """Build a shareable evidence object without collecting a hostname."""

    return {
        "schema": "edgesafe-evidence-v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "pythonVersion": platform.python_version(),
        "checks": [asdict(item) for item in results],
    }



def render_markdown_report(results: Iterable[CheckResult]) -> str:
    """Render existing check results as a deterministic Markdown handoff."""
    items = list(results)
    counts = {status: sum(item.status == status for item in items) for status in ("PASS", "WARN", "FAIL")}
    lines = [
        "# EdgeSafe Diagnostic Report",
        "",
        f"Summary: {counts['PASS']} PASS · {counts['WARN']} WARN · {counts['FAIL']} FAIL",
        "",
        "## Findings",
    ]
    lines.extend(f"- {item.status} {item.name} — {item.detail}" for item in items)
    first_failure = next((item for item in items if item.status == "FAIL"), None)
    lines.extend(["", "## Next verification"])
    if first_failure is None:
        lines.append("No failing check was supplied. Continue with the next planned verification.")
    else:
        lines.append(
            f"Start by reviewing `{first_failure.name}`. This is a triage hint, not a proven root cause."
        )
    return "\n".join(lines) + "\n"


def write_evidence_bundle(path: str, results: Iterable[CheckResult]) -> Path:
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = build_evidence_bundle(results)
    target.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return target


def _dedupe(values: Iterable) -> list:
    result = []
    seen = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edgesafe-doctor",
        description="Run non-invasive EdgeSafe deployment health checks.",
    )
    parser.add_argument(
        "--config",
        help="JSON check plan with http, tcp, and files arrays.",
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
        "--file",
        action="append",
        default=[],
        dest="files",
        metavar="PATH",
        help="Required readable file; repeat for multiple paths.",
    )
    parser.add_argument(
        "--evidence",
        metavar="PATH",
        help="Write a structured JSON evidence bundle to PATH.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the legacy JSON check list instead of the table.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = DoctorConfig()
    if args.config:
        try:
            config = load_check_config(args.config)
        except ValueError as exc:
            parser.error(str(exc))

    http_urls = _dedupe([*config.http_urls, *args.http])
    tcp_targets = _dedupe([*config.tcp_targets, *args.tcp])
    file_paths = _dedupe([*config.file_paths, *args.files])

    results = run_checks(
        http_urls=http_urls,
        tcp_targets=tcp_targets,
        file_paths=file_paths,
    )

    if args.evidence:
        try:
            evidence_path = write_evidence_bundle(args.evidence, results)
        except OSError as exc:
            parser.error(f"cannot write evidence bundle: {exc}")
        if not args.json:
            print(f"EVIDENCE  {evidence_path}")

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

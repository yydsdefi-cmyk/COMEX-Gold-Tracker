"""Ordinary HTTPS download only; no cookies, login, or challenge bypass."""
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .parser import SOURCE_URL, ReportError

MAX_BYTES = 10 * 1024 * 1024


class OfficialRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname not in {"www.cmegroup.com", "cmegroup.com"}:
            raise ReportError("Refusing redirect outside official CME HTTPS hosts")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_report(timeout=20, attempts=2):
    opener = build_opener(OfficialRedirects())
    last_error = None
    for i in range(attempts):
        try:
            req = Request(SOURCE_URL, headers={
                "User-Agent": "COMEX-Gold-Tracker/0.1 (public official stock report)",
                "Accept": "application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "Cache-Control": "no-cache",
            })
            with opener.open(req, timeout=timeout) as response:
                blob = response.read(MAX_BYTES + 1)
                if len(blob) > MAX_BYTES:
                    raise ReportError("Official report exceeds 10 MB size limit")
                if response.status != 200:
                    raise ReportError(f"Unexpected HTTP status {response.status}")
                metadata = {"method": "official_https_download", "http_status": response.status,
                            "final_url": response.url, "headers": {k: response.headers.get(k)
                            for k in ("Content-Type", "Content-Length", "Last-Modified", "ETag", "Date")}}
                return blob, metadata
        except HTTPError as exc:
            if exc.code not in {500, 502, 503, 504}:
                raise ReportError(f"CME HTTP {exc.code}; stop, no access-control bypass") from exc
            last_error = exc
        except (URLError, TimeoutError, OSError) as exc:
            last_error = exc
        if i + 1 < attempts:
            time.sleep(1 + i)
    raise ReportError(f"Official download failed after {attempts} attempt(s): {last_error}")

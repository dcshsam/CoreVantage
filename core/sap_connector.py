"""
CodeVantage SAP System Connector
Connects to ECC / S/4HANA backend via REST OData or pyrfc (optional).
Fetches ABAP source code for analysis.
"""

from __future__ import annotations
import os
import base64
import logging
from typing import List, Optional
import requests

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 10
READ_TIMEOUT    = 60


class SAPConnector:
    """
    Connects to a SAP system and retrieves ABAP source code objects.

    Supports two modes:
    - REST/OData (default): uses SAP Gateway / Netweaver REST API
    - pyrfc (optional):     direct RFC connection (requires SAP NW RFC SDK)
    """

    def __init__(self, host: str, client: str, user: str, password: str,
                 sysnr: str = "00", lang: str = "EN", use_ssl: bool = True):
        self.host     = host.rstrip("/")
        self.client   = client
        self.user     = user
        self.password = password
        self.sysnr    = sysnr
        self.lang     = lang
        self.use_ssl  = use_ssl
        self._session = self._build_session()

    def _build_session(self) -> requests.Session:
        s = requests.Session()
        creds = base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
        s.headers.update({
            "Authorization": f"Basic {creds}",
            "sap-client":    self.client,
            "Accept":        "application/json",
            "Content-Type":  "application/json",
        })
        s.verify = False  # In enterprise environments, set to CA cert bundle
        return s

    @property
    def base_url(self) -> str:
        scheme = "https" if self.use_ssl else "http"
        return f"{scheme}://{self.host}"

    def ping(self) -> tuple[bool, str]:
        """Test connectivity to the SAP system."""
        try:
            url = f"{self.base_url}/sap/opu/odata/sap/ZCOREVANTAGE_SRV/$metadata"
            # Fall back to standard catalog service if custom service not deployed
            url_fallback = f"{self.base_url}/sap/opu/odata/iwfnd/CATALOGSERVICE/ServiceCollection"
            try:
                r = self._session.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
                if r.status_code < 400:
                    return True, "Connected via ZCOREVANTAGE_SRV"
            except Exception:
                pass
            r = self._session.get(url_fallback, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
            if r.status_code < 400:
                return True, f"Connected to SAP system (client {self.client})"
            return False, f"HTTP {r.status_code}: {r.text[:200]}"
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection refused: {e}"
        except Exception as e:
            return False, str(e)

    def get_program_source(self, program_name: str) -> Optional[str]:
        """
        Fetch ABAP program source code.
        Tries OData first, then falls back to SOAP/RFC-over-HTTP.
        """
        # Try standard ADT REST API (SAP ABAP Development Tools)
        source = self._adt_get_source(program_name.upper())
        if source:
            return source
        logger.warning("ADT API unavailable, trying RFC fallback for %s", program_name)
        return self._rfc_get_source(program_name.upper())

    def _adt_get_source(self, name: str) -> Optional[str]:
        """SAP ADT (ABAP Development Tools) REST API for source retrieval."""
        try:
            url = f"{self.base_url}/sap/bc/adt/programs/programs/{name}/source/main"
            r   = self._session.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                                    headers={"Accept": "text/plain"})
            if r.status_code == 200:
                return r.text
        except Exception as exc:
            logger.debug("ADT API failed: %s", exc)
        return None

    def _rfc_get_source(self, name: str) -> Optional[str]:
        """Optional pyrfc-based source retrieval."""
        try:
            import pyrfc  # type: ignore
            conn = pyrfc.Connection(
                ashost=self.host, sysnr=self.sysnr,
                client=self.client, user=self.user,
                passwd=self.password, lang=self.lang,
            )
            result = conn.call("RFC_READ_REPORT", PROGRAM=name)
            conn.close()
            return "\n".join(line["LINE"] for line in result.get("QTAB", []))
        except ImportError:
            logger.debug("pyrfc not installed")
        except Exception as exc:
            logger.debug("RFC source fetch failed: %s", exc)
        return None

    def list_custom_programs(self, prefix: str = "Z") -> List[dict]:
        """
        Returns a list of custom programs (Z/Y namespace) from the system.
        Uses ABAP OData catalog if available, else returns empty list.
        """
        try:
            url = (f"{self.base_url}/sap/opu/odata/sap/ZCOREVANTAGE_SRV/Programs"
                   f"?$filter=startswith(ProgramName,'{prefix}')&$top=200&$format=json")
            r   = self._session.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
            if r.status_code == 200:
                return r.json().get("d", {}).get("results", [])
        except Exception as exc:
            logger.debug("Program list fetch failed: %s", exc)
        return []


def connector_from_env() -> SAPConnector:
    return SAPConnector(
        host=os.getenv("SAP_HOST", "localhost"),
        client=os.getenv("SAP_CLIENT", "100"),
        user=os.getenv("SAP_USER", ""),
        password=os.getenv("SAP_PASSWORD", ""),
        sysnr=os.getenv("SAP_SYSNR", "00"),
        lang=os.getenv("SAP_LANG", "EN"),
    )

#clearpass.py

#---- standard libs

import requests

class ClearPassClient:
    """
    Minimal ClearPass API client
    """

    def __init__(self, server: str, *, https_prefix: str = "https://", verify_ssl: bool = False, timeout: int = 15):
        self.server = server
        self.https_prefix = https_prefix
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({"accept": "application/json"})

    def request(self, api_paths: dict, method: str, endpoint_key: str, token: str | None = None,
                *, path_suffix: str = "", params: dict | None = None, json_body: dict | None = None):
        base = self.https_prefix + self.server
        path = api_paths[endpoint_key]
        url = base + path + (path_suffix or "")

        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        resp = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json_body,
            headers=headers if headers else None,
            verify=self.verify_ssl,
            timeout=self.timeout,
        )

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            content_type = resp.headers.get("content-type", "")
            body = resp.text
            if len(body) > 4000:
                body = body[:4000] + "\n... (truncated)"

            request_json = json_body
            if isinstance(request_json, dict):
                masked = dict(request_json)
                for k in ("client_secret", "radius_secret", "tacacs_secret", "password", "enable_password"):
                    if k in masked:
                        masked[k] = "***"
                request_json = masked

            msg = (
                f"HTTP {resp.status_code} {resp.reason}\n"
                f"URL: {resp.url}\n"
                f"Method: {method.upper()}\n"
                f"Content-Type: {content_type}\n"
                f"Response body:\n{body}"
            )
            if request_json is not None:
                msg += f"\n\nRequest JSON:\n{request_json}"

            raise requests.HTTPError(msg, response=resp) from e

        if resp.status_code == 204 or not resp.content:
            return None

        try:
            return resp.json()
        except ValueError:
            return resp.text

    def login(self, api_paths: dict, credentials: dict) -> dict:
        payload = {
            "grant_type": credentials["grant_type"],
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
        }
        return self.request(api_paths, "POST", "oauth", json_body=payload)

    def nad_list(self, api_paths: dict, token: str, *, offset: int = 0, limit: int = 25, sort: str = "+id"):
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "calculate_count": "false",
        }
        return self.request(api_paths, "GET", "nad", token=token, params=params)

    def nad_create(self, api_paths: dict, token: str, payload: dict):
        return self.request(api_paths, "POST", "nad", token=token, json_body=payload)

    def nad_delete(self, api_paths: dict, token: str, device_id: int):
        return self.request(api_paths, "DELETE", "nad", token=token, path_suffix=f"/{device_id}")


        # ---- Endpoint (Identities > Endpoint) ----

    def endpoint_list(self, api_paths: dict, token: str, *, offset: int = 0, limit: int = 25, sort: str = "+id"):
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "calculate_count": "false",
        }
        return self.request(api_paths, "GET", "endpoint", token=token, params=params)

    def endpoint_get(self, api_paths: dict, token: str, *, endpoint_id: int | None = None, mac_address: str | None = None):
        if endpoint_id is not None:
            return self.request(api_paths, "GET", "endpoint", token=token, path_suffix=f"/{endpoint_id}")

        if mac_address is not None:
            return self.request(api_paths, "GET", "endpoint", token=token, path_suffix=f"/mac-address/{mac_address}")

        raise ValueError("endpoint_get requires either endpoint_id or mac_address")

    def endpoint_add(self, api_paths: dict, token: str, payload: dict):
        return self.request(api_paths, "POST", "endpoint", token=token, json_body=payload)

    def endpoint_delete(self, api_paths: dict, token: str, *, endpoint_id: int | None = None, mac_address: str | None = None):
        if endpoint_id is not None:
            return self.request(api_paths, "DELETE", "endpoint", token=token, path_suffix=f"/{endpoint_id}")

        if mac_address is not None:
            return self.request(api_paths, "DELETE", "endpoint", token=token, path_suffix=f"/mac-address/{mac_address}")

        raise ValueError("endpoint_delete requires either endpoint_id or mac_address")
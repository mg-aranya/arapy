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

    def network_device_list(self, api_paths: dict, token: str, *, offset: int = 0, limit: int = 25, sort: str = "+id", filter: str | None = None, calculate_count: bool | None = None):
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
        }
        if calculate_count is not None:
            params["calculate_count"] = calculate_count
        if filter is not None:
            params["filter"] = filter

        return self.request(api_paths, "GET", "network_device", token=token, params=params)

    def network_device_create(self, api_paths: dict, token: str, payload: dict):
        return self.request(api_paths, "POST", "network_device", token=token, json_body=payload)

    def network_device_delete(self, api_paths: dict, token: str, device_id: int):
        return self.request(api_paths, "DELETE", "network_device", token=token, path_suffix=f"/{device_id}")

    def network_device_get(self, api_paths: dict, token: str, *, device_id: int):
        return self.request(api_paths, "GET", "network_device", token=token, path_suffix=f"/{device_id}")


        # ---- Endpoint (Identities > Endpoint) ----

    def endpoint_list(self, api_paths: dict, token: str, *, offset: int = 0, limit: int = 25, sort: str = "+id", filter: str | None = None, calculate_count: bool | None = None):
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
        }
        if calculate_count is not None:
            params["calculate_count"] = calculate_count
        if filter is not None:
            params["filter"] = filter

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

    # ---- Device (Identities > Device Accounts) ----

    def device_list(self, api_paths: dict, token: str, *, offset: int = 0, limit: int = 25, sort: str = "-id", filter: str | None = None, calculate_count: bool | None = None):
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
        }
        if calculate_count is not None:
            params["calculate_count"] = calculate_count
        if filter is not None:
            params["filter"] = filter

        return self.request(api_paths, "GET", "device", token=token, params=params)

    def device_create(self, api_paths: dict, token: str, payload: dict):
        return self.request(api_paths, "POST", "device", token=token, json_body=payload)

    def device_get(self, api_paths: dict, token: str, *, device_id: int):
        return self.request(api_paths, "GET", "device", token=token, path_suffix=f"/{device_id}")

    def device_update(self, api_paths: dict, token: str, device_id: int, payload: dict):
        return self.request(api_paths, "PATCH", "device", token=token, path_suffix=f"/{device_id}", json_body=payload)

    def device_delete(self, api_paths: dict, token: str, device_id: int):
        return self.request(api_paths, "DELETE", "device", token=token, path_suffix=f"/{device_id}")

    def device_get_by_mac(self, api_paths: dict, token: str, mac_address: str):
        return self.request(api_paths, "GET", "device", token=token, path_suffix=f"/mac/{mac_address}")

    def device_update_by_mac(self, api_paths: dict, token: str, mac_address: str, payload: dict):
        return self.request(api_paths, "PATCH", "device", token=token, path_suffix=f"/mac/{mac_address}", json_body=payload)

    def device_delete_by_mac(self, api_paths: dict, token: str, mac_address: str):
        return self.request(api_paths, "DELETE", "device", token=token, path_suffix=f"/mac/{mac_address}")

    # ---- User (Identities > User Accounts) ----

    def user_list(self, api_paths: dict, token: str, *, offset: int = 0, limit: int = 25, sort: str = "+id", filter: str | None = None, calculate_count: bool | None = None):
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
        }
        if calculate_count is not None:
            params["calculate_count"] = calculate_count
        if filter is not None:
            params["filter"] = filter

        return self.request(api_paths, "GET", "guest-user", token=token, params=params)

    def user_create(self, api_paths: dict, token: str, payload: dict):
        return self.request(api_paths, "POST", "guest-user", token=token, json_body=payload)

    def user_get(self, api_paths: dict, token: str, user_id: int):
        return self.request(api_paths, "GET", "guest-user", token=token, path_suffix=f"/{user_id}")

    def user_update(self, api_paths: dict, token: str, user_id: int, payload: dict):
        return self.request(api_paths, "PATCH", "guest-user", token=token, path_suffix=f"/{user_id}", json_body=payload)

    def user_delete(self, api_paths: dict, token: str, user_id: int):
        return self.request(api_paths, "DELETE", "guest-user", token=token, path_suffix=f"/{user_id}")

    # ---- API Client (Identities > API Clients) ----

    def api_client_list(self, api_paths: dict, token: str, *, offset: int = 0, limit: int = 25, sort: str = "+id", filter: str | None = None, calculate_count: bool | None = None):
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
        }
        if calculate_count is not None:
            params["calculate_count"] = calculate_count
        if filter is not None:
            params["filter"] = filter

        return self.request(api_paths, "GET", "api_client", token=token, params=params)

    def api_client_create(self, api_paths: dict, token: str, payload: dict):
        return self.request(api_paths, "POST", "api_client", token=token, json_body=payload)

    def api_client_get(self, api_paths: dict, token: str, client_id: str):
        return self.request(api_paths, "GET", "api_client", token=token, path_suffix=f"/{client_id}")

    def api_client_update(self, api_paths: dict, token: str, client_id: str, payload: dict):
        return self.request(api_paths, "PATCH", "api_client", token=token, path_suffix=f"/{client_id}", json_body=payload)

    def api_client_delete(self, api_paths: dict, token: str, client_id: str):
        return self.request(api_paths, "DELETE", "api_client", token=token, path_suffix=f"/{client_id}")

    # ---- Auth Method (Policy Elements > Authentication Methods) ----

    def auth_method_list(self, api_paths: dict, token: str, *, offset: int = 0, limit: int = 25, sort: str = "+id", filter: str | None = None, calculate_count: bool | None = None):
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
        }
        if calculate_count is not None:
            params["calculate_count"] = calculate_count
        if filter is not None:
            params["filter"] = filter

        return self.request(api_paths, "GET", "auth_method", token=token, params=params)

    def auth_method_create(self, api_paths: dict, token: str, payload: dict):
        return self.request(api_paths, "POST", "auth_method", token=token, json_body=payload)

    def auth_method_get(self, api_paths: dict, token: str, method_id: int):
        return self.request(api_paths, "GET", "auth_method", token=token, path_suffix=f"/{method_id}")

    def auth_method_update(self, api_paths: dict, token: str, method_id: int, payload: dict):
        return self.request(api_paths, "PATCH", "auth_method", token=token, path_suffix=f"/{method_id}", json_body=payload)

    def auth_method_delete(self, api_paths: dict, token: str, method_id: int):
        return self.request(api_paths, "DELETE", "auth_method", token=token, path_suffix=f"/{method_id}")

    # ---- Enforcement Profile (Policy Elements > Enforcement Profiles) ----

    def enforcement_profile_list(self, api_paths: dict, token: str, *, offset: int = 0, limit: int = 25, sort: str = "+id", filter: str | None = None, calculate_count: bool | None = None):
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
        }
        if calculate_count is not None:
            params["calculate_count"] = calculate_count
        if filter is not None:
            params["filter"] = filter

        return self.request(api_paths, "GET", "enforcement_profile", token=token, params=params)

    def enforcement_profile_get(self, api_paths: dict, token: str, profile_id: int):
        return self.request(api_paths, "GET", "enforcement_profile", token=token, path_suffix=f"/{profile_id}")

    # ---- Network Device Group (Policy Elements > Network Device Groups) ----

    def network_device_group_list(self, api_paths: dict, token: str, *, offset: int = 0, limit: int = 25, sort: str = "+id", filter: str | None = None, calculate_count: bool | None = None):
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
        }
        if calculate_count is not None:
            params["calculate_count"] = calculate_count
        if filter is not None:
            params["filter"] = filter

        return self.request(api_paths, "GET", "network_device_group", token=token, params=params)

    def network_device_group_create(self, api_paths: dict, token: str, payload: dict):
        return self.request(api_paths, "POST", "network_device_group", token=token, json_body=payload)

    def network_device_group_get(self, api_paths: dict, token: str, *, group_id: int):
        return self.request(api_paths, "GET", "network_device_group", token=token, path_suffix=f"/{group_id}")

    def network_device_group_update(self, api_paths: dict, token: str, group_id: int, payload: dict):
        return self.request(api_paths, "PATCH", "network_device_group", token=token, path_suffix=f"/{group_id}", json_body=payload)

    def network_device_group_replace(self, api_paths: dict, token: str, group_id: int, payload: dict):
        return self.request(api_paths, "PUT", "network_device_group", token=token, path_suffix=f"/{group_id}", json_body=payload)

    def network_device_group_delete(self, api_paths: dict, token: str, group_id: int):
        return self.request(api_paths, "DELETE", "network_device_group", token=token, path_suffix=f"/{group_id}")

    def network_device_group_get_by_name(self, api_paths: dict, token: str, name: str):
        return self.request(api_paths, "GET", "network_device_group", token=token, path_suffix=f"/name/{name}")

    def network_device_group_update_by_name(self, api_paths: dict, token: str, name: str, payload: dict):
        return self.request(api_paths, "PATCH", "network_device_group", token=token, path_suffix=f"/name/{name}", json_body=payload)

    def network_device_group_replace_by_name(self, api_paths: dict, token: str, name: str, payload: dict):
        return self.request(api_paths, "PUT", "network_device_group", token=token, path_suffix=f"/name/{name}", json_body=payload)

    def network_device_group_delete_by_name(self, api_paths: dict, token: str, name: str):
        return self.request(api_paths, "DELETE", "network_device_group", token=token, path_suffix=f"/name/{name}")
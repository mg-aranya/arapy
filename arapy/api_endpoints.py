#api_endpoints.py

"""
ClearPass 6.11.13 API endpoints
"""

API_ENDPOINTS = {
    "oauth": "/api/oauth",
    # Policy Elements
    "network_device": "/api/network-device",
    "network_device_group": "/api/network-device-group",
    "auth_method": "/api/auth-method",
    "enforcement_profile": "/api/enforcement-profile",
    "authorization_profile": "/api/authorization-profile",
    "device_category": "/api/device-category",
    "application_dictionary": "/api/application-dictionary",
    # Identities
    "endpoint": "/api/endpoint",
    "device": "/api/device",
    "guest_user": "/api/guest-user",
    "api_client": "/api/api-client",
    # Certificates
    "CSR": "/api/cert-sign-request",
    "server_cert": "/api/server-cert",
    "certificate": "/api/trusted-ca",
    # Logs & Insights
    "insight_endpoint": "/api/insight/endpoint",
    "system_event": "/api/system-event",
}


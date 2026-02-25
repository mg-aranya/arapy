#api_endpoints.py

"""
ClearPass 6.11.13 API endpoints
"""

API_ENDPOINTS = {
    # ----API Operations
    # API Operations > TokenEndpoint
    "oauth": "/api/oauth",
    # API Operations > TokenInfo
    "oauth-me": "/api/oauth/me",
    # API Operations > TokenPrivileges
    "oauth-privileges": "/api/oauth/privileges",

    # ----Certificate Authority
    #TODO later

    #----Guest Actions
    #TODO later

    #----Guest Configuration
    #TODO later

    #----Tools and Utilities
    #TODO later

    #----Platform Certificates
    # Platform Certificates > Certificate Signing Request
    "cert-sign-request": "/api/cert-sign-request",
    # Platform Certificates > Certificate Trust List
    "cert-trust-list": "/api/cert-trust-list",
    # Platform Certificates > Certificate Trust List Details
    "cert-trust-list-details": "/api/cert-trust-list-details",
    # Platform Certificates > Client Cert
    "client-cert": "/api/client-cert",
    # Platform Certificates > Revocation List
    "revocation-list": "/api/revocation-list",
    # Platform Certificates > Self Signed Cert
    "self-signed-cert": "/api/self-signed-cert",
    # Platform Certificates > Server Certificate
    "server-cert": "/api/server-cert",
    # Platform Certificates > Service Certificate
    "service-cert": "/api/service-cert",

    #----Identities
    # Identities > API Client
    "api-client": "/api/api-client",
    # Identities > Deny Listed Users
    "deny-listed-users": "/api/deny-listed-users",
    # Identities > Device
    "device": "/api/device",
    # Identities > Endpoint
    "endpoint": "/api/endpoint",
    # Identities > External Account
    "external-account": "/api/external-account",
    # Identities > Guest User
    # Keep key name in sync with ClearPassClient.user-* (uses 'guest-user')
    "guest-user": "/api/guest-user",
    # Identities > Local User
    "local-user": "/api/local-user",
    # Identities > Static Host List
    "static-host-list": "/api/static-host-list",

    #----Logs
    # Logs > Endpoint Info
    "insight-endpoint-mac": "/api/insight/endpoint/mac",
    # Logs > Login Audit
    "login-audit": "/api/login-audit",
    # Logs > System Event
    "system-event": "/api/system-event",

    #----Local Server Configuration
    # Local Server Configuration > AD Domain
    "ad-domain": "/api/ad-domain",
    # Local Server Configuration > Access Control
    "access-control": "/api/server/access-control",
    # Local Server Configuration > CPPM Version
    "cppm-version": "/api/cppm-version",
    # Local Server Configuration > Server Configuration
    "server-configuration": "/api/cluster/server",
    # Local Server Configuration > Server FIPS
    "server-fips": "/api/server/fips",
    # Local Server Configuration > Server SNMP
    "server-snmp": "/api/server/snmp",
    # Local Server Configuration > Server Version
    "server-version": "/api/server/version",
    # Local Server Configuration > Service Parameter
    "service-parameter": "/api/service-parameter",
    # Local Server Configuration > System Service Control
    "system-service-control": "/api/server/service",

    #----Global Server Configuration
    # Global Server Configuration > Admin Privilege
    "admin-privileges": "/api/admin-privilege",
    # Global Server Configuration > Admin User
    "admin-user": "/api/admin-user",
    # Global Server Configuration > Admin User Password Policy
    "admin-user-password-policy": "/api/admin-user/password-policy",
    # Global Server Configuration > Application License
    "application-license": "/api/application-license",
    # Global Server Configuration > Attribute
    "attribute": "/api/attribute",
    # Global Server Configuration > ClearPass Portal
    "clearpass-portal": "/api/clearpass-portal",
    # Global Server Configuration > Cluster DB Sync
    "cluster-db-sync": "/api/cluster/db-sync",
    # Global Server Configuration > Cluster Wide Parameters
    "cluster-wide-parameters": "/api/cluster/parameters",
    # Global Server Configuration > Data Filter
    "data-filter": "/api/data-filter",
    # Global Server Configuration > File Backup Server
    "file-backup-server": "/api/file-backup-server",
    # Global Server Configuration > List All Privileges
    "list-all-privileges": "/api/oauth/all-privileges",
    # Global Server Configuration > Local User Password Policy
    "local-user-password-policy": "/api/local-user/password-policy",
    # Global Server Configuration > Messaging Setup
    "essaging-setup": "/api/messaging-setup",
    # Global Server Configuration > Operator Profile
    "operator-profile": "/api/operator-profile",
    # Global Server Configuration > Policy Manager Zone
    "policy-manager-zone": "/api/server/policy-manager-zones",
    # Global Server Configuration > SNMP Trap Receiver
    "snmp-trap-receiver": "/api/snmp-trap-receiver",

    #----Integrations
    #TODO later

    # ----Policy Elements
    # Policy Elements > Application Dictionary
    "application-dictionary": "/api/application-dictionary",
    # Policy Elements > Auth Method
    "auth-method": "/api/auth-method",
    # Policy Elements > Auth Source
    "auth-source": "/api/auth-source",
    # Policy Elements > Enforcement Policy
    "enforcement-policy": "/api/enforcement-policy",
    # Policy Elements > Network Device
    "network-device": "/api/network-device",
    # Policy Elements > Network Device Group
    "network-device-group": "/api/network-device-group",
    # Policy Elements > Posture Policy
    "posture-policy": "/api/posture-policy",
    # Policy Elements > RADIUS Dictionary
    "radius-dictionary": "/api/radius-dictionary",
    # Policy Elements > RADIUS Dynamic Authorization Template
    "radius-dynamic-authorization-template": "/api/radius-dynamic-authorization-template",
    # Policy Elements > RADIUS Proxy Target
    "proxy-target": "/api/proxy-target",
    # Policy Elements > Role
    "role": "/api/role",
    # Policy Elements > Role Mapping
    "role-mapping": "/api/role-mapping",
    # Policy Elements > Service
    "service": "/api/service",
    # Policy Elements > TACACS Service Dictionary
    "tacacs-service-dictionary": "/api/tacacs-service-dictionary",

    #----Endpoint Visibility
    #TODO later

    #----Session Control
    #TODO later

    #----Enforcement Profile
    #TODO later

    #----Insight
    #TODO later
    
    #----DEV
    # These are not actual API endpoints, but are used for testing the CLI tool during development. They can be removed later.
    "test": "/api/network-device",    

}


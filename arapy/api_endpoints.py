#api_endpoints.py

"""
ClearPass 6.11.13 API endpoints
"""

API_ENDPOINTS = {
    # ----API Operations
    # API Operations > TokenEndpoint
    "oauth": "/api/oauth",
    # API Operations > TokenInfo
    "oauth_me": "/api/oauth/me",
    # API Operations > TokenPrivileges
    "oauth_privileges": "/api/oauth/privileges",

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
    "cert_sign_request": "/api/cert-sign-request",
    # Platform Certificates > Certificate Trust List
    "cert_trust_list": "/api/cert-trust-list",
    # Platform Certificates > Certificate Trust List Details
    "cert_trust_list_details": "/api/cert-trust-list-details",
    # Platform Certificates > Client Cert
    "client_cert": "/api/client-cert",
    # Platform Certificates > Revocation List
    "revocation_list": "/api/revocation-list",
    # Platform Certificates > Self Signed Cert
    "self_signed_cert": "/api/self-signed-cert",
    # Platform Certificates > Server Certificate
    "server_cert": "/api/server-cert",
    # Platform Certificates > Service Certificate
    "service_cert": "/api/service-cert",

    #----Identities
    # Identities > API Client
    "api_client": "/api/api-client",
    # Identities > Deny Listed Users
    "deny_listed_users": "/api/deny-listed-users",
    # Identities > Device
    "device": "/api/device",
    # Identities > Endpoint
    "endpoint": "/api/endpoint",
    # Identities > External Account
    "external_account": "/api/external-account",
    # Identities > Guest User
    # Keep key name in sync with ClearPassClient.user_* (uses 'guest-user')
    "guest-user": "/api/guest-user",
    # Identities > Local User
    "local_user": "/api/local-user",
    # Identities > Static Host List
    "static_host_list": "/api/static-host-list",

    #----Logs
    # Logs > Endpoint Info
    "insight_endpoint_mac": "/api/insight/endpoint/mac",
    # Logs > Login Audit
    "login_audit": "/api/login-audit",
    # Logs > System Event
    "system_event": "/api/system-event",

    #----Local Server Configuration
    # Local Server Configuration > AD Domain
    "ad_domain": "/api/ad-domain",
    # Local Server Configuration > Access Control
    "access_control": "/api/server/access-control",
    # Local Server Configuration > CPPM Version
    "cppm_version": "/api/cppm-version",
    # Local Server Configuration > Server Configuration
    "server_configuration": "/api/cluster/server",
    # Local Server Configuration > Server FIPS
    "server_fips": "/api/server/fips",
    # Local Server Configuration > Server SNMP
    "server_snmp": "/api/server/snmp",
    # Local Server Configuration > Server Version
    "server_version": "/api/server/version",
    # Local Server Configuration > Service Parameter
    "service_parameter": "/api/service-parameter",
    # Local Server Configuration > System Service Control
    "system_service_control": "/api/server/service",

    #----Global Server Configuration
    # Global Server Configuration > Admin Privilege
    "admin_privileges": "/api/admin-privilege",
    # Global Server Configuration > Admin User
    "admin_user": "/api/admin-user",
    # Global Server Configuration > Admin User Password Policy
    "admin_user_password_policy": "/api/admin-user/password-policy",
    # Global Server Configuration > Application License
    "application_license": "/api/application-license",
    # Global Server Configuration > Attribute
    "attribute": "/api/attribute",
    # Global Server Configuration > ClearPass Portal
    "clearpass_portal": "/api/clearpass-portal",
    # Global Server Configuration > Cluster DB Sync
    "cluster_db_sync": "/api/cluster/db-sync",
    # Global Server Configuration > Cluster Wide Parameters
    "cluster_wide_parameters": "/api/cluster/parameters",
    # Global Server Configuration > Data Filter
    "data_filter": "/api/data-filter",
    # Global Server Configuration > File Backup Server
    "file_backup_server": "/api/file-backup-server",
    # Global Server Configuration > List All Privileges
    "list_all_privileges": "/api/oauth/all-privileges",
    # Global Server Configuration > Local User Password Policy
    "local_user_password_policy": "/api/local-user/password-policy",
    # Global Server Configuration > Messaging Setup
    "essaging_setup": "/api/messaging-setup",
    # Global Server Configuration > Operator Profile
    "operator_profile": "/api/operator-profile",
    # Global Server Configuration > Policy Manager Zone
    "policy_manager_zone": "/api/server/policy-manager-zones",
    # Global Server Configuration > SNMP Trap Receiver
    "snmp_trap_receiver": "/api/snmp-trap-receiver",

    #----Integrations
    #TODO later

    # ----Policy Elements
    # Policy Elements > Application Dictionary
    "application_dictionary": "/api/application-dictionary",
    # Policy Elements > Auth Method
    "auth_method": "/api/auth-method",
    # Policy Elements > Auth Source
    "auth_source": "/api/auth-source",
    # Policy Elements > Enforcement Policy
    "enforcement_policy": "/api/enforcement-policy",
    # Policy Elements > Network Device
    "network_device": "/api/network-device",
    # Policy Elements > Network Device Group
    "network_device_group": "/api/network-device-group",
    # Policy Elements > Posture Policy
    "posture_policy": "/api/posture-policy",
    # Policy Elements > RADIUS Dictionary
    "radius_dictionary": "/api/radius-dictionary",
    # Policy Elements > RADIUS Dynamic Authorization Template
    "radius_dynamic_authorization_template": "/api/radius-dynamic-authorization-template",
    # Policy Elements > RADIUS Proxy Target
    "proxy_target": "/api/proxy-target",
    # Policy Elements > Role
    "role": "/api/role",
    # Policy Elements > Role Mapping
    "role_mapping": "/api/role-mapping",
    # Policy Elements > Service
    "service": "/api/service",
    # Policy Elements > TACACS Service Dictionary
    "tacacs_service_dictionary": "/api/tacacs-service-dictionary",

    #----Endpoint Visibility
    #TODO later

    #----Session Control
    #TODO later

    #----Enforcement Profile
    #TODO later

    #----Insight
    #TODO later




    

}


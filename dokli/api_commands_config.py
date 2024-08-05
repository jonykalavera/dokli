from enum import Enum

import openapi_client


class ApiEntity(Enum):
    """API Entity."""

    admin = "admin"
    auth = "auth"
    application = "application"
    backup = "backup"
    certificates = "certificates"
    cluster = "cluster"
    compose = "compose"
    deployment = "deployment"
    destination = "destination"
    docker = "docker"
    domain = "domain"
    mariadb = "mariadb"
    mongo = "mongo"
    mounts = "mounts"
    mysql = "mysql"
    notification = "notification"
    port = "port"
    postgres = "postgres"
    project = "project"
    redirects = "redirects"
    redis = "redis"
    registry = "registry"
    security = "security"
    settings = "settings"
    sshKey = "sshKey"
    user = "user"


API_ENTITY_MAP = {
    ApiEntity.admin: openapi_client.AdminApi,
    ApiEntity.auth: openapi_client.AuthApi,
    ApiEntity.application: openapi_client.ApplicationApi,
    ApiEntity.backup: openapi_client.BackupApi,
    ApiEntity.certificates: openapi_client.CertificatesApi,
    ApiEntity.compose: openapi_client.ComposeApi,
    ApiEntity.deployment: openapi_client.DeploymentApi,
    ApiEntity.destination: openapi_client.DestinationApi,
    ApiEntity.domain: openapi_client.DomainApi,
    ApiEntity.mariadb: openapi_client.MariadbApi,
    ApiEntity.mongo: openapi_client.MongoApi,
    ApiEntity.mysql: openapi_client.MysqlApi,
    ApiEntity.notification: openapi_client.NotificationApi,
    ApiEntity.postgres: openapi_client.PostgresApi,
    ApiEntity.project: openapi_client.ProjectApi,
    ApiEntity.redirects: openapi_client.RedirectsApi,
    ApiEntity.redis: openapi_client.RedisApi,
    ApiEntity.registry: openapi_client.RegistryApi,
    ApiEntity.sshKey: openapi_client.SshKeyApi,
    ApiEntity.docker: openapi_client.DockerApi,
    ApiEntity.mounts: openapi_client.MountsApi,
    ApiEntity.port: openapi_client.PortApi,
    ApiEntity.user: openapi_client.UserApi,
    ApiEntity.cluster: openapi_client.ClusterApi,
    ApiEntity.security: openapi_client.SecurityApi,
    ApiEntity.settings: openapi_client.SettingsApi,
}


class ApiVerb(Enum):
    """API Verb."""

    verbs = "verbs"
    addManager = "addManager"
    addWorker = "addWorker"
    all = "all"
    allByCompose = "allByCompose"
    allServices = "allServices"
    assignDomainServer = "assignDomainServer"
    assignPermissions = "assignPermissions"
    byApplicationId = "byApplicationId"
    byAuthId = "byAuthId"
    byUserId = "byUserId"
    changeStatus = "changeStatus"
    checkAndUpdateImage = "checkAndUpdateImage"
    cleanAll = "cleanAll"
    cleanDockerBuilder = "cleanDockerBuilder"
    cleanDockerPrune = "cleanDockerPrune"
    cleanGithubApp = "cleanGithubApp"
    cleanMonitoring = "cleanMonitoring"
    cleanQueues = "cleanQueues"
    cleanSSHPrivateKey = "cleanSSHPrivateKey"
    cleanStoppedContainers = "cleanStoppedContainers"
    cleanUnusedImages = "cleanUnusedImages"
    cleanUnusedVolumes = "cleanUnusedVolumes"
    create = "create"
    createAdmin = "createAdmin"
    createDiscord = "createDiscord"
    createEmail = "createEmail"
    createSlack = "createSlack"
    createTelegram = "createTelegram"
    createUser = "createUser"
    createUserInvitation = "createUserInvitation"
    delete = "delete"
    deploy = "deploy"
    deployTemplate = "deployTemplate"
    disable2FA = "disable2FA"
    enableSelfHostedRegistry = "enableSelfHostedRegistry"
    generate = "generate"
    generate2FASecret = "generate2FASecret"
    generateDomain = "generateDomain"
    generateToken = "generateToken"
    generateWildcard = "generateWildcard"
    get = "get"
    getBranches = "getBranches"
    getConfig = "getConfig"
    getContainers = "getContainers"
    getContainersByAppLabel = "getContainersByAppLabel"
    getContainersByAppNameMatch = "getContainersByAppNameMatch"
    getDefaultCommand = "getDefaultCommand"
    getDokployVersion = "getDokployVersion"
    getIp = "getIp"
    getNodes = "getNodes"
    getOpenApiDocument = "getOpenApiDocument"
    getRepositories = "getRepositories"
    getTags = "getTags"
    getUserByToken = "getUserByToken"
    haveGithubConfigured = "haveGithubConfigured"
    login = "login"
    logout = "logout"
    manualBackupMariadb = "manualBackupMariadb"
    manualBackupMongo = "manualBackupMongo"
    manualBackupMySql = "manualBackupMySql"
    manualBackupPostgres = "manualBackupPostgres"
    markRunning = "markRunning"
    one = "one"
    randomizeCompose = "randomizeCompose"
    readAppMonitoring = "readAppMonitoring"
    readDirectories = "readDirectories"
    readMiddlewareTraefikConfig = "readMiddlewareTraefikConfig"
    readTraefikConfig = "readTraefikConfig"
    readTraefikFile = "readTraefikFile"
    readWebServerTraefikConfig = "readWebServerTraefikConfig"
    redeploy = "redeploy"
    refreshToken = "refreshToken"
    reload = "reload"
    reloadServer = "reloadServer"
    reloadTraefik = "reloadTraefik"
    remove = "remove"
    removeUser = "removeUser"
    removeWorker = "removeWorker"
    saveBuildType = "saveBuildType"
    saveDockerProvider = "saveDockerProvider"
    saveEnvironment = "saveEnvironment"
    saveExternalPort = "saveExternalPort"
    saveGithubProvider = "saveGithubProvider"
    saveGitProdiver = "saveGitProdiver"
    saveSSHPrivateKey = "saveSSHPrivateKey"
    start = "start"
    stop = "stop"
    templates = "templates"
    testConnection = "testConnection"
    testDiscordConnection = "testDiscordConnection"
    testEmailConnection = "testEmailConnection"
    testRegistry = "testRegistry"
    testSlackConnection = "testSlackConnection"
    testTelegramConnection = "testTelegramConnection"
    toggleDashboard = "toggleDashboard"
    update = "update"
    updateByAdmin = "updateByAdmin"
    updateDiscord = "updateDiscord"
    updateDockerCleanup = "updateDockerCleanup"
    updateEmail = "updateEmail"
    updateMiddlewareTraefikConfig = "updateMiddlewareTraefikConfig"
    updateServer = "updateServer"
    updateSlack = "updateSlack"
    updateTelegram = "updateTelegram"
    updateTraefikConfig = "updateTraefikConfig"
    updateTraefikFile = "updateTraefikFile"
    updateWebServerTraefikConfig = "updateWebServerTraefikConfig"
    verify2FASetup = "verify2FASetup"
    verifyLogin2FA = "verifyLogin2FA"
    verifyToken = "verifyToken"


API_VERB_MAP = {
    ApiEntity.admin: {
        ApiVerb.one: "admin_one_with_http_info",
        ApiVerb.createUserInvitation: "admin_create_user_invitation_with_http_info",
        ApiVerb.removeUser: "admin_remove_user_with_http_info",
        ApiVerb.getUserByToken: "admin_get_user_by_token_with_http_info",
        ApiVerb.assignPermissions: "admin_assign_permissions_with_http_info",
        ApiVerb.cleanGithubApp: "admin_clean_github_app_with_http_info",
        ApiVerb.getRepositories: "admin_get_repositories_with_http_info",
        ApiVerb.getBranches: "admin_get_branches_with_http_info",
        ApiVerb.haveGithubConfigured: "admin_have_github_configured_with_http_info",
    },
    ApiEntity.docker: {
        ApiVerb.getContainers: "docker_get_containers_with_http_info",
        ApiVerb.getConfig: "docker_get_config_with_http_info",
        ApiVerb.getContainersByAppNameMatch: "docker_get_containers_by_app_name_match_with_http_info",
        ApiVerb.getContainersByAppLabel: "docker_get_containers_by_app_label_with_http_info",
    },
    ApiEntity.auth: {
        ApiVerb.createAdmin: "auth_create_admin_with_http_info",
        ApiVerb.createUser: "auth_create_user_with_http_info",
        ApiVerb.login: "auth_login_with_http_info",
        ApiVerb.get: "auth_get_with_http_info",
        ApiVerb.logout: "auth_logout_with_http_info",
        ApiVerb.update: "auth_update_with_http_info",
        ApiVerb.generateToken: "auth_generate_token_with_http_info",
        ApiVerb.one: "auth_one_with_http_info",
        ApiVerb.updateByAdmin: "auth_update_by_admin_with_http_info",
        ApiVerb.generate2FASecret: "auth_generate2_f_a_secret_with_http_info",
        ApiVerb.verify2FASetup: "auth_verify2_f_a_setup_with_http_info",
        ApiVerb.verifyLogin2FA: "auth_verify_login2_f_a_with_http_info",
        ApiVerb.disable2FA: "auth_disable2_f_a_with_http_info",
        ApiVerb.verifyToken: "auth_verify_token_with_http_info",
    },
    ApiEntity.project: {
        ApiVerb.create: "project_create_with_http_info",
        ApiVerb.one: "project_one_with_http_info",
        ApiVerb.all: "project_all_with_http_info",
        ApiVerb.remove: "project_remove_with_http_info",
        ApiVerb.update: "project_update_with_http_info",
    },
    ApiEntity.application: {
        ApiVerb.create: "application_create_with_http_info",
        ApiVerb.one: "application_one_with_http_info",
        ApiVerb.reload: "application_reload_with_http_info",
        ApiVerb.delete: "application_delete_with_http_info",
        ApiVerb.stop: "application_stop_with_http_info",
        ApiVerb.start: "application_start_with_http_info",
        ApiVerb.redeploy: "application_redeploy_with_http_info",
        ApiVerb.saveEnvironment: "application_save_environment_with_http_info",
        ApiVerb.saveBuildType: "application_save_build_type_with_http_info",
        ApiVerb.saveGithubProvider: "application_save_github_provider_with_http_info",
        ApiVerb.saveDockerProvider: "application_save_docker_provider_with_http_info",
        ApiVerb.saveGitProdiver: "application_save_git_prodiver_with_http_info",
        ApiVerb.markRunning: "application_mark_running_with_http_info",
        ApiVerb.update: "application_update_with_http_info",
        ApiVerb.refreshToken: "application_refresh_token_with_http_info",
        ApiVerb.deploy: "application_deploy_with_http_info",
        ApiVerb.cleanQueues: "application_clean_queues_with_http_info",
        ApiVerb.readTraefikConfig: "application_read_traefik_config_with_http_info",
        ApiVerb.updateTraefikConfig: "application_update_traefik_config_with_http_info",
        ApiVerb.readAppMonitoring: "application_read_app_monitoring_with_http_info",
    },
    ApiEntity.mysql: {
        ApiVerb.create: "mysql_create_with_http_info",
        ApiVerb.one: "mysql_one_with_http_info",
        ApiVerb.start: "mysql_start_with_http_info",
        ApiVerb.stop: "mysql_stop_with_http_info",
        ApiVerb.saveExternalPort: "mysql_save_external_port_with_http_info",
        ApiVerb.deploy: "mysql_deploy_with_http_info",
        ApiVerb.changeStatus: "mysql_change_status_with_http_info",
        ApiVerb.reload: "mysql_reload_with_http_info",
        ApiVerb.remove: "mysql_remove_with_http_info",
        ApiVerb.saveEnvironment: "mysql_save_environment_with_http_info",
        ApiVerb.update: "mysql_update_with_http_info",
    },
    ApiEntity.postgres: {
        ApiVerb.create: "postgres_create_with_http_info",
        ApiVerb.one: "postgres_one_with_http_info",
        ApiVerb.start: "postgres_start_with_http_info",
        ApiVerb.stop: "postgres_stop_with_http_info",
        ApiVerb.saveExternalPort: "postgres_save_external_port_with_http_info",
        ApiVerb.deploy: "postgres_deploy_with_http_info",
        ApiVerb.changeStatus: "postgres_change_status_with_http_info",
        ApiVerb.remove: "postgres_remove_with_http_info",
        ApiVerb.saveEnvironment: "postgres_save_environment_with_http_info",
        ApiVerb.reload: "postgres_reload_with_http_info",
        ApiVerb.update: "postgres_update_with_http_info",
    },
    ApiEntity.redis: {
        ApiVerb.create: "redis_create_with_http_info",
        ApiVerb.one: "redis_one_with_http_info",
        ApiVerb.start: "redis_start_with_http_info",
        ApiVerb.reload: "redis_reload_with_http_info",
        ApiVerb.stop: "redis_stop_with_http_info",
        ApiVerb.saveExternalPort: "redis_save_external_port_with_http_info",
        ApiVerb.deploy: "redis_deploy_with_http_info",
        ApiVerb.changeStatus: "redis_change_status_with_http_info",
        ApiVerb.remove: "redis_remove_with_http_info",
        ApiVerb.saveEnvironment: "redis_save_environment_with_http_info",
        ApiVerb.update: "redis_update_with_http_info",
    },
    ApiEntity.mongo: {
        ApiVerb.create: "mongo_create_with_http_info",
        ApiVerb.one: "mongo_one_with_http_info",
        ApiVerb.start: "mongo_start_with_http_info",
        ApiVerb.stop: "mongo_stop_with_http_info",
        ApiVerb.saveExternalPort: "mongo_save_external_port_with_http_info",
        ApiVerb.deploy: "mongo_deploy_with_http_info",
        ApiVerb.changeStatus: "mongo_change_status_with_http_info",
        ApiVerb.reload: "mongo_reload_with_http_info",
        ApiVerb.remove: "mongo_remove_with_http_info",
        ApiVerb.saveEnvironment: "mongo_save_environment_with_http_info",
        ApiVerb.update: "mongo_update_with_http_info",
    },
    ApiEntity.mariadb: {
        ApiVerb.create: "mariadb_create_with_http_info",
        ApiVerb.one: "mariadb_one_with_http_info",
        ApiVerb.start: "mariadb_start_with_http_info",
        ApiVerb.stop: "mariadb_stop_with_http_info",
        ApiVerb.saveExternalPort: "mariadb_save_external_port_with_http_info",
        ApiVerb.deploy: "mariadb_deploy_with_http_info",
        ApiVerb.changeStatus: "mariadb_change_status_with_http_info",
        ApiVerb.remove: "mariadb_remove_with_http_info",
        ApiVerb.saveEnvironment: "mariadb_save_environment_with_http_info",
        ApiVerb.reload: "mariadb_reload_with_http_info",
        ApiVerb.update: "mariadb_update_with_http_info",
    },
    ApiEntity.compose: {
        ApiVerb.create: "compose_create_with_http_info",
        ApiVerb.one: "compose_one_with_http_info",
        ApiVerb.update: "compose_update_with_http_info",
        ApiVerb.delete: "compose_delete_with_http_info",
        ApiVerb.cleanQueues: "compose_clean_queues_with_http_info",
        ApiVerb.allServices: "compose_all_services_with_http_info",
        ApiVerb.randomizeCompose: "compose_randomize_compose_with_http_info",
        ApiVerb.deploy: "compose_deploy_with_http_info",
        ApiVerb.redeploy: "compose_redeploy_with_http_info",
        ApiVerb.stop: "compose_stop_with_http_info",
        ApiVerb.getDefaultCommand: "compose_get_default_command_with_http_info",
        ApiVerb.refreshToken: "compose_refresh_token_with_http_info",
        ApiVerb.deployTemplate: "compose_deploy_template_with_http_info",
        ApiVerb.templates: "compose_templates_with_http_info",
        ApiVerb.getTags: "compose_get_tags_with_http_info",
    },
    ApiEntity.user: {
        ApiVerb.all: "user_all_with_http_info",
        ApiVerb.byAuthId: "user_by_auth_id_with_http_info",
        ApiVerb.byUserId: "user_by_user_id_with_http_info",
    },
    ApiEntity.domain: {
        ApiVerb.create: "domain_create_with_http_info",
        ApiVerb.byApplicationId: "domain_by_application_id_with_http_info",
        ApiVerb.generateDomain: "domain_generate_domain_with_http_info",
        ApiVerb.generateWildcard: "domain_generate_wildcard_with_http_info",
        ApiVerb.update: "domain_update_with_http_info",
        ApiVerb.one: "domain_one_with_http_info",
        ApiVerb.delete: "domain_delete_with_http_info",
    },
    ApiEntity.destination: {
        ApiVerb.create: "destination_create_with_http_info",
        ApiVerb.testConnection: "destination_test_connection_with_http_info",
        ApiVerb.one: "destination_one_with_http_info",
        ApiVerb.all: "destination_all_with_http_info",
        ApiVerb.remove: "destination_remove_with_http_info",
        ApiVerb.update: "destination_update_with_http_info",
    },
    ApiEntity.backup: {
        ApiVerb.create: "backup_create_with_http_info",
        ApiVerb.one: "backup_one_with_http_info",
        ApiVerb.update: "backup_update_with_http_info",
        ApiVerb.remove: "backup_remove_with_http_info",
        ApiVerb.manualBackupPostgres: "backup_manual_backup_postgres_with_http_info",
        ApiVerb.manualBackupMySql: "backup_manual_backup_my_sql_with_http_info",
        ApiVerb.manualBackupMariadb: "backup_manual_backup_mariadb_with_http_info",
        ApiVerb.manualBackupMongo: "backup_manual_backup_mongo_with_http_info",
    },
    ApiEntity.deployment: {
        ApiVerb.all: "deployment_all_with_http_info",
        ApiVerb.allByCompose: "deployment_all_by_compose_with_http_info",
    },
    ApiEntity.mounts: {
        ApiVerb.create: "mounts_create_with_http_info",
        ApiVerb.remove: "mounts_remove_with_http_info",
        ApiVerb.one: "mounts_one_with_http_info",
        ApiVerb.update: "mounts_update_with_http_info",
    },
    ApiEntity.certificates: {
        ApiVerb.create: "certificates_create_with_http_info",
        ApiVerb.one: "certificates_one_with_http_info",
        ApiVerb.remove: "certificates_remove_with_http_info",
        ApiVerb.all: "certificates_all_with_http_info",
    },
    ApiEntity.settings: {
        ApiVerb.reloadServer: "settings_reload_server_with_http_info",
        ApiVerb.reloadTraefik: "settings_reload_traefik_with_http_info",
        ApiVerb.toggleDashboard: "settings_toggle_dashboard_with_http_info",
        ApiVerb.cleanUnusedImages: "settings_clean_unused_images_with_http_info",
        ApiVerb.cleanUnusedVolumes: "settings_clean_unused_volumes_with_http_info",
        ApiVerb.cleanStoppedContainers: "settings_clean_stopped_containers_with_http_info",
        ApiVerb.cleanDockerBuilder: "settings_clean_docker_builder_with_http_info",
        ApiVerb.cleanDockerPrune: "settings_clean_docker_prune_with_http_info",
        ApiVerb.cleanAll: "settings_clean_all_with_http_info",
        ApiVerb.cleanMonitoring: "settings_clean_monitoring_with_http_info",
        ApiVerb.saveSSHPrivateKey: "settings_save_s_s_h_private_key_with_http_info",
        ApiVerb.assignDomainServer: "settings_assign_domain_server_with_http_info",
        ApiVerb.cleanSSHPrivateKey: "settings_clean_s_s_h_private_key_with_http_info",
        ApiVerb.updateDockerCleanup: "settings_update_docker_cleanup_with_http_info",
        ApiVerb.readTraefikConfig: "settings_read_traefik_config_with_http_info",
        ApiVerb.updateTraefikConfig: "settings_update_traefik_config_with_http_info",
        ApiVerb.readWebServerTraefikConfig: "settings_read_web_server_traefik_config_with_http_info",
        ApiVerb.updateWebServerTraefikConfig: "settings_update_web_server_traefik_config_with_http_info",
        ApiVerb.readMiddlewareTraefikConfig: "settings_read_middleware_traefik_config_with_http_info",
        ApiVerb.updateMiddlewareTraefikConfig: "settings_update_middleware_traefik_config_with_http_info",
        ApiVerb.checkAndUpdateImage: "settings_check_and_update_image_with_http_info",
        ApiVerb.updateServer: "settings_update_server_with_http_info",
        ApiVerb.getDokployVersion: "settings_get_dokploy_version_with_http_info",
        ApiVerb.readDirectories: "settings_read_directories_with_http_info",
        ApiVerb.updateTraefikFile: "settings_update_traefik_file_with_http_info",
        ApiVerb.readTraefikFile: "settings_read_traefik_file_with_http_info",
        ApiVerb.getIp: "settings_get_ip_with_http_info",
        ApiVerb.getOpenApiDocument: "settings_get_open_api_document_with_http_info",
    },
    ApiEntity.security: {
        ApiVerb.create: "security_create_with_http_info",
        ApiVerb.one: "security_one_with_http_info",
        ApiVerb.delete: "security_delete_with_http_info",
        ApiVerb.update: "security_update_with_http_info",
    },
    ApiEntity.redirects: {
        ApiVerb.create: "redirects_create_with_http_info",
        ApiVerb.one: "redirects_one_with_http_info",
        ApiVerb.delete: "redirects_delete_with_http_info",
        ApiVerb.update: "redirects_update_with_http_info",
    },
    ApiEntity.port: {
        ApiVerb.create: "port_create_with_http_info",
        ApiVerb.one: "port_one_with_http_info",
        ApiVerb.delete: "port_delete_with_http_info",
        ApiVerb.update: "port_update_with_http_info",
    },
    ApiEntity.registry: {
        ApiVerb.create: "registry_create_with_http_info",
        ApiVerb.remove: "registry_remove_with_http_info",
        ApiVerb.update: "registry_update_with_http_info",
        ApiVerb.all: "registry_all_with_http_info",
        ApiVerb.one: "registry_one_with_http_info",
        ApiVerb.testRegistry: "registry_test_registry_with_http_info",
        ApiVerb.enableSelfHostedRegistry: "registry_enable_self_hosted_registry_with_http_info",
    },
    ApiEntity.cluster: {
        ApiVerb.getNodes: "cluster_get_nodes_with_http_info",
        ApiVerb.removeWorker: "cluster_remove_worker_with_http_info",
        ApiVerb.addWorker: "cluster_add_worker_with_http_info",
        ApiVerb.addManager: "cluster_add_manager_with_http_info",
    },
    ApiEntity.notification: {
        ApiVerb.createSlack: "notification_create_slack_with_http_info",
        ApiVerb.updateSlack: "notification_update_slack_with_http_info",
        ApiVerb.testSlackConnection: "notification_test_slack_connection_with_http_info",
        ApiVerb.createTelegram: "notification_create_telegram_with_http_info",
        ApiVerb.updateTelegram: "notification_update_telegram_with_http_info",
        ApiVerb.testTelegramConnection: "notification_test_telegram_connection_with_http_info",
        ApiVerb.createDiscord: "notification_create_discord_with_http_info",
        ApiVerb.updateDiscord: "notification_update_discord_with_http_info",
        ApiVerb.testDiscordConnection: "notification_test_discord_connection_with_http_info",
        ApiVerb.createEmail: "notification_create_email_with_http_info",
        ApiVerb.updateEmail: "notification_update_email_with_http_info",
        ApiVerb.testEmailConnection: "notification_test_email_connection_with_http_info",
        ApiVerb.remove: "notification_remove_with_http_info",
        ApiVerb.one: "notification_one_with_http_info",
        ApiVerb.all: "notification_all_with_http_info",
    },
    ApiEntity.sshKey: {
        ApiVerb.create: "ssh_key_create_with_http_info",
        ApiVerb.remove: "ssh_key_remove_with_http_info",
        ApiVerb.one: "ssh_key_one_with_http_info",
        ApiVerb.all: "ssh_key_all_with_http_info",
        ApiVerb.generate: "ssh_key_generate_with_http_info",
        ApiVerb.update: "ssh_key_update_with_http_info",
    },
}

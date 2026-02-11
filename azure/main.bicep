// ========================
// HOPE Backend - Azure Infrastructure
// Azure Bicep template for App Service deployment
// ========================

@description('Base name for all resources')
param appName string = 'hope-api'

@description('Location for all resources')
param location string = resourceGroup().location

@description('PostgreSQL admin username')
param postgresAdminUser string = 'hopeadmin'

@description('PostgreSQL admin password')
@secure()
param postgresAdminPassword string

@description('App Service SKU (B1 for student account)')
param appServiceSku string = 'B1'

// Variables
var acrName = replace('${appName}acr', '-', '')
var appServicePlanName = '${appName}-plan'
var webAppName = appName
var postgresServerName = '${appName}-db'
var postgresDbName = 'hope_production'

// ========================
// Azure Container Registry
// ========================
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// ========================
// App Service Plan (Linux)
// ========================
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  properties: {
    reserved: true // Required for Linux
  }
  sku: {
    name: appServiceSku
    tier: 'Basic'
  }
}

// ========================
// Web App (Container)
// ========================
resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${acr.properties.loginServer}/${appName}:latest'
      alwaysOn: true
      healthCheckPath: '/health'
      appSettings: [
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://${acr.properties.loginServer}'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_USERNAME'
          value: acr.listCredentials().username
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
          value: acr.listCredentials().passwords[0].value
        }
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'HOPE_ENV'
          value: 'production'
        }
        {
          name: 'HOPE_DB_HOST'
          value: '${postgresServerName}.postgres.database.azure.com'
        }
        {
          name: 'HOPE_DB_PORT'
          value: '5432'
        }
        {
          name: 'HOPE_DB_NAME'
          value: postgresDbName
        }
        {
          name: 'HOPE_DB_USER'
          value: postgresAdminUser
        }
        {
          name: 'HOPE_DB_SSL_MODE'
          value: 'require'
        }
      ]
    }
    httpsOnly: true
  }
}

// ========================
// PostgreSQL Flexible Server
// ========================
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: postgresServerName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '15'
    administratorLogin: postgresAdminUser
    administratorLoginPassword: postgresAdminPassword
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }
}

// PostgreSQL Database
resource postgresDb 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  parent: postgresServer
  name: postgresDbName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Firewall rule to allow Azure services
resource postgresFirewall 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  parent: postgresServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// ========================
// Outputs
// ========================
output acrLoginServer string = acr.properties.loginServer
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output postgresHost string = '${postgresServerName}.postgres.database.azure.com'

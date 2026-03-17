@description('Function App name')
param name string

@description('Location for the Function App')
param location string

@description('Tags for the resource')
param tags object = {}

@description('App Service Plan resource ID')
param appServicePlanId string

@description('Storage account name')
param storageAccountName string

@description('Azure Communication Services connection string')
@secure()
param communicationServicesConnectionString string

@description('Sender email address configured in ACS')
param senderEmail string

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: storageAccountName
}

resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: name
  location: location
  tags: union(tags, { 'azd-service-name': 'api' })
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: appServicePlanId
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'Python|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'COMMUNICATION_SERVICES_CONNECTION_STRING'
          value: communicationServicesConnectionString
        }
        {
          name: 'SENDER_EMAIL'
          value: senderEmail
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
      cors: {
        allowedOrigins: [
          'https://www.connectedcode.org'
          'https://connectedcode.org'
          'http://localhost:8000'
          'http://127.0.0.1:8000'
        ]
      }
    }
  }
}

output uri string = 'https://${functionApp.properties.defaultHostName}'
output name string = functionApp.name
output id string = functionApp.id

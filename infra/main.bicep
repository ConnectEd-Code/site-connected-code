targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment (used to generate resource names)')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Email address for the sender (configured in ACS)')
param senderEmail string = 'DoNotReply@connectedcode.org'

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// Storage Account (required for Azure Functions)
module storage './modules/storage.bicep' = {
  name: 'storage'
  scope: rg
  params: {
    name: '${abbrs.storageStorageAccounts}${resourceToken}'
    location: location
    tags: tags
  }
}

// Application Insights + Log Analytics
module monitoring './modules/monitoring.bicep' = {
  name: 'monitoring'
  scope: rg
  params: {
    logAnalyticsName: '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: '${abbrs.insightsComponents}${resourceToken}'
    location: location
    tags: tags
  }
}

// Azure Communication Services (for email)
module communication './modules/communication.bicep' = {
  name: 'communication'
  scope: rg
  params: {
    name: '${abbrs.communicationCommunicationServices}${resourceToken}'
    tags: tags
  }
}

// App Service Plan (Consumption / Flex Consumption for Functions)
module appServicePlan './modules/appserviceplan.bicep' = {
  name: 'appServicePlan'
  scope: rg
  params: {
    name: '${abbrs.webServerFarms}${resourceToken}'
    location: location
    tags: tags
  }
}

// Function App
module functionApp './modules/functionapp.bicep' = {
  name: 'functionApp'
  scope: rg
  params: {
    name: '${abbrs.webSitesFunctions}${resourceToken}'
    location: location
    tags: tags
    appServicePlanId: appServicePlan.outputs.id
    storageAccountName: storage.outputs.name
    applicationInsightsConnectionString: monitoring.outputs.applicationInsightsConnectionString
    communicationServicesConnectionString: communication.outputs.connectionString
    senderEmail: senderEmail
  }
}

output AZURE_FUNCTION_URL string = functionApp.outputs.uri
output AZURE_FUNCTION_NAME string = functionApp.outputs.name
output RESOURCE_GROUP_NAME string = rg.name

@description('Communication Services name')
param name string

@description('Tags for the resource')
param tags object = {}

// Azure Communication Services is a global service, location must be 'global'
resource communicationService 'Microsoft.Communication/CommunicationServices@2023-04-01' = {
  name: name
  location: 'global'
  tags: tags
  properties: {
    dataLocation: 'Australia'
  }
}

output name string = communicationService.name
output id string = communicationService.id
output connectionString string = listKeys(communicationService.id, '2023-04-01').primaryConnectionString

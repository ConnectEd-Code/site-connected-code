@description('Communication Services name')
param name string

@description('Tags for the resource')
param tags object = {}

@description('Custom email domain (e.g. connectedcode.org)')
param emailDomain string = 'connectedcode.org'

// Azure Communication Services is a global service, location must be 'global'
resource communicationService 'Microsoft.Communication/CommunicationServices@2023-04-01' = {
  name: name
  location: 'global'
  tags: tags
  properties: {
    dataLocation: 'Australia'
    linkedDomains: [
      customDomain.id
    ]
  }
}

// Email Communication Service
resource emailService 'Microsoft.Communication/emailServices@2023-04-01' = {
  name: '${name}-email'
  location: 'global'
  tags: tags
  properties: {
    dataLocation: 'Australia'
  }
}

// Custom domain for sending email
resource customDomain 'Microsoft.Communication/emailServices/domains@2023-04-01' = {
  parent: emailService
  name: emailDomain
  location: 'global'
  tags: tags
  properties: {
    domainManagement: 'CustomerManaged'
    userEngagementTracking: 'Disabled'
  }
}

output name string = communicationService.name
output id string = communicationService.id
output connectionString string = listKeys(communicationService.id, '2023-04-01').primaryConnectionString
output emailServiceName string = emailService.name
output customDomainName string = customDomain.name

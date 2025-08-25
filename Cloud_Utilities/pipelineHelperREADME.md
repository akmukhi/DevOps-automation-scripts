# Cloud Pipeline Helper

A comprehensive Python tool for managing cloud pipelines across multiple platforms including AWS, Azure, and Google Cloud Platform. This tool provides a unified interface for creating, managing, and deploying applications through cloud-native CI/CD pipelines.

## Features

### 🌐 Multi-Cloud Support
- **AWS**: CodePipeline, CodeBuild, ECS, EKS, Lambda
- **Azure**: Azure DevOps, Azure Pipelines, AKS, Container Instances
- **GCP**: Cloud Build, Cloud Run, GKE, Cloud Functions

### 🚀 Core Functionality
- **Pipeline Creation**: Create pipelines from configuration files
- **Pipeline Management**: Start, stop, and monitor pipeline executions
- **Service Deployment**: Deploy applications with comprehensive configuration
- **Status Monitoring**: Real-time pipeline status and execution tracking
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Logging**: Detailed logging for debugging and monitoring

### 🛠️ Advanced Features
- **Configuration Management**: YAML/JSON-based configuration
- **Environment Variables**: Secure environment variable management
- **Resource Tagging**: Automatic resource tagging for cost management
- **Health Checks**: Built-in health check configuration
- **Rollback Support**: Automatic rollback on deployment failures
- **Timeout Management**: Configurable timeouts for all operations

## Installation

### Prerequisites

```bash
# Install required Python packages
pip install boto3 requests pyyaml

# For AWS
pip install boto3

# For Azure
pip install azure-mgmt-resource azure-identity

# For GCP
pip install google-cloud-build google-cloud-run
```

### Environment Setup

```bash
# AWS Configuration
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"
export AWS_PIPELINE_ROLE_ARN="arn:aws:iam::123456789012:role/CodePipelineServiceRole"

# Azure Configuration
export AZURE_DEVOPS_TOKEN="your-pat-token"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"

# GCP Configuration
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

## Quick Start

### Basic Usage

```bash
# Create a pipeline
python pipelineHeler.py --config pipeline-config.yml --create

# Start pipeline execution
python pipelineHeler.py --config pipeline-config.yml --start

# Check pipeline status
python pipelineHeler.py --config pipeline-config.yml --status pipeline-123

# Deploy a service
python pipelineHeler.py --config pipeline-config.yml --deploy deployment-config.yml
```

### Command Line Options

```bash
# Create pipeline with custom timeout
python pipelineHeler.py --config pipeline-config.yml --create --timeout 7200

# Start pipeline and wait for completion
python pipelineHeler.py --config pipeline-config.yml --start --wait

# Deploy with specific configuration
python pipelineHeler.py --config pipeline-config.yml --deploy deployment-config.yml --wait
```

## Configuration

### Pipeline Configuration

Create a YAML configuration file for your pipeline:

```yaml
name: "my-app-pipeline"
platform: "aws"  # aws, azure, gcp
region: "us-west-2"
projectId: "my-project-id"
resourceGroup: "my-resource-group"  # Azure only

pipelineDefinition:
  source:
    type: "CodeCommit"
    repository: "my-app-repo"
    branch: "main"
  
  build:
    type: "CodeBuild"
    projectName: "my-app-build"
  
  deploy:
    type: "ECS"
    clusterName: "my-app-cluster"
    serviceName: "my-app-service"

environmentVariables:
  ENVIRONMENT: "production"
  DATABASE_URL: "postgresql://user:pass@host:5432/db"

tags:
  Environment: "production"
  Project: "my-app"

timeout: 3600
retryCount: 3
```

### Deployment Configuration

```yaml
serviceName: "my-web-app"
imageTag: "v1.2.3"
environment: "production"

replicas: 3
rollbackEnabled: true

resources:
  cpu: "500m"
  memory: "1Gi"

healthCheck:
  path: "/health"
  port: 8080
  initialDelaySeconds: 30

environmentVariables:
  NODE_ENV: "production"
  PORT: "8080"
```

## Platform-Specific Examples

### AWS CodePipeline

```yaml
name: "aws-web-app-pipeline"
platform: "aws"
region: "us-west-2"

pipelineDefinition:
  source:
    type: "CodeCommit"
    repository: "my-web-app"
    branch: "main"
  
  build:
    type: "CodeBuild"
    projectName: "my-web-app-build"
    buildSpec: "buildspec.yml"
  
  deploy:
    type: "ECS"
    clusterName: "my-web-app-cluster"
    serviceName: "my-web-app-service"
    imageTag: "latest"

environmentVariables:
  AWS_DEFAULT_REGION: "us-west-2"
  ECS_CLUSTER: "my-web-app-cluster"
```

### Azure DevOps Pipeline

```yaml
name: "azure-web-app-pipeline"
platform: "azure"
region: "East US"
projectId: "my-azure-org"
resourceGroup: "my-project"

pipelineDefinition:
  source:
    type: "AzureRepos"
    repository: "my-web-app"
    branch: "main"
  
  build:
    type: "AzurePipelines"
    buildDefinition: "my-web-app-build"
    buildYaml: "azure-pipelines.yml"
  
  deploy:
    type: "AKS"
    clusterName: "my-aks-cluster"
    namespace: "production"
    serviceName: "my-web-app"

environmentVariables:
  AZURE_SUBSCRIPTION_ID: "${AZURE_SUBSCRIPTION_ID}"
  AZURE_RESOURCE_GROUP: "my-resource-group"
```

### Google Cloud Build

```yaml
name: "gcp-web-app-pipeline"
platform: "gcp"
region: "us-central1"
projectId: "my-gcp-project"

pipelineDefinition:
  source:
    type: "CloudSource"
    repository: "my-web-app"
    branch: "main"
  
  build:
    type: "CloudBuild"
    buildConfig: "cloudbuild.yaml"
  
  deploy:
    type: "CloudRun"
    serviceName: "my-web-app"
    imageTag: "latest"
    region: "us-central1"

environmentVariables:
  GOOGLE_CLOUD_PROJECT: "my-gcp-project"
  GOOGLE_CLOUD_REGION: "us-central1"
```

## Usage Examples

### Example 1: Create and Deploy a Web Application

```bash
# 1. Create pipeline configuration
cat > pipeline-config.yml << EOF
name: "web-app-pipeline"
platform: "aws"
region: "us-west-2"
pipelineDefinition:
  source:
    type: "CodeCommit"
    repository: "web-app"
  build:
    type: "CodeBuild"
    projectName: "web-app-build"
  deploy:
    type: "ECS"
    clusterName: "web-app-cluster"
    serviceName: "web-app-service"
EOF

# 2. Create deployment configuration
cat > deployment-config.yml << EOF
serviceName: "web-app"
imageTag: "v1.0.0"
environment: "production"
replicas: 3
resources:
  cpu: "500m"
  memory: "1Gi"
EOF

# 3. Create and start pipeline
python pipelineHeler.py --config pipeline-config.yml --create
python pipelineHeler.py --config pipeline-config.yml --start --wait

# 4. Deploy service
python pipelineHeler.py --config pipeline-config.yml --deploy deployment-config.yml
```

### Example 2: Multi-Environment Deployment

```bash
# Production deployment
python pipelineHeler.py \
  --config production-pipeline.yml \
  --deploy production-deployment.yml \
  --wait

# Staging deployment
python pipelineHeler.py \
  --config staging-pipeline.yml \
  --deploy staging-deployment.yml \
  --wait
```

### Example 3: Programmatic Usage

```python
from pipelineHeler import CloudPipelineHelper, PipelineConfig, CloudPlatform, DeploymentConfig

# Create pipeline configuration
config = PipelineConfig(
    name="my-app-pipeline",
    platform=CloudPlatform.AWS,
    region="us-west-2",
    pipelineDefinition={
        'source': {'type': 'CodeCommit', 'repository': 'my-app'},
        'build': {'type': 'CodeBuild', 'projectName': 'my-app-build'},
        'deploy': {'type': 'ECS', 'clusterName': 'my-app-cluster'}
    }
)

# Initialize helper
helper = CloudPipelineHelper(CloudPlatform.AWS, config)

# Create pipeline
result = helper.createPipeline()
if result.success:
    print(f"Pipeline created: {result.pipelineId}")
    
    # Start pipeline
    result = helper.startPipeline(result.pipelineId)
    if result.success:
        # Wait for completion
        result = helper.waitForCompletion(result.pipelineId)
        print(f"Pipeline completed: {result.status}")

# Deploy service
deployConfig = DeploymentConfig(
    serviceName="my-app",
    imageTag="v1.0.0",
    environment="production",
    replicas=3
)

result = helper.deployService(deployConfig)
print(f"Deployment result: {result.status}")
```

## Advanced Features

### Health Checks

Configure health checks for your services:

```yaml
healthCheck:
  path: "/health"
  port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
  successThreshold: 1
```

### Resource Management

Define resource requirements:

```yaml
resources:
  cpu: "500m"  # 0.5 CPU cores
  memory: "1Gi"  # 1 GB memory
  cpuLimit: "1000m"  # 1 CPU core limit
  memoryLimit: "2Gi"  # 2 GB memory limit
```

### Environment Variables

Secure environment variable management:

```yaml
environmentVariables:
  NODE_ENV: "production"
  DATABASE_URL: "postgresql://user:pass@host:5432/db"
  API_KEY: "${API_KEY}"  # Will be replaced with actual value
```

### Secrets Management

```yaml
secrets:
  - name: "database-password"
    key: "DB_PASSWORD"
  - name: "api-key"
    key: "API_KEY"
```

## Error Handling

The tool provides comprehensive error handling:

- **Authentication Errors**: Clear messages for missing credentials
- **Configuration Errors**: Validation of configuration files
- **Network Errors**: Retry mechanisms for transient failures
- **Resource Errors**: Detailed error messages for resource conflicts
- **Timeout Handling**: Configurable timeouts with clear error messages

## Monitoring and Logging

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Pipeline Status Monitoring

```bash
# Monitor pipeline status
python pipelineHeler.py --config pipeline-config.yml --status pipeline-123

# Wait for completion with timeout
python pipelineHeler.py --config pipeline-config.yml --start --wait --timeout 7200
```

## Integration with CI/CD

### GitHub Actions Integration

```yaml
name: Deploy to Cloud
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: pip install boto3 requests pyyaml
    
    - name: Deploy to AWS
      run: |
        python Cloud_Utilities/pipelineHeler.py \
          --config pipeline-config.yml \
          --deploy deployment-config.yml \
          --wait
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### GitLab CI Integration

```yaml
deploy:
  stage: deploy
  script:
    - pip install boto3 requests pyyaml
    - python Cloud_Utilities/pipelineHeler.py --config pipeline-config.yml --deploy deployment-config.yml --wait
  environment:
    name: production
  only:
    - main
```

## Troubleshooting

### Common Issues

#### Authentication Errors
```
Error: Failed to initialize AWS client: NoCredentialsError
```
**Solution**: Set up AWS credentials using AWS CLI or environment variables.

#### Configuration Errors
```
Error: Error loading config: 'name' is required
```
**Solution**: Ensure all required fields are present in configuration file.

#### Pipeline Creation Errors
```
Error: AWS pipeline creation failed: AccessDenied
```
**Solution**: Ensure IAM role has necessary permissions for CodePipeline.

#### Deployment Errors
```
Error: Failed to deploy service: Service already exists
```
**Solution**: Use unique service names or enable force deployment.

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Set debug environment variable
export DEBUG=1

# Run with verbose output
python pipelineHeler.py --config pipeline-config.yml --create --verbose
```

## Best Practices

### Security
1. **Use IAM Roles**: Configure proper IAM roles for pipeline execution
2. **Secrets Management**: Use cloud-native secrets management services
3. **Environment Variables**: Never commit sensitive data to configuration files
4. **Access Control**: Implement least-privilege access policies

### Performance
1. **Resource Optimization**: Configure appropriate resource limits
2. **Caching**: Enable build caching for faster deployments
3. **Parallel Execution**: Use parallel stages where possible
4. **Timeout Configuration**: Set appropriate timeouts for each stage

### Reliability
1. **Health Checks**: Implement comprehensive health checks
2. **Rollback Strategy**: Enable automatic rollback on failures
3. **Monitoring**: Set up monitoring and alerting
4. **Testing**: Include testing stages in pipelines

### Cost Management
1. **Resource Tagging**: Tag all resources for cost tracking
2. **Resource Limits**: Set appropriate resource limits
3. **Cleanup**: Implement cleanup procedures for unused resources
4. **Monitoring**: Monitor resource usage and costs

## Contributing

To contribute to the cloud pipeline helper:

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all quality checks pass

## License

This tool is part of the DevOps automation scripts project.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the configuration examples
3. Check cloud provider documentation
4. Verify authentication and permissions

---

**Happy deploying! 🚀**

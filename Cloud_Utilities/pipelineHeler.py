#!/usr/bin/env python3
"""
Cloud Pipeline Helper
A comprehensive tool for managing cloud pipelines across multiple platforms.
Supports AWS, Azure, GCP with CI/CD integration and deployment automation.
"""

import os
import sys
import json
import yaml
import argparse
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import boto3
import requests
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CloudPlatform(Enum):
    """Supported cloud platforms."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

class PipelineStatus(Enum):
    """Pipeline status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PipelineConfig:
    """Configuration for a cloud pipeline."""
    name: str
    platform: CloudPlatform
    region: str
    projectId: Optional[str] = None
    resourceGroup: Optional[str] = None
    pipelineDefinition: Dict[str, Any] = None
    environmentVariables: Dict[str, str] = None
    tags: Dict[str, str] = None
    timeout: int = 3600  # 1 hour default
    retryCount: int = 3

@dataclass
class PipelineResult:
    """Result of a pipeline operation."""
    success: bool
    pipelineId: str
    status: PipelineStatus
    startTime: datetime
    endTime: Optional[datetime] = None
    duration: Optional[float] = None
    logs: List[str] = None
    artifacts: List[str] = None
    errorMessage: Optional[str] = None

@dataclass
class DeploymentConfig:
    """Configuration for deployment operations."""
    serviceName: str
    imageTag: str
    environment: str
    replicas: int = 1
    resources: Dict[str, str] = None
    healthCheck: Dict[str, Any] = None
    rollbackEnabled: bool = True

class CloudPipelineHelper:
    """Main class for cloud pipeline management."""
    
    def __init__(self, platform: CloudPlatform, config: PipelineConfig):
        self.platform = platform
        self.config = config
        self.client = self._initialize_client()
        
    def _initialize_client(self) -> Any:
        """Initialize cloud platform client."""
        if self.platform == CloudPlatform.AWS:
            return self._init_aws_client()
        elif self.platform == CloudPlatform.AZURE:
            return self._init_azure_client()
        elif self.platform == CloudPlatform.GCP:
            return self._init_gcp_client()
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")
    
    def _init_aws_client(self) -> boto3.client:
        """Initialize AWS client."""
        try:
            return boto3.client(
                'codepipeline',
                region_name=self.config.region
            )
        except Exception as e:
            logger.error(f"Failed to initialize AWS client: {e}")
            raise
    
    def _init_azure_client(self) -> Any:
        """Initialize Azure client."""
        try:
            # Azure DevOps REST API client
            return AzureDevOpsClient(
                organization=self.config.projectId,
                project=self.config.resourceGroup,
                token=os.getenv('AZURE_DEVOPS_TOKEN')
            )
        except Exception as e:
            logger.error(f"Failed to initialize Azure client: {e}")
            raise
    
    def _init_gcp_client(self) -> Any:
        """Initialize GCP client."""
        try:
            # Google Cloud Build client
            return GoogleCloudBuildClient(
                project_id=self.config.projectId,
                region=self.config.region
            )
        except Exception as e:
            logger.error(f"Failed to initialize GCP client: {e}")
            raise
    
    def createPipeline(self) -> PipelineResult:
        """Create a new pipeline."""
        logger.info(f"Creating pipeline: {self.config.name}")
        
        try:
            if self.platform == CloudPlatform.AWS:
                return self._create_aws_pipeline()
            elif self.platform == CloudPlatform.AZURE:
                return self._create_azure_pipeline()
            elif self.platform == CloudPlatform.GCP:
                return self._create_gcp_pipeline()
        except Exception as e:
            logger.error(f"Failed to create pipeline: {e}")
            return PipelineResult(
                success=False,
                pipelineId="",
                status=PipelineStatus.FAILED,
                startTime=datetime.now(),
                errorMessage=str(e)
            )
    
    def _create_aws_pipeline(self) -> PipelineResult:
        """Create AWS CodePipeline."""
        try:
            response = self.client.create_pipeline(
                pipeline={
                    'name': self.config.name,
                    'roleArn': self._get_aws_role_arn(),
                    'stages': self._convert_to_aws_stages(),
                    'artifactStore': {
                        'type': 'S3',
                        'location': f"{self.config.name}-artifacts"
                    }
                }
            )
            
            return PipelineResult(
                success=True,
                pipelineId=response['pipeline']['name'],
                status=PipelineStatus.PENDING,
                startTime=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"AWS pipeline creation failed: {e}")
    
    def _create_azure_pipeline(self) -> PipelineResult:
        """Create Azure DevOps pipeline."""
        try:
            pipeline_definition = {
                'name': self.config.name,
                'configuration': {
                    'path': '/azure-pipelines.yml',
                    'repository': {
                        'id': self.config.projectId,
                        'type': 'azureReposGit'
                    }
                }
            }
            
            response = self.client.create_pipeline(pipeline_definition)
            
            return PipelineResult(
                success=True,
                pipelineId=response['id'],
                status=PipelineStatus.PENDING,
                startTime=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"Azure pipeline creation failed: {e}")
    
    def _create_gcp_pipeline(self) -> PipelineResult:
        """Create Google Cloud Build trigger."""
        try:
            trigger_config = {
                'name': self.config.name,
                'description': f'Pipeline for {self.config.name}',
                'triggerTemplate': {
                    'projectId': self.config.projectId,
                    'repoName': 'default',
                    'branchName': 'main'
                },
                'build': {
                    'steps': self._convert_to_gcp_steps(),
                    'timeout': f"{self.config.timeout}s"
                }
            }
            
            response = self.client.create_trigger(trigger_config)
            
            return PipelineResult(
                success=True,
                pipelineId=response['id'],
                status=PipelineStatus.PENDING,
                startTime=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"GCP pipeline creation failed: {e}")
    
    def startPipeline(self, pipelineId: str) -> PipelineResult:
        """Start a pipeline execution."""
        logger.info(f"Starting pipeline: {pipelineId}")
        
        try:
            if self.platform == CloudPlatform.AWS:
                return self._start_aws_pipeline(pipelineId)
            elif self.platform == CloudPlatform.AZURE:
                return self._start_azure_pipeline(pipelineId)
            elif self.platform == CloudPlatform.GCP:
                return self._start_gcp_pipeline(pipelineId)
        except Exception as e:
            logger.error(f"Failed to start pipeline: {e}")
            return PipelineResult(
                success=False,
                pipelineId=pipelineId,
                status=PipelineStatus.FAILED,
                startTime=datetime.now(),
                errorMessage=str(e)
            )
    
    def _start_aws_pipeline(self, pipelineId: str) -> PipelineResult:
        """Start AWS CodePipeline execution."""
        try:
            response = self.client.start_pipeline_execution(
                name=pipelineId
            )
            
            return PipelineResult(
                success=True,
                pipelineId=pipelineId,
                status=PipelineStatus.RUNNING,
                startTime=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"AWS pipeline start failed: {e}")
    
    def _start_azure_pipeline(self, pipelineId: str) -> PipelineResult:
        """Start Azure DevOps pipeline run."""
        try:
            response = self.client.run_pipeline(pipelineId)
            
            return PipelineResult(
                success=True,
                pipelineId=pipelineId,
                status=PipelineStatus.RUNNING,
                startTime=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"Azure pipeline start failed: {e}")
    
    def _start_gcp_pipeline(self, pipelineId: str) -> PipelineResult:
        """Start Google Cloud Build trigger."""
        try:
            response = self.client.run_trigger(pipelineId)
            
            return PipelineResult(
                success=True,
                pipelineId=pipelineId,
                status=PipelineStatus.RUNNING,
                startTime=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"GCP pipeline start failed: {e}")
    
    def getPipelineStatus(self, pipelineId: str) -> PipelineResult:
        """Get current pipeline status."""
        try:
            if self.platform == CloudPlatform.AWS:
                return self._get_aws_pipeline_status(pipelineId)
            elif self.platform == CloudPlatform.AZURE:
                return self._get_azure_pipeline_status(pipelineId)
            elif self.platform == CloudPlatform.GCP:
                return self._get_gcp_pipeline_status(pipelineId)
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            return PipelineResult(
                success=False,
                pipelineId=pipelineId,
                status=PipelineStatus.FAILED,
                startTime=datetime.now(),
                errorMessage=str(e)
            )
    
    def _get_aws_pipeline_status(self, pipelineId: str) -> PipelineResult:
        """Get AWS CodePipeline status."""
        try:
            response = self.client.get_pipeline_state(name=pipelineId)
            
            # Get the latest execution
            executions = self.client.list_pipeline_executions(
                pipelineName=pipelineId,
                maxResults=1
            )
            
            if executions['pipelineExecutionSummaries']:
                execution = executions['pipelineExecutionSummaries'][0]
                status = self._map_aws_status(execution['status'])
                startTime = execution['startTime']
                
                return PipelineResult(
                    success=status in [PipelineStatus.SUCCESS],
                    pipelineId=pipelineId,
                    status=status,
                    startTime=startTime
                )
            
            return PipelineResult(
                success=False,
                pipelineId=pipelineId,
                status=PipelineStatus.PENDING,
                startTime=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"AWS pipeline status check failed: {e}")
    
    def _get_azure_pipeline_status(self, pipelineId: str) -> PipelineResult:
        """Get Azure DevOps pipeline status."""
        try:
            response = self.client.get_run(pipelineId)
            
            status = self._map_azure_status(response['result'])
            startTime = datetime.fromisoformat(response['startTime'].replace('Z', '+00:00'))
            
            return PipelineResult(
                success=status == PipelineStatus.SUCCESS,
                pipelineId=pipelineId,
                status=status,
                startTime=startTime
            )
            
        except Exception as e:
            raise Exception(f"Azure pipeline status check failed: {e}")
    
    def _get_gcp_pipeline_status(self, pipelineId: str) -> PipelineResult:
        """Get Google Cloud Build status."""
        try:
            response = self.client.get_build(pipelineId)
            
            status = self._map_gcp_status(response['status'])
            startTime = datetime.fromisoformat(response['startTime'].replace('Z', '+00:00'))
            
            return PipelineResult(
                success=status == PipelineStatus.SUCCESS,
                pipelineId=pipelineId,
                status=status,
                startTime=startTime
            )
            
        except Exception as e:
            raise Exception(f"GCP pipeline status check failed: {e}")
    
    def _map_aws_status(self, awsStatus: str) -> PipelineStatus:
        """Map AWS status to PipelineStatus."""
        statusMap = {
            'InProgress': PipelineStatus.RUNNING,
            'Succeeded': PipelineStatus.SUCCESS,
            'Failed': PipelineStatus.FAILED,
            'Stopped': PipelineStatus.CANCELLED
        }
        return statusMap.get(awsStatus, PipelineStatus.PENDING)
    
    def _map_azure_status(self, azureStatus: str) -> PipelineStatus:
        """Map Azure status to PipelineStatus."""
        statusMap = {
            'succeeded': PipelineStatus.SUCCESS,
            'failed': PipelineStatus.FAILED,
            'canceled': PipelineStatus.CANCELLED
        }
        return statusMap.get(azureStatus, PipelineStatus.RUNNING)
    
    def _map_gcp_status(self, gcpStatus: str) -> PipelineStatus:
        """Map GCP status to PipelineStatus."""
        statusMap = {
            'SUCCESS': PipelineStatus.SUCCESS,
            'FAILURE': PipelineStatus.FAILED,
            'TIMEOUT': PipelineStatus.FAILED,
            'CANCELLED': PipelineStatus.CANCELLED
        }
        return statusMap.get(gcpStatus, PipelineStatus.RUNNING)
    
    def waitForCompletion(self, pipelineId: str, timeout: int = 3600) -> PipelineResult:
        """Wait for pipeline completion with timeout."""
        logger.info(f"Waiting for pipeline completion: {pipelineId}")
        
        startTime = datetime.now()
        timeoutTime = startTime + timedelta(seconds=timeout)
        
        while datetime.now() < timeoutTime:
            result = self.getPipelineStatus(pipelineId)
            
            if result.status in [PipelineStatus.SUCCESS, PipelineStatus.FAILED, PipelineStatus.CANCELLED]:
                result.endTime = datetime.now()
                result.duration = (result.endTime - result.startTime).total_seconds()
                return result
            
            time.sleep(30)  # Check every 30 seconds
        
        # Timeout reached
        return PipelineResult(
            success=False,
            pipelineId=pipelineId,
            status=PipelineStatus.FAILED,
            startTime=startTime,
            endTime=datetime.now(),
            duration=timeout,
            errorMessage="Pipeline execution timed out"
        )
    
    def deployService(self, deploymentConfig: DeploymentConfig) -> PipelineResult:
        """Deploy a service using the pipeline."""
        logger.info(f"Deploying service: {deploymentConfig.serviceName}")
        
        try:
            if self.platform == CloudPlatform.AWS:
                return self._deploy_aws_service(deploymentConfig)
            elif self.platform == CloudPlatform.AZURE:
                return self._deploy_azure_service(deploymentConfig)
            elif self.platform == CloudPlatform.GCP:
                return self._deploy_gcp_service(deploymentConfig)
        except Exception as e:
            logger.error(f"Failed to deploy service: {e}")
            return PipelineResult(
                success=False,
                pipelineId="",
                status=PipelineStatus.FAILED,
                startTime=datetime.now(),
                errorMessage=str(e)
            )
    
    def _deploy_aws_service(self, config: DeploymentConfig) -> PipelineResult:
        """Deploy service to AWS ECS/EKS."""
        try:
            # Create deployment pipeline
            pipelineConfig = PipelineConfig(
                name=f"{config.serviceName}-deploy",
                platform=CloudPlatform.AWS,
                region=self.config.region,
                pipelineDefinition={
                    'source': {
                        'type': 'S3',
                        'location': f"{config.serviceName}-source"
                    },
                    'build': {
                        'type': 'CodeBuild',
                        'projectName': f"{config.serviceName}-build"
                    },
                    'deploy': {
                        'type': 'ECS',
                        'clusterName': f"{config.serviceName}-cluster",
                        'serviceName': config.serviceName,
                        'imageTag': config.imageTag
                    }
                }
            )
            
            # Create and start pipeline
            pipeline = CloudPipelineHelper(CloudPlatform.AWS, pipelineConfig)
            result = pipeline.createPipeline()
            
            if result.success:
                result = pipeline.startPipeline(result.pipelineId)
                if result.success:
                    result = pipeline.waitForCompletion(result.pipelineId)
            
            return result
            
        except Exception as e:
            raise Exception(f"AWS service deployment failed: {e}")
    
    def _deploy_azure_service(self, config: DeploymentConfig) -> PipelineResult:
        """Deploy service to Azure Container Instances/AKS."""
        try:
            # Create deployment pipeline
            pipelineConfig = PipelineConfig(
                name=f"{config.serviceName}-deploy",
                platform=CloudPlatform.AZURE,
                region=self.config.region,
                projectId=self.config.projectId,
                resourceGroup=self.config.resourceGroup,
                pipelineDefinition={
                    'source': {
                        'type': 'AzureRepos',
                        'repository': config.serviceName
                    },
                    'build': {
                        'type': 'AzurePipelines',
                        'buildDefinition': f"{config.serviceName}-build"
                    },
                    'deploy': {
                        'type': 'AKS',
                        'clusterName': f"{config.serviceName}-cluster",
                        'namespace': config.environment,
                        'imageTag': config.imageTag
                    }
                }
            )
            
            # Create and start pipeline
            pipeline = CloudPipelineHelper(CloudPlatform.AZURE, pipelineConfig)
            result = pipeline.createPipeline()
            
            if result.success:
                result = pipeline.startPipeline(result.pipelineId)
                if result.success:
                    result = pipeline.waitForCompletion(result.pipelineId)
            
            return result
            
        except Exception as e:
            raise Exception(f"Azure service deployment failed: {e}")
    
    def _deploy_gcp_service(self, config: DeploymentConfig) -> PipelineResult:
        """Deploy service to Google Cloud Run/GKE."""
        try:
            # Create deployment pipeline
            pipelineConfig = PipelineConfig(
                name=f"{config.serviceName}-deploy",
                platform=CloudPlatform.GCP,
                region=self.config.region,
                projectId=self.config.projectId,
                pipelineDefinition={
                    'source': {
                        'type': 'CloudSource',
                        'repository': config.serviceName
                    },
                    'build': {
                        'type': 'CloudBuild',
                        'buildConfig': f"{config.serviceName}-build"
                    },
                    'deploy': {
                        'type': 'CloudRun',
                        'serviceName': config.serviceName,
                        'imageTag': config.imageTag,
                        'region': self.config.region
                    }
                }
            )
            
            # Create and start pipeline
            pipeline = CloudPipelineHelper(CloudPlatform.GCP, pipelineConfig)
            result = pipeline.createPipeline()
            
            if result.success:
                result = pipeline.startPipeline(result.pipelineId)
                if result.success:
                    result = pipeline.waitForCompletion(result.pipelineId)
            
            return result
            
        except Exception as e:
            raise Exception(f"GCP service deployment failed: {e}")
    
    def _get_aws_role_arn(self) -> str:
        """Get AWS IAM role ARN for pipeline."""
        # This should be configured based on your AWS setup
        return os.getenv('AWS_PIPELINE_ROLE_ARN', 'arn:aws:iam::123456789012:role/CodePipelineServiceRole')
    
    def _convert_to_aws_stages(self) -> List[Dict]:
        """Convert pipeline definition to AWS stages."""
        stages = []
        
        if self.config.pipelineDefinition:
            if 'source' in self.config.pipelineDefinition:
                stages.append({
                    'name': 'Source',
                    'actions': [{
                        'name': 'Source',
                        'actionTypeId': {
                            'category': 'Source',
                            'owner': 'AWS',
                            'provider': 'CodeCommit',
                            'version': '1'
                        },
                        'configuration': {
                            'RepositoryName': self.config.pipelineDefinition['source'].get('repository', 'my-repo'),
                            'BranchName': 'main'
                        }
                    }]
                })
            
            if 'build' in self.config.pipelineDefinition:
                stages.append({
                    'name': 'Build',
                    'actions': [{
                        'name': 'Build',
                        'actionTypeId': {
                            'category': 'Build',
                            'owner': 'AWS',
                            'provider': 'CodeBuild',
                            'version': '1'
                        },
                        'configuration': {
                            'ProjectName': self.config.pipelineDefinition['build'].get('projectName', 'my-build')
                        }
                    }]
                })
        
        return stages
    
    def _convert_to_gcp_steps(self) -> List[Dict]:
        """Convert pipeline definition to GCP build steps."""
        steps = []
        
        if self.config.pipelineDefinition:
            if 'build' in self.config.pipelineDefinition:
                steps.append({
                    'name': 'gcr.io/cloud-builders/docker',
                    'args': ['build', '-t', 'gcr.io/$PROJECT_ID/my-app', '.']
                })
                steps.append({
                    'name': 'gcr.io/cloud-builders/docker',
                    'args': ['push', 'gcr.io/$PROJECT_ID/my-app']
                })
        
        return steps

class AzureDevOpsClient:
    """Azure DevOps REST API client."""
    
    def __init__(self, organization: str, project: str, token: str):
        self.organization = organization
        self.project = project
        self.token = token
        self.base_url = f"https://dev.azure.com/{organization}/{project}"
        self.headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }
    
    def create_pipeline(self, pipeline_definition: Dict) -> Dict:
        """Create Azure DevOps pipeline."""
        url = f"{self.base_url}/_apis/pipelines?api-version=6.0-preview.1"
        response = requests.post(url, headers=self.headers, json=pipeline_definition)
        response.raise_for_status()
        return response.json()
    
    def run_pipeline(self, pipeline_id: str) -> Dict:
        """Run Azure DevOps pipeline."""
        url = f"{self.base_url}/_apis/pipelines/{pipeline_id}/runs?api-version=6.0-preview.1"
        response = requests.post(url, headers=self.headers, json={})
        response.raise_for_status()
        return response.json()
    
    def get_run(self, run_id: str) -> Dict:
        """Get Azure DevOps pipeline run."""
        url = f"{self.base_url}/_apis/pipelines/runs/{run_id}?api-version=6.0-preview.1"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

class GoogleCloudBuildClient:
    """Google Cloud Build client."""
    
    def __init__(self, project_id: str, region: str):
        self.project_id = project_id
        self.region = region
        # In a real implementation, you would use google-cloud-build library
        # For now, we'll use REST API calls
    
    def create_trigger(self, trigger_config: Dict) -> Dict:
        """Create Google Cloud Build trigger."""
        # This would use the google-cloud-build library
        # For demonstration, return a mock response
        return {'id': f'trigger-{int(time.time())}'}
    
    def run_trigger(self, trigger_id: str) -> Dict:
        """Run Google Cloud Build trigger."""
        # This would use the google-cloud-build library
        # For demonstration, return a mock response
        return {'id': f'build-{int(time.time())}'}
    
    def get_build(self, build_id: str) -> Dict:
        """Get Google Cloud Build status."""
        # This would use the google-cloud-build library
        # For demonstration, return a mock response
        return {
            'status': 'SUCCESS',
            'startTime': datetime.now().isoformat() + 'Z'
        }

def loadPipelineConfig(configFile: str) -> PipelineConfig:
    """Load pipeline configuration from file."""
    try:
        with open(configFile, 'r') as f:
            data = yaml.safe_load(f) if configFile.endswith('.yml') else json.load(f)
        
        return PipelineConfig(
            name=data['name'],
            platform=CloudPlatform(data['platform']),
            region=data['region'],
            projectId=data.get('projectId'),
            resourceGroup=data.get('resourceGroup'),
            pipelineDefinition=data.get('pipelineDefinition', {}),
            environmentVariables=data.get('environmentVariables', {}),
            tags=data.get('tags', {}),
            timeout=data.get('timeout', 3600),
            retryCount=data.get('retryCount', 3)
        )
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Cloud Pipeline Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipelineHeler.py --config pipeline-config.yml --create
  python pipelineHeler.py --config pipeline-config.yml --start
  python pipelineHeler.py --config pipeline-config.yml --status pipeline-123
  python pipelineHeler.py --config pipeline-config.yml --deploy service-config.yml
        """
    )
    
    parser.add_argument(
        '--config',
        required=True,
        help='Path to pipeline configuration file'
    )
    
    parser.add_argument(
        '--create',
        action='store_true',
        help='Create a new pipeline'
    )
    
    parser.add_argument(
        '--start',
        action='store_true',
        help='Start pipeline execution'
    )
    
    parser.add_argument(
        '--status',
        help='Get pipeline status by ID'
    )
    
    parser.add_argument(
        '--deploy',
        help='Deploy service using configuration file'
    )
    
    parser.add_argument(
        '--wait',
        action='store_true',
        help='Wait for pipeline completion'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=3600,
        help='Timeout in seconds for pipeline operations'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = loadPipelineConfig(args.config)
        
        # Initialize pipeline helper
        helper = CloudPipelineHelper(config.platform, config)
        
        if args.create:
            result = helper.createPipeline()
            print(f"Pipeline created: {result.pipelineId}")
            
        elif args.start:
            # For demo, use a mock pipeline ID
            pipelineId = "pipeline-123"
            result = helper.startPipeline(pipelineId)
            print(f"Pipeline started: {result.pipelineId}")
            
            if args.wait:
                result = helper.waitForCompletion(pipelineId, args.timeout)
                print(f"Pipeline completed: {result.status}")
                
        elif args.status:
            result = helper.getPipelineStatus(args.status)
            print(f"Pipeline status: {result.status}")
            
        elif args.deploy:
            # Load deployment configuration
            with open(args.deploy, 'r') as f:
                deployData = yaml.safe_load(f) if args.deploy.endswith('.yml') else json.load(f)
            
            deployConfig = DeploymentConfig(
                serviceName=deployData['serviceName'],
                imageTag=deployData['imageTag'],
                environment=deployData['environment'],
                replicas=deployData.get('replicas', 1),
                resources=deployData.get('resources'),
                healthCheck=deployData.get('healthCheck'),
                rollbackEnabled=deployData.get('rollbackEnabled', True)
            )
            
            result = helper.deployService(deployConfig)
            print(f"Deployment result: {result.status}")
            
        else:
            parser.print_help()
            return 1
        
        return 0 if result.success else 1
        
    except Exception as e:
        logger.error(f"Pipeline operation failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

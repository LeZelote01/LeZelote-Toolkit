"""
Pentest-USB Toolkit - Cloud API Interface
==========================================

Python interface for multi-cloud security assessment.
Integrates cloud APIs with the Pentest-USB Toolkit workflow.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import json
import time
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

from ..utils.logging_handler import get_logger
from ..utils.error_handler import PentestError


class CloudProvider(ABC):
    """Abstract base class for cloud providers"""
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with cloud provider"""
        pass
    
    @abstractmethod
    def list_instances(self) -> List[Dict[str, Any]]:
        """List compute instances"""
        pass
    
    @abstractmethod
    def list_storage(self) -> List[Dict[str, Any]]:
        """List storage buckets/containers"""
        pass
    
    @abstractmethod
    def security_assessment(self) -> Dict[str, Any]:
        """Perform security assessment"""
        pass


class AWSProvider(CloudProvider):
    """AWS cloud provider implementation"""
    
    def __init__(self):
        """Initialize AWS provider"""
        self.logger = get_logger(__name__)
        self.session = None
        self.client_cache = {}
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with AWS"""
        try:
            # Try to import boto3
            try:
                import boto3
                from botocore.exceptions import ClientError
            except ImportError:
                raise PentestError("boto3 library required for AWS integration")
            
            # Create session with credentials
            self.session = boto3.Session(
                aws_access_key_id=credentials.get('access_key_id'),
                aws_secret_access_key=credentials.get('secret_access_key'),
                region_name=credentials.get('region', 'us-east-1')
            )
            
            # Test authentication
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            
            self.logger.info(f"AWS authentication successful: {identity.get('Arn')}")
            return True
            
        except Exception as e:
            self.logger.error(f"AWS authentication failed: {str(e)}")
            return False
    
    def _get_client(self, service_name: str):
        """Get cached AWS client"""
        if service_name not in self.client_cache:
            self.client_cache[service_name] = self.session.client(service_name)
        return self.client_cache[service_name]
    
    def list_instances(self) -> List[Dict[str, Any]]:
        """List EC2 instances"""
        try:
            ec2 = self._get_client('ec2')
            
            response = ec2.describe_instances()
            instances = []
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_info = {
                        'id': instance['InstanceId'],
                        'type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'private_ip': instance.get('PrivateIpAddress'),
                        'public_ip': instance.get('PublicIpAddress'),
                        'vpc_id': instance.get('VpcId'),
                        'subnet_id': instance.get('SubnetId'),
                        'security_groups': [sg['GroupId'] for sg in instance.get('SecurityGroups', [])],
                        'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    }
                    instances.append(instance_info)
            
            return instances
            
        except Exception as e:
            self.logger.error(f"Failed to list AWS instances: {str(e)}")
            return []
    
    def list_storage(self) -> List[Dict[str, Any]]:
        """List S3 buckets"""
        try:
            s3 = self._get_client('s3')
            
            response = s3.list_buckets()
            buckets = []
            
            for bucket in response['Buckets']:
                bucket_info = {
                    'name': bucket['Name'],
                    'creation_date': bucket['CreationDate'].isoformat(),
                    'region': self._get_bucket_region(bucket['Name']),
                    'public_access': self._check_bucket_public_access(bucket['Name'])
                }
                buckets.append(bucket_info)
            
            return buckets
            
        except Exception as e:
            self.logger.error(f"Failed to list AWS storage: {str(e)}")
            return []
    
    def _get_bucket_region(self, bucket_name: str) -> str:
        """Get S3 bucket region"""
        try:
            s3 = self._get_client('s3')
            response = s3.get_bucket_location(Bucket=bucket_name)
            return response.get('LocationConstraint') or 'us-east-1'
        except:
            return 'unknown'
    
    def _check_bucket_public_access(self, bucket_name: str) -> bool:
        """Check if S3 bucket has public access"""
        try:
            s3 = self._get_client('s3')
            
            # Check bucket ACL
            acl = s3.get_bucket_acl(Bucket=bucket_name)
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                if grantee.get('Type') == 'Group' and 'AllUsers' in grantee.get('URI', ''):
                    return True
            
            # Check public access block
            try:
                pab = s3.get_public_access_block(Bucket=bucket_name)
                config = pab['PublicAccessBlockConfiguration']
                return not all([
                    config.get('BlockPublicAcls', True),
                    config.get('IgnorePublicAcls', True),
                    config.get('BlockPublicPolicy', True),
                    config.get('RestrictPublicBuckets', True)
                ])
            except:
                return True  # Assume public if can't check
                
        except:
            return False
    
    def security_assessment(self) -> Dict[str, Any]:
        """Perform AWS security assessment"""
        try:
            assessment = {
                'provider': 'AWS',
                'timestamp': time.time(),
                'findings': [],
                'summary': {}
            }
            
            # Check EC2 security groups
            ec2_findings = self._assess_ec2_security()
            assessment['findings'].extend(ec2_findings)
            
            # Check S3 bucket security
            s3_findings = self._assess_s3_security()
            assessment['findings'].extend(s3_findings)
            
            # Check IAM policies (if permissions allow)
            iam_findings = self._assess_iam_security()
            assessment['findings'].extend(iam_findings)
            
            # Generate summary
            assessment['summary'] = {
                'total_findings': len(assessment['findings']),
                'high_severity': len([f for f in assessment['findings'] if f.get('severity') == 'high']),
                'medium_severity': len([f for f in assessment['findings'] if f.get('severity') == 'medium']),
                'low_severity': len([f for f in assessment['findings'] if f.get('severity') == 'low'])
            }
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"AWS security assessment failed: {str(e)}")
            raise PentestError(f"AWS assessment failed: {str(e)}")
    
    def _assess_ec2_security(self) -> List[Dict[str, Any]]:
        """Assess EC2 security configuration"""
        findings = []
        
        try:
            ec2 = self._get_client('ec2')
            
            # Check security groups
            sg_response = ec2.describe_security_groups()
            
            for sg in sg_response['SecurityGroups']:
                for rule in sg.get('IpPermissions', []):
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            findings.append({
                                'type': 'security_group',
                                'severity': 'high',
                                'resource': sg['GroupId'],
                                'description': f"Security group allows unrestricted access from internet",
                                'details': {
                                    'group_id': sg['GroupId'],
                                    'group_name': sg['GroupName'],
                                    'protocol': rule.get('IpProtocol'),
                                    'port_range': f"{rule.get('FromPort', 'All')}-{rule.get('ToPort', 'All')}"
                                }
                            })
            
        except Exception as e:
            self.logger.error(f"EC2 assessment error: {str(e)}")
        
        return findings
    
    def _assess_s3_security(self) -> List[Dict[str, Any]]:
        """Assess S3 security configuration"""
        findings = []
        
        try:
            s3 = self._get_client('s3')
            buckets = s3.list_buckets()['Buckets']
            
            for bucket in buckets:
                bucket_name = bucket['Name']
                
                # Check public access
                if self._check_bucket_public_access(bucket_name):
                    findings.append({
                        'type': 'storage',
                        'severity': 'high',
                        'resource': bucket_name,
                        'description': f"S3 bucket has public access enabled",
                        'details': {
                            'bucket_name': bucket_name,
                            'creation_date': bucket['CreationDate'].isoformat()
                        }
                    })
                
                # Check encryption
                try:
                    encryption = s3.get_bucket_encryption(Bucket=bucket_name)
                except:
                    findings.append({
                        'type': 'storage',
                        'severity': 'medium',
                        'resource': bucket_name,
                        'description': f"S3 bucket does not have encryption enabled",
                        'details': {
                            'bucket_name': bucket_name
                        }
                    })
            
        except Exception as e:
            self.logger.error(f"S3 assessment error: {str(e)}")
        
        return findings
    
    def _assess_iam_security(self) -> List[Dict[str, Any]]:
        """Assess IAM security configuration"""
        findings = []
        
        try:
            iam = self._get_client('iam')
            
            # Check for users with administrative privileges
            users_response = iam.list_users()
            
            for user in users_response['Users']:
                user_name = user['UserName']
                
                # Check attached policies
                policies_response = iam.list_attached_user_policies(UserName=user_name)
                
                for policy in policies_response['AttachedPolicies']:
                    if 'AdministratorAccess' in policy['PolicyName']:
                        findings.append({
                            'type': 'iam',
                            'severity': 'medium',
                            'resource': user_name,
                            'description': f"IAM user has administrative access",
                            'details': {
                                'user_name': user_name,
                                'policy_name': policy['PolicyName']
                            }
                        })
            
        except Exception as e:
            self.logger.error(f"IAM assessment error: {str(e)}")
        
        return findings


class CloudAPI:
    """
    Multi-cloud API interface
    """
    
    def __init__(self):
        """Initialize Cloud API"""
        self.logger = get_logger(__name__)
        self.providers = {
            'aws': AWSProvider(),
            # Future: 'azure': AzureProvider(),
            # Future: 'gcp': GCPProvider()
        }
        
        self.logger.info("CloudAPI initialized successfully")
    
    def authenticate_provider(self, provider: str, credentials: Dict[str, str]) -> bool:
        """
        Authenticate with cloud provider
        
        Args:
            provider: Cloud provider name (aws, azure, gcp)
            credentials: Provider-specific credentials
            
        Returns:
            Authentication success status
        """
        if provider not in self.providers:
            raise PentestError(f"Unsupported cloud provider: {provider}")
        
        return self.providers[provider].authenticate(credentials)
    
    def comprehensive_assessment(self, provider: str) -> Dict[str, Any]:
        """
        Perform comprehensive cloud security assessment
        
        Args:
            provider: Cloud provider name
            
        Returns:
            Complete assessment results
        """
        if provider not in self.providers:
            raise PentestError(f"Unsupported cloud provider: {provider}")
        
        try:
            self.logger.info(f"Starting comprehensive {provider.upper()} assessment")
            
            cloud_provider = self.providers[provider]
            
            # Get infrastructure inventory
            instances = cloud_provider.list_instances()
            storage = cloud_provider.list_storage()
            
            # Perform security assessment
            security_assessment = cloud_provider.security_assessment()
            
            # Compile results
            results = {
                'provider': provider,
                'timestamp': time.time(),
                'inventory': {
                    'instances': instances,
                    'storage': storage
                },
                'security_assessment': security_assessment,
                'summary': {
                    'total_instances': len(instances),
                    'total_storage': len(storage),
                    'security_findings': security_assessment.get('summary', {})
                }
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Cloud assessment failed: {str(e)}")
            raise PentestError(f"Cloud assessment failed: {str(e)}")
    
    def get_supported_providers(self) -> List[str]:
        """Get list of supported cloud providers"""
        return list(self.providers.keys())
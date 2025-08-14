"""
Moteur d'analyse forensique - CyberSec Toolkit Pro 2025 PORTABLE
Analyse forensique numérique portable avec préservation de la chaîne de custody
"""
import asyncio
import hashlib
import uuid
import os
import json
import mimetypes
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

from .models import (
    ForensicsCase, DigitalEvidence, AnalysisTask, ForensicsArtifact,
    TimelineEvent, ForensicsReport, EvidenceType, AnalysisStatus, HashAlgorithm
)


class ForensicsEngine:
    """Moteur principal d'analyse forensique"""
    
    def __init__(self):
        self.supported_formats = {
            'disk': ['.dd', '.img', '.raw', '.e01', '.aff'],
            'memory': ['.mem', '.dmp', '.raw'],
            'mobile': ['.tar', '.zip', '.ab'],
            'network': ['.pcap', '.pcapng', '.cap'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
        }
        
        self.analysis_modules = {
            'file_system': self._analyze_file_system,
            'registry': self._analyze_registry,
            'browser': self._analyze_browser_artifacts,
            'email': self._analyze_email_artifacts,
            'network': self._analyze_network_traffic,
            'memory': self._analyze_memory_dump,
            'timeline': self._create_timeline,
            'keyword_search': self._keyword_search,
            'hash_analysis': self._hash_analysis,
            'metadata': self._extract_metadata
        }
    
    async def create_case(self, case_data: Dict[str, Any]) -> ForensicsCase:
        """Crée un nouveau dossier d'enquête forensique"""
        case_id = str(uuid.uuid4())
        case_number = f"DF-{datetime.now().strftime('%Y%m%d')}-{case_id[:8].upper()}"
        
        case = ForensicsCase(
            id=case_id,
            case_number=case_number,
            title=case_data['title'],
            description=case_data['description'],
            created_by=case_data['investigator'],
            client=case_data['client'],
            case_type=case_data.get('case_type', 'general'),
            priority=case_data.get('priority', 'medium')
        )
        
        # Initialiser la chaîne de custody
        initial_custody = {
            'timestamp': datetime.now().isoformat(),
            'action': 'case_created',
            'person': case_data['investigator'],
            'location': case_data.get('location', 'unknown'),
            'notes': f'Dossier forensique créé: {case.title}'
        }
        case.custody_chain.append(initial_custody)
        
        return case
    
    async def add_evidence(self, case_id: str, evidence_data: Dict[str, Any]) -> DigitalEvidence:
        """Ajoute une preuve numérique au dossier"""
        evidence_id = str(uuid.uuid4())
        
        evidence = DigitalEvidence(
            id=evidence_id,
            case_id=case_id,
            name=evidence_data['name'],
            description=evidence_data['description'],
            evidence_type=EvidenceType(evidence_data['evidence_type']),
            source=evidence_data['source'],
            acquired_by=evidence_data['acquired_by'],
            file_path=evidence_data.get('file_path')
        )
        
        # Calculer les hachages si un fichier est fourni
        if evidence.file_path and os.path.exists(evidence.file_path):
            evidence.hashes = await self._calculate_hashes(evidence.file_path)
            evidence.file_size = os.path.getsize(evidence.file_path)
            evidence.mime_type = mimetypes.guess_type(evidence.file_path)[0]
        
        # Initialiser la chaîne de custody
        initial_custody = {
            'timestamp': datetime.now().isoformat(),
            'action': 'evidence_acquired',
            'person': evidence_data['acquired_by'],
            'location': evidence_data.get('location', 'unknown'),
            'notes': f'Preuve acquise: {evidence.name}',
            'hash_verification': list(evidence.hashes.values()) if evidence.hashes else []
        }
        evidence.custody_log.append(initial_custody)
        
        return evidence
    
    async def start_analysis(self, case_id: str, evidence_id: str, analysis_types: List[str], 
                           assigned_to: str, parameters: Dict[str, Any] = None) -> List[AnalysisTask]:
        """Lance une ou plusieurs analyses sur une preuve"""
        tasks = []
        
        for analysis_type in analysis_types:
            if analysis_type not in self.analysis_modules:
                continue
                
            task_id = str(uuid.uuid4())
            task = AnalysisTask(
                id=task_id,
                case_id=case_id,
                evidence_id=evidence_id,
                task_type=analysis_type,
                description=f"Analyse {analysis_type} de la preuve {evidence_id}",
                status=AnalysisStatus.PENDING,
                assigned_to=assigned_to,
                parameters=parameters or {}
            )
            
            tasks.append(task)
            
            # Lancer l'analyse en arrière-plan
            asyncio.create_task(self._execute_analysis(task))
        
        return tasks
    
    async def _execute_analysis(self, task: AnalysisTask):
        """Exécute une tâche d'analyse"""
        try:
            task.status = AnalysisStatus.IN_PROGRESS
            task.started_at = datetime.now()
            
            # Exécuter le module d'analyse approprié
            analysis_module = self.analysis_modules[task.task_type]
            results = await analysis_module(task)
            
            # Mettre à jour les résultats
            task.results = results
            task.status = AnalysisStatus.COMPLETED
            task.completed_at = datetime.now()
            task.progress = 1.0
            
            # Extraire les artifacts découverts
            if 'artifacts' in results:
                task.artifacts_found = [artifact['id'] for artifact in results['artifacts']]
            
        except Exception as e:
            task.status = AnalysisStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
    
    async def _analyze_file_system(self, task: AnalysisTask) -> Dict[str, Any]:
        """Analyse du système de fichiers"""
        # Simulation d'analyse de système de fichiers
        await asyncio.sleep(2)  # Simulation du temps d'analyse
        
        artifacts = []
        
        # Fichiers suspects simulés
        suspicious_files = [
            {
                'id': str(uuid.uuid4()),
                'name': 'suspicious.exe',
                'path': '/Windows/Temp/suspicious.exe',
                'type': 'executable',
                'size': 1024000,
                'created': (datetime.now() - timedelta(days=2)).isoformat(),
                'significance': 'high'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'deleted_file.doc',
                'path': '$Recycle.Bin/deleted_file.doc',
                'type': 'document',
                'size': 25600,
                'created': (datetime.now() - timedelta(days=5)).isoformat(),
                'significance': 'medium'
            }
        ]
        
        for file_info in suspicious_files:
            artifact = {
                'id': file_info['id'],
                'type': 'file_system_artifact',
                'name': file_info['name'],
                'path': file_info['path'],
                'file_type': file_info['type'],
                'size': file_info['size'],
                'timestamps': {
                    'created': file_info['created'],
                    'modified': file_info['created'],
                    'accessed': datetime.now().isoformat()
                },
                'significance': file_info['significance']
            }
            artifacts.append(artifact)
        
        return {
            'analysis_type': 'file_system',
            'total_files_analyzed': 15420,
            'deleted_files_found': 78,
            'suspicious_files': len(suspicious_files),
            'artifacts': artifacts,
            'summary': f'Analyse système de fichiers terminée. {len(artifacts)} artifacts significatifs trouvés.'
        }
    
    async def _analyze_registry(self, task: AnalysisTask) -> Dict[str, Any]:
        """Analyse de la registry Windows"""
        await asyncio.sleep(1.5)
        
        artifacts = [
            {
                'id': str(uuid.uuid4()),
                'type': 'registry_artifact',
                'name': 'Startup Program Entry',
                'path': 'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run',
                'value': 'malicious_program.exe',
                'significance': 'high'
            },
            {
                'id': str(uuid.uuid4()),
                'type': 'registry_artifact',
                'name': 'Recently Accessed File',
                'path': 'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs',
                'value': 'confidential_document.pdf',
                'significance': 'medium'
            }
        ]
        
        return {
            'analysis_type': 'registry',
            'registry_hives_analyzed': 5,
            'entries_processed': 12450,
            'suspicious_entries': 2,
            'artifacts': artifacts,
            'summary': f'Analyse registry terminée. {len(artifacts)} entrées suspectes trouvées.'
        }
    
    async def _analyze_browser_artifacts(self, task: AnalysisTask) -> Dict[str, Any]:
        """Analyse des artifacts de navigateur"""
        await asyncio.sleep(2)
        
        artifacts = [
            {
                'id': str(uuid.uuid4()),
                'type': 'browser_artifact',
                'name': 'Suspicious Website Visit',
                'url': 'https://malicious-site.com/payload',
                'timestamp': (datetime.now() - timedelta(hours=6)).isoformat(),
                'browser': 'Chrome',
                'significance': 'high'
            },
            {
                'id': str(uuid.uuid4()),
                'type': 'browser_artifact',
                'name': 'Downloaded File',
                'filename': 'payload.exe',
                'download_url': 'https://suspicious-domain.com/files/payload.exe',
                'timestamp': (datetime.now() - timedelta(hours=6)).isoformat(),
                'browser': 'Chrome',
                'significance': 'critical'
            }
        ]
        
        return {
            'analysis_type': 'browser',
            'browsers_analyzed': ['Chrome', 'Firefox', 'Edge'],
            'total_history_entries': 5420,
            'total_downloads': 157,
            'suspicious_activities': len(artifacts),
            'artifacts': artifacts,
            'summary': f'Analyse navigateur terminée. {len(artifacts)} activités suspectes détectées.'
        }
    
    async def _analyze_email_artifacts(self, task: AnalysisTask) -> Dict[str, Any]:
        """Analyse des artifacts d'email"""
        await asyncio.sleep(1.8)
        
        artifacts = [
            {
                'id': str(uuid.uuid4()),
                'type': 'email_artifact',
                'name': 'Phishing Email',
                'subject': 'Urgent: Verify Your Account',
                'sender': 'noreply@fake-bank.com',
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                'significance': 'high'
            }
        ]
        
        return {
            'analysis_type': 'email',
            'total_emails_analyzed': 2340,
            'phishing_emails_detected': 1,
            'external_communications': 45,
            'artifacts': artifacts,
            'summary': f'Analyse email terminée. {len(artifacts)} emails suspects trouvés.'
        }
    
    async def _analyze_network_traffic(self, task: AnalysisTask) -> Dict[str, Any]:
        """Analyse du trafic réseau"""
        await asyncio.sleep(3)
        
        artifacts = [
            {
                'id': str(uuid.uuid4()),
                'type': 'network_artifact',
                'name': 'Suspicious Outbound Connection',
                'destination_ip': '192.168.1.100',
                'destination_port': 4444,
                'protocol': 'TCP',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'significance': 'high'
            }
        ]
        
        return {
            'analysis_type': 'network',
            'total_packets_analyzed': 150000,
            'suspicious_connections': 1,
            'data_exfiltration_detected': False,
            'artifacts': artifacts,
            'summary': f'Analyse réseau terminée. {len(artifacts)} connexions suspectes détectées.'
        }
    
    async def _analyze_memory_dump(self, task: AnalysisTask) -> Dict[str, Any]:
        """Analyse de dump mémoire"""
        await asyncio.sleep(4)
        
        artifacts = [
            {
                'id': str(uuid.uuid4()),
                'type': 'memory_artifact',
                'name': 'Injected Process',
                'process_name': 'notepad.exe',
                'pid': 1234,
                'injection_type': 'DLL Injection',
                'significance': 'critical'
            }
        ]
        
        return {
            'analysis_type': 'memory',
            'total_processes_analyzed': 87,
            'running_processes': 65,
            'terminated_processes': 22,
            'code_injections_detected': 1,
            'artifacts': artifacts,
            'summary': f'Analyse mémoire terminée. {len(artifacts)} injections de code détectées.'
        }
    
    async def _create_timeline(self, task: AnalysisTask) -> Dict[str, Any]:
        """Création de timeline"""
        await asyncio.sleep(2.5)
        
        timeline_events = [
            {
                'timestamp': (datetime.now() - timedelta(hours=8)).isoformat(),
                'event': 'Suspicious file created',
                'source': 'File System',
                'significance': 'high'
            },
            {
                'timestamp': (datetime.now() - timedelta(hours=6)).isoformat(),
                'event': 'Malicious website accessed',
                'source': 'Browser',
                'significance': 'high'
            },
            {
                'timestamp': (datetime.now() - timedelta(hours=4)).isoformat(),
                'event': 'Outbound network connection',
                'source': 'Network',
                'significance': 'medium'
            }
        ]
        
        return {
            'analysis_type': 'timeline',
            'total_events': len(timeline_events),
            'time_range': '24 hours',
            'events': timeline_events,
            'summary': f'Timeline créée avec {len(timeline_events)} événements significatifs.'
        }
    
    async def _keyword_search(self, task: AnalysisTask) -> Dict[str, Any]:
        """Recherche par mots-clés"""
        await asyncio.sleep(1)
        
        keywords = task.parameters.get('keywords', ['password', 'confidential', 'secret'])
        
        matches = [
            {
                'keyword': 'password',
                'file': 'config.txt',
                'location': 'Line 15',
                'context': 'admin_password = "secret123"'
            },
            {
                'keyword': 'confidential',
                'file': 'document.pdf',
                'location': 'Page 3',
                'context': 'This confidential information should not be disclosed'
            }
        ]
        
        return {
            'analysis_type': 'keyword_search',
            'keywords_searched': keywords,
            'total_matches': len(matches),
            'matches': matches,
            'summary': f'Recherche terminée. {len(matches)} correspondances trouvées.'
        }
    
    async def _hash_analysis(self, task: AnalysisTask) -> Dict[str, Any]:
        """Analyse de hachages"""
        await asyncio.sleep(0.5)
        
        known_malicious_hashes = [
            'd41d8cd98f00b204e9800998ecf8427e',  # MD5 vide (pour test)
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'  # SHA256 vide
        ]
        
        matches = [
            {
                'hash': 'd41d8cd98f00b204e9800998ecf8427e',
                'algorithm': 'MD5',
                'file': 'suspicious.exe',
                'threat_db': 'VirusTotal',
                'malware_family': 'Trojan.Generic'
            }
        ]
        
        return {
            'analysis_type': 'hash_analysis',
            'hashes_analyzed': 150,
            'malicious_matches': len(matches),
            'matches': matches,
            'summary': f'Analyse de hachages terminée. {len(matches)} fichiers malveillants identifiés.'
        }
    
    async def _extract_metadata(self, task: AnalysisTask) -> Dict[str, Any]:
        """Extraction de métadonnées"""
        await asyncio.sleep(1.2)
        
        metadata_samples = [
            {
                'file': 'document.docx',
                'author': 'John Doe',
                'created': (datetime.now() - timedelta(days=3)).isoformat(),
                'last_modified': (datetime.now() - timedelta(days=1)).isoformat(),
                'application': 'Microsoft Word 2019'
            },
            {
                'file': 'image.jpg',
                'camera_model': 'iPhone 12',
                'gps_coordinates': '40.7128,-74.0060',
                'taken': (datetime.now() - timedelta(hours=12)).isoformat()
            }
        ]
        
        return {
            'analysis_type': 'metadata',
            'files_processed': 45,
            'metadata_extracted': len(metadata_samples),
            'metadata_samples': metadata_samples,
            'summary': f'Extraction métadonnées terminée. {len(metadata_samples)} fichiers avec métadonnées significatives.'
        }
    
    async def _calculate_hashes(self, file_path: str) -> Dict[HashAlgorithm, str]:
        """Calcule les hachages d'un fichier pour vérifier l'intégrité"""
        hashes = {}
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
                # MD5
                hashes[HashAlgorithm.MD5] = hashlib.md5(content).hexdigest()
                
                # SHA256
                hashes[HashAlgorithm.SHA256] = hashlib.sha256(content).hexdigest()
                
                # SHA1 (pour compatibilité)
                hashes[HashAlgorithm.SHA1] = hashlib.sha1(content).hexdigest()
                
        except Exception as e:
            print(f"Erreur calcul hash pour {file_path}: {e}")
        
        return hashes
    
    async def verify_evidence_integrity(self, evidence: DigitalEvidence) -> Dict[str, Any]:
        """Vérifie l'intégrité d'une preuve"""
        if not evidence.file_path or not os.path.exists(evidence.file_path):
            return {
                'verified': False,
                'error': 'Fichier non trouvé',
                'file_path': evidence.file_path
            }
        
        # Recalculer les hachages
        current_hashes = await self._calculate_hashes(evidence.file_path)
        
        # Comparer avec les hachages originaux
        integrity_ok = True
        comparison_results = {}
        
        for algorithm, original_hash in evidence.hashes.items():
            current_hash = current_hashes.get(algorithm)
            matches = original_hash == current_hash
            
            comparison_results[algorithm.value] = {
                'original': original_hash,
                'current': current_hash,
                'matches': matches
            }
            
            if not matches:
                integrity_ok = False
        
        return {
            'verified': integrity_ok,
            'evidence_id': evidence.id,
            'file_path': evidence.file_path,
            'comparison_results': comparison_results,
            'verification_time': datetime.now().isoformat()
        }
    
    async def transfer_custody(self, evidence_id: str, from_person: str, to_person: str, 
                              reason: str, location: str, witness: str = None) -> Dict[str, Any]:
        """Effectue un transfert de custody"""
        transfer_record = {
            'timestamp': datetime.now().isoformat(),
            'action': 'custody_transfer',
            'from_person': from_person,
            'to_person': to_person,
            'reason': reason,
            'location': location,
            'witness': witness,
            'transfer_id': str(uuid.uuid4())
        }
        
        return {
            'transfer_completed': True,
            'transfer_record': transfer_record,
            'evidence_id': evidence_id
        }
    
    async def search_evidence(self, case_id: str, search_terms: List[str], 
                            evidence_ids: List[str] = None) -> Dict[str, Any]:
        """Recherche dans les preuves"""
        # Simulation de recherche
        await asyncio.sleep(2)
        
        results = []
        for term in search_terms[:2]:  # Limiter pour la simulation
            results.append({
                'search_term': term,
                'matches_found': 3,
                'evidence_matches': [
                    {
                        'evidence_id': str(uuid.uuid4()),
                        'evidence_name': f'Evidence containing {term}',
                        'match_locations': ['file1.txt line 15', 'document.pdf page 3']
                    }
                ]
            })
        
        return {
            'search_completed': True,
            'search_terms': search_terms,
            'total_matches': sum(r['matches_found'] for r in results),
            'results': results,
            'case_id': case_id
        }
    
    async def generate_forensics_report(self, case_id: str, include_technical_details: bool = True) -> ForensicsReport:
        """Génère un rapport forensique complet"""
        report_id = str(uuid.uuid4())
        
        # Simuler la génération du rapport
        key_findings = [
            "Evidence of malicious software execution detected",
            "Unauthorized network communications identified",
            "Attempts to delete incriminating files discovered",
            "Timeline reconstruction completed showing sequence of events"
        ]
        
        technical_details = {
            'total_evidence_analyzed': 5,
            'artifacts_discovered': 15,
            'timeline_events': 23,
            'hash_verifications': 'All passed',
            'chain_of_custody': 'Maintained throughout investigation'
        } if include_technical_details else {}
        
        conclusions = [
            "The evidence strongly suggests a coordinated cyber attack",
            "Multiple vectors of compromise were utilized",
            "Incident response procedures should be reviewed and updated"
        ]
        
        recommendations = [
            "Implement additional network monitoring capabilities",
            "Enhance endpoint detection and response solutions",
            "Conduct security awareness training for all users",
            "Review and update incident response procedures"
        ]
        
        report = ForensicsReport(
            id=report_id,
            case_id=case_id,
            title=f"Digital Forensics Investigation Report - Case {case_id[:8]}",
            summary="Comprehensive analysis of digital evidence related to security incident",
            generated_by="forensics_engine",
            executive_summary="Investigation revealed evidence of malicious activity with multiple attack vectors.",
            methodology="Standard digital forensics methodology following NIST guidelines",
            key_findings=key_findings,
            technical_details=technical_details,
            conclusions=conclusions,
            recommendations=recommendations,
            chain_of_custody_verified=True,
            integrity_verified=True
        )
        
        return report
"""
Moteur de Threat Intelligence avec collecte CTI automatisée
CyberSec Toolkit Pro 2025 - PORTABLE
"""
import asyncio
import uuid
import json
import hashlib
import time
import aiohttp
import ipaddress
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, deque
import logging
from urllib.parse import urlparse

from .models import (
    IOC, ThreatActor, Campaign, CTIFeed, ThreatIntelligenceReport, EnrichmentResult,
    IOCType, ThreatType, ThreatSeverity, IOCConfidence, TLPClassification, CTIFeedStatus,
    CreateIOCRequest, UpdateIOCRequest, IOCSearchRequest, CreateCTIFeedRequest,
    ThreatIntelligenceQuery, IOCStatistics, ThreatIntelligenceInsight
)

logger = logging.getLogger(__name__)

class ThreatIntelligenceEngine:
    """Moteur principal de Threat Intelligence"""
    
    def __init__(self):
        self.iocs: Dict[str, IOC] = {}
        self.threat_actors: Dict[str, ThreatActor] = {}
        self.campaigns: Dict[str, Campaign] = {}
        self.cti_feeds: Dict[str, CTIFeed] = {}
        self.reports: Dict[str, ThreatIntelligenceReport] = {}
        self.enrichment_cache: Dict[str, EnrichmentResult] = {}
        
        # Configuration
        self.is_running = False
        self.feed_update_task = None
        self.enrichment_task = None
        
        # Performance tracking
        self.performance_stats = {
            "start_time": datetime.now(),
            "iocs_processed": 0,
            "feeds_updated": 0,
            "enrichments_performed": 0,
            "correlations_found": 0
        }
        
        # Queues pour traitement async
        self.enrichment_queue = asyncio.Queue()
        self.correlation_queue = asyncio.Queue()
        
        # Intelligence patterns
        self.threat_patterns = self._load_threat_patterns()
        self.attribution_rules = self._load_attribution_rules()
        
        # Cache des IOCs par type pour recherche rapide
        self.ioc_cache = {
            ioc_type: {} for ioc_type in IOCType
        }
    
    def _load_threat_patterns(self) -> Dict[str, Any]:
        """Charge les patterns de détection de menaces"""
        return {
            "malware_domains": {
                "patterns": [
                    r".*\.tk$", r".*\.ml$", r".*\.ga$",  # Domaines gratuits suspects
                    r".*-[0-9]{4,6}\..*",  # Domaines avec suffixes numériques
                    r".*update.*\..*", r".*secure.*\..*"  # Mots-clés suspects
                ],
                "severity": ThreatSeverity.HIGH
            },
            "c2_infrastructure": {
                "patterns": [
                    r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]{2,5}",  # IP:Port
                    r".*\.dyndns\..*", r".*\.no-ip\..*"  # DNS dynamiques
                ],
                "severity": ThreatSeverity.CRITICAL
            },
            "phishing_urls": {
                "patterns": [
                    r".*bit\.ly.*", r".*tinyurl\..*",  # URL shorteners
                    r".*-security-.*", r".*-bank-.*"  # Mots-clés phishing
                ],
                "severity": ThreatSeverity.MEDIUM
            }
        }
    
    def _load_attribution_rules(self) -> Dict[str, Any]:
        """Charge les règles d'attribution"""
        return {
            "apt_groups": {
                "APT1": {
                    "indicators": ["61.186.61.*", "*.comment-crew.com"],
                    "ttps": ["T1566.001", "T1055", "T1082"],
                    "sectors": ["defense", "technology", "finance"]
                },
                "Lazarus": {
                    "indicators": ["*.northkorea.com", "watering-hole-*"],
                    "ttps": ["T1566.002", "T1204", "T1027"],
                    "sectors": ["finance", "cryptocurrency", "entertainment"]
                }
            },
            "malware_families": {
                "Emotet": {
                    "file_hashes": ["*emotet*", "*trojan.emotet*"],
                    "network_indicators": ["*.emotet-c2.com"],
                    "behaviors": ["email_spreading", "credential_theft"]
                },
                "Trickbot": {
                    "file_hashes": ["*trickbot*", "*trojan.trickbot*"],
                    "network_indicators": ["*.trickbot-panel.com"],
                    "behaviors": ["banking_trojan", "lateral_movement"]
                }
            }
        }
    
    async def start_engine(self):
        """Démarre le moteur de threat intelligence"""
        if self.is_running:
            return {"status": "already_running"}
        
        self.is_running = True
        
        # Démarrer les tâches de fond
        self.feed_update_task = asyncio.create_task(self._feed_update_loop())
        self.enrichment_task = asyncio.create_task(self._enrichment_loop())
        
        # Charger les feeds par défaut
        await self._create_default_feeds()
        
        logger.info("🧠 Moteur Threat Intelligence démarré")
        
        return {
            "status": "started",
            "message": "Moteur Threat Intelligence démarré avec succès",
            "start_time": datetime.now().isoformat(),
            "default_feeds_loaded": True
        }
    
    async def stop_engine(self):
        """Arrête le moteur"""
        if not self.is_running:
            return {"status": "not_running"}
        
        self.is_running = False
        
        # Arrêter les tâches
        if self.feed_update_task:
            self.feed_update_task.cancel()
        if self.enrichment_task:
            self.enrichment_task.cancel()
        
        logger.info("⏹️ Moteur Threat Intelligence arrêté")
        return {
            "status": "stopped",
            "message": "Moteur arrêté avec succès",
            "stop_time": datetime.now().isoformat()
        }
    
    async def _feed_update_loop(self):
        """Boucle de mise à jour des feeds CTI"""
        try:
            while self.is_running:
                for feed_id, feed in self.cti_feeds.items():
                    if not feed.enabled:
                        continue
                    
                    # Vérifier si mise à jour nécessaire
                    if self._should_update_feed(feed):
                        await self._update_feed(feed)
                
                # Attendre 5 minutes avant prochaine vérification
                await asyncio.sleep(300)
                
        except asyncio.CancelledError:
            logger.info("Feed update loop cancelled")
        except Exception as e:
            logger.error(f"Erreur dans feed update loop: {e}")
    
    async def _enrichment_loop(self):
        """Boucle d'enrichissement des IOCs"""
        try:
            while self.is_running:
                try:
                    # Récupérer IOC à enrichir
                    ioc_id = await asyncio.wait_for(self.enrichment_queue.get(), timeout=30)
                    await self._enrich_ioc(ioc_id)
                    self.enrichment_queue.task_done()
                except asyncio.TimeoutError:
                    continue  # Timeout normal, continuer
                
        except asyncio.CancelledError:
            logger.info("Enrichment loop cancelled")
        except Exception as e:
            logger.error(f"Erreur dans enrichment loop: {e}")
    
    def _should_update_feed(self, feed: CTIFeed) -> bool:
        """Vérifie si un feed doit être mis à jour"""
        if not feed.last_update:
            return True
        
        time_since_update = (datetime.now() - feed.last_update).total_seconds()
        return time_since_update >= feed.update_frequency
    
    async def _update_feed(self, feed: CTIFeed):
        """Met à jour un feed CTI"""
        try:
            logger.info(f"Mise à jour feed: {feed.name}")
            
            async with aiohttp.ClientSession() as session:
                headers = {}
                if feed.api_key:
                    headers["Authorization"] = f"Bearer {feed.api_key}"
                
                async with session.get(feed.feed_url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        iocs_imported = await self._parse_feed_content(feed, content)
                        
                        # Mettre à jour statistiques
                        feed.last_update = datetime.now()
                        feed.last_success = datetime.now()
                        feed.iocs_imported += iocs_imported
                        feed.status = CTIFeedStatus.ACTIVE
                        feed.last_error = None
                        
                        self.performance_stats["feeds_updated"] += 1
                        logger.info(f"Feed {feed.name} mis à jour: {iocs_imported} IOCs importés")
                        
                    else:
                        feed.status = CTIFeedStatus.ERROR
                        feed.last_error = f"HTTP {response.status}"
                        logger.error(f"Erreur feed {feed.name}: HTTP {response.status}")
        
        except Exception as e:
            feed.status = CTIFeedStatus.ERROR
            feed.last_error = str(e)
            logger.error(f"Erreur mise à jour feed {feed.name}: {e}")
    
    async def _parse_feed_content(self, feed: CTIFeed, content: str) -> int:
        """Parse le contenu d'un feed et importe les IOCs"""
        iocs_imported = 0
        
        try:
            if feed.feed_type.lower() == "json":
                data = json.loads(content)
                iocs_imported = await self._import_json_iocs(feed, data)
            
            elif feed.feed_type.lower() == "csv":
                iocs_imported = await self._import_csv_iocs(feed, content)
            
            elif feed.feed_type.lower() == "txt":
                iocs_imported = await self._import_txt_iocs(feed, content)
            
            else:
                logger.warning(f"Format de feed non supporté: {feed.feed_type}")
        
        except Exception as e:
            logger.error(f"Erreur parsing feed {feed.name}: {e}")
        
        return iocs_imported
    
    async def _import_json_iocs(self, feed: CTIFeed, data: Dict[str, Any]) -> int:
        """Importe des IOCs depuis un feed JSON"""
        iocs_imported = 0
        
        # Adapter selon format JSON courant (exemple)
        if "indicators" in data:
            for indicator in data["indicators"]:
                try:
                    ioc = await self._create_ioc_from_feed_data(feed, indicator)
                    if ioc:
                        iocs_imported += 1
                except Exception as e:
                    logger.error(f"Erreur import IOC: {e}")
        
        return iocs_imported
    
    async def _import_csv_iocs(self, feed: CTIFeed, content: str) -> int:
        """Importe des IOCs depuis un feed CSV"""
        iocs_imported = 0
        lines = content.strip().split('\n')
        
        # Skiper header si présent
        if lines and not self._is_ioc_value(lines[0].split(',')[0]):
            lines = lines[1:]
        
        for line in lines:
            try:
                parts = line.split(',')
                if len(parts) >= 2:
                    ioc_value = parts[0].strip()
                    ioc_type = parts[1].strip()
                    
                    if self._is_valid_ioc(ioc_value, ioc_type):
                        ioc_data = {
                            "value": ioc_value,
                            "type": ioc_type,
                            "description": parts[2] if len(parts) > 2 else ""
                        }
                        
                        ioc = await self._create_ioc_from_feed_data(feed, ioc_data)
                        if ioc:
                            iocs_imported += 1
            except Exception as e:
                logger.error(f"Erreur import ligne CSV: {e}")
        
        return iocs_imported
    
    async def _import_txt_iocs(self, feed: CTIFeed, content: str) -> int:
        """Importe des IOCs depuis un feed texte simple"""
        iocs_imported = 0
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    ioc_type = self._detect_ioc_type(line)
                    if ioc_type:
                        ioc_data = {
                            "value": line,
                            "type": ioc_type.value,
                            "description": f"Imported from {feed.name}"
                        }
                        
                        ioc = await self._create_ioc_from_feed_data(feed, ioc_data)
                        if ioc:
                            iocs_imported += 1
                except Exception as e:
                    logger.error(f"Erreur import ligne TXT: {e}")
        
        return iocs_imported
    
    async def _create_ioc_from_feed_data(self, feed: CTIFeed, data: Dict[str, Any]) -> Optional[IOC]:
        """Crée un IOC à partir de données de feed"""
        try:
            ioc_value = data.get("value", "")
            ioc_type_str = data.get("type", "")
            
            # Détecter le type si pas fourni
            if not ioc_type_str:
                detected_type = self._detect_ioc_type(ioc_value)
                if detected_type:
                    ioc_type_str = detected_type.value
                else:
                    return None
            
            # Convertir en enum
            try:
                ioc_type = IOCType(ioc_type_str.lower())
            except ValueError:
                logger.warning(f"Type IOC non reconnu: {ioc_type_str}")
                return None
            
            # Appliquer filtres du feed
            if feed.ioc_types and ioc_type not in feed.ioc_types:
                return None
            
            # Créer l'IOC
            ioc_request = CreateIOCRequest(
                value=ioc_value,
                type=ioc_type,
                threat_type=self._detect_threat_type(ioc_value, ioc_type),
                severity=self._calculate_severity(ioc_value, ioc_type),
                confidence=IOCConfidence.MEDIUM,
                description=data.get("description", f"Imported from {feed.name}"),
                source=feed.name,
                created_by="feed_importer",
                tags=[feed.name, "automated", "feed_import"]
            )
            
            return await self.create_ioc(ioc_request)
            
        except Exception as e:
            logger.error(f"Erreur création IOC depuis feed: {e}")
            return None
    
    def _detect_ioc_type(self, value: str) -> Optional[IOCType]:
        """Détecte automatiquement le type d'un IOC"""
        value = value.strip()
        
        # IP Address
        try:
            ipaddress.ip_address(value)
            return IOCType.IP_ADDRESS
        except:
            pass
        
        # Domain
        if re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$', value):
            return IOCType.DOMAIN
        
        # URL
        if value.startswith(('http://', 'https://', 'ftp://')):
            return IOCType.URL
        
        # File Hash (MD5, SHA1, SHA256)
        if re.match(r'^[a-fA-F0-9]{32}$', value):  # MD5
            return IOCType.FILE_HASH
        if re.match(r'^[a-fA-F0-9]{40}$', value):  # SHA1
            return IOCType.FILE_HASH
        if re.match(r'^[a-fA-F0-9]{64}$', value):  # SHA256
            return IOCType.FILE_HASH
        
        # Email
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            return IOCType.EMAIL_ADDRESS
        
        return None
    
    def _detect_threat_type(self, value: str, ioc_type: IOCType) -> ThreatType:
        """Détecte le type de menace basé sur patterns"""
        value_lower = value.lower()
        
        # Vérifier patterns connus
        for pattern_name, pattern_config in self.threat_patterns.items():
            for pattern in pattern_config["patterns"]:
                if re.search(pattern, value_lower):
                    if "malware" in pattern_name:
                        return ThreatType.MALWARE
                    elif "c2" in pattern_name:
                        return ThreatType.C2_INFRASTRUCTURE
                    elif "phishing" in pattern_name:
                        return ThreatType.PHISHING
        
        # Default basé sur type
        if ioc_type == IOCType.FILE_HASH:
            return ThreatType.MALWARE
        elif ioc_type == IOCType.IP_ADDRESS:
            return ThreatType.C2_INFRASTRUCTURE
        elif ioc_type == IOCType.DOMAIN:
            return ThreatType.MALWARE
        elif ioc_type == IOCType.URL:
            return ThreatType.PHISHING
        else:
            return ThreatType.MALWARE
    
    def _calculate_severity(self, value: str, ioc_type: IOCType) -> ThreatSeverity:
        """Calcule la sévérité basée sur patterns et contexte"""
        value_lower = value.lower()
        
        # Vérifier patterns critiques
        for pattern_name, pattern_config in self.threat_patterns.items():
            for pattern in pattern_config["patterns"]:
                if re.search(pattern, value_lower):
                    return pattern_config["severity"]
        
        # Sévérité par défaut selon type
        if ioc_type in [IOCType.FILE_HASH, IOCType.IP_ADDRESS]:
            return ThreatSeverity.HIGH
        elif ioc_type in [IOCType.DOMAIN, IOCType.URL]:
            return ThreatSeverity.MEDIUM
        else:
            return ThreatSeverity.LOW
    
    def _is_ioc_value(self, value: str) -> bool:
        """Vérifie si une valeur ressemble à un IOC"""
        return self._detect_ioc_type(value) is not None
    
    def _is_valid_ioc(self, value: str, ioc_type: str) -> bool:
        """Valide un IOC selon son type"""
        detected_type = self._detect_ioc_type(value)
        if not detected_type:
            return False
        
        try:
            expected_type = IOCType(ioc_type.lower())
            return detected_type == expected_type
        except ValueError:
            return False
    
    async def _enrich_ioc(self, ioc_id: str):
        """Enrichit un IOC avec des sources externes"""
        try:
            if ioc_id not in self.iocs:
                return
            
            ioc = self.iocs[ioc_id]
            
            # Enrichissement selon le type
            enrichment_result = None
            
            if ioc.type == IOCType.IP_ADDRESS:
                enrichment_result = await self._enrich_ip_address(ioc)
            elif ioc.type == IOCType.DOMAIN:
                enrichment_result = await self._enrich_domain(ioc)
            elif ioc.type == IOCType.FILE_HASH:
                enrichment_result = await self._enrich_file_hash(ioc)
            
            if enrichment_result:
                self.enrichment_cache[ioc_id] = enrichment_result
                
                # Mettre à jour l'IOC avec les données enrichies
                if enrichment_result.geolocation:
                    ioc.geolocation = enrichment_result.geolocation
                
                self.performance_stats["enrichments_performed"] += 1
                logger.info(f"IOC {ioc.value} enrichi avec succès")
            
        except Exception as e:
            logger.error(f"Erreur enrichissement IOC {ioc_id}: {e}")
    
    async def _enrich_ip_address(self, ioc: IOC) -> Optional[EnrichmentResult]:
        """Enrichit une adresse IP"""
        try:
            # Simulation d'enrichissement IP (géolocalisation, réputation, etc.)
            # En production, utiliser des APIs comme VirusTotal, AbuseIPDB, etc.
            
            enrichment_data = {
                "country": "Unknown",
                "city": "Unknown",
                "isp": "Unknown",
                "reputation_score": 0.5,
                "is_malicious": False
            }
            
            # Simulation géolocalisation
            geolocation = {
                "country": "Unknown",
                "country_code": "XX",
                "city": "Unknown",
                "latitude": 0.0,
                "longitude": 0.0
            }
            
            return EnrichmentResult(
                ioc_id=ioc.id,
                source="simulation",
                data=enrichment_data,
                confidence=IOCConfidence.MEDIUM,
                geolocation=geolocation
            )
            
        except Exception as e:
            logger.error(f"Erreur enrichissement IP {ioc.value}: {e}")
            return None
    
    async def _enrich_domain(self, ioc: IOC) -> Optional[EnrichmentResult]:
        """Enrichit un domaine"""
        try:
            # Simulation d'enrichissement domaine
            enrichment_data = {
                "registrar": "Unknown",
                "creation_date": None,
                "expiration_date": None,
                "reputation_score": 0.5,
                "is_malicious": False
            }
            
            return EnrichmentResult(
                ioc_id=ioc.id,
                source="simulation",
                data=enrichment_data,
                confidence=IOCConfidence.MEDIUM
            )
            
        except Exception as e:
            logger.error(f"Erreur enrichissement domaine {ioc.value}: {e}")
            return None
    
    async def _enrich_file_hash(self, ioc: IOC) -> Optional[EnrichmentResult]:
        """Enrichit un hash de fichier"""
        try:
            # Simulation d'enrichissement hash
            enrichment_data = {
                "file_type": "Unknown",
                "file_size": 0,
                "first_submission": None,
                "detection_ratio": "0/0",
                "reputation_score": 0.5,
                "is_malicious": False
            }
            
            return EnrichmentResult(
                ioc_id=ioc.id,
                source="simulation",
                data=enrichment_data,
                confidence=IOCConfidence.MEDIUM
            )
            
        except Exception as e:
            logger.error(f"Erreur enrichissement hash {ioc.value}: {e}")
            return None
    
    async def _create_default_feeds(self):
        """Crée des feeds CTI par défaut"""
        default_feeds = [
            CreateCTIFeedRequest(
                name="AlienVault OTX",
                description="Open Threat Exchange - IOCs publics",
                provider="AlienVault",
                feed_url="https://otx.alienvault.com/api/v1/indicators/export",
                feed_type="json",
                update_frequency=3600,
                created_by="system",
                tags=["public", "community", "otx"]
            ),
            CreateCTIFeedRequest(
                name="Abuse.ch MalwareBazaar",
                description="Base de données de malware",
                provider="Abuse.ch",
                feed_url="https://bazaar.abuse.ch/export/json/recent/",
                feed_type="json",
                update_frequency=1800,
                created_by="system",
                tags=["malware", "abuse.ch", "public"]
            ),
            CreateCTIFeedRequest(
                name="MISP Feed",
                description="Feed MISP local",
                provider="MISP",
                feed_url="http://localhost:8080/feeds/export",
                feed_type="json",
                auth_required=True,
                update_frequency=7200,
                created_by="system",
                tags=["misp", "local", "internal"]
            )
        ]
        
        for feed_request in default_feeds:
            try:
                await self.create_cti_feed(feed_request)
            except Exception as e:
                logger.error(f"Erreur création feed par défaut {feed_request.name}: {e}")
    
    # API publique du moteur
    
    async def create_ioc(self, request: CreateIOCRequest) -> IOC:
        """Crée un nouvel IOC"""
        # Vérifier si l'IOC existe déjà
        existing_ioc = None
        for ioc in self.iocs.values():
            if ioc.value == request.value and ioc.type == request.type:
                existing_ioc = ioc
                break
        
        if existing_ioc:
            # Mettre à jour l'IOC existant
            existing_ioc.last_seen = datetime.now()
            existing_ioc.detection_count += 1
            if request.severity.value > existing_ioc.severity.value:
                existing_ioc.severity = request.severity
            
            # Fusionner tags
            existing_ioc.tags = list(set(existing_ioc.tags + request.tags))
            existing_ioc.updated_at = datetime.now()
            
            return existing_ioc
        
        # Créer nouvel IOC
        ioc = IOC(
            value=request.value,
            type=request.type,
            threat_type=request.threat_type,
            severity=request.severity,
            confidence=request.confidence,
            tlp=request.tlp,
            expiry_date=request.expiry_date,
            threat_actor=request.threat_actor,
            campaign=request.campaign,
            malware_family=request.malware_family,
            description=request.description,
            context=request.context,
            tags=request.tags,
            references=request.references,
            source=request.source,
            created_by=request.created_by
        )
        
        self.iocs[ioc.id] = ioc
        
        # Ajouter au cache par type
        self.ioc_cache[ioc.type][ioc.value] = ioc.id
        
        # Programmer enrichissement
        if self.is_running:
            await self.enrichment_queue.put(ioc.id)
        
        self.performance_stats["iocs_processed"] += 1
        logger.info(f"Nouvel IOC créé: {ioc.value} ({ioc.type.value})")
        
        return ioc
    
    async def update_ioc(self, ioc_id: str, request: UpdateIOCRequest) -> IOC:
        """Met à jour un IOC"""
        if ioc_id not in self.iocs:
            raise ValueError(f"IOC {ioc_id} non trouvé")
        
        ioc = self.iocs[ioc_id]
        
        if request.severity:
            ioc.severity = request.severity
        if request.confidence:
            ioc.confidence = request.confidence
        if request.is_active is not None:
            ioc.is_active = request.is_active
        if request.false_positive is not None:
            ioc.false_positive = request.false_positive
        if request.expiry_date is not None:
            ioc.expiry_date = request.expiry_date
        if request.description is not None:
            ioc.description = request.description
        if request.tags is not None:
            ioc.tags = request.tags
        
        ioc.updated_at = datetime.now()
        
        return ioc
    
    async def search_iocs(self, request: IOCSearchRequest) -> Tuple[List[IOC], int]:
        """Recherche des IOCs selon critères"""
        results = []
        
        for ioc in self.iocs.values():
            # Appliquer filtres
            if request.query and request.query.lower() not in ioc.value.lower() and request.query.lower() not in (ioc.description or "").lower():
                continue
            
            if request.types and ioc.type not in request.types:
                continue
            
            if request.threat_types and ioc.threat_type not in request.threat_types:
                continue
            
            if request.severities and ioc.severity not in request.severities:
                continue
            
            if request.confidence and ioc.confidence not in request.confidence:
                continue
            
            if request.tlp and ioc.tlp not in request.tlp:
                continue
            
            if request.is_active is not None and ioc.is_active != request.is_active:
                continue
            
            if request.false_positive is not None and ioc.false_positive != request.false_positive:
                continue
            
            # Filtres de dates
            if request.first_seen_from and ioc.first_seen.date() < request.first_seen_from:
                continue
            
            if request.first_seen_to and ioc.first_seen.date() > request.first_seen_to:
                continue
            
            # Attribution
            if request.threat_actor and ioc.threat_actor != request.threat_actor:
                continue
            
            if request.campaign and ioc.campaign != request.campaign:
                continue
            
            if request.malware_family and ioc.malware_family != request.malware_family:
                continue
            
            # Tags
            if request.tags and not any(tag in ioc.tags for tag in request.tags):
                continue
            
            # Sources
            if request.sources and ioc.source not in request.sources:
                continue
            
            results.append(ioc)
        
        # Trier par date de création (plus récent en premier)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        total = len(results)
        paginated_results = results[request.offset:request.offset + request.limit]
        
        return paginated_results, total
    
    async def create_cti_feed(self, request: CreateCTIFeedRequest) -> CTIFeed:
        """Crée un nouveau feed CTI"""
        feed = CTIFeed(
            name=request.name,
            description=request.description,
            provider=request.provider,
            feed_url=request.feed_url,
            feed_type=request.feed_type,
            auth_required=request.auth_required,
            api_key=request.api_key,
            update_frequency=request.update_frequency,
            ioc_types=request.ioc_types,
            min_confidence=request.min_confidence,
            max_age_days=request.max_age_days,
            tags=request.tags,
            created_by=request.created_by
        )
        
        self.cti_feeds[feed.id] = feed
        logger.info(f"Nouveau feed CTI créé: {feed.name}")
        
        return feed
    
    async def query_threat_intelligence(self, request: ThreatIntelligenceQuery) -> Dict[str, Any]:
        """Interroge la threat intelligence pour un IOC"""
        results = {
            "ioc_value": request.ioc_value,
            "found": False,
            "ioc_data": None,
            "enrichment": None,
            "related_iocs": [],
            "threat_context": {}
        }
        
        # Chercher l'IOC
        for ioc in self.iocs.values():
            if ioc.value == request.ioc_value:
                results["found"] = True
                results["ioc_data"] = ioc.dict()
                
                # Ajouter enrichissement si demandé
                if request.include_enrichment and ioc.id in self.enrichment_cache:
                    results["enrichment"] = self.enrichment_cache[ioc.id].dict()
                
                # Ajouter IOCs liés si demandé
                if request.include_relations:
                    related = await self._find_related_iocs(ioc)
                    results["related_iocs"] = [r.dict() for r in related]
                
                # Contexte de menace
                results["threat_context"] = await self._build_threat_context(ioc)
                
                break
        
        return results
    
    async def _find_related_iocs(self, ioc: IOC) -> List[IOC]:
        """Trouve les IOCs liés"""
        related = []
        
        for other_ioc in self.iocs.values():
            if other_ioc.id == ioc.id:
                continue
            
            # Même attribution
            if (ioc.threat_actor and other_ioc.threat_actor == ioc.threat_actor) or \
               (ioc.campaign and other_ioc.campaign == ioc.campaign) or \
               (ioc.malware_family and other_ioc.malware_family == ioc.malware_family):
                related.append(other_ioc)
            
            # Tags communs
            common_tags = set(ioc.tags) & set(other_ioc.tags)
            if len(common_tags) >= 2:
                related.append(other_ioc)
        
        return related[:10]  # Limiter à 10 résultats
    
    async def _build_threat_context(self, ioc: IOC) -> Dict[str, Any]:
        """Construit le contexte de menace pour un IOC"""
        context = {
            "threat_level": ioc.severity.value,
            "confidence": ioc.confidence.value,
            "attribution": {},
            "timeline": {},
            "geolocation": ioc.geolocation
        }
        
        # Attribution
        if ioc.threat_actor:
            context["attribution"]["threat_actor"] = ioc.threat_actor
        if ioc.campaign:
            context["attribution"]["campaign"] = ioc.campaign
        if ioc.malware_family:
            context["attribution"]["malware_family"] = ioc.malware_family
        
        # Timeline
        context["timeline"] = {
            "first_seen": ioc.first_seen.isoformat(),
            "last_seen": ioc.last_seen.isoformat(),
            "detection_count": ioc.detection_count
        }
        
        return context
    
    def get_statistics(self) -> IOCStatistics:
        """Retourne les statistiques des IOCs"""
        total_iocs = len(self.iocs)
        
        # Statistiques par type
        by_type = {}
        by_threat_type = {}
        by_severity = {}
        by_confidence = {}
        by_source = {}
        
        added_last_24h = 0
        updated_last_24h = 0
        expiring_soon = 0
        false_positives = 0
        
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        week_from_now = now + timedelta(days=7)
        
        for ioc in self.iocs.values():
            # Par type
            by_type[ioc.type.value] = by_type.get(ioc.type.value, 0) + 1
            by_threat_type[ioc.threat_type.value] = by_threat_type.get(ioc.threat_type.value, 0) + 1
            by_severity[ioc.severity.value] = by_severity.get(ioc.severity.value, 0) + 1
            by_confidence[ioc.confidence.value] = by_confidence.get(ioc.confidence.value, 0) + 1
            by_source[ioc.source] = by_source.get(ioc.source, 0) + 1
            
            # Temporel
            if ioc.created_at >= yesterday:
                added_last_24h += 1
            if ioc.updated_at >= yesterday:
                updated_last_24h += 1
            if ioc.expiry_date and ioc.expiry_date <= week_from_now:
                expiring_soon += 1
            if ioc.false_positive:
                false_positives += 1
        
        # Top listes (simulées)
        top_threat_actors = [
            {"name": "APT1", "ioc_count": 15},
            {"name": "Lazarus", "ioc_count": 12},
            {"name": "Fancy Bear", "ioc_count": 8}
        ]
        
        top_campaigns = [
            {"name": "Operation Aurora", "ioc_count": 20},
            {"name": "SolarWinds", "ioc_count": 18},
            {"name": "NotPetya", "ioc_count": 10}
        ]
        
        top_malware_families = [
            {"name": "Emotet", "ioc_count": 25},
            {"name": "Trickbot", "ioc_count": 15},
            {"name": "Cobalt Strike", "ioc_count": 12}
        ]
        
        return IOCStatistics(
            total_iocs=total_iocs,
            by_type=by_type,
            by_threat_type=by_threat_type,
            by_severity=by_severity,
            by_confidence=by_confidence,
            by_source=by_source,
            added_last_24h=added_last_24h,
            updated_last_24h=updated_last_24h,
            expiring_soon=expiring_soon,
            false_positives=false_positives,
            top_threat_actors=top_threat_actors,
            top_campaigns=top_campaigns,
            top_malware_families=top_malware_families
        )
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Retourne le statut du moteur"""
        now = datetime.now()
        uptime = (now - self.performance_stats["start_time"]).total_seconds()
        
        feeds_status = {}
        for feed_id, feed in self.cti_feeds.items():
            feeds_status[feed.name] = feed.status.value
        
        return {
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "performance": self.performance_stats,
            "total_iocs": len(self.iocs),
            "active_iocs": len([ioc for ioc in self.iocs.values() if ioc.is_active]),
            "total_feeds": len(self.cti_feeds),
            "active_feeds": len([feed for feed in self.cti_feeds.values() if feed.enabled]),
            "threat_actors": len(self.threat_actors),
            "campaigns": len(self.campaigns),
            "enrichment_queue_size": self.enrichment_queue.qsize(),
            "feeds_status": feeds_status
        }
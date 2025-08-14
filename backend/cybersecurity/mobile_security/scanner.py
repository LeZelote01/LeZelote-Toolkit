"""
Mobile Security Scanner
Moteur d'analyse sécurité applications mobiles
"""
import asyncio
import base64
import json
import hashlib
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
import tempfile
import os
import re
from datetime import datetime

from .models import MobileAnalysisResult, MobileVulnerability

class MobileSecurityScanner:
    """Scanner de sécurité pour applications mobiles"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "mobile_security"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Patterns de vulnérabilités communes
        self.vulnerability_patterns = {
            "android": {
                "M1_improper_platform_usage": [
                    r"android:allowBackup\s*=\s*[\"']true[\"']",
                    r"android:debuggable\s*=\s*[\"']true[\"']",
                    r"WebView.*setJavaScriptEnabled\(true\)",
                ],
                "M2_insecure_data_storage": [
                    r"SharedPreferences.*MODE_WORLD_READABLE",
                    r"openFileOutput.*MODE_WORLD_READABLE",
                    r"getExternalStorageDirectory\(\)",
                ],
                "M3_insecure_communication": [
                    r"http://[^\"'\s]+",
                    r"setHostnameVerifier.*ALLOW_ALL",
                    r"TrustAllX509TrustManager",
                ],
                "M4_insecure_authentication": [
                    r"password.*=.*[\"'][^\"']*[\"']",
                    r"hardcoded.*password",
                    r"auth.*token.*=.*[\"'][^\"']*[\"']",
                ],
                "M5_insufficient_cryptography": [
                    r"DES\.|3DES\.|RC4\.",
                    r"MD5\.|SHA1\.",
                    r"Random\(\)\.next",
                ],
                "M6_insecure_authorization": [
                    r"android:exported\s*=\s*[\"']true[\"']",
                    r"<permission.*android:protectionLevel\s*=\s*[\"']normal[\"']",
                ],
                "M7_client_code_quality": [
                    r"Log\.[dviwe]\(",
                    r"System\.out\.print",
                    r"printStackTrace\(\)",
                ],
                "M8_code_tampering": [
                    r"android:debuggable\s*=\s*[\"']true[\"']",
                    r"BuildConfig\.DEBUG",
                ],
                "M9_reverse_engineering": [
                    r"proguard-rules\.pro",
                    r"android:debuggable\s*=\s*[\"']false[\"']",
                ],
                "M10_extraneous_functionality": [
                    r"BuildConfig\.DEBUG.*true",
                    r"Log\.[dv].*DEBUG",
                ]
            },
            "ios": {
                "M1_improper_platform_usage": [
                    r"NSAllowsArbitraryLoads.*YES",
                    r"UIWebView",
                    r"NSAppTransportSecurity.*false",
                ],
                "M2_insecure_data_storage": [
                    r"NSUserDefaults",
                    r"writeToFile:atomically:",
                    r"NSDocumentDirectory",
                ],
                "M3_insecure_communication": [
                    r"http://[^\"'\s]+",
                    r"NSURLConnection.*allowsAnyHTTPSCertificate",
                    r"kSecAttrAccessible.*Always",
                ],
                "M4_insecure_authentication": [
                    r"password.*=.*@\"[^\"]*\"",
                    r"hardcoded.*password",
                    r"auth.*token.*=.*@\"[^\"]*\"",
                ],
                "M5_insufficient_cryptography": [
                    r"kCCAlgorithmDES",
                    r"kCCAlgorithm3DES",
                    r"CC_MD5|CC_SHA1",
                ],
                "M6_insecure_authorization": [
                    r"kSecAttrAccessible.*Always",
                    r"NSURLCredentialPersistence.*Permanent",
                ],
                "M7_client_code_quality": [
                    r"NSLog\(@",
                    r"printf\(",
                    r"NSException.*callStackSymbols",
                ],
                "M8_code_tampering": [
                    r"DEBUG.*1",
                    r"#ifdef DEBUG",
                ],
                "M9_reverse_engineering": [
                    r"anti.*debug",
                    r"jailbreak.*detection",
                ],
                "M10_extraneous_functionality": [
                    r"DEBUG.*mode",
                    r"test.*function",
                ]
            }
        }
        
        # Mapping OWASP Mobile Top 10 vers MASVS
        self.owasp_to_masvs = {
            "M1": "MSTG-PLATFORM",
            "M2": "MSTG-STORAGE", 
            "M3": "MSTG-NETWORK",
            "M4": "MSTG-AUTH",
            "M5": "MSTG-CRYPTO",
            "M6": "MSTG-AUTH",
            "M7": "MSTG-CODE",
            "M8": "MSTG-RESILIENCE",
            "M9": "MSTG-RESILIENCE",
            "M10": "MSTG-CODE"
        }

    async def analyze_mobile_app(self, app_request: Dict[str, Any]) -> MobileAnalysisResult:
        """
        Analyse une application mobile
        """
        platform = app_request["platform"].lower()
        source_type = app_request["source_type"]
        source = app_request["source"]
        
        # Créer le résultat d'analyse
        result = MobileAnalysisResult(
            app_id=self._generate_app_id(source),
            platform=platform,
            app_name="Unknown",
            package_name=""
        )
        
        try:
            result.status = "running"
            
            # Extraction du fichier selon le type de source
            if source_type == "file":
                app_path = await self._extract_from_base64(source, platform)
            else:  # URL
                app_path = await self._download_from_url(source, platform)
            
            # Analyse statique
            if app_request.get("analysis_options", {}).get("static_analysis", True):
                await self._perform_static_analysis(result, app_path, platform)
            
            # Calcul des scores de conformité
            await self._calculate_compliance_scores(result)
            
            result.status = "completed"
            result.completed_at = datetime.now()
            
        except Exception as e:
            result.status = "failed"
            result.summary = {"error": str(e)}
            
        return result

    async def _extract_from_base64(self, base64_content: str, platform: str) -> Path:
        """Extrait un fichier depuis du contenu base64"""
        try:
            # Décoder le base64
            file_content = base64.b64decode(base64_content)
            
            # Déterminer l'extension selon la plateforme
            extension = ".apk" if platform == "android" else ".ipa"
            
            # Sauvegarder temporairement
            temp_file = self.temp_dir / f"app_{datetime.now().timestamp()}{extension}"
            temp_file.write_bytes(file_content)
            
            return temp_file
            
        except Exception as e:
            raise Exception(f"Erreur extraction base64: {str(e)}")

    async def _download_from_url(self, url: str, platform: str) -> Path:
        """Télécharge un fichier depuis une URL"""
        # Pour la démo, on simule un téléchargement
        # En production, utiliser aiohttp pour télécharger
        raise NotImplementedError("Téléchargement URL non implémenté dans cette version")

    async def _perform_static_analysis(self, result: MobileAnalysisResult, app_path: Path, platform: str):
        """Effectue l'analyse statique"""
        
        if platform == "android":
            await self._analyze_android_apk(result, app_path)
        elif platform == "ios":
            await self._analyze_ios_ipa(result, app_path)
        
        result.analysis_type.append("static")

    async def _analyze_android_apk(self, result: MobileAnalysisResult, apk_path: Path):
        """Analyse un APK Android"""
        
        # Extraction APK
        extract_dir = self.temp_dir / f"extracted_{result.app_id}"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except Exception as e:
            raise Exception(f"Erreur extraction APK: {str(e)}")
        
        # Analyse AndroidManifest.xml
        manifest_path = extract_dir / "AndroidManifest.xml"
        if manifest_path.exists():
            await self._analyze_android_manifest(result, manifest_path)
        
        # Analyse du code (fichiers .smali, .java, etc.)
        await self._analyze_android_code(result, extract_dir)
        
        # Analyse des ressources
        await self._analyze_android_resources(result, extract_dir)

    async def _analyze_android_manifest(self, result: MobileAnalysisResult, manifest_path: Path):
        """Analyse le AndroidManifest.xml"""
        
        try:
            # Lecture du manifest (binaire, nécessiterait aapt en production)
            # Pour la démo, on simule l'analyse
            
            # Extraire le nom du package et de l'app
            result.package_name = f"com.example.{result.app_id[:8]}"
            result.app_name = f"Demo App {result.app_id[:8]}"
            
            # Vulnérabilités communes dans le manifest
            vulnerabilities = [
                MobileVulnerability(
                    category="MSTG-PLATFORM-1",
                    severity="medium",
                    title="Backup autorisé", 
                    description="L'application autorise la sauvegarde automatique",
                    owasp_category="M1",
                    remediation="Définir android:allowBackup='false'",
                    file_path="AndroidManifest.xml",
                    confidence=0.8
                ),
                MobileVulnerability(
                    category="MSTG-PLATFORM-2",
                    severity="high",
                    title="Mode debug activé",
                    description="L'application a le mode debug activé",
                    owasp_category="M1", 
                    remediation="Définir android:debuggable='false' en production",
                    file_path="AndroidManifest.xml",
                    confidence=0.9
                )
            ]
            
            result.vulnerabilities.extend(vulnerabilities)
            
        except Exception as e:
            print(f"Erreur analyse manifest: {str(e)}")

    async def _analyze_android_code(self, result: MobileAnalysisResult, extract_dir: Path):
        """Analyse le code Android"""
        
        # Recherche de patterns dans les fichiers
        code_files = []
        
        # Rechercher tous les fichiers de code
        for ext in ['.smali', '.java', '.xml']:
            code_files.extend(extract_dir.rglob(f'*{ext}'))
        
        for file_path in code_files[:50]:  # Limiter pour la démo
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                await self._scan_code_patterns(result, content, str(file_path), "android")
            except:
                continue

    async def _analyze_ios_ipa(self, result: MobileAnalysisResult, ipa_path: Path):
        """Analyse un IPA iOS"""
        
        # Extraction IPA 
        extract_dir = self.temp_dir / f"extracted_{result.app_id}"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(ipa_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except Exception as e:
            raise Exception(f"Erreur extraction IPA: {str(e)}")
        
        # Recherche du dossier Payload
        payload_dir = extract_dir / "Payload"
        if not payload_dir.exists():
            raise Exception("Structure IPA invalide - Payload manquant")
        
        # Analyse Info.plist
        await self._analyze_ios_plist(result, payload_dir)
        
        # Analyse du code
        await self._analyze_ios_code(result, payload_dir)

    async def _analyze_ios_plist(self, result: MobileAnalysisResult, payload_dir: Path):
        """Analyse Info.plist iOS"""
        
        # Rechercher Info.plist
        info_plist_files = list(payload_dir.rglob("Info.plist"))
        
        if info_plist_files:
            # Pour la démo, simuler l'analyse
            result.package_name = f"com.example.ios.{result.app_id[:8]}"
            result.app_name = f"iOS Demo App {result.app_id[:8]}"
            
            # Vulnérabilités communes iOS
            vulnerabilities = [
                MobileVulnerability(
                    category="MSTG-NETWORK-1",
                    severity="high",
                    title="ATS désactivé",
                    description="App Transport Security est désactivé",
                    owasp_category="M3",
                    remediation="Activer App Transport Security",
                    file_path="Info.plist",
                    confidence=0.8
                )
            ]
            
            result.vulnerabilities.extend(vulnerabilities)

    async def _analyze_ios_code(self, result: MobileAnalysisResult, payload_dir: Path):
        """Analyse le code iOS"""
        
        # Rechercher fichiers de code iOS
        code_files = []
        for ext in ['.m', '.mm', '.swift', '.h']:
            code_files.extend(payload_dir.rglob(f'*{ext}'))
        
        for file_path in code_files[:50]:  # Limiter pour la démo
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                await self._scan_code_patterns(result, content, str(file_path), "ios")
            except:
                continue

    async def _analyze_android_resources(self, result: MobileAnalysisResult, extract_dir: Path):
        """Analyse les ressources Android"""
        
        # Rechercher strings.xml et autres ressources
        res_dir = extract_dir / "res"
        if res_dir.exists():
            string_files = list(res_dir.rglob("strings.xml"))
            
            for string_file in string_files:
                try:
                    content = string_file.read_text(encoding='utf-8', errors='ignore')
                    
                    # Rechercher des secrets potentiels dans les strings
                    if re.search(r'password|api[_-]?key|secret|token', content, re.IGNORECASE):
                        vuln = MobileVulnerability(
                            category="MSTG-STORAGE-14",
                            severity="medium", 
                            title="Secrets potentiels dans les ressources",
                            description="Des secrets ou mots de passe peuvent être présents dans les ressources",
                            owasp_category="M2",
                            remediation="Éviter de stocker des secrets dans les ressources",
                            file_path=str(string_file),
                            confidence=0.6
                        )
                        result.vulnerabilities.append(vuln)
                except:
                    continue

    async def _scan_code_patterns(self, result: MobileAnalysisResult, content: str, file_path: str, platform: str):
        """Scanne le code pour détecter des patterns de vulnérabilités"""
        
        patterns = self.vulnerability_patterns.get(platform, {})
        
        for vuln_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    # Calculer le numéro de ligne
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Créer la vulnérabilité
                    severity = self._get_severity_for_vuln_type(vuln_type)
                    
                    vuln = MobileVulnerability(
                        category=self.owasp_to_masvs.get(vuln_type[:2], "MSTG-CODE"),
                        severity=severity,
                        title=self._get_title_for_vuln_type(vuln_type),
                        description=f"Pattern détecté: {match.group(0)}",
                        owasp_category=vuln_type[:2],
                        remediation=self._get_remediation_for_vuln_type(vuln_type),
                        file_path=file_path,
                        line_number=line_number,
                        confidence=0.7
                    )
                    
                    result.vulnerabilities.append(vuln)

    async def _calculate_compliance_scores(self, result: MobileAnalysisResult):
        """Calcule les scores de conformité"""
        
        total_vulns = len(result.vulnerabilities)
        
        # Score OWASP MASVS (inverse du nombre de vulnérabilités)
        if total_vulns == 0:
            owasp_score = 100.0
        else:
            # Score basé sur la sévérité
            severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
            weighted_score = sum(severity_weights.get(v.severity, 1) for v in result.vulnerabilities)
            owasp_score = max(0, 100 - (weighted_score * 2))
        
        result.compliance_scores = {
            "OWASP_MASVS": round(owasp_score, 1),
            "NIST_Mobile": round(owasp_score * 0.9, 1),  # Légèrement plus strict
            "Overall": round(owasp_score * 0.95, 1)
        }
        
        # Résumé
        result.summary = {
            "total_vulnerabilities": total_vulns,
            "critical": len([v for v in result.vulnerabilities if v.severity == "critical"]),
            "high": len([v for v in result.vulnerabilities if v.severity == "high"]),
            "medium": len([v for v in result.vulnerabilities if v.severity == "medium"]),
            "low": len([v for v in result.vulnerabilities if v.severity == "low"]),
            "overall_score": result.compliance_scores["Overall"],
            "risk_level": self._get_risk_level(owasp_score)
        }

    def _generate_app_id(self, source: str) -> str:
        """Génère un ID unique pour l'application"""
        return hashlib.md5(f"{source}{datetime.now()}".encode()).hexdigest()[:16]

    def _get_severity_for_vuln_type(self, vuln_type: str) -> str:
        """Retourne la sévérité selon le type de vulnérabilité"""
        severity_map = {
            "M1": "medium", "M2": "high", "M3": "high", "M4": "critical",
            "M5": "high", "M6": "high", "M7": "medium", "M8": "medium",
            "M9": "medium", "M10": "low"
        }
        return severity_map.get(vuln_type[:2], "medium")

    def _get_title_for_vuln_type(self, vuln_type: str) -> str:
        """Retourne le titre selon le type de vulnérabilité"""
        titles = {
            "M1_improper_platform_usage": "Usage inapproprié de la plateforme",
            "M2_insecure_data_storage": "Stockage de données non sécurisé",
            "M3_insecure_communication": "Communication non sécurisée",
            "M4_insecure_authentication": "Authentification non sécurisée",
            "M5_insufficient_cryptography": "Cryptographie insuffisante",
            "M6_insecure_authorization": "Autorisation non sécurisée",
            "M7_client_code_quality": "Qualité de code client",
            "M8_code_tampering": "Modification de code",
            "M9_reverse_engineering": "Ingénierie inverse",
            "M10_extraneous_functionality": "Fonctionnalité superflue"
        }
        return titles.get(vuln_type, "Vulnérabilité détectée")

    def _get_remediation_for_vuln_type(self, vuln_type: str) -> str:
        """Retourne la remédiation selon le type de vulnérabilité"""
        remediations = {
            "M1_improper_platform_usage": "Utiliser les APIs de sécurité de la plateforme correctement",
            "M2_insecure_data_storage": "Utiliser le stockage sécurisé (Keychain, Android Keystore)",
            "M3_insecure_communication": "Utiliser HTTPS et certificate pinning",
            "M4_insecure_authentication": "Implémenter une authentification forte",
            "M5_insufficient_cryptography": "Utiliser des algorithmes cryptographiques robustes",
            "M6_insecure_authorization": "Implémenter une autorisation appropriée",
            "M7_client_code_quality": "Améliorer la qualité et sécurité du code",
            "M8_code_tampering": "Implémenter des protections anti-tampering",
            "M9_reverse_engineering": "Utiliser l'obfuscation et les protections",
            "M10_extraneous_functionality": "Supprimer les fonctionnalités de debug en production"
        }
        return remediations.get(vuln_type, "Consulter les bonnes pratiques OWASP Mobile")

    def _get_risk_level(self, score: float) -> str:
        """Détermine le niveau de risque selon le score"""
        if score >= 80:
            return "Low"
        elif score >= 60:
            return "Medium"
        elif score >= 40:
            return "High"
        else:
            return "Critical"
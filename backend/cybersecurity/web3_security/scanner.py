"""
Web3 Security Scanner
Moteur d'analyse pour smart contracts et blockchain
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
import re
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .models import (
    ContractAuditResult, ContractVulnerability, GasAnalysis,
    DeFiProtocolAnalysis, NFTSecurityAnalysis
)

class Web3SecurityScanner:
    """Scanner de sécurité Web3 et smart contracts"""
    
    def __init__(self):
        # Patterns de vulnérabilités Solidity
        self.vulnerability_patterns = {
            "reentrancy": {
                "pattern": r"\.call\{value:.*?\}\(|\.call\(|external.*payable",
                "severity": "critical",
                "title": "Vulnérabilité de réentrance",
                "description": "Fonction vulnérable aux attaques de réentrance",
                "swc_id": "SWC-107"
            },
            "overflow": {
                "pattern": r"[\+\-\*](?!.*SafeMath|.*\.add\(|.*\.sub\(|.*\.mul\()",
                "severity": "high", 
                "title": "Risque d'overflow/underflow",
                "description": "Opération arithmétique sans protection contre l'overflow",
                "swc_id": "SWC-101"
            },
            "unchecked_call": {
                "pattern": r"\.call\(.*?\);(?!\s*require)",
                "severity": "medium",
                "title": "Appel externe non vérifié",
                "description": "Appel externe sans vérification du retour",
                "swc_id": "SWC-104"
            },
            "tx_origin": {
                "pattern": r"tx\.origin",
                "severity": "medium",
                "title": "Utilisation de tx.origin",
                "description": "Utilisation dangereuse de tx.origin pour l'authentification",
                "swc_id": "SWC-115"
            },
            "time_manipulation": {
                "pattern": r"block\.timestamp|now(?!\w)",
                "severity": "medium",
                "title": "Dépendance au timestamp",
                "description": "Logique dépendante de block.timestamp manipulable",
                "swc_id": "SWC-116"
            },
            "access_control": {
                "pattern": r"onlyOwner|require\(.*owner|modifier.*owner",
                "severity": "high",
                "title": "Contrôle d'accès faible",
                "description": "Implémentation de contrôle d'accès potentiellement faible",
                "swc_id": "SWC-105"
            }
        }
        
        # Standards de bonnes pratiques
        self.best_practices = {
            "uses_safemath": r"SafeMath|\.add\(|\.sub\(|\.mul\(",
            "has_modifiers": r"modifier\s+\w+",
            "has_events": r"event\s+\w+",
            "uses_require": r"require\(",
            "uses_openzeppelin": r"import.*openzeppelin|OpenZeppelin",
            "has_documentation": r"///|/\*\*"
        }
        
        # Analyse DeFi spécifique
        self.defi_patterns = {
            "flash_loan": r"flashLoan|flashBorrow",
            "oracle_usage": r"oracle|getPrice|latestRoundData",
            "liquidity_pool": r"addLiquidity|removeLiquidity|swap",
            "governance": r"vote|proposal|delegate",
            "yield_farming": r"stake|unstake|harvest|reward"
        }

    async def audit_smart_contract(self, audit_request: Dict[str, Any]) -> ContractAuditResult:
        """Lance un audit complet de smart contract"""
        
        chain = audit_request.get("chain", "ethereum")
        contract_address = audit_request.get("contract_address")
        source_code = audit_request.get("source_code", "")
        audit_scope = audit_request.get("audit_scope", [])
        contract_type = audit_request.get("contract_type", "general")
        
        result = ContractAuditResult(
            chain=chain,
            contract_address=contract_address,
            contract_type=contract_type,
            audit_options=audit_request
        )
        
        try:
            result.status = "running"
            
            # 1. Récupération du code source si nécessaire
            if contract_address and not source_code:
                source_code = await self._fetch_contract_source(chain, contract_address)
            
            if not source_code:
                # Générer un exemple de code pour la démonstration
                source_code = self._generate_sample_contract(contract_type)
            
            # 2. Analyse statique des vulnérabilités
            vulnerabilities = await self._analyze_vulnerabilities(source_code, audit_scope)
            result.vulnerabilities = vulnerabilities
            
            # 3. Analyse du gas
            gas_analysis = await self._analyze_gas_usage(source_code)
            result.gas_analysis = gas_analysis
            
            # 4. Vérification des standards
            standards_compliance = await self._check_standards_compliance(source_code, contract_type)
            result.standards_compliance = standards_compliance
            
            # 5. Vérification des bonnes pratiques
            best_practices = await self._check_best_practices(source_code)
            result.best_practices = best_practices
            
            # 6. Calcul des métriques
            result.total_vulnerabilities = len(vulnerabilities)
            result.critical_vulnerabilities = len([v for v in vulnerabilities if v.severity == "critical"])
            result.high_vulnerabilities = len([v for v in vulnerabilities if v.severity == "high"])
            
            # Score de sécurité (100 - pénalités)
            penalty = (result.critical_vulnerabilities * 30 + 
                      result.high_vulnerabilities * 15 +
                      len([v for v in vulnerabilities if v.severity == "medium"]) * 5 +
                      len([v for v in vulnerabilities if v.severity == "low"]) * 2)
            result.security_score = max(0, 100 - penalty)
            
            result.status = "completed"
            result.completed_at = datetime.now()
            result.duration = (result.completed_at - result.started_at).total_seconds()
            
        except Exception as e:
            result.status = "failed"
            result.audit_options["error"] = str(e)
        
        return result

    async def _fetch_contract_source(self, chain: str, address: str) -> str:
        """Récupère le code source d'un contrat (simulation)"""
        # En production, utiliser les APIs Etherscan, BSCScan, PolygonScan, etc.
        await asyncio.sleep(1)  # Simulation d'appel API
        
        # Retourner un exemple de contrat selon la chaîne
        if chain == "ethereum":
            return self._generate_sample_contract("token")
        elif chain == "bsc":
            return self._generate_sample_contract("defi")
        elif chain == "polygon":
            return self._generate_sample_contract("nft")
        else:
            return self._generate_sample_contract("general")

    def _generate_sample_contract(self, contract_type: str) -> str:
        """Génère un exemple de contrat pour la démonstration"""
        
        if contract_type == "token":
            return '''
pragma solidity ^0.8.0;

contract SampleToken {
    mapping(address => uint256) public balances;
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    function transfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount);
        balances[msg.sender] -= amount;  // Potential underflow
        balances[to] += amount;  // Potential overflow
    }
    
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        msg.sender.call{value: amount}("");  // Reentrancy vulnerability
        balances[msg.sender] = 0;
    }
}
'''
        elif contract_type == "defi":
            return '''
pragma solidity ^0.8.0;

contract DeFiProtocol {
    mapping(address => uint256) public stakes;
    uint256 public rewardRate = 100;
    
    function stake(uint256 amount) public {
        stakes[msg.sender] += amount;
    }
    
    function calculateReward() public view returns (uint256) {
        return stakes[msg.sender] * rewardRate * block.timestamp;  // Time manipulation
    }
    
    function emergencyWithdraw() public {
        require(tx.origin == owner);  // tx.origin vulnerability
        payable(msg.sender).transfer(address(this).balance);
    }
}
'''
        else:
            return '''
pragma solidity ^0.8.0;

contract GeneralContract {
    address public owner;
    mapping(address => bool) public authorized;
    
    constructor() {
        owner = msg.sender;
    }
    
    function authorize(address user) public {
        require(msg.sender == owner);
        authorized[user] = true;
    }
    
    function sensitiveFunction() public {
        require(authorized[msg.sender]);
        // Some sensitive logic
    }
}
'''

    async def _analyze_vulnerabilities(self, source_code: str, audit_scope: List[str]) -> List[ContractVulnerability]:
        """Analyse les vulnérabilités dans le code source"""
        vulnerabilities = []
        
        lines = source_code.split('\n')
        
        for category, pattern_info in self.vulnerability_patterns.items():
            if audit_scope and category not in audit_scope:
                continue
                
            pattern = pattern_info["pattern"]
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    vuln = ContractVulnerability(
                        audit_id="",  # Sera défini par l'appelant
                        category=category,
                        severity=pattern_info["severity"],
                        title=pattern_info["title"],
                        description=f"{pattern_info['description']} (ligne {line_num})",
                        location=f"ligne {line_num}: {line.strip()}",
                        impact=self._get_impact_description(pattern_info["severity"]),
                        remediation=self._get_remediation_advice(category),
                        confidence=0.8,
                        swc_id=pattern_info.get("swc_id")
                    )
                    vulnerabilities.append(vuln)
        
        return vulnerabilities

    async def _analyze_gas_usage(self, source_code: str) -> List[GasAnalysis]:
        """Analyse l'utilisation du gas"""
        gas_analysis = []
        
        # Analyser les fonctions pour estimer la consommation de gas
        function_pattern = r"function\s+(\w+)\s*\([^)]*\)\s*(?:public|external|private|internal)?"
        functions = re.findall(function_pattern, source_code)
        
        for func_name in functions:
            # Estimation simplifiée basée sur le nom et le contenu
            estimated_gas = self._estimate_function_gas(func_name, source_code)
            optimization_potential = self._calculate_optimization_potential(func_name, source_code)
            suggestions = self._get_gas_optimization_suggestions(func_name)
            
            analysis = GasAnalysis(
                function_name=func_name,
                estimated_gas=estimated_gas,
                optimization_potential=optimization_potential,
                suggestions=suggestions
            )
            gas_analysis.append(analysis)
        
        return gas_analysis

    async def _check_standards_compliance(self, source_code: str, contract_type: str) -> Dict[str, bool]:
        """Vérifie la conformité aux standards"""
        compliance = {}
        
        if contract_type == "token":
            compliance["ERC20"] = bool(re.search(r"transfer\s*\(|balanceOf\s*\(|approve\s*\(", source_code))
            compliance["SafeMath"] = bool(re.search(r"SafeMath|\.add\(|\.sub\(", source_code))
        elif contract_type == "nft":
            compliance["ERC721"] = bool(re.search(r"ownerOf\s*\(|tokenURI\s*\(", source_code))
            compliance["ERC165"] = bool(re.search(r"supportsInterface\s*\(", source_code))
        elif contract_type == "defi":
            compliance["Oracle_Usage"] = bool(re.search(r"oracle|getPrice", source_code))
            compliance["Slippage_Protection"] = bool(re.search(r"slippage|minAmount", source_code))
        
        compliance["OpenZeppelin"] = bool(re.search(r"openzeppelin|OpenZeppelin", source_code))
        compliance["Proper_Events"] = bool(re.search(r"event\s+\w+", source_code))
        
        return compliance

    async def _check_best_practices(self, source_code: str) -> Dict[str, bool]:
        """Vérifie les bonnes pratiques"""
        practices = {}
        
        for practice, pattern in self.best_practices.items():
            practices[practice] = bool(re.search(pattern, source_code))
        
        return practices

    def _estimate_function_gas(self, func_name: str, source_code: str) -> int:
        """Estime la consommation de gas d'une fonction"""
        base_gas = 21000  # Gas de base pour une transaction
        
        # Facteurs influençant le gas
        if "transfer" in func_name.lower():
            return base_gas + 20000
        elif "stake" in func_name.lower() or "deposit" in func_name.lower():
            return base_gas + 45000
        elif "withdraw" in func_name.lower():
            return base_gas + 35000 
        elif "view" in source_code or "pure" in source_code:
            return 0  # Fonctions view/pure gratuites
        else:
            return base_gas + 25000

    def _calculate_optimization_potential(self, func_name: str, source_code: str) -> int:
        """Calcule le potentiel d'optimisation en %"""
        optimization = 0
        
        # Vérifier des patterns d'optimisation
        if not re.search(r"SafeMath|\.add\(|\.sub\(", source_code):
            optimization += 15  # Utiliser SafeMath peut optimiser
        
        if re.search(r"storage\s+\w+", source_code):
            optimization += 10  # Variables storage peuvent être optimisées
        
        if re.search(r"for\s*\(", source_code):
            optimization += 20  # Boucles peuvent être optimisées
        
        return min(optimization, 40)  # Max 40% d'optimisation

    def _get_gas_optimization_suggestions(self, func_name: str) -> List[str]:
        """Retourne des suggestions d'optimisation du gas"""
        suggestions = []
        
        if "transfer" in func_name.lower():
            suggestions.extend([
                "Utiliser des transferts groupés pour réduire les coûts",
                "Implémenter une logique de cache pour les balances"
            ])
        elif "stake" in func_name.lower():
            suggestions.extend([
                "Optimiser le calcul des récompenses",
                "Utiliser des variables packed pour réduire le stockage"
            ])
        
        suggestions.extend([
            "Utiliser 'memory' au lieu de 'storage' quand possible",
            "Minimiser les appels externes dans les boucles",
            "Utiliser des events au lieu de storage pour les logs"
        ])
        
        return suggestions[:3]  # Limiter à 3 suggestions

    def _get_impact_description(self, severity: str) -> str:
        """Retourne la description de l'impact selon la sévérité"""
        impacts = {
            "critical": "Perte totale de fonds, exploitation immédiate possible",
            "high": "Perte partielle de fonds, exploitation complexe mais réalisable", 
            "medium": "Fonctionnement incorrect, exploitation dans certaines conditions",
            "low": "Problème mineur, impact limité sur la sécurité"
        }
        return impacts.get(severity, "Impact non défini")

    def _get_remediation_advice(self, category: str) -> str:
        """Retourne des conseils de remédiation"""
        remediations = {
            "reentrancy": "Utiliser le pattern Checks-Effects-Interactions, implémenter un mutex",
            "overflow": "Utiliser SafeMath ou Solidity 0.8+ avec overflow automatique",
            "unchecked_call": "Vérifier la valeur de retour avec require() ou utiliser des appels sécurisés",
            "tx_origin": "Utiliser msg.sender au lieu de tx.origin pour l'authentification",
            "time_manipulation": "Éviter la dépendance stricte à block.timestamp, utiliser des oracles",
            "access_control": "Implémenter des modifiers robustes avec OpenZeppelin AccessControl"
        }
        return remediations.get(category, "Consulter les bonnes pratiques de sécurité Solidity")

    async def analyze_defi_protocol(self, source_code: str) -> DeFiProtocolAnalysis:
        """Analyse spécifique aux protocoles DeFi"""
        
        # Détection du type de protocole
        protocol_type = "general"
        if re.search(r"swap|exchange|dex", source_code, re.IGNORECASE):
            protocol_type = "dex"
        elif re.search(r"lend|borrow|lending", source_code, re.IGNORECASE):
            protocol_type = "lending"
        elif re.search(r"stake|staking", source_code, re.IGNORECASE):
            protocol_type = "staking"
        elif re.search(r"yield|farm|harvest", source_code, re.IGNORECASE):
            protocol_type = "yield_farming"
        
        # Analyse des risques
        liquidity_risks = []
        if re.search(r"addLiquidity|removeLiquidity", source_code):
            liquidity_risks.append("Risque d'impermanent loss")
            liquidity_risks.append("Manipulation des pools de liquidité")
        
        flash_loan_vulnerabilities = []
        if re.search(r"flashLoan|flashBorrow", source_code):
            flash_loan_vulnerabilities.append("Arbitrage flash loan possible")
            flash_loan_vulnerabilities.append("Manipulation de prix via flash loans")
        
        # Risque de manipulation d'oracle
        oracle_risk = "low"
        if re.search(r"oracle|getPrice|latestRoundData", source_code):
            oracle_risk = "medium"
            if not re.search(r"multiple.*oracle|chainlink.*oracle", source_code):
                oracle_risk = "high"
        
        governance_issues = []
        if re.search(r"vote|proposal|delegate", source_code):
            if not re.search(r"timelock|delay", source_code):
                governance_issues.append("Absence de timelock pour les propositions critiques")
            if not re.search(r"quorum", source_code):
                governance_issues.append("Pas de quorum minimum défini")
        
        return DeFiProtocolAnalysis(
            protocol_type=protocol_type,
            liquidity_risks=liquidity_risks,
            flash_loan_vulnerabilities=flash_loan_vulnerabilities,
            oracle_manipulation_risk=oracle_risk,
            governance_issues=governance_issues,
            tokenomics_analysis={"distribution": "unknown", "inflation": "unknown"}
        )

    async def analyze_nft_security(self, source_code: str) -> NFTSecurityAnalysis:
        """Analyse spécifique aux NFTs"""
        
        # Analyse des métadonnées
        metadata_security = {
            "on_chain_metadata": bool(re.search(r"tokenURI.*return.*string", source_code)),
            "immutable_metadata": bool(re.search(r"immutable|constant.*tokenURI", source_code)),
            "ipfs_usage": bool(re.search(r"ipfs://", source_code))
        }
        
        # Vulnérabilités de royalties
        royalty_vulnerabilities = []
        if re.search(r"royalty|fee", source_code):
            if not re.search(r"EIP2981|royaltyInfo", source_code):
                royalty_vulnerabilities.append("Standard de royalties non-conforme")
        
        # Compatibilité marketplace
        marketplace_compatibility = {
            "opensea": bool(re.search(r"opensea|0x495f947276749ce646f68ac8c248420045cb7b5e", source_code)),
            "erc721": bool(re.search(r"ERC721|ownerOf|tokenURI", source_code)),
            "erc1155": bool(re.search(r"ERC1155|balanceOf.*tokenId", source_code))
        }
        
        # Risque de manipulation de rareté
        rarity_risk = "low"
        if re.search(r"random|rand|block\.timestamp.*%", source_code):
            rarity_risk = "high"
        elif re.search(r"chainlink.*vrf|provable", source_code):
            rarity_risk = "low"
        else:
            rarity_risk = "medium"
        
        # Vérification de provenance
        provenance_verification = bool(re.search(r"provenance|merkle|hash.*original", source_code))
        
        return NFTSecurityAnalysis(
            metadata_security=metadata_security,
            royalty_vulnerabilities=royalty_vulnerabilities,
            marketplace_compatibility=marketplace_compatibility,
            rarity_manipulation_risk=rarity_risk,
            provenance_verification=provenance_verification
        )
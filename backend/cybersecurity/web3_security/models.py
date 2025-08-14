"""
Web3 Security Models
Modèles Pydantic pour la sécurité Web3 et smart contracts
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class SmartContractRequest(BaseModel):
    """Requête d'audit de smart contract"""
    chain: str = Field(..., description="Blockchain: ethereum|bsc|polygon|arbitrum")
    contract_address: Optional[str] = Field(None, description="Adresse du contrat")
    source_code: Optional[str] = Field(None, description="Code source Solidity")
    audit_scope: List[str] = Field(
        default_factory=lambda: ["reentrancy", "overflow", "access_control", "front_running"],
        description="Types de vulnérabilités à auditer"
    )
    contract_type: str = Field(default="general", description="Type: token|defi|nft|dao|general")
    audit_options: Dict[str, Any] = Field(default_factory=dict, description="Options avancées")

class ContractVulnerability(BaseModel):
    """Vulnérabilité dans un smart contract"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_id: str = Field(..., description="ID de l'audit")
    category: str = Field(..., description="Catégorie de vulnérabilité")
    severity: str = Field(..., description="Severity: critical|high|medium|low")
    title: str = Field(..., description="Titre de la vulnérabilité")
    description: str = Field(..., description="Description détaillée")
    location: Optional[str] = Field(None, description="Ligne/fonction affectée")
    impact: str = Field(..., description="Impact potentiel")
    remediation: str = Field(..., description="Recommandations de correction")
    confidence: float = Field(..., description="Niveau de confiance 0-1")
    cwe_id: Optional[str] = Field(None, description="CWE ID si applicable")
    swc_id: Optional[str] = Field(None, description="SWC ID (Smart Contract Weakness)")
    detected_at: datetime = Field(default_factory=datetime.now)

class GasAnalysis(BaseModel):
    """Analyse des coûts de gas"""
    function_name: str = Field(..., description="Nom de la fonction")
    estimated_gas: int = Field(..., description="Gas estimé")
    optimization_potential: int = Field(..., description="Potentiel d'optimisation en %")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions d'optimisation")

class ContractAuditResult(BaseModel):
    """Résultat d'audit de smart contract"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chain: str = Field(..., description="Blockchain auditée")
    contract_address: Optional[str] = Field(None, description="Adresse du contrat")
    contract_type: str = Field(..., description="Type de contrat")
    status: str = Field(default="pending", description="Status: pending|running|completed|failed")
    
    # Résultats
    vulnerabilities: List[ContractVulnerability] = Field(default_factory=list)
    gas_analysis: List[GasAnalysis] = Field(default_factory=list)
    
    # Métriques
    total_vulnerabilities: int = 0
    critical_vulnerabilities: int = 0
    high_vulnerabilities: int = 0
    security_score: float = 100.0
    
    # Analyse de conformité
    standards_compliance: Dict[str, bool] = Field(default_factory=dict)
    best_practices: Dict[str, bool] = Field(default_factory=dict)
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None)
    duration: Optional[float] = Field(None, description="Durée en secondes")
    
    # Metadata
    audit_options: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Web3SecurityMetrics(BaseModel):
    """Métriques Web3 Security"""
    total_audits: int = 0
    total_contracts_audited: int = 0
    vulnerabilities_by_chain: Dict[str, int] = Field(default_factory=dict)
    vulnerabilities_by_severity: Dict[str, int] = Field(default_factory=dict)
    most_common_vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list)
    average_security_score: float = 0.0
    chains_supported: List[str] = Field(default_factory=lambda: [
        "ethereum", "bsc", "polygon", "arbitrum"
    ])

class Web3SecurityStatus(BaseModel):
    """Status du service Web3 Security"""
    status: str = "operational"
    service: str = "Web3 Security"
    version: str = "1.0.0-portable"
    features: Dict[str, bool] = Field(default_factory=lambda: {
        "smart_contract_audit": True,
        "solidity_analysis": True,
        "gas_optimization": True,
        "vulnerability_detection": True,
        "standards_compliance": True,
        "multi_chain_support": True,
        "defi_protocols": True,
        "nft_analysis": True
    })
    supported_chains: List[str] = Field(default_factory=lambda: [
        "Ethereum", "BSC", "Polygon", "Arbitrum", "Optimism", "Avalanche"
    ])
    vulnerability_categories: List[str] = Field(default_factory=lambda: [
        "reentrancy", "overflow", "access_control", "front_running",
        "time_manipulation", "denial_of_service", "unchecked_calls",
        "integer_issues", "race_conditions", "tx_origin"
    ])
    standards_supported: List[str] = Field(default_factory=lambda: [
        "ERC-20", "ERC-721", "ERC-1155", "OpenZeppelin", "DeFi"
    ])
    active_audits: int = 0
    completed_audits: int = 0
    metrics: Optional[Web3SecurityMetrics] = None

class DeFiProtocolAnalysis(BaseModel):
    """Analyse spécifique aux protocoles DeFi"""
    protocol_type: str = Field(..., description="Type: dex|lending|staking|yield_farming")
    liquidity_risks: List[str] = Field(default_factory=list)
    flash_loan_vulnerabilities: List[str] = Field(default_factory=list)
    oracle_manipulation_risk: str = Field(..., description="low|medium|high")
    governance_issues: List[str] = Field(default_factory=list)
    tokenomics_analysis: Dict[str, Any] = Field(default_factory=dict)

class NFTSecurityAnalysis(BaseModel):
    """Analyse spécifique aux NFTs"""
    metadata_security: Dict[str, Any] = Field(default_factory=dict)
    royalty_vulnerabilities: List[str] = Field(default_factory=list)
    marketplace_compatibility: Dict[str, bool] = Field(default_factory=dict)
    rarity_manipulation_risk: str = Field(..., description="low|medium|high")
    provenance_verification: bool = Field(default=False)
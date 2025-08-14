"""
Modèles de données pour Business AI - CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - Intelligence artificielle business et décisions stratégiques
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
import uuid

# Modèles pour les métriques business
class BusinessMetric(BaseModel):
    metric_name: str = Field(..., description="Nom de la métrique")
    current_value: Union[float, int, str] = Field(..., description="Valeur actuelle")
    target_value: Optional[Union[float, int, str]] = Field(None, description="Valeur cible")
    unit: str = Field(..., description="Unité de mesure")
    category: str = Field(..., description="Catégorie: financial, operational, security, customer")
    trend: str = Field(..., description="Tendance: increasing, decreasing, stable")
    benchmark_percentile: Optional[float] = Field(None, description="Percentile par rapport au benchmark industrie")

class BusinessKPI(BaseModel):
    kpi_name: str = Field(..., description="Nom du KPI")
    current_value: float = Field(..., description="Valeur actuelle")
    target_value: float = Field(..., description="Valeur cible")
    period: str = Field(..., description="Période: daily, weekly, monthly, quarterly, yearly")
    performance_status: str = Field(..., description="Statut: excellent, good, warning, critical")
    improvement_percentage: Optional[float] = Field(None, description="Pourcentage d'amélioration vs période précédente")

# Modèles pour les analyses business
class BusinessAnalysisRequest(BaseModel):
    analysis_type: str = Field(..., description="Type d'analyse: performance, roi, risk_business, optimization, competitive")
    business_context: Dict[str, Any] = Field(..., description="Contexte business")
    time_period: int = Field(30, description="Période d'analyse en jours")
    metrics_to_analyze: Optional[List[str]] = Field(None, description="Métriques spécifiques à analyser")
    strategic_objectives: Optional[List[str]] = Field(None, description="Objectifs stratégiques")
    competitive_analysis: Optional[bool] = Field(False, description="Inclure analyse concurrentielle")

class BusinessOptimizationRequest(BaseModel):
    optimization_area: str = Field(..., description="Zone d'optimisation: costs, processes, security_spending, resource_allocation, pricing")
    current_situation: Dict[str, Any] = Field(..., description="Situation actuelle")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Contraintes à respecter")
    optimization_goals: List[str] = Field(..., description="Objectifs d'optimisation")
    budget_limit: Optional[float] = Field(None, description="Limite budgétaire pour optimisations")
    timeline_months: Optional[int] = Field(12, description="Horizon temporel en mois")

# Modèles pour les calculs ROI
class ROICalculation(BaseModel):
    investment_name: str = Field(..., description="Nom de l'investissement")
    initial_investment: float = Field(..., description="Investissement initial")
    annual_benefits: float = Field(..., description="Bénéfices annuels")
    annual_costs: float = Field(..., description="Coûts annuels")
    roi_percentage: float = Field(..., description="ROI en pourcentage")
    payback_period_months: float = Field(..., description="Période de retour en mois")
    net_present_value: float = Field(..., description="Valeur actuelle nette")
    internal_rate_return: Optional[float] = Field(None, description="Taux de rentabilité interne")
    sensitivity_analysis: Optional[Dict[str, float]] = Field(None, description="Analyse de sensibilité")

class InvestmentScenario(BaseModel):
    scenario_name: str = Field(..., description="Nom du scénario")
    probability: float = Field(..., description="Probabilité de réalisation (0-1)")
    roi_calculation: ROICalculation = Field(..., description="Calcul ROI pour ce scénario")
    key_assumptions: List[str] = Field(..., description="Hypothèses clés")
    risk_factors: List[str] = Field(..., description="Facteurs de risque")

# Modèles pour les recommandations
class BusinessRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Titre de la recommandation")
    description: str = Field(..., description="Description détaillée")
    category: str = Field(..., description="Catégorie: cost_optimization, revenue_growth, risk_mitigation, efficiency, innovation")
    priority: str = Field(..., description="Priorité: critical, high, medium, low")
    estimated_impact: Dict[str, Any] = Field(..., description="Impact estimé")
    implementation_complexity: str = Field(..., description="Complexité: simple, moderate, complex, very_complex")
    estimated_timeline: str = Field(..., description="Délai estimé")
    required_resources: Optional[List[str]] = Field(None, description="Ressources nécessaires")
    success_metrics: Optional[List[str]] = Field(None, description="Métriques de succès")
    dependencies: Optional[List[str]] = Field(None, description="Dépendances avec autres recommandations")

class StrategicInitiative(BaseModel):
    initiative_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Nom de l'initiative")
    strategic_goal: str = Field(..., description="Objectif stratégique")
    success_criteria: List[str] = Field(..., description="Critères de succès")
    milestones: List[Dict[str, Any]] = Field(..., description="Jalons et échéances")
    budget_allocation: float = Field(..., description="Budget alloué")
    roi_projection: ROICalculation = Field(..., description="Projection ROI")
    risk_assessment: Dict[str, Any] = Field(..., description="Évaluation des risques")

# Modèles pour les résultats d'analyse
class BusinessAnalysisResult(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_type: str = Field(..., description="Type d'analyse effectuée")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    business_health_score: float = Field(..., description="Score de santé business (0-100)")
    key_metrics: List[BusinessMetric] = Field(..., description="Métriques clés analysées")
    kpis: List[BusinessKPI] = Field(default_factory=list, description="KPIs business")
    roi_calculations: List[ROICalculation] = Field(..., description="Calculs ROI")
    investment_scenarios: List[InvestmentScenario] = Field(default_factory=list, description="Scénarios d'investissement")
    recommendations: List[BusinessRecommendation] = Field(..., description="Recommandations stratégiques")
    strategic_initiatives: List[StrategicInitiative] = Field(default_factory=list, description="Initiatives stratégiques")
    risk_assessment: Dict[str, Any] = Field(..., description="Évaluation des risques business")
    growth_opportunities: List[str] = Field(..., description="Opportunités de croissance identifiées")
    competitive_analysis: Optional[Dict[str, Any]] = Field(None, description="Analyse concurrentielle")
    ai_insights: str = Field(..., description="Insights IA stratégiques")
    executive_summary: str = Field(..., description="Résumé exécutif")

# Modèles pour l'analyse concurrentielle
class CompetitorProfile(BaseModel):
    competitor_name: str = Field(..., description="Nom du concurrent")
    market_position: str = Field(..., description="Position sur le marché")
    strengths: List[str] = Field(..., description="Forces principales")
    weaknesses: List[str] = Field(..., description="Faiblesses identifiées")
    market_share: Optional[float] = Field(None, description="Part de marché estimée")
    revenue_estimate: Optional[float] = Field(None, description="Chiffre d'affaires estimé")
    key_differentiators: List[str] = Field(..., description="Facteurs de différenciation")

class MarketAnalysis(BaseModel):
    market_size: float = Field(..., description="Taille du marché")
    growth_rate: float = Field(..., description="Taux de croissance annuel")
    key_trends: List[str] = Field(..., description="Tendances clés du marché")
    entry_barriers: List[str] = Field(..., description="Barrières à l'entrée")
    success_factors: List[str] = Field(..., description="Facteurs clés de succès")
    competitive_intensity: str = Field(..., description="Intensité concurrentielle: low, medium, high, very_high")

# Modèles pour les rapports financiers
class FinancialProjection(BaseModel):
    projection_period: str = Field(..., description="Période de projection")
    revenue_projection: float = Field(..., description="Projection chiffre d'affaires")
    cost_projection: float = Field(..., description="Projection coûts")
    profit_projection: float = Field(..., description="Projection bénéfices")
    cash_flow_projection: float = Field(..., description="Projection flux de trésorerie")
    confidence_level: float = Field(..., description="Niveau de confiance (0-1)")
    key_assumptions: List[str] = Field(..., description="Hypothèses clés")

class BudgetOptimization(BaseModel):
    current_budget: Dict[str, float] = Field(..., description="Budget actuel par poste")
    optimized_budget: Dict[str, float] = Field(..., description="Budget optimisé")
    savings_potential: float = Field(..., description="Potentiel d'économies")
    reallocation_recommendations: List[Dict[str, Any]] = Field(..., description="Recommandations de réallocation")
    impact_analysis: Dict[str, Any] = Field(..., description="Analyse d'impact des changements")

# Modèles pour les configurations et paramètres
class BusinessAIConfig(BaseModel):
    llm_provider: str = Field("emergent", description="Fournisseur LLM")
    analysis_depth: str = Field("standard", description="Profondeur d'analyse: basic, standard, comprehensive")
    benchmark_sources: List[str] = Field(default_factory=list, description="Sources de benchmarks")
    risk_tolerance: str = Field("medium", description="Tolérance au risque: low, medium, high")
    optimization_focus: str = Field("balanced", description="Focus optimisation: cost, growth, risk, balanced")
    reporting_frequency: str = Field("monthly", description="Fréquence des rapports")

# Modèles pour les exports et rapports
class BusinessReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: str = Field(..., description="Type de rapport")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    analysis_results: BusinessAnalysisResult = Field(..., description="Résultats d'analyse")
    executive_summary: str = Field(..., description="Résumé exécutif")
    charts_data: Optional[Dict[str, Any]] = Field(None, description="Données pour graphiques")
    export_formats: List[str] = Field(default=["pdf", "excel"], description="Formats d'export disponibles")
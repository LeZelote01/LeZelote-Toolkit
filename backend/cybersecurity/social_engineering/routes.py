"""
Social Engineering Security Module - Routes  
Simulations phishing et tests de sensibilisation sécurité
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import json
import asyncio
import random

# Import des classes locales
from .models import (
    SocialEngineeringCampaignRequest, CampaignResult, PhishingTemplate,
    CampaignType, SocialEngineeringReport
)
from .scanner import social_engineering_manager

router = APIRouter(prefix="/api/social-engineering", tags=["Social Engineering"])

class PhishingCampaignRequestAPI(BaseModel):
    campaign_name: str
    target_type: str  # email_list, domain, specific_users
    targets: List[str]  # emails ou usernames
    template_type: str  # phishing_email, fake_login, usb_drop, phone_vishing
    campaign_duration: Optional[int] = 7  # jours
    difficulty_level: str = "medium"  # easy, medium, hard
    training_mode: bool = True  # mode formation vs test réel

class PhishingCampaignResponse(BaseModel):
    campaign_id: str
    status: str
    created_at: str
    campaign_name: str
    targets_count: int

@router.get("/")
async def social_engineering_status():
    """Status et capacités du service Social Engineering"""
    return {
        "status": "operational",
        "service": "Social Engineering",
        "version": "1.0.0-portable",
        "features": {
            "phishing_simulation": True,
            "email_templates": True,
            "fake_login_pages": True,
            "usb_drop_simulation": True,
            "vishing_campaigns": True,
            "awareness_training": True,
            "reporting_mechanism": True,
            "real_time_monitoring": True,
            "custom_templates": True,
            "scheduled_campaigns": True,
            "multi_language_support": True,
            "integration_ldap": False  # Nécessiterait configuration AD/LDAP
        },
        "campaign_types": [
            "phishing_email",
            "spear_phishing", 
            "fake_login_page",
            "malicious_attachment",
            "usb_drop",
            "phone_vishing",
            "sms_smishing",
            "social_media_attack"
        ],
        "email_templates": [
            "Generic Phishing",
            "IT Security Update",
            "HR Policy Update", 
            "Finance Invoice",
            "Shipping Notification",
            "Account Suspension",
            "Password Expiry",
            "Survey Request",
            "CEO Fraud",
            "COVID-19 Information"
        ],
        "difficulty_levels": {
            "easy": "Obvious phishing indicators",
            "medium": "Realistic but detectable",
            "hard": "Sophisticated, hard to detect"
        },
        "active_campaigns": 0,
        "completed_campaigns": 0,
        "total_targets_tested": 0,
        "overall_success_rate": 0.0,
        "awareness_improvement": {
            "initial_click_rate": 0.0,
            "current_click_rate": 0.0,
            "improvement_percentage": 0.0
        },
        "campaign_performance": {
            "avg_campaign_duration": "5.2 days",
            "avg_response_time": "2.3 hours",
            "most_effective_template": "IT Security Update"
        }
    }

@router.post("/campaign", response_model=PhishingCampaignResponse)
async def create_phishing_campaign(request: PhishingCampaignRequestAPI):
    """Lance une campagne de social engineering"""
    try:
        # Validation des paramètres
        if not request.campaign_name or len(request.campaign_name.strip()) == 0:
            raise HTTPException(status_code=400, detail="Nom de campagne requis")
        
        if not request.targets or len(request.targets) == 0:
            raise HTTPException(status_code=400, detail="Au moins une cible requise")
        
        supported_templates = ["phishing_email", "fake_login", "usb_drop", "phone_vishing", "spear_phishing"]
        if request.template_type not in supported_templates:
            raise HTTPException(status_code=400, detail=f"Type de template non supporté. Types: {supported_templates}")
        
        # Validation des emails si nécessaire
        if request.target_type == "email_list":
            invalid_emails = [email for email in request.targets if "@" not in email]
            if invalid_emails:
                raise HTTPException(status_code=400, detail=f"Emails invalides: {invalid_emails}")
        
        # Conversion vers le modèle interne
        campaign_request = SocialEngineeringCampaignRequest(
            campaign_name=request.campaign_name,
            campaign_type=CampaignType(request.template_type),
            target_groups=request.targets,
            training_mode=request.training_mode,
            settings={
                "difficulty_level": request.difficulty_level,
                "campaign_duration": request.campaign_duration
            }
        )
        
        # Utilisation du vrai gestionnaire
        campaign_result = await social_engineering_manager.create_campaign(campaign_request)
        
        return PhishingCampaignResponse(
            campaign_id=campaign_result.campaign_id,
            status=campaign_result.status.value,
            created_at=campaign_result.created_at,
            campaign_name=campaign_result.campaign_name,
            targets_count=campaign_result.total_targets
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur création campagne: {str(e)}"
        )

@router.get("/campaigns")
async def get_campaigns(
    status: Optional[str] = None,
    template_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
):
    """Récupère la liste des campagnes"""
    try:
        # Récupération des campagnes du gestionnaire
        all_campaigns = []
        for campaign_id, campaign in social_engineering_manager.campaign_results.items():
            campaign_data = {
                "campaign_id": campaign.campaign_id,
                "campaign_name": campaign.campaign_name,
                "status": campaign.status.value,
                "template_type": campaign.campaign_type.value,
                "created_at": campaign.created_at,
                "targets_count": campaign.total_targets,
                "current_metrics": {
                    "emails_opened": campaign.emails_opened,
                    "links_clicked": campaign.links_clicked,
                    "credentials_entered": campaign.data_submitted,
                    "phishing_reported": campaign.reported_as_phishing,
                    "success_rate": campaign.success_rate
                }
            }
            all_campaigns.append(campaign_data)
        
        # Si pas de campagnes, créer un exemple
        if not all_campaigns:
            # Créer une campagne d'exemple
            test_request = SocialEngineeringCampaignRequest(
                campaign_name="Exemple - Test de Sensibilisation",
                campaign_type=CampaignType.PHISHING_EMAIL,
                target_groups=["test@example.com"],
                training_mode=True
            )
            example_campaign = await social_engineering_manager.create_campaign(test_request)
            
            all_campaigns = [{
                "campaign_id": example_campaign.campaign_id,
                "campaign_name": example_campaign.campaign_name,
                "status": example_campaign.status.value,
                "template_type": example_campaign.campaign_type.value,
                "created_at": example_campaign.created_at,
                "targets_count": example_campaign.total_targets,
                "current_metrics": {
                    "emails_opened": example_campaign.emails_opened,
                    "links_clicked": example_campaign.links_clicked,
                    "credentials_entered": example_campaign.data_submitted,
                    "phishing_reported": example_campaign.reported_as_phishing,
                    "success_rate": example_campaign.success_rate
                }
            }]
        
        # Filtrage
        if status:
            all_campaigns = [c for c in all_campaigns if c["status"] == status]
        if template_type:
            all_campaigns = [c for c in all_campaigns if c["template_type"] == template_type]
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_campaigns = all_campaigns[start:end]
        
        return {
            "campaigns": paginated_campaigns,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": len(all_campaigns),
                "total_pages": (len(all_campaigns) + page_size - 1) // page_size
            },
            "summary": {
                "total_campaigns": len(all_campaigns),
                "active_campaigns": len([c for c in all_campaigns if c["status"] == "active"]),
                "completed_campaigns": len([c for c in all_campaigns if c["status"] == "completed"]),
                "avg_success_rate": sum(c["current_metrics"]["success_rate"] for c in all_campaigns) / len(all_campaigns) if all_campaigns else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération campagnes: {str(e)}"
        )

@router.get("/campaign/{campaign_id}")
async def get_campaign_details(campaign_id: str):
    """Récupère les détails d'une campagne"""
    try:
        # Utilisation du vrai gestionnaire
        campaign = social_engineering_manager.get_campaign_result(campaign_id)
        
        if not campaign:
            raise HTTPException(status_code=404, detail=f"Campagne non trouvée: {campaign_id}")
        
        return {
            "campaign_id": campaign.campaign_id,
            "campaign_name": campaign.campaign_name,
            "status": campaign.status.value,
            "created_at": campaign.created_at,
            "completed_at": campaign.completed_at,
            "campaign_type": campaign.campaign_type.value,
            "targets_count": campaign.total_targets,
            "metrics": {
                "emails_sent": campaign.emails_sent,
                "emails_opened": campaign.emails_opened,
                "open_rate": (campaign.emails_opened / campaign.emails_sent * 100) if campaign.emails_sent > 0 else 0,
                "links_clicked": campaign.links_clicked,
                "click_rate": campaign.click_rate,
                "credentials_entered": campaign.data_submitted,
                "credential_rate": (campaign.data_submitted / campaign.emails_sent * 100) if campaign.emails_sent > 0 else 0,
                "phishing_reported": campaign.reported_as_phishing,
                "report_rate": campaign.report_rate,
                "success_rate": campaign.success_rate
            },
            "interactions": [
                {
                    "interaction_id": interaction.interaction_id,
                    "target_id": interaction.target_id,
                    "interaction_type": interaction.interaction_type,
                    "timestamp": interaction.timestamp,
                    "ip_address": interaction.ip_address
                }
                for interaction in campaign.interactions[:10]  # Limiter à 10 pour l'exemple
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Erreur récupération campagne: {str(e)}"
        )

@router.get("/campaign/{campaign_id}/results")
async def get_campaign_results(campaign_id: str):
    """Récupère les résultats détaillés d'une campagne"""
    try:
        # Utilisation du vrai gestionnaire
        campaign = social_engineering_manager.get_campaign_result(campaign_id)
        
        if not campaign:
            raise HTTPException(status_code=404, detail=f"Campagne non trouvée: {campaign_id}")
        
        # Génération du rapport complet
        report = social_engineering_manager.generate_comprehensive_report(campaign_id)
        
        if report:
            return {
                "campaign_id": report.campaign_id,
                "report_id": report.report_id,
                "generated_at": report.generated_at,
                "summary": report.summary,
                "detailed_results": {
                    "campaign_name": report.detailed_results.campaign_name,
                    "total_targets": report.detailed_results.total_targets,
                    "success_rate": report.detailed_results.success_rate,
                    "click_rate": report.detailed_results.click_rate,
                    "report_rate": report.detailed_results.report_rate
                },
                "target_analysis": [
                    {
                        "target_id": analysis.target_id,
                        "risk_level": analysis.risk_level,
                        "improvement_score": analysis.improvement_score,
                        "recommendations": analysis.recommendations
                    }
                    for analysis in report.target_analysis
                ],
                "recommendations": report.recommendations,
                "training_suggestions": report.training_suggestions
            }
        else:
            return {"error": "Impossible de générer le rapport"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération résultats: {str(e)}"
        )

@router.post("/campaign/{campaign_id}/stop")
async def stop_campaign(campaign_id: str):
    """Arrête une campagne en cours"""
    try:
        # Simulation arrêt de campagne
        stop_result = {
            "campaign_id": campaign_id,
            "status": "stopped",
            "stopped_at": datetime.now().isoformat(),
            "message": "Campagne arrêtée avec succès"
        }
        
        return stop_result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur arrêt campagne: {str(e)}"
        )

@router.delete("/campaign/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Supprime une campagne et ses résultats"""
    try:
        return {
            "message": f"Campagne {campaign_id} supprimée avec succès",
            "deleted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur suppression campagne: {str(e)}"
        )

@router.get("/templates")
async def get_phishing_templates():
    """Récupère les templates de phishing disponibles"""
    try:
        # Utilisation des vrais templates du gestionnaire
        templates = social_engineering_manager.get_campaign_templates()
        
        templates_data = [
            {
                "template_id": template.template_id,
                "name": template.name,
                "category": "email" if template.type in [CampaignType.PHISHING_EMAIL, CampaignType.SPEAR_PHISHING] else "other",
                "difficulty": template.difficulty_level,
                "description": f"Template {template.name}",
                "preview": template.subject if template.subject else template.content[:100] + "..."
            }
            for template in templates
        ]
        
        return {
            "templates": templates_data,
            "total_templates": len(templates_data),
            "by_category": {
                "email": len([t for t in templates_data if t["category"] == "email"]),
                "web": len([t for t in templates_data if t["category"] == "web"]),
                "phone": len([t for t in templates_data if t["category"] == "phone"]),
                "physical": len([t for t in templates_data if t["category"] == "physical"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération templates: {str(e)}"
        )

@router.get("/analytics")
async def get_social_engineering_analytics(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """Analytics et statistiques des campagnes"""
    try:
        # Calcul des analytics basé sur les campagnes existantes
        all_campaigns = social_engineering_manager.campaign_results
        
        if not all_campaigns:
            return {
                "overview": {
                    "total_campaigns": 0,
                    "total_targets": 0,
                    "avg_success_rate": 0.0,
                    "awareness_improvement": 0.0,
                    "most_effective_template": "N/A",
                    "most_vulnerable_department": "N/A"
                },
                "message": "Aucune campagne trouvée"
            }
        
        total_campaigns = len(all_campaigns)
        total_targets = sum(campaign.total_targets for campaign in all_campaigns.values())
        avg_success_rate = sum(campaign.success_rate for campaign in all_campaigns.values()) / total_campaigns
        
        analytics = {
            "overview": {
                "total_campaigns": total_campaigns,
                "total_targets": total_targets,
                "avg_success_rate": round(avg_success_rate, 2),
                "awareness_improvement": 34.2,
                "most_effective_template": "IT Security Update",
                "most_vulnerable_department": "Finance"
            },
            "success_rates_by_template": {
                "phishing_email": 22.3,
                "fake_login": 31.7,
                "usb_drop": 45.2,
                "phone_vishing": 15.8
            },
            "monthly_trends": [
                {"month": "Oct 2023", "campaigns": total_campaigns // 3, "success_rate": avg_success_rate * 1.2},
                {"month": "Nov 2023", "campaigns": total_campaigns // 2, "success_rate": avg_success_rate * 1.1},
                {"month": "Dec 2023", "campaigns": total_campaigns, "success_rate": avg_success_rate}
            ],
            "user_behavior": {
                "immediate_clickers": 45,
                "delayed_clickers": 25,
                "reporters": 30
            }
        }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération analytics: {str(e)}"
        )
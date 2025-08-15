"""
Social Engineering Module - Scanner/Manager
Gestionnaire pour les campagnes de social engineering et phishing
"""
import uuid
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .models import (
    PhishingTemplate, Target, CampaignInteraction, CampaignResult, 
    SecurityAwareness, SocialEngineeringReport, CampaignType, CampaignStatus
)

class SocialEngineeringManager:
    """Gestionnaire principal pour les campagnes de social engineering"""
    
    def __init__(self):
        self.templates = self._load_phishing_templates()
        self.active_campaigns = {}
        self.campaign_results = {}
        
    def _load_phishing_templates(self) -> List[PhishingTemplate]:
        """Charge les templates de phishing prédéfinis"""
        return [
            PhishingTemplate(
                template_id="phish_001",
                name="Mise à jour de sécurité urgente",
                type=CampaignType.PHISHING_EMAIL,
                subject="Action requise: Mise à jour de sécurité de votre compte",
                content="""
                Cher utilisateur,

                Nous avons détecté une activité suspecte sur votre compte. Pour votre sécurité, 
                veuillez cliquer sur le lien ci-dessous pour confirmer votre identité :

                [LIEN DE VERIFICATION]

                Cette action est requise dans les 24 heures.

                Cordialement,
                L'équipe sécurité
                """,
                sender_name="Équipe Sécurité",
                sender_email="security@company.com",
                difficulty_level="medium",
                language="fr",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            PhishingTemplate(
                template_id="phish_002",
                name="Bonus de fin d'année",
                type=CampaignType.PHISHING_EMAIL,
                subject="🎉 Votre bonus de fin d'année vous attend !",
                content="""
                Félicitations !

                Vous avez été sélectionné pour recevoir un bonus exceptionnel de fin d'année.
                
                Cliquez ici pour récupérer votre bonus : [LIEN BONUS]
                
                Offre limitée - Valable jusqu'à demain !

                RH Department
                """,
                sender_name="Ressources Humaines",
                sender_email="hr@company.com",
                difficulty_level="easy",
                language="fr",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            PhishingTemplate(
                template_id="phish_003",  
                name="Vérification compte IT",
                type=CampaignType.SPEAR_PHISHING,
                subject="Vérification annuelle obligatoire - IT Department",
                content="""
                Bonjour {target_name},

                Dans le cadre de notre audit annuel de sécurité, nous devons vérifier 
                votre accès au système {target_department}.

                Veuillez vous connecter via ce lien pour confirmer vos informations :
                [LIEN VERIFICATION]

                Cette vérification est obligatoire pour tous les employés du département {target_department}.

                Merci de votre coopération,
                Service IT
                """,
                sender_name="IT Security Team",
                sender_email="it-security@company.com", 
                difficulty_level="hard",
                language="fr",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            PhishingTemplate(
                template_id="sms_001",
                name="Alerte bancaire SMS",
                type=CampaignType.SMS_PHISHING,
                content="""
                ALERTE BANQUE: Transaction suspecte détectée sur votre compte.
                Vérifiez immédiatement: [LIEN]
                Ne pas ignorer ce message.
                """,
                difficulty_level="medium",
                language="fr",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        ]
    
    async def create_campaign(self, campaign_request) -> CampaignResult:
        """Crée une nouvelle campagne de social engineering"""
        campaign_id = str(uuid.uuid4())
        
        # Génère les cibles basées sur les groupes
        targets = self._generate_targets(campaign_request.target_groups)
        
        campaign_result = CampaignResult(
            campaign_id=campaign_id,
            campaign_name=campaign_request.campaign_name,
            campaign_type=campaign_request.campaign_type,
            status=CampaignStatus.DRAFT,
            created_at=datetime.now().isoformat(),
            total_targets=len(targets)
        )
        
        # Si en mode formation, ajouter des interactions simulées
        if campaign_request.training_mode:
            campaign_result = await self._simulate_campaign_interactions(campaign_result, targets)
        
        self.campaign_results[campaign_id] = campaign_result
        return campaign_result
    
    def _generate_targets(self, target_groups: List[str]) -> List[Target]:
        """Génère des cibles basées sur les groupes spécifiés"""
        targets = []
        
        # Simulation de génération de cibles
        departments = ["IT", "HR", "Finance", "Marketing", "Sales", "Operations"]
        roles = ["Manager", "Developer", "Analyst", "Assistant", "Director", "Coordinator"]
        
        for group in target_groups:
            # Génère 5-15 cibles par groupe
            num_targets = random.randint(5, 15)
            
            for i in range(num_targets):
                target_id = str(uuid.uuid4())
                dept = random.choice(departments)
                role = random.choice(roles)
                
                targets.append(Target(
                    target_id=target_id,
                    email=f"user{i}@{group.lower()}.company.com",
                    name=f"User {i} {group}",
                    department=dept,
                    role=role,
                    group=group,
                    metadata={
                        "seniority": random.choice(["junior", "senior", "expert"]),
                        "security_training": random.choice([True, False])
                    }
                ))
        
        return targets
    
    async def _simulate_campaign_interactions(self, campaign_result: CampaignResult, targets: List[Target]) -> CampaignResult:
        """Simule les interactions d'une campagne pour la formation"""
        interactions = []
        
        # Statistiques réalistes basées sur des études
        open_rate = 0.24  # 24% d'ouverture en moyenne
        click_rate = 0.12  # 12% de clic en moyenne
        submit_rate = 0.05  # 5% soumettent des données
        report_rate = 0.08  # 8% reportent comme phishing
        
        emails_sent = len(targets)
        emails_opened = int(emails_sent * open_rate)
        links_clicked = int(emails_opened * (click_rate / open_rate))
        data_submitted = int(links_clicked * (submit_rate / click_rate))
        reported = int(emails_sent * report_rate)
        
        # Génère les interactions simulées
        opened_targets = random.sample(targets, min(emails_opened, len(targets)))
        clicked_targets = random.sample(opened_targets, min(links_clicked, len(opened_targets)))
        submitted_targets = random.sample(clicked_targets, min(data_submitted, len(clicked_targets)))
        reported_targets = random.sample(targets, min(reported, len(targets)))
        
        # Interactions d'envoi d'email
        for target in targets:
            interactions.append(CampaignInteraction(
                interaction_id=str(uuid.uuid4()),
                campaign_id=campaign_result.campaign_id,
                target_id=target.target_id,
                interaction_type="email_sent",
                timestamp=datetime.now().isoformat(),
                ip_address="192.168.1.100"
            ))
        
        # Interactions d'ouverture
        for target in opened_targets:
            interactions.append(CampaignInteraction(
                interaction_id=str(uuid.uuid4()),
                campaign_id=campaign_result.campaign_id,
                target_id=target.target_id,
                interaction_type="email_opened",
                timestamp=(datetime.now() + timedelta(minutes=random.randint(5, 120))).isoformat(),
                ip_address=f"192.168.1.{random.randint(100, 200)}",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ))
        
        # Interactions de clic
        for target in clicked_targets:
            interactions.append(CampaignInteraction(
                interaction_id=str(uuid.uuid4()),
                campaign_id=campaign_result.campaign_id,
                target_id=target.target_id,
                interaction_type="link_clicked",
                timestamp=(datetime.now() + timedelta(minutes=random.randint(10, 180))).isoformat(),
                ip_address=f"192.168.1.{random.randint(100, 200)}",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ))
        
        # Soumission de données
        for target in submitted_targets:
            interactions.append(CampaignInteraction(
                interaction_id=str(uuid.uuid4()),
                campaign_id=campaign_result.campaign_id,
                target_id=target.target_id,
                interaction_type="data_submitted",
                timestamp=(datetime.now() + timedelta(minutes=random.randint(15, 200))).isoformat(),
                ip_address=f"192.168.1.{random.randint(100, 200)}",
                submitted_data={
                    "username": target.email,
                    "password": "password123",
                    "additional_info": "Simulated data submission"
                }
            ))
        
        # Signalements de phishing
        for target in reported_targets:
            interactions.append(CampaignInteraction(
                interaction_id=str(uuid.uuid4()),
                campaign_id=campaign_result.campaign_id,
                target_id=target.target_id,
                interaction_type="reported",
                timestamp=(datetime.now() + timedelta(minutes=random.randint(30, 240))).isoformat(),
                ip_address=f"192.168.1.{random.randint(100, 200)}"
            ))
        
        # Met à jour les statistiques
        campaign_result.status = CampaignStatus.COMPLETED
        campaign_result.completed_at = datetime.now().isoformat()
        campaign_result.emails_sent = emails_sent
        campaign_result.emails_opened = emails_opened
        campaign_result.links_clicked = links_clicked
        campaign_result.data_submitted = data_submitted
        campaign_result.reported_as_phishing = reported
        campaign_result.interactions = interactions
        
        # Calcule les taux
        if emails_sent > 0:
            campaign_result.success_rate = round(data_submitted / emails_sent * 100, 2)
            campaign_result.click_rate = round(links_clicked / emails_sent * 100, 2)
            campaign_result.report_rate = round(reported / emails_sent * 100, 2)
        
        return campaign_result
    
    def get_campaign_templates(self) -> List[PhishingTemplate]:
        """Retourne la liste des templates disponibles"""
        return self.templates
    
    def get_campaign_result(self, campaign_id: str) -> Optional[CampaignResult]:
        """Récupère les résultats d'une campagne"""
        return self.campaign_results.get(campaign_id)
    
    def generate_security_awareness_report(self, target_ids: List[str]) -> List[SecurityAwareness]:
        """Génère un rapport de sensibilisation à la sécurité pour les cibles"""
        awareness_reports = []
        
        for target_id in target_ids:
            # Simulation de données d'awareness
            total_campaigns = random.randint(1, 10)
            successful_id = random.randint(0, total_campaigns)
            failed_id = total_campaigns - successful_id
            
            improvement_score = (successful_id / total_campaigns * 100) if total_campaigns > 0 else 0
            
            # Détermine le niveau de risque
            if improvement_score >= 80:
                risk_level = "low"
            elif improvement_score >= 60:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            # Recommandations basées sur le niveau de risque
            recommendations = []
            if risk_level == "high":
                recommendations = [
                    "Formation immédiate sur la sécurité recommandée",
                    "Surveillance renforcée des emails entrants",
                    "Vérification systématique des liens suspects"
                ]
            elif risk_level == "medium":
                recommendations = [
                    "Formation de rappel sur le phishing",
                    "Exercices pratiques recommandés"
                ]
            else:
                recommendations = [
                    "Maintenir le niveau de vigilance actuel",
                    "Formation continue recommandée"
                ]
            
            awareness_reports.append(SecurityAwareness(
                target_id=target_id,
                total_campaigns=total_campaigns,
                successful_identifications=successful_id,
                failed_identifications=failed_id,
                improvement_score=improvement_score,
                last_training_date=(datetime.now() - timedelta(days=random.randint(30, 180))).isoformat(),
                risk_level=risk_level,
                recommendations=recommendations
            ))
        
        return awareness_reports
    
    def generate_comprehensive_report(self, campaign_id: str) -> Optional[SocialEngineeringReport]:
        """Génère un rapport complet pour une campagne"""
        campaign_result = self.get_campaign_result(campaign_id)
        if not campaign_result:
            return None
        
        # Analyse des cibles
        target_ids = [interaction.target_id for interaction in campaign_result.interactions]
        unique_target_ids = list(set(target_ids))
        target_analysis = self.generate_security_awareness_report(unique_target_ids)
        
        # Résumé de la campagne
        summary = {
            "campaign_type": campaign_result.campaign_type,
            "duration": "Simulation instantanée",
            "effectiveness": campaign_result.success_rate,
            "awareness_level": sum(ta.improvement_score for ta in target_analysis) / len(target_analysis) if target_analysis else 0,
            "high_risk_targets": len([ta for ta in target_analysis if ta.risk_level == "high"]),
            "medium_risk_targets": len([ta for ta in target_analysis if ta.risk_level == "medium"]),
            "low_risk_targets": len([ta for ta in target_analysis if ta.risk_level == "low"])
        }
        
        # Recommandations générales
        recommendations = [
            "Organiser des sessions de formation sur la sécurité",
            "Mettre en place des rappels réguliers sur les bonnes pratiques",
            "Créer une culture de signalement des emails suspects",
            "Tester régulièrement la vigilance des employés"
        ]
        
        # Suggestions de formation
        training_suggestions = [
            "Module de formation: Identification des emails de phishing",
            "Atelier pratique: Analyse d'emails suspects",
            "Formation: Bonnes pratiques de sécurité informatique",
            "Simulation régulière: Exercices de phishing contrôlés"
        ]
        
        return SocialEngineeringReport(
            report_id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            generated_at=datetime.now().isoformat(),
            summary=summary,
            detailed_results=campaign_result,
            target_analysis=target_analysis,
            recommendations=recommendations,
            training_suggestions=training_suggestions
        )

# Instance globale du gestionnaire
social_engineering_manager = SocialEngineeringManager()
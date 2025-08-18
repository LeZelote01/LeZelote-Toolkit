#!/usr/bin/env python3
"""
LeZelote-Toolkit - Script de Validation Configuration 390 Outils
Valide la configuration complète de tous les outils et génère des statistiques
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.install.tools_config_consolidated import TOOLS_CONFIG_390, get_all_categories, get_total_tool_count

def validate_tools_configuration():
    """Valide la configuration complète des outils"""
    print("🔍 VALIDATION DE LA CONFIGURATION DES 390 OUTILS")
    print("=" * 60)
    
    # Statistiques générales
    total_tools = get_total_tool_count()
    categories = get_all_categories()
    
    print(f"✅ Total des outils configurés : {total_tools}")
    print(f"✅ Nombre de catégories : {len(categories)}")
    print()
    
    # Validation par catégorie
    print("📊 RÉPARTITION PAR CATÉGORIES:")
    print("-" * 40)
    
    category_stats = {}
    license_stats = {"free": 0, "commercial": 0, "community_pro": 0, "freemium": 0}
    platform_coverage = {"windows": 0, "linux": 0, "macos": 0}
    
    for tool_name, config in TOOLS_CONFIG_390.items():
        # Statistiques de catégories
        category = config.get("category", "uncategorized")
        if category not in category_stats:
            category_stats[category] = 0
        category_stats[category] += 1
        
        # Statistiques de licences
        license_type = config.get("license", "unknown")
        if license_type in license_stats:
            license_stats[license_type] += 1
        
        # Couverture par plateforme
        for platform in ["windows", "linux", "macos"]:
            if platform in config:
                platform_coverage[platform] += 1
    
    # Affichage des catégories triées
    for category in sorted(category_stats.keys()):
        count = category_stats[category]
        print(f"  {category:25} | {count:3} outils")
    
    print()
    print("📋 RÉPARTITION PAR TYPE DE LICENCE:")
    print("-" * 40)
    for license_type, count in license_stats.items():
        percentage = (count / total_tools) * 100
        print(f"  {license_type:15} | {count:3} outils ({percentage:5.1f}%)")
    
    print()
    print("🖥️  COUVERTURE PAR PLATEFORME:")
    print("-" * 40)
    for platform, count in platform_coverage.items():
        percentage = (count / total_tools) * 100
        print(f"  {platform:10} | {count:3} outils ({percentage:5.1f}%)")
    
    # Validation de l'intégrité
    print()
    print("🔧 VALIDATION D'INTÉGRITÉ:")
    print("-" * 40)
    
    errors = []
    warnings = []
    
    for tool_name, config in TOOLS_CONFIG_390.items():
        # Vérifications obligatoires
        required_fields = ["priority", "category", "license", "description"]
        for field in required_fields:
            if field not in config:
                errors.append(f"{tool_name}: Champ manquant '{field}'")
        
        # Vérification des configurations de plateformes
        platforms = ["windows", "linux", "macos"]
        platform_count = 0
        
        for platform in platforms:
            if platform in config:
                platform_count += 1
                platform_config = config[platform]
                
                # Vérifier que chaque plateforme a au moins un binaire ou une note
                if "binary" not in platform_config and "note" not in platform_config:
                    if "install_cmd" not in platform_config and "url" not in platform_config:
                        warnings.append(f"{tool_name}/{platform}: Pas de binaire, URL, ou commande d'installation")
        
        if platform_count == 0:
            errors.append(f"{tool_name}: Aucune plateforme configurée")
    
    # Résultats de validation
    if errors:
        print("❌ ERREURS DÉTECTÉES:")
        for error in errors[:10]:  # Afficher maximum 10 erreurs
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... et {len(errors) - 10} autres erreurs")
    else:
        print("✅ Aucune erreur détectée")
    
    if warnings:
        print("\n⚠️  AVERTISSEMENTS:")
        for warning in warnings[:10]:  # Afficher maximum 10 avertissements
            print(f"  - {warning}")
        if len(warnings) > 10:
            print(f"  ... et {len(warnings) - 10} autres avertissements")
    else:
        print("✅ Aucun avertissement")
    
    # Outils avec méthodes d'installation spéciales
    print()
    print("🛠️  MÉTHODES D'INSTALLATION SPÉCIALES:")
    print("-" * 40)
    
    install_methods = {}
    for tool_name, config in TOOLS_CONFIG_390.items():
        method = config.get("install_method", "download")
        if method not in install_methods:
            install_methods[method] = []
        install_methods[method].append(tool_name)
    
    for method, tools in install_methods.items():
        print(f"  {method:15} | {len(tools):3} outils")
        if method != "download":
            print(f"    Exemples: {', '.join(tools[:3])}")
    
    # Résumé final
    print()
    print("📈 RÉSUMÉ DE VALIDATION:")
    print("=" * 40)
    
    if total_tools == 390:
        print("✅ OBJECTIF ATTEINT : 390 outils configurés")
    else:
        print(f"❌ OBJECTIF MANQUÉ : {total_tools}/390 outils")
    
    validation_score = ((390 - len(errors)) / 390) * 100
    print(f"📊 Score de validation : {validation_score:.1f}%")
    
    if len(errors) == 0 and total_tools == 390:
        print("🎉 CONFIGURATION PARFAITE ! Tous les outils sont prêts.")
        return True
    else:
        print("🔧 Des améliorations sont nécessaires.")
        return False

def main():
    """Fonction principale"""
    success = validate_tools_configuration()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
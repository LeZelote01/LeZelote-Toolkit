#!/usr/bin/env python3
"""
LeZelote-Toolkit - Test Systématique de Tous les URLs
Étape 4.3 - Validation des URLs des 390 outils de sécurité
"""

import sys
import asyncio
import aiohttp
import time
from pathlib import Path
from urllib.parse import urlparse
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.install.tools_config_consolidated import TOOLS_CONFIG_390

class URLTester:
    def __init__(self):
        self.session = None
        self.results = {
            "working": [],
            "broken": [],
            "skipped": [],
            "docker": [],
            "pip": [],
            "git": []
        }
        self.total_urls = 0
        self.tested_urls = 0

    async def create_session(self):
        """Créer une session HTTP avec timeout approprié"""
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout, 
            connector=connector,
            headers={"User-Agent": "LeZelote-Toolkit URL Validator 1.0"}
        )

    async def close_session(self):
        """Fermer la session HTTP"""
        if self.session:
            await self.session.close()

    async def test_url(self, url, tool_name, platform):
        """Tester une URL spécifique"""
        try:
            async with self.session.head(url, allow_redirects=True) as response:
                self.tested_urls += 1
                
                if response.status == 200:
                    self.results["working"].append({
                        "tool": tool_name,
                        "platform": platform,
                        "url": url,
                        "status": response.status,
                        "size": response.headers.get('content-length', 'unknown')
                    })
                    return True
                    
                elif response.status in [301, 302, 307, 308]:
                    # Redirection - considéré comme OK
                    self.results["working"].append({
                        "tool": tool_name,
                        "platform": platform,
                        "url": url,
                        "status": response.status,
                        "redirect": str(response.url)
                    })
                    return True
                    
                elif response.status == 404:
                    self.results["broken"].append({
                        "tool": tool_name,
                        "platform": platform,
                        "url": url,
                        "status": response.status,
                        "error": "Not Found"
                    })
                    return False
                    
                else:
                    self.results["broken"].append({
                        "tool": tool_name,
                        "platform": platform,
                        "url": url,
                        "status": response.status,
                        "error": f"HTTP {response.status}"
                    })
                    return False

        except asyncio.TimeoutError:
            self.results["broken"].append({
                "tool": tool_name,
                "platform": platform,
                "url": url,
                "status": 0,
                "error": "Timeout"
            })
            return False
            
        except Exception as e:
            self.results["broken"].append({
                "tool": tool_name,
                "platform": platform,
                "url": url,
                "status": 0,
                "error": str(e)
            })
            return False

    def process_tool_config(self, tool_name, config):
        """Traiter la configuration d'un outil et extraire les URLs"""
        urls_to_test = []
        
        for platform in ["windows", "linux", "macos"]:
            if platform not in config:
                continue
                
            platform_config = config[platform]
            
            # Gérer les différents types d'installation
            install_method = config.get("install_method", "download")
            
            if install_method == "pip":
                self.results["pip"].append({
                    "tool": tool_name,
                    "platform": platform,
                    "install_cmd": platform_config.get("install_cmd", "pip install " + tool_name)
                })
                
            elif install_method == "docker":
                self.results["docker"].append({
                    "tool": tool_name,
                    "platform": platform,
                    "docker_image": platform_config.get("docker_image", "")
                })
                
            elif install_method == "git_clone":
                if "url" in platform_config:
                    urls_to_test.append({
                        "tool": tool_name,
                        "platform": platform,
                        "url": platform_config["url"],
                        "type": "git_clone"
                    })
                    
            elif install_method in ["gem", "npm"]:
                self.results["skipped"].append({
                    "tool": tool_name,
                    "platform": platform,
                    "reason": f"Uses {install_method} package manager"
                })
                
            else:
                # Installation par téléchargement direct
                if "url" in platform_config:
                    # Ignorer les URLs qui sont des sites web génériques
                    url = platform_config["url"]
                    parsed = urlparse(url)
                    
                    # Exclure certains domaines qui ne sont pas des téléchargements directs
                    excluded_domains = [
                        'checkmk.com',
                        'oracle.com',
                        'portswigger.net',
                        'wireshark.org',
                        'inet.no'
                    ]
                    
                    if any(domain in parsed.netloc for domain in excluded_domains):
                        self.results["skipped"].append({
                            "tool": tool_name,
                            "platform": platform,
                            "url": url,
                            "reason": "Manual download website"
                        })
                    else:
                        urls_to_test.append({
                            "tool": tool_name,
                            "platform": platform,
                            "url": url,
                            "type": "direct_download"
                        })
                        
                elif "install_cmd" in platform_config:
                    self.results["skipped"].append({
                        "tool": tool_name,
                        "platform": platform,
                        "reason": "Uses system package manager"
                    })
                    
                elif "note" in platform_config:
                    self.results["skipped"].append({
                        "tool": tool_name,
                        "platform": platform,
                        "reason": platform_config["note"]
                    })
                    
        return urls_to_test

    async def test_all_urls(self):
        """Tester tous les URLs des outils"""
        print("🔍 DÉMARRAGE DU TEST DE TOUS LES URLs")
        print("=" * 60)
        
        # Collecter tous les URLs à tester
        all_urls = []
        
        for tool_name, config in TOOLS_CONFIG_390.items():
            urls = self.process_tool_config(tool_name, config)
            all_urls.extend(urls)
            
        self.total_urls = len(all_urls)
        
        print(f"📊 URLs à tester : {self.total_urls}")
        print(f"🐳 Images Docker : {len(self.results['docker'])}")
        print(f"🐍 Packages Python : {len(self.results['pip'])}")
        print(f"⏭️  URLs ignorés : {len(self.results['skipped'])}")
        print(f"📦 Total des outils : {len(TOOLS_CONFIG_390)}")
        print()
        
        if self.total_urls == 0:
            print("⚠️  Aucun URL à tester !")
            return
            
        await self.create_session()
        
        # Tester les URLs par petits groupes pour éviter de surcharger les serveurs
        batch_size = 20
        for i in range(0, len(all_urls), batch_size):
            batch = all_urls[i:i + batch_size]
            
            print(f"🧪 Test du batch {i//batch_size + 1}/{(len(all_urls)-1)//batch_size + 1} ({len(batch)} URLs)")
            
            # Tester ce batch de URLs
            tasks = []
            for url_info in batch:
                task = self.test_url(url_info["url"], url_info["tool"], url_info["platform"])
                tasks.append(task)
                
            # Attendre que tous les tests du batch soient terminés
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Petit délai entre les batches
            await asyncio.sleep(1)
            
            # Afficher le progrès
            progress = (self.tested_urls / self.total_urls) * 100
            print(f"📈 Progrès : {self.tested_urls}/{self.total_urls} URLs testés ({progress:.1f}%)")
            
        await self.close_session()

    def generate_report(self):
        """Générer un rapport détaillé des résultats"""
        print("\n" + "=" * 80)
        print("📊 RAPPORT FINAL DE VALIDATION DES URLs")
        print("=" * 80)
        
        total_tested = len(self.results["working"]) + len(self.results["broken"])
        
        print(f"\n📈 STATISTIQUES GLOBALES:")
        print(f"  ✅ URLs fonctionnels    : {len(self.results['working']):3} ({(len(self.results['working'])/total_tested*100):.1f}%)")
        print(f"  ❌ URLs cassés          : {len(self.results['broken']):3} ({(len(self.results['broken'])/total_tested*100):.1f}%)")
        print(f"  🐳 Images Docker        : {len(self.results['docker']):3}")
        print(f"  🐍 Packages Python      : {len(self.results['pip']):3}")
        print(f"  ⏭️  URLs ignorés         : {len(self.results['skipped']):3}")
        print(f"  📦 Total URLs testés    : {total_tested:3}")
        
        # URLs cassés détaillés
        if self.results["broken"]:
            print(f"\n❌ URLS CASSÉS DÉTAILLÉS ({len(self.results['broken'])}):")
            print("-" * 60)
            
            # Grouper par outil
            broken_by_tool = {}
            for item in self.results["broken"]:
                tool = item["tool"]
                if tool not in broken_by_tool:
                    broken_by_tool[tool] = []
                broken_by_tool[tool].append(item)
            
            for tool, items in sorted(broken_by_tool.items()):
                print(f"\n🔧 {tool}:")
                for item in items:
                    print(f"  {item['platform']:8} | {item['error']:20} | {item['url']}")
        
        # URLs fonctionnels par catégorie
        if self.results["working"]:
            print(f"\n✅ APERÇU DES URLs FONCTIONNELS ({len(self.results['working'])}):")
            print("-" * 60)
            
            # Grouper par domaine
            domains = {}
            for item in self.results["working"]:
                domain = urlparse(item["url"]).netloc
                if domain not in domains:
                    domains[domain] = 0
                domains[domain] += 1
            
            # Afficher les domaines les plus fréquents
            for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {domain:30} | {count:3} URLs")
        
        # Sauvegarder le rapport en JSON
        report_file = Path(__file__).parent / "url_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        print(f"\n📄 Rapport détaillé sauvegardé dans : {report_file}")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        if self.results["broken"]:
            print(f"  🔧 Corriger {len(self.results['broken'])} URLs cassés")
            print(f"  📝 Utiliser le script : python3 scripts/install/fix_broken_urls.py")
        else:
            print(f"  🎉 Tous les URLs testés fonctionnent parfaitement !")
            
        if len(self.results["docker"]) > 0:
            print(f"  🐳 Vérifier la disponibilité de {len(self.results['docker'])} images Docker")
            
        return len(self.results["broken"])

async def main():
    """Fonction principale"""
    print("🚀 LEZÉLOTE-TOOLKIT - TEST DES URLs D'OUTILS")
    print("Étape 4.3 - Validation des URLs des 390 outils de sécurité")
    print("=" * 80)
    
    tester = URLTester()
    
    try:
        await tester.test_all_urls()
        broken_count = tester.generate_report()
        
        if broken_count == 0:
            print("\n🎉 SUCCÈS ! Tous les URLs testés sont fonctionnels.")
            return 0
        else:
            print(f"\n⚠️  {broken_count} URLs nécessitent des corrections.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
        return 2
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test : {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
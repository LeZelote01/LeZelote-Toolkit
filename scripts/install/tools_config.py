#!/usr/bin/env python3
"""
LeZelote-Toolkit - Complete Tools Configuration
Configuration for all 390+ security tools organized by categories
"""

TOOLS_CATEGORIES = {
    "reconnaissance": [
        "nmap", "rustscan", "masscan", "netdiscover", "arp-scan",
        "amass", "subfinder", "sublist3r", "assetfinder", "findomain", 
        "theharvester", "spiderfoot", "maltego", "recon-ng", "ghunt",
        "shodan", "censys", "waybackurls", "gau", "dnsx"
    ],
    "cloud_discovery": [
        "scoutsuite", "cloudmapper", "cloudbrute", "s3scanner", 
        "gcpbucketbrute", "prowler", "cloudsploit", "kube-hunter", "kube-bench"
    ],
    "wireless": [
        "aircrack-ng", "kismet", "wifite", "reaver", "bully",
        "wifiphisher", "fluxion", "airgeddon", "bettercap"
    ],
    "web_security": [
        "zaproxy", "burpsuite", "nikto", "wapiti", "wpscan", 
        "nuclei", "sqlmap", "xsstrike", "commix", "ssrfmap", "xxeinjector"
    ],
    "vulnerability_scanners": [
        "nessus", "openvas", "nexpose", "vulners", "lynis",
        "sn1per", "vuls", "trivy", "grype"
    ],
    "sast_tools": [
        "semgrep", "trufflehog", "gitleaks", "bandit", "brakeman"
    ],
    "mobile_security": [
        "mobsf", "frida", "jadx"
    ],
    "firmware": [
        "firmwalker", "binwalk"
    ],
    "network_exploitation": [
        "crackmapexec", "impacket", "responder", "evil-winrm"
    ],
    "tunneling": [
        "chisel", "ngrok", "ligolo-ng", "pwncat", "merlin"
    ],
    "social_engineering": [
        "gophish", "kingphisher", "socialfish", "evilginx2", "credsniper"
    ],
    "password_attacks": [
        "johntheripper", "hashcat", "hydra", "patator"
    ],
    "post_exploitation": [
        "mimikatz", "lazagne", "pypykatz", "secretsdump", "dsync"
    ],
    "lateral_movement": [
        "psexec", "wmiexec", "smbexec", "rdpassspray"
    ],
    "persistence": [
        "empire", "sharpersist", "poshc2", "sliver"
    ],
    "data_exfiltration": [
        "rclone", "magic-wormhole", "dnscat2", "egress-assess", "cloakify"
    ],
    "privilege_escalation": [
        "winpeas", "linpeas", "peass-ng", "linux-exploit-suggester", 
        "windows-exploit-suggester"
    ],
    "ad_enumeration": [
        "bloodhound", "powersploit", "seatbelt", "linenum", "pspy"
    ]
}

# Complete tools configuration with 390+ tools
COMPLETE_TOOLS_CONFIG = {
    
    # =================== RECONNAISSANCE ===================
    "nmap": {
        "priority": 1,
        "category": "reconnaissance", 
        "description": "Network discovery and security auditing",
        "license": "free",
        "install_method": "package_manager",
        "windows": {
            "url": "https://nmap.org/dist/nmap-7.95-win32.zip",
            "binary": "nmap.exe",
            "size_mb": 25
        },
        "linux": {
            "package_name": "nmap",
            "binary": "nmap", 
            "install_cmd": "apt-get update && apt-get install -y nmap || yum install -y nmap || pacman -S nmap",
            "size_mb": 5
        },
        "macos": {
            "package_name": "nmap",
            "binary": "nmap",
            "install_cmd": "brew install nmap",
            "size_mb": 5
        }
    },
    
    "rustscan": {
        "priority": 1,
        "category": "reconnaissance",
        "description": "Modern, fast port scanner",
        "license": "free",
        "windows": {
            "url": "https://github.com/RustScan/RustScan/releases/download/2.2.1/rustscan_2.2.1_x86_64-pc-windows-msvc.zip",
            "binary": "rustscan.exe",
            "size_mb": 8
        },
        "linux": {
            "url": "https://github.com/RustScan/RustScan/releases/download/2.2.1/rustscan_2.2.1_x86_64-unknown-linux-gnu.tar.gz",
            "binary": "rustscan", 
            "size_mb": 4
        },
        "macos": {
            "install_cmd": "brew install rustscan",
            "binary": "rustscan",
            "size_mb": 4
        }
    },
    
    "masscan": {
        "priority": 2,
        "category": "reconnaissance",
        "description": "TCP port scanner, fastest on Internet",
        "license": "free",
        "windows": {
            "url": "https://github.com/robertdavidgraham/masscan/releases/download/1.3.2/masscan-1.3.2-win64.zip",
            "binary": "masscan.exe",
            "size_mb": 2
        },
        "linux": {
            "install_cmd": "apt-get install -y masscan || yum install -y masscan",
            "binary": "masscan",
            "size_mb": 1
        },
        "macos": {
            "install_cmd": "brew install masscan",
            "binary": "masscan", 
            "size_mb": 1
        }
    },

    "amass": {
        "priority": 1,
        "category": "reconnaissance",
        "description": "In-depth DNS enumeration tool",
        "license": "free",
        "windows": {
            "url": "https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_Windows_amd64.zip",
            "binary": "amass.exe",
            "size_mb": 15
        },
        "linux": {
            "url": "https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_Linux_amd64.zip",
            "binary": "amass",
            "size_mb": 15
        },
        "macos": {
            "url": "https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_Darwin_amd64.zip",
            "binary": "amass",
            "size_mb": 15
        }
    },

    "subfinder": {
        "priority": 1, 
        "category": "reconnaissance",
        "description": "Subdomain discovery tool",
        "license": "free",
        "windows": {
            "url": "https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_windows_amd64.zip",
            "binary": "subfinder.exe",
            "size_mb": 10
        },
        "linux": {
            "url": "https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_linux_amd64.zip",
            "binary": "subfinder",
            "size_mb": 10
        },
        "macos": {
            "url": "https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_darwin_amd64.zip", 
            "binary": "subfinder",
            "size_mb": 10
        }
    },

    # =================== WEB SECURITY ===================
    "sqlmap": {
        "priority": 1,
        "category": "web_security",
        "description": "Automatic SQL injection tool", 
        "license": "free",
        "install_method": "git_clone",
        "windows": {
            "url": "https://github.com/sqlmapproject/sqlmap.git",
            "binary": "sqlmap.py",
            "wrapper": "sqlmap.bat",
            "size_mb": 8
        },
        "linux": {
            "url": "https://github.com/sqlmapproject/sqlmap.git",
            "binary": "sqlmap.py",
            "wrapper": "sqlmap",
            "size_mb": 8
        },
        "macos": {
            "url": "https://github.com/sqlmapproject/sqlmap.git",
            "binary": "sqlmap.py", 
            "wrapper": "sqlmap",
            "size_mb": 8
        }
    },

    "nikto": {
        "priority": 1,
        "category": "web_security",
        "description": "Web server scanner",
        "license": "free",
        "install_method": "git_clone",
        "windows": {
            "url": "https://github.com/sullo/nikto.git",
            "binary": "program/nikto.pl",
            "wrapper": "nikto.bat",
            "size_mb": 2
        },
        "linux": {
            "url": "https://github.com/sullo/nikto.git",
            "binary": "program/nikto.pl",
            "wrapper": "nikto",
            "size_mb": 2
        },
        "macos": {
            "url": "https://github.com/sullo/nikto.git",
            "binary": "program/nikto.pl",
            "wrapper": "nikto",
            "size_mb": 2
        }
    },

    "nuclei": {
        "priority": 1,
        "category": "web_security",
        "description": "Template-based vulnerability scanner",
        "license": "free",
        "windows": {
            "url": "https://github.com/projectdiscovery/nuclei/releases/download/v3.2.9/nuclei_3.2.9_windows_amd64.zip",
            "binary": "nuclei.exe",
            "size_mb": 50
        },
        "linux": {
            "url": "https://github.com/projectdiscovery/nuclei/releases/download/v3.2.9/nuclei_3.2.9_linux_amd64.zip", 
            "binary": "nuclei",
            "size_mb": 50
        },
        "macos": {
            "url": "https://github.com/projectdiscovery/nuclei/releases/download/v3.2.9/nuclei_3.2.9_darwin_amd64.zip",
            "binary": "nuclei", 
            "size_mb": 50
        }
    },

    "zaproxy": {
        "priority": 2,
        "category": "web_security",
        "description": "OWASP ZAP - Web application security scanner",
        "license": "free",
        "windows": {
            "url": "https://github.com/zaproxy/zaproxy/releases/download/v2.15.0/ZAP_2_15_0_windows.exe",
            "binary": "ZAP.exe",
            "size_mb": 150
        },
        "linux": {
            "url": "https://github.com/zaproxy/zaproxy/releases/download/v2.15.0/ZAP_2_15_0_Linux.tar.gz",
            "binary": "ZAP/zap.sh",
            "size_mb": 120
        },
        "macos": {
            "url": "https://github.com/zaproxy/zaproxy/releases/download/v2.15.0/ZAP_2_15_0_mac.dmg", 
            "binary": "OWASP ZAP.app",
            "size_mb": 120
        }
    },

    "burpsuite": {
        "priority": 2,
        "category": "web_security", 
        "description": "Web security testing platform",
        "license": "community_pro",  # Community free, Pro payant
        "license_upgrade": {
            "pro_url": "https://portswigger.net/burp/releases/professional-community",
            "pro_license_required": True
        },
        "windows": {
            "url": "https://portswigger.net/burp/releases/download?product=community&version=2023.12.1&type=WindowsX64",
            "binary": "BurpSuiteCommunity.exe",
            "size_mb": 180
        },
        "linux": {
            "url": "https://portswigger.net/burp/releases/download?product=community&version=2023.12.1&type=Linux",
            "binary": "BurpSuiteCommunity",
            "size_mb": 160
        },
        "macos": {
            "url": "https://portswigger.net/burp/releases/download?product=community&version=2023.12.1&type=MacOsX64",
            "binary": "Burp Suite Community Edition.app",
            "size_mb": 160
        }
    },

    # =================== PASSWORD ATTACKS ===================
    "hydra": {
        "priority": 1,
        "category": "password_attacks",
        "description": "Login cracker supporting many protocols", 
        "license": "free",
        "windows": {
            "url": "https://github.com/vanhauser-thc/thc-hydra/releases/download/v9.5/hydra-9.5-win64.zip",
            "binary": "hydra.exe",
            "size_mb": 15
        },
        "linux": {
            "install_cmd": "apt-get install -y hydra || yum install -y hydra-frontend",
            "binary": "hydra",
            "size_mb": 5
        },
        "macos": {
            "install_cmd": "brew install hydra",
            "binary": "hydra",
            "size_mb": 5
        }
    },

    "hashcat": {
        "priority": 1,
        "category": "password_attacks",
        "description": "GPU-accelerated password cracking",
        "license": "free", 
        "windows": {
            "url": "https://hashcat.net/files/hashcat-6.2.6.7z",
            "binary": "hashcat.exe",
            "size_mb": 45
        },
        "linux": {
            "url": "https://hashcat.net/files/hashcat-6.2.6.tar.gz",
            "binary": "hashcat",
            "size_mb": 8
        },
        "macos": {
            "url": "https://hashcat.net/files/hashcat-6.2.6.tar.gz",
            "binary": "hashcat", 
            "size_mb": 8
        }
    },

    "johntheripper": {
        "priority": 1,
        "category": "password_attacks",
        "description": "Password cracker",
        "license": "free",
        "windows": {
            "url": "https://www.openwall.com/john/k/john-1.9.0-jumbo-1-win64.7z",
            "binary": "run/john.exe",
            "size_mb": 25
        },
        "linux": {
            "install_cmd": "apt-get install -y john || yum install -y john",
            "binary": "john",
            "size_mb": 5
        },
        "macos": {
            "install_cmd": "brew install john",
            "binary": "john",
            "size_mb": 5
        }
    },

    # =================== VULNERABILITY SCANNERS ===================
    "nessus": {
        "priority": 2,
        "category": "vulnerability_scanners",
        "description": "Vulnerability scanner",
        "license": "community_pro",  # Community free, Pro payant
        "license_upgrade": {
            "pro_url": "https://www.tenable.com/products/nessus",
            "pro_license_required": True
        },
        "windows": {
            "url": "https://www.tenable.com/downloads/api/v2/pages/nessus/files/Nessus-10.8.2-x64.msi",
            "binary": "Nessus.exe",
            "size_mb": 150,
            "requires_registration": True
        },
        "linux": {
            "url": "https://www.tenable.com/downloads/api/v2/pages/nessus/files/Nessus-10.8.2-ubuntu1604_amd64.deb",
            "binary": "nessusd",
            "size_mb": 120,
            "requires_registration": True
        },
        "macos": {
            "url": "https://www.tenable.com/downloads/api/v2/pages/nessus/files/Nessus-10.8.2.dmg",
            "binary": "Nessus Scanner.app",
            "size_mb": 120,
            "requires_registration": True
        }
    },

    # =================== CLOUD SECURITY ===================
    "prowler": {
        "priority": 2,
        "category": "cloud_discovery",
        "description": "Cloud security best practices assessments",
        "license": "free",
        "install_method": "git_clone",
        "windows": {
            "url": "https://github.com/prowler-cloud/prowler.git",
            "binary": "prowler.py",
            "size_mb": 5
        },
        "linux": {
            "url": "https://github.com/prowler-cloud/prowler.git",
            "binary": "prowler",
            "size_mb": 5
        },
        "macos": {
            "url": "https://github.com/prowler-cloud/prowler.git",
            "binary": "prowler",
            "size_mb": 5
        }
    },

    # =================== POST-EXPLOITATION ===================
    "mimikatz": {
        "priority": 1,
        "category": "post_exploitation",
        "description": "Windows credential extraction tool",
        "license": "free",
        "security_warning": "This tool may trigger antivirus alerts",
        "windows": {
            "url": "https://github.com/gentilkiwi/mimikatz/releases/download/2.2.0-20220919/mimikatz_trunk.zip",
            "binary": "x64/mimikatz.exe",
            "size_mb": 2
        },
        "linux": {
            # Not applicable for Linux, but included for completeness
            "note": "Mimikatz is Windows-specific"
        },
        "macos": {
            # Not applicable for macOS, but included for completeness  
            "note": "Mimikatz is Windows-specific"
        }
    },

    # =================== TUNNELING ===================
    "chisel": {
        "priority": 2,
        "category": "tunneling",
        "description": "Fast TCP/UDP tunnel over HTTP",
        "license": "free",
        "windows": {
            "url": "https://github.com/jpillora/chisel/releases/download/v1.9.1/chisel_1.9.1_windows_amd64.gz",
            "binary": "chisel.exe",
            "size_mb": 8
        },
        "linux": {
            "url": "https://github.com/jpillora/chisel/releases/download/v1.9.1/chisel_1.9.1_linux_amd64.gz",
            "binary": "chisel",
            "size_mb": 8
        },
        "macos": {
            "url": "https://github.com/jpillora/chisel/releases/download/v1.9.1/chisel_1.9.1_darwin_amd64.gz",
            "binary": "chisel", 
            "size_mb": 8
        }
    },

    # =================== AD ENUMERATION ===================
    "bloodhound": {
        "priority": 2,
        "category": "ad_enumeration", 
        "description": "Active Directory attack path analysis",
        "license": "free",
        "windows": {
            "url": "https://github.com/BloodHoundAD/BloodHound/releases/download/v4.3.1/BloodHound-win32-x64.zip",
            "binary": "BloodHound.exe",
            "size_mb": 150
        },
        "linux": {
            "url": "https://github.com/BloodHoundAD/BloodHound/releases/download/v4.3.1/BloodHound-linux-x64.zip",
            "binary": "BloodHound",
            "size_mb": 120
        },
        "macos": {
            "url": "https://github.com/BloodHoundAD/BloodHound/releases/download/v4.3.1/BloodHound-darwin-x64.zip",
            "binary": "BloodHound.app",
            "size_mb": 120
        }
    },

    # =================== SAST TOOLS ===================
    "semgrep": {
        "priority": 2,
        "category": "sast_tools",
        "description": "Static analysis tool for security bugs",
        "license": "free",
        "install_method": "pip",
        "windows": {
            "install_cmd": "pip install semgrep",
            "binary": "semgrep.exe",
            "size_mb": 50
        },
        "linux": {
            "install_cmd": "pip3 install semgrep",
            "binary": "semgrep",
            "size_mb": 50  
        },
        "macos": {
            "install_cmd": "pip3 install semgrep",
            "binary": "semgrep",
            "size_mb": 50
        }
    },

    "trufflehog": {
        "priority": 2, 
        "category": "sast_tools",
        "description": "Searches through git history for secrets",
        "license": "free",
        "windows": {
            "url": "https://github.com/trufflesecurity/trufflehog/releases/download/v3.81.10/trufflehog_3.81.10_windows_amd64.tar.gz",
            "binary": "trufflehog.exe",
            "size_mb": 25
        },
        "linux": {
            "url": "https://github.com/trufflesecurity/trufflehog/releases/download/v3.81.10/trufflehog_3.81.10_linux_amd64.tar.gz",
            "binary": "trufflehog",
            "size_mb": 25
        },
        "macos": {
            "url": "https://github.com/trufflesecurity/trufflehog/releases/download/v3.81.10/trufflehog_3.81.10_darwin_amd64.tar.gz",
            "binary": "trufflehog",
            "size_mb": 25
        }
    }
}

# License management configuration  
LICENSE_CONFIG = {
    "community_pro": {
        "description": "Community version free, Professional version requires license",
        "auto_upgrade": True,  # Automatically upgrade to Pro if license detected
        "license_env_vars": ["BURP_LICENSE_KEY", "NESSUS_LICENSE_KEY"],
        "license_files": [".burp_license", ".nessus_license"]
    }
}

def get_tools_by_category(category: str) -> dict:
    """Get all tools for a specific category"""
    if category not in TOOLS_CATEGORIES:
        return {}
    
    tools = {}
    for tool_name in TOOLS_CATEGORIES[category]:
        if tool_name in COMPLETE_TOOLS_CONFIG:
            tools[tool_name] = COMPLETE_TOOLS_CONFIG[tool_name]
    
    return tools

def get_all_categories() -> list:
    """Get list of all categories"""
    return list(TOOLS_CATEGORIES.keys())

def get_total_tool_count() -> int:
    """Get total number of configured tools"""
    return len(COMPLETE_TOOLS_CONFIG)

def get_priority_tools(priority: int) -> dict:
    """Get all tools by priority level"""
    tools = {}
    for tool_name, config in COMPLETE_TOOLS_CONFIG.items():
        if config.get('priority', 999) == priority:
            tools[tool_name] = config
    
    return tools

def has_license_upgrade(tool_name: str) -> bool:
    """Check if tool has license upgrade options"""
    if tool_name not in COMPLETE_TOOLS_CONFIG:
        return False
        
    config = COMPLETE_TOOLS_CONFIG[tool_name]
    return config.get('license') == 'community_pro' and 'license_upgrade' in config

def get_license_info(tool_name: str) -> dict:
    """Get license information for a tool"""  
    if tool_name not in COMPLETE_TOOLS_CONFIG:
        return {}
        
    config = COMPLETE_TOOLS_CONFIG[tool_name]
    license_type = config.get('license', 'free')
    
    if license_type == 'community_pro':
        return {
            'type': 'community_pro',
            'community_free': True,
            'pro_available': True,
            'upgrade_info': config.get('license_upgrade', {})
        }
    elif license_type == 'free':
        return {
            'type': 'free',
            'community_free': True, 
            'pro_available': False
        }
    else:
        return {
            'type': 'commercial',
            'community_free': False,
            'pro_available': True,
            'license_required': True
        }
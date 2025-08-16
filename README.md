# Pentest-USB Toolkit

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

## Overview

The **Pentest-USB Toolkit** is a comprehensive, portable penetration testing framework designed to run directly from a USB drive. It integrates hundreds of security tools and provides a unified interface for reconnaissance, vulnerability assessment, exploitation, post-exploitation, and reporting.

## 🚀 Features

### Core Capabilities
- **Portable Architecture**: Runs entirely from USB drive with no installation required
- **Multi-Platform Support**: Compatible with Windows, Linux, and macOS
- **Integrated Tool Suite**: 100+ security tools pre-configured and ready to use
- **Unified Interface**: Both CLI and Web-based interfaces available
- **Automated Workflows**: Intelligent orchestration of security testing phases
- **Stealth Operations**: Advanced evasion techniques for covert testing

### Module Overview
1. **Reconnaissance Module**
   - Network scanning and enumeration
   - Domain and subdomain discovery
   - OSINT gathering and correlation
   - Cloud asset discovery
   - Wireless network analysis

2. **Vulnerability Assessment Module**
   - Web application scanning
   - Network vulnerability assessment
   - Cloud security auditing
   - Static code analysis
   - Mobile application security testing

3. **Exploitation Module**
   - Web application exploitation
   - Network service exploitation
   - Binary exploitation techniques
   - Social engineering campaigns
   - Wireless network attacks

4. **Post-Exploitation Module**
   - Credential harvesting
   - Lateral movement techniques
   - Persistence mechanisms
   - Data exfiltration methods
   - Evidence cleanup

5. **Reporting Module**
   - Professional report generation
   - Executive summary creation
   - Compliance mapping (PCI-DSS, HIPAA, etc.)
   - Interactive dashboards
   - Evidence correlation

## 📋 Requirements

### System Requirements
- **Storage**: 32GB+ USB drive (64GB+ recommended)
- **RAM**: 8GB minimum (16GB+ recommended)
- **CPU**: 64-bit processor, 2+ cores
- **OS**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.14+

### Supported Platforms
- ✅ Windows (64-bit)
- ✅ Linux (64-bit) 
- ✅ macOS (64-bit Intel/Apple Silicon)

## 🛠 Installation

### Quick Setup
1. **Download** the latest release from the GitHub releases page
2. **Extract** to your USB drive root directory
3. **Run** the setup script for your platform:

#### Windows
```powershell
.\scripts\install\setup.ps1
```

#### Linux/macOS
```bash
chmod +x scripts/install/setup.sh
./scripts/install/setup.sh
```

### Manual Installation
Refer to `docs/installation.md` for detailed manual installation instructions.

## 🚀 Usage

### Command Line Interface
```bash
# Launch CLI (Windows)
.\launch.bat

# Launch CLI (Linux/macOS)
./launch.sh
```

### Web Interface
```bash
# Start web interface
pentest-tool web --port 8080
```

### Basic Commands
```bash
# Quick network scan
pentest-tool scan --target 192.168.1.0/24 --profile quick

# Web application assessment
pentest-tool web --url https://example.com --profile comprehensive

# Generate report
pentest-tool report --project my_project --format pdf
```

## 📁 Project Structure

```
Pentest-USB/
├── core/                 # Core engine and utilities
├── modules/              # Functional modules
├── tools/                # Integrated security tools
├── data/                 # Wordlists, templates, databases
├── interfaces/           # CLI and web interfaces
├── runtime/              # Portable runtimes (Python, Java)
├── scripts/              # Installation and maintenance scripts
├── logs/                 # System and audit logs
├── outputs/              # Raw scan results
├── reports/              # Generated reports
├── config/               # Configuration files
├── tests/                # Test suite
└── docs/                 # Documentation
```

## 🔒 Security & Legal Notice

### Important Legal Notice
**⚠️ This toolkit is intended for authorized security testing only.**

- Only use on systems you own or have explicit written permission to test
- Ensure compliance with local laws and regulations
- Follow responsible disclosure practices
- This software is provided for educational and professional security testing purposes

### Consent Management
The toolkit includes built-in consent verification mechanisms:
- Pre-engagement authorization checks
- Scope validation and boundaries
- Audit trail maintenance
- Evidence handling protocols

## 🛡 Stealth Features

### Evasion Capabilities
- **Memory Execution**: No artifacts left on target systems
- **Traffic Obfuscation**: Encrypted C2 communications
- **Process Injection**: Living-off-the-land techniques
- **AV Evasion**: Dynamic payload generation
- **Sandbox Detection**: Environmental awareness

### Operational Security
- Encrypted data storage on USB
- Secure credential management
- Automated cleanup procedures
- Forensic anti-analysis features

## 📊 Reporting

### Report Formats
- **PDF**: Professional penetration test reports
- **HTML**: Interactive web-based reports  
- **DOCX**: Microsoft Word compatible
- **JSON/XML**: Machine-readable formats
- **CSV**: Data analysis and metrics

### Compliance Frameworks
- PCI-DSS Security Standards
- HIPAA Healthcare Requirements
- GDPR Privacy Regulations
- SOX Financial Controls
- NIST Cybersecurity Framework

## 🔧 Configuration

### Tool Configuration
Edit `config/main_config.yaml` to customize:
- Tool execution parameters
- Scan profiles and templates
- Output formats and destinations
- Stealth and evasion settings

### Network Configuration
Configure proxy settings in `config/network_config.yaml`:
```yaml
proxy:
  http_proxy: "http://proxy.example.com:8080"
  https_proxy: "https://proxy.example.com:8080"
  no_proxy: "localhost,127.0.0.1"
```

## 🚀 Advanced Usage

### Custom Scan Profiles
Create custom scan profiles in `data/templates/scan_profiles/`:
```json
{
  "name": "custom_web_scan",
  "modules": ["reconnaissance", "vulnerability"],
  "tools": ["nmap", "zap", "nikto"],
  "parameters": {
    "intensity": "aggressive",
    "timeout": 3600
  }
}
```

### API Integration
Use the REST API for automation:
```python
import requests

# Start a scan
response = requests.post('http://localhost:8080/api/scan', json={
    'target': '192.168.1.100',
    'profile': 'network_comprehensive'
})
```

## 🤝 Contributing

We welcome contributions! Please see `docs/developer_guide.md` for:
- Development environment setup
- Coding standards and guidelines
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

The authors and contributors of this project are not responsible for any misuse or damage caused by this software. This toolkit is intended solely for legitimate security testing purposes on systems where you have explicit authorization. Users are fully responsible for compliance with applicable laws and regulations.

## 📞 Support

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues page
- **Discussions**: GitHub Discussions
- **Security**: security@pentestusb.dev

---

**⭐ Star this repository if you find it useful!**

*Developed with ❤️ by the Pentest-USB Team*
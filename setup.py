"""Setup configuration for Pentest-USB Toolkit"""

from setuptools import setup, find_packages

setup(
    name="pentest-usb-toolkit",
    version="1.0.0",
    author="Pentest-USB Development Team",
    description="Comprehensive penetration testing toolkit for USB deployment",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0.1",
        "psutil>=5.9.6",
        "flask>=3.0.0",
        "streamlit>=1.28.1"
    ],
    python_requires=">=3.9",
)
from setuptools import setup, find_packages

setup(
    name="frappe_ecc_agents",
    version="2.1.0",
    description="Frappe Enterprise Cloud Suite (ECC) Autonomous AI Agents Framework (53 Agents across 8 Pillars)",
    author="Frappe ECC Autonomous Engineering Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "python-docx>=0.8.11",
    ],
    entry_points={
        "console_scripts": [
            "frappe-agent=frappe_ecc_agents.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Frappe",
    ],
)

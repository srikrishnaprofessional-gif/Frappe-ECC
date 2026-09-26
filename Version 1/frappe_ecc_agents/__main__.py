"""
Frappe ECC Agents package execution entry point (`python -m frappe_ecc_agents`).
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())

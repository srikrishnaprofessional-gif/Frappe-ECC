#!/usr/bin/env python3
"""
Frappe ECC Autonomous Agent CLI Runner
Direct executable entrypoint to run, inspect, and orchestrate all 53 Frappe AI Agents.
"""

import sys
import os

# Ensure package root is in python search path
package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

from frappe_ecc_agents.cli import main

if __name__ == "__main__":
    sys.exit(main())

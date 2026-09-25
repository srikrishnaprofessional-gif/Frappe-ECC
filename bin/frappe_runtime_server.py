#!/usr/bin/env python3
"""
Frappe Local Runtime Server CLI Executable
Spins up the local machine Frappe runtime and Desk simulator on localhost.
"""

import sys
import os

# Ensure package root is on sys.path
package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

from frappe_ecc_agents.runtime_server import run_server

if __name__ == "__main__":
    port = 8050
    open_browser = True

    for arg in sys.argv[1:]:
        if arg.isdigit():
            port = int(arg)
        elif arg == "--no-browser":
            open_browser = False

    run_server(port=port, open_browser=open_browser)

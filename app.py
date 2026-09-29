"""
SAT-SA Entrypoint for Render / Hosting
This redirects the execution to the new React/Python adapter API.
"""

import os
import sys

if __name__ == "__main__":
    api_path = os.path.join(os.path.dirname(__file__), "frontend", "api.py")
    os.execv(sys.executable, [sys.executable, api_path])

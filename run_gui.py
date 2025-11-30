"""
Launcher script for MLB Statistics Query GUI

This script launches the natural language query interface for MLB statistics.
"""

import sys
import os

# Add src and utils directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))
sys.path.insert(0, os.path.join(current_dir, 'utils'))

# Import and run the GUI
from mlb_gui import main

if __name__ == "__main__":
    print("Starting MLB Statistics Query GUI...")
    main()

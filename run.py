import subprocess
import sys

subprocess.run([sys.executable, 'setup.py'])
subprocess.run([sys.executable, 'main.py'])
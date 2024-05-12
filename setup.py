import subprocess
import sys

# Install modules
print("\n\nInstalling modules...")
try:
  # Check pip is available
  subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
  
  # Install packages
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
  print("All packages have been successfully installed.")

except subprocess.CalledProcessError as e:
  print(f"Failed to install packages. Error: {e}")

except FileNotFoundError as e:
  print(f"Requirements file not found. Error: {e}")
print("Done.")

# Get tube data from TFL
print("\n\nGetting tube line data from TFL...")
subprocess.run(['python', 'get_lines_and_routes.py'])
print("Done.")

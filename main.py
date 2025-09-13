import subprocess
import sys
import os

env = os.environ.copy()
env['PYTHONPATH'] = os.getcwd()

subprocess.run([sys.executable, 'Server/app.py'], env=env)
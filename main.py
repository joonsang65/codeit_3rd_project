import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))

from model_dev.run_pipes import run_pipe

if __name__ == "__main__":
    run_pipe(mode='inpaint')

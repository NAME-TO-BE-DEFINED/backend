import os
import sys
sys.path.append(os.path.abspath("src"))
from src.api import app




if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
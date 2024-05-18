import os
import sys
sys.path.append(os.path.abspath("src"))
from src.api import app




if __name__ == "__main__":
    app.run(debug=True)
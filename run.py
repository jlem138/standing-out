# run.py

import os

from app import create_app

config_name = os.environ.get('FLASK_CONFIG') or 'development'
app = create_app(config_name)

# The script is only true if is run directly
if __name__ == '__main__':
    app.run()

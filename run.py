"""
run.py

Entry point to start the Flask application.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run the Flask app on a single port (adjust if needed)
    app.run(host='0.0.0.0', port=5001, threaded=True, debug=True)

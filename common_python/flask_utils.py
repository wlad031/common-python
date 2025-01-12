import os
import re
import logging
from flask import Flask

logging.basicConfig(level=logging.INFO)

class HealthFilter(logging.Filter):
    """Custom filter to ignore /health endpoint."""
    def filter(self, record):
        return '/health' not in record.getMessage()

def configure_logging(app):
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)

    health_filter = HealthFilter()
    for handler in werkzeug_logger.handlers:
        handler.addFilter(health_filter)

    flask_logger = logging.getLogger('flask-requests')
    flask_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(health_filter)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    flask_logger.addHandler(console_handler)
    app.logger.handlers = [console_handler]
    app.logger.setLevel(logging.INFO)

def log_request_info(app):
    if request.path != '/health':
        # app.logger.info("Request Headers: %s", request.headers)
        app.logger.info("Request Body: %s", request.get_data(as_text=True))
        app.logger.info("Request Sender: %s", request.remote_addr)


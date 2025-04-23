"""
Configuration management for the Databricks Genie Slack Bot.
"""
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LOAD ENVIRONMENT VARIABLES FROM .ENV FILE IF IT EXISTS
dotenv_path = os.path.join(os.getcwd(), ".env")
logger.info(f"Looking for .env file at: {dotenv_path}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"__file__ location: {__file__}")
if os.path.exists(dotenv_path):
    logger.info(f".env file found at {dotenv_path}")
    with open(dotenv_path, 'r') as f:
        logger.info(f".env contents: {f.read()}")
    load_dotenv(dotenv_path=dotenv_path, override=True)
else:
    logger.warning(f".env file not found at {dotenv_path}")

# SLACK CONFIGURATION
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
logger.info(f"SLACK_BOT_TOKEN is {'set' if SLACK_BOT_TOKEN else 'not set'}")
logger.info(f"SLACK_SIGNING_SECRET is {'set' if SLACK_SIGNING_SECRET else 'not set'}")
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")

# DATABRICKS CONFIGURATION
DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")
SPACE_ID = os.environ.get("SPACE_ID")

# BOT CONFIGURATION
MAINTAIN_CONTEXT = os.environ.get("MAINTAIN_CONTEXT", "true").lower() == "true"
FORMAT_TABLES = os.environ.get("FORMAT_TABLES", "true").lower() == "true"
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "15"))
RETRY_INTERVAL = int(os.environ.get("RETRY_INTERVAL", "2"))

# VALIDATE CONFIGURATIONS
def validate_config():
    """Validates that all required configuration values are set"""
    required_vars = {
        'SLACK_BOT_TOKEN': SLACK_BOT_TOKEN,
        'SLACK_CHANNEL_ID': SLACK_CHANNEL_ID,
        'SLACK_SIGNING_SECRET': SLACK_SIGNING_SECRET,
        'DATABRICKS_TOKEN': DATABRICKS_TOKEN,
        'SPACE_ID': SPACE_ID
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True

# PRINT CONFIGURATION STATUS
def print_config_status():
    """Prints the current configuration status"""
    print("Current Configuration:")
    print(f"  Slack Bot Token: {'Set' if SLACK_BOT_TOKEN else 'Missing'}")
    print(f"  Slack Channel ID: {'Set' if SLACK_CHANNEL_ID else 'Missing'}")
    print(f"  Databricks Host: {DATABRICKS_HOST}")
    print(f"  Databricks Token: {'Set' if DATABRICKS_TOKEN else 'Missing'}")
    print(f"  Space ID: {'Set' if SPACE_ID else 'Missing'}")
    print(f"  Maintain Context: {MAINTAIN_CONTEXT}")
    print(f"  Format Tables: {FORMAT_TABLES}")
    print(f"  Max Retries: {MAX_RETRIES}")
    print(f"  Retry Interval: {RETRY_INTERVAL} seconds")
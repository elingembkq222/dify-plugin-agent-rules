#!/usr/bin/env python3
"""
Database Initialization Script

This script initializes the database tables for the rule engine.
It can be run directly or imported as a module.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from provider.rule_storage import init_rule_db

def main():
    """Main function to initialize the database."""
    # Get the database URL from environment variable or use default
    rule_db_url = os.environ.get("RULE_DB_URL", "sqlite:///rule_engine.db")
    
    print(f"Initializing database with URL: {rule_db_url}")
    
    try:
        init_rule_db(rule_db_url)
        print("✅ Database initialized successfully!")
        print("Tables created:")
        print("- x_rule_sets")
    except Exception as e:
        print(f"❌ Failed to initialize database: {str(e)}")
        print("Please check your database connection and try again.")
        print(f"Error details: {type(e).__name__}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Configuration Management
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    
    # Trading
    INITIAL_BALANCE = float(os.getenv("INITIAL_BALANCE", "10000"))
    RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.02"))
    
    # Risk Management
    MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", "500"))
    MAX_DAILY_LOSS_PERCENT = float(os.getenv("MAX_DAILY_LOSS_PERCENT", "5.0"))
    MAX_CONSECUTIVE_LOSSES = int(os.getenv("MAX_CONSECUTIVE_LOSSES", "3"))
    MAX_OPEN_TRADES = int(os.getenv("MAX_OPEN_TRADES", "5"))
    MIN_SIGNAL_CONFIDENCE = float(os.getenv("MIN_SIGNAL_CONFIDENCE", "6.0"))
    
    # Server
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_DEBUG = True
    SERVER_PORT = 5000


class ProductionConfig(Config):
    """Production configuration"""
    FLASK_DEBUG = False
    SERVER_HOST = "0.0.0.0"


class TestingConfig(Config):
    """Testing configuration"""
    FLASK_ENV = "testing"
    INITIAL_BALANCE = 5000


def get_config():
    """Get config based on environment"""
    env = os.getenv("FLASK_ENV", "production")
    
    if env == "development":
        return DevelopmentConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return ProductionConfig()

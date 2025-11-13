"""
Rule Storage Module

This module provides functionality to initialize and manage the rule database,
including CRUD operations for rule sets.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import create_engine, Column, String, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Global variables for database connection
engine = None
SessionLocal = None

Base = declarative_base()


class RuleSet(Base):
    """RuleSet model for storing rule sets in the database."""
    __tablename__ = "x_rule_sets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    target = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    applies_when = Column(JSON, nullable=True)
    rules = Column(JSON, nullable=False)
    on_fail = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_rule_db(db_url: str) -> None:
    """
    Initialize the rule database with the given connection URL.
    
    Args:
        db_url: Database connection URL (e.g., "sqlite:///rule_engine.db" or "mysql+pymysql://user:password@localhost:3306/rule_engine?charset=utf8mb4")
    """
    global engine, SessionLocal
    
    # MySQL specific configuration
    engine_kwargs = {}
    if db_url.startswith("mysql+pymysql://"):
        engine_kwargs.update({
            'encoding': 'utf-8',
            'pool_pre_ping': True,
            'pool_recycle': 3600
        })
    
    engine = create_engine(db_url, **engine_kwargs)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Get a database session.
    
    Returns:
        SQLAlchemy session object
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_rule_db first.")
    
    return SessionLocal()


def add_rule_set(rule_data: Dict[str, Any]) -> str:
    """
    Add a new rule set to the database.
    
    Args:
        rule_data: Dictionary containing rule set data
        
    Returns:
        ID of the created rule set
    """
    db = get_db()
    try:
        # Create new rule set
        rule_set = RuleSet(
            target=rule_data.get("target", "default"),
            name=rule_data.get("name", ""),
            description=rule_data.get("description", ""),
            applies_when=rule_data.get("applies_when", []),
            rules=rule_data.get("rules", []),
            on_fail=rule_data.get("on_fail", {"action": "block", "notify": ["user"]})
        )
        
        db.add(rule_set)
        db.commit()
        db.refresh(rule_set)
        
        return rule_set.id
    finally:
        db.close()


def get_rule_set(rule_set_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a rule set by ID.
    
    Args:
        rule_set_id: ID of the rule set to retrieve
        
    Returns:
        Rule set data as dictionary, or None if not found
    """
    db = get_db()
    try:
        rule_set = db.query(RuleSet).filter(RuleSet.id == rule_set_id).first()
        if rule_set:
            return {
                "id": rule_set.id,
                "target": rule_set.target,
                "name": rule_set.name,
                "description": rule_set.description,
                "applies_when": rule_set.applies_when or [],
                "rules": rule_set.rules,
                "on_fail": rule_set.on_fail or {"action": "block", "notify": ["user"]},
                "created_at": rule_set.created_at.isoformat() if rule_set.created_at else None,
                "updated_at": rule_set.updated_at.isoformat() if rule_set.updated_at else None
            }
        return None
    finally:
        db.close()


def get_rule_sets_by_target(target: str) -> List[Dict[str, Any]]:
    """
    Get all rule sets for a specific target.
    
    Args:
        target: Target to filter rule sets by
        
    Returns:
        List of rule set data dictionaries
    """
    db = get_db()
    try:
        rule_sets = db.query(RuleSet).filter(RuleSet.target == target).all()
        return [
            {
                "id": rs.id,
                "target": rs.target,
                "name": rs.name,
                "description": rs.description,
                "applies_when": rs.applies_when or [],
                "rules": rs.rules,
                "on_fail": rs.on_fail or {"action": "block", "notify": ["user"]},
                "created_at": rs.created_at.isoformat() if rs.created_at else None,
                "updated_at": rs.updated_at.isoformat() if rs.updated_at else None
            }
            for rs in rule_sets
        ]
    finally:
        db.close()


def list_all_rule_sets() -> List[Dict[str, Any]]:
    """
    List all rule sets in the database.
    
    Returns:
        List of rule set data dictionaries
    """
    db = get_db()
    try:
        rule_sets = db.query(RuleSet).all()
        return [
            {
                "id": rs.id,
                "target": rs.target,
                "name": rs.name,
                "description": rs.description,
                "applies_when": rs.applies_when or [],
                "rules": rs.rules,
                "on_fail": rs.on_fail or {"action": "block", "notify": ["user"]},
                "created_at": rs.created_at.isoformat() if rs.created_at else None,
                "updated_at": rs.updated_at.isoformat() if rs.updated_at else None
            }
            for rs in rule_sets
        ]
    finally:
        db.close()


def update_rule_set(rule_set_id: str, rule_data: Dict[str, Any]) -> bool:
    """
    Update an existing rule set.
    
    Args:
        rule_set_id: ID of the rule set to update
        rule_data: Updated rule set data
        
    Returns:
        True if update was successful, False otherwise
    """
    db = get_db()
    try:
        rule_set = db.query(RuleSet).filter(RuleSet.id == rule_set_id).first()
        if not rule_set:
            return False
        
        # Update fields if provided
        if "target" in rule_data:
            rule_set.target = rule_data["target"]
        if "name" in rule_data:
            rule_set.name = rule_data["name"]
        if "description" in rule_data:
            rule_set.description = rule_data["description"]
        if "applies_when" in rule_data:
            rule_set.applies_when = rule_data["applies_when"]
        if "rules" in rule_data:
            rule_set.rules = rule_data["rules"]
        if "on_fail" in rule_data:
            rule_set.on_fail = rule_data["on_fail"]
        
        rule_set.updated_at = datetime.utcnow()
        db.commit()
        
        return True
    finally:
        db.close()


def delete_rule_set(rule_set_id: str) -> bool:
    """
    Delete a rule set by ID.
    
    Args:
        rule_set_id: ID of the rule set to delete
        
    Returns:
        True if deletion was successful, False otherwise
    """
    db = get_db()
    try:
        rule_set = db.query(RuleSet).filter(RuleSet.id == rule_set_id).first()
        if not rule_set:
            return False
        
        db.delete(rule_set)
        db.commit()
        
        return True
    finally:
        db.close()
import datetime
import json
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

DATABASE_URL = get_settings().database_url
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class HealingRecord(Base):
    __tablename__ = "healing_history"

    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, index=True)
    error_signature = Column(Text)
    original_code = Column(Text)
    healed_code = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class AutoFixDiffLog(Base):
    """Stores before/after diffs for each auto-fix attempt."""
    __tablename__ = "auto_fix_diffs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    test_name = Column(String, index=True)
    attempt_number = Column(Integer, default=1)
    failure_type = Column(String)  # "script_issue", "application_defect", "environment_issue"
    error_log = Column(Text)
    original_code = Column(Text)
    healed_code = Column(Text)
    diff_summary = Column(Text)
    success = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class WorkflowSession(Base):
    """Tracks a complete end-to-end workflow: input -> manual tests -> confirmation -> scripts -> execution -> report"""
    __tablename__ = "workflow_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    input_type = Column(String)  # "prompt" or "document"
    input_content = Column(Text)  # The original prompt or extracted document text
    document_filename = Column(String, nullable=True)
    
    # Environment & data settings
    environment = Column(String, default="dev")  # "dev.ges.store" or "uat.ges.store"
    data_mode = Column(String, default="inline")  # "inline" or "data-driven"
    retry_cap = Column(Integer, default=3)
    
    # Image attachments (JSON array of file paths)
    image_paths = Column(Text, nullable=True)  # JSON array of uploaded image paths
    
    # DOM context captured before generation
    dom_context = Column(Text, nullable=True)  # JSON string of extracted DOM elements
    
    manual_test_cases = Column(Text, nullable=True)  # JSON string of generated manual test cases
    user_confirmed = Column(Boolean, default=False)
    pom_script_code = Column(Text, nullable=True)
    pom_page_code = Column(Text, nullable=True)
    execution_status = Column(String, nullable=True)  # "pending", "scripts_ready", "executing", "passed", "failed", "healed", "error"
    execution_attempts = Column(Integer, default=0)
    execution_errors = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    healing_diffs = Column(Text, nullable=True)  # JSON array of auto-fix diff logs
    report_path = Column(String, nullable=True)
    report_csv_path = Column(String, nullable=True)
    
    # Git tracking
    git_commit_hash = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

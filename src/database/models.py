"""Database models"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import json

Base = declarative_base()


class Character(Base):
    """Character model for storing cached character data"""
    
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    species = Column(String(100), nullable=False, index=True)
    origin_name = Column(String(255), nullable=True, index=True)
    image_url = Column(String(500), nullable=True)
    data = Column(JSON, nullable=False)  # Full character JSON from API
    synced_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # Composite index for common filter combinations
    __table_args__ = (
        Index("idx_character_status_species", "status", "species"),
        Index("idx_character_origin", "origin_name"),
        UniqueConstraint("id", name="uq_character_id")
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "species": self.species,
            "origin_name": self.origin_name,
            "image_url": self.image_url,
            "data": self.data,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ApiCall(Base):
    """API call audit trail for analytics and debugging"""
    
    __tablename__ = "api_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(String(36), nullable=False, index=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False, index=True)
    response_time_ms = Column(Integer, nullable=False)
    cache_hit = Column(Integer, default=0)  # 1 if cache hit, 0 otherwise
    consumer_ip = Column(String(45), nullable=True, index=True)
    request_params = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    
    __table_args__ = (
        Index("idx_api_call_created_at", "created_at"),
        Index("idx_api_call_correlation", "correlation_id"),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "correlation_id": self.correlation_id,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "response_time_ms": self.response_time_ms,
            "cache_hit": bool(self.cache_hit),
            "consumer_ip": self.consumer_ip,
            "request_params": self.request_params,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(Base):
    """Audit log for sensitive operations"""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(String(36), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(50), nullable=False)
    changes = Column(JSON, nullable=True)  # Before/after values
    user_ip = Column(String(45), nullable=True)
    status = Column(String(20), nullable=False, default="success")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    
    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_created_at", "created_at"),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "correlation_id": self.correlation_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "changes": self.changes,
            "user_ip": self.user_ip,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CacheMetadata(Base):
    """Cache metadata for TTL and invalidation tracking"""
    
    __tablename__ = "cache_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(500), nullable=False, unique=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(50), nullable=True, index=True)
    ttl_seconds = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    access_count = Column(Integer, default=0)
    
    __table_args__ = (
        Index("idx_cache_expires_at", "expires_at"),
        Index("idx_cache_entity", "entity_type", "entity_id"),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "cache_key": self.cache_key,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "ttl_seconds": self.ttl_seconds,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "access_count": self.access_count,
        }

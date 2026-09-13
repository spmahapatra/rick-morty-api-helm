"""Database repositories for data access"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from .models import Character, ApiCall, AuditLog, CacheMetadata
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CharacterRepository:
    """Repository for character data operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, character_id: int) -> Optional[Character]:
        """Get character by ID"""
        try:
            return self.session.query(Character).filter(Character.id == character_id).first()
        except Exception as e:
            logger.error(f"Error getting character {character_id}: {e}")
            return None
    
    def get_all(self, skip: int = 0, limit: int = 10) -> List[Character]:
        """Get all characters with pagination"""
        try:
            return self.session.query(Character).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting characters: {e}")
            return []
    
    def filter_by_status(self, status: str, skip: int = 0, limit: int = 10) -> List[Character]:
        """Filter characters by status"""
        try:
            return self.session.query(Character).filter(
                Character.status == status
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error filtering characters by status {status}: {e}")
            return []
    
    def filter_by_species(self, species: str, skip: int = 0, limit: int = 10) -> List[Character]:
        """Filter characters by species"""
        try:
            return self.session.query(Character).filter(
                Character.species == species
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error filtering characters by species {species}: {e}")
            return []
    
    def filter_by_origin(self, origin_name: str, skip: int = 0, limit: int = 10) -> List[Character]:
        """Filter characters by origin"""
        try:
            return self.session.query(Character).filter(
                Character.origin_name.ilike(f"%{origin_name}%")
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error filtering characters by origin {origin_name}: {e}")
            return []
    
    def upsert(self, character_data: Dict[str, Any]) -> Optional[Character]:
        """Insert or update character"""
        try:
            character_id = character_data.get("id")
            existing = self.session.query(Character).filter(Character.id == character_id).first()
            
            if existing:
                # Update existing
                for key, value in character_data.items():
                    if key != "id" and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
            else:
                # Create new
                character = Character(**character_data)
                self.session.add(character)
                existing = character
            
            self.session.commit()
            return existing
        except Exception as e:
            logger.error(f"Error upserting character: {e}")
            self.session.rollback()
            return None
    
    def upsert_many(self, characters_data: List[Dict[str, Any]]) -> List[Character]:
        """Insert or update multiple characters"""
        try:
            results = []
            for char_data in characters_data:
                result = self.upsert(char_data)
                if result:
                    results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error upserting multiple characters: {e}")
            return []
    
    def delete(self, character_id: int) -> bool:
        """Delete character"""
        try:
            self.session.query(Character).filter(Character.id == character_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting character {character_id}: {e}")
            self.session.rollback()
            return False
    
    def count(self) -> int:
        """Count total characters"""
        try:
            return self.session.query(func.count(Character.id)).scalar()
        except Exception as e:
            logger.error(f"Error counting characters: {e}")
            return 0


class ApiCallRepository:
    """Repository for API call audit trail"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, api_call_data: Dict[str, Any]) -> Optional[ApiCall]:
        """Create new API call record"""
        try:
            api_call = ApiCall(**api_call_data)
            self.session.add(api_call)
            self.session.commit()
            return api_call
        except Exception as e:
            logger.error(f"Error creating API call record: {e}")
            self.session.rollback()
            return None
    
    def get_by_correlation_id(self, correlation_id: str) -> List[ApiCall]:
        """Get all API calls by correlation ID"""
        try:
            return self.session.query(ApiCall).filter(
                ApiCall.correlation_id == correlation_id
            ).order_by(desc(ApiCall.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting API calls for correlation {correlation_id}: {e}")
            return []
    
    def get_stats_by_endpoint(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get API call statistics by endpoint"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            stats = self.session.query(
                ApiCall.endpoint,
                func.count(ApiCall.id).label("total_calls"),
                func.avg(ApiCall.response_time_ms).label("avg_response_time"),
                func.sum(ApiCall.cache_hit).label("cache_hits")
            ).filter(
                ApiCall.created_at >= since
            ).group_by(ApiCall.endpoint).all()
            
            return [{
                "endpoint": stat.endpoint,
                "total_calls": stat.total_calls,
                "avg_response_time_ms": round(stat.avg_response_time or 0, 2),
                "cache_hits": stat.cache_hits or 0,
                "cache_hit_ratio": round((stat.cache_hits or 0) / stat.total_calls * 100, 2)
            } for stat in stats]
        except Exception as e:
            logger.error(f"Error getting API call statistics: {e}")
            return []
    
    def cleanup_old_records(self, days: int = 30) -> int:
        """Delete API call records older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted = self.session.query(ApiCall).filter(
                ApiCall.created_at < cutoff_date
            ).delete()
            self.session.commit()
            logger.info(f"Cleaned up {deleted} old API call records")
            return deleted
        except Exception as e:
            logger.error(f"Error cleaning up API call records: {e}")
            self.session.rollback()
            return 0


class AuditLogRepository:
    """Repository for audit logging"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, audit_data: Dict[str, Any]) -> Optional[AuditLog]:
        """Create new audit log record"""
        try:
            audit_log = AuditLog(**audit_data)
            self.session.add(audit_log)
            self.session.commit()
            return audit_log
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            self.session.rollback()
            return None
    
    def get_by_correlation_id(self, correlation_id: str) -> List[AuditLog]:
        """Get audit logs by correlation ID"""
        try:
            return self.session.query(AuditLog).filter(
                AuditLog.correlation_id == correlation_id
            ).order_by(desc(AuditLog.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []
    
    def get_by_entity(self, entity_type: str, entity_id: str) -> List[AuditLog]:
        """Get audit logs for a specific entity"""
        try:
            return self.session.query(AuditLog).filter(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id
            ).order_by(desc(AuditLog.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting entity audit logs: {e}")
            return []

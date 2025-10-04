"""
Module: models
Description: SQLAlchemy database models for air quality data
Author: NASA Space Apps Team
Created: October 4, 2025
"""

import logging
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

logger = logging.getLogger(__name__)

Base = declarative_base()


class AirQualityData(Base):
    """Air quality measurement data from various sources"""
    
    __tablename__ = "air_quality_data"
    
    id = Column(Integer, primary_key=True)
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    source = Column(String(50), nullable=False)
    pm25 = Column(Float)
    pm10 = Column(Float)
    no2 = Column(Float)
    o3 = Column(Float)
    co = Column(Float)
    so2 = Column(Float)
    aqi = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Forecast(Base):
    """Air quality forecast data"""
    
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True)
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    forecast_timestamp = Column(DateTime, nullable=False)
    created_timestamp = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50))
    pm25_forecast = Column(Float)
    pm10_forecast = Column(Float)
    no2_forecast = Column(Float)
    o3_forecast = Column(Float)
    aqi_forecast = Column(Integer)
    confidence_score = Column(Float)


class Alert(Base):
    """Air quality alert notifications"""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True)
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    status = Column(String(20), default="active")

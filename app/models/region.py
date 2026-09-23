from sqlalchemy import Column, String, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Region(Base):
    __tablename__ = "regions"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(128), nullable=False)
    biome = Column(String(255), nullable=False)
    area_ha = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    dominant_species = Column(JSON, nullable=False, default=list)
    climate_type = Column(String(128), nullable=False)
    fluxnet_site_id = Column(String(64), nullable=True)
    fluxnet_site_name = Column(String(255), nullable=True)
    mean_annual_precip_mm = Column(Float, nullable=False)
    mean_temp_c = Column(Float, nullable=False)
    elevation_m = Column(Float, nullable=False)
    baseline_agb = Column(Float, nullable=False)
    baseline_soc = Column(Float, nullable=False)
    description = Column(Text, nullable=True)

    stands = relationship("Stand", back_populates="region", cascade="all, delete-orphan")
    flux_timeseries = relationship("FluxTimeSeries", back_populates="region", cascade="all, delete-orphan")

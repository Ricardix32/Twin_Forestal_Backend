from sqlalchemy import Column, String, Float, Integer, Text, JSON
from app.core.database import Base

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    tag = Column(String(128), nullable=False)
    type = Column(String(64), nullable=False)
    description = Column(Text, nullable=False)
    
    thinning_intensity_pct = Column(Float, nullable=False, default=0.0)
    thinning_schedule_years = Column(JSON, nullable=False, default=list)
    prescribed_burn_interval_years = Column(Integer, nullable=False, default=0)
    reforestation_species = Column(String(255), nullable=False, default="")
    fuel_break_width_m = Column(Float, nullable=False, default=0.0)
    
    trajectory = Column(JSON, nullable=False, default=list)
    metrics_summary = Column(JSON, nullable=False, default=dict)

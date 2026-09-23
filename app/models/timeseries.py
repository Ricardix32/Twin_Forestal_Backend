from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class FluxTimeSeries(Base):
    __tablename__ = "flux_timeseries"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(String(64), ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    month = Column(String(32), nullable=False)
    timestamp = Column(String(32), nullable=False)
    
    # Climate drivers
    temp_c = Column(Float, nullable=False)
    precip_mm = Column(Float, nullable=False)
    vpd_kpa = Column(Float, nullable=False)
    rad_mj_m2 = Column(Float, nullable=False)
    
    # 3-PG simulated fluxes
    pg3_gpp = Column(Float, nullable=False)
    pg3_nee = Column(Float, nullable=False)
    pg3_reco = Column(Float, nullable=False)
    pg3_agb = Column(Float, nullable=False)
    
    # Deep Learning hybrid corrected
    hybrid_gpp = Column(Float, nullable=False)
    hybrid_nee = Column(Float, nullable=False)
    hybrid_reco = Column(Float, nullable=False)
    hybrid_ci_upper = Column(Float, nullable=False)
    hybrid_ci_lower = Column(Float, nullable=False)
    
    # FLUXNET in-situ observations
    fluxnet_gpp = Column(Float, nullable=False)
    fluxnet_nee = Column(Float, nullable=False)
    fluxnet_reco = Column(Float, nullable=False)

    region = relationship("Region", back_populates="flux_timeseries")

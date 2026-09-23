from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Stand(Base):
    __tablename__ = "stands"

    id = Column(Integer, primary_key=True, index=True)
    stand_id = Column(String(64), index=True, nullable=False)
    region_id = Column(String(64), ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Raster grid position
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    
    # Geographic location
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    
    # Forest Stand attributes
    species = Column(String(128), nullable=False)
    stand_age = Column(Integer, nullable=False)
    
    # Carbon & Biometrics
    agb_mgc_ha = Column(Float, nullable=False)
    gedi_height_m = Column(Float, nullable=False)
    soc_mgc_ha = Column(Float, nullable=False)
    
    # Remote Sensing Indices
    ndvi = Column(Float, nullable=False)
    ndwi = Column(Float, nullable=False)
    fuel_moisture_pct = Column(Float, nullable=False)
    fwi_risk = Column(Float, nullable=False)
    
    # Fluxes (gpp, nee, reco)
    gpp_flux = Column(Float, nullable=False)
    nee_flux = Column(Float, nullable=False)
    reco_flux = Column(Float, nullable=False)
    
    # Topography
    slope_pct = Column(Float, nullable=False)
    aspect = Column(String(64), nullable=False)
    elevation_m = Column(Integer, nullable=False)

    region = relationship("Region", back_populates="stands")

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


class CreditType(str, Enum):
    CAPTURE_CREDIT = "capture_credit"
    SEQUESTRATION_CREDIT = "sequestration_credit"
    BONUS_CREDIT = "bonus_credit"


class CreditRate(str, Enum):
    RATE_2022_2025 = "2022_2025"  # $85/ton for DAC, $60/ton for others
    RATE_2026_2032 = "2026_2032"  # $85/ton for DAC, $60/ton for others
    RATE_2033_2045 = "2033_2045"  # $85/ton for DAC, $60/ton for others


class BonusCreditType(str, Enum):
    DOMESTIC_CONTENT = "domestic_content"
    ENERGY_COMMUNITY = "energy_community"
    CARBON_INTENSITY = "carbon_intensity"


class ForecastPeriod(BaseModel):
    year: int
    co2_captured_tons: float
    credit_rate: float
    total_credits: float
    bonus_credits: float = 0.0
    total_value: float


class CreditForecast(BaseModel):
    facility_info: Dict[str, Any]
    forecast_periods: List[ForecastPeriod]
    total_credits_10_years: float
    total_value_10_years: float
    total_credits_12_years: float
    total_value_12_years: float
    average_annual_credits: float
    average_annual_value: float
    bonus_opportunities: List[Dict[str, Any]]
    assumptions: Dict[str, Any]
    recommendations: List[str]


class ForecastingRequest(BaseModel):
    session_id: str
    facility_info: Dict[str, Any]
    annual_co2_captured: float
    capture_efficiency: float
    sequestration_method: str
    sequestration_location: str
    start_date: str
    domestic_content_percentage: Optional[float] = None
    energy_community_eligible: Optional[bool] = None
    carbon_intensity_data: Optional[Dict[str, Any]] = None


class ForecastingResponse(BaseModel):
    session_id: str
    forecast: CreditForecast
    confidence_score: float = Field(ge=0.0, le=1.0)
    warnings: List[str] = []
    next_steps: List[str] = []


class CreditCalculation(BaseModel):
    base_credit_rate: float
    bonus_multipliers: Dict[str, float]
    total_multiplier: float
    effective_credit_rate: float
    annual_credits: float
    annual_value: float


class TimelineProjection(BaseModel):
    year: int
    cumulative_credits: float
    cumulative_value: float
    payback_period: Optional[int] = None
    roi_percentage: Optional[float] = None 
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app.models.forecasting import (
    CreditForecast, ForecastPeriod, CreditCalculation, TimelineProjection,
    CreditType, CreditRate, BonusCreditType
)
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService


class ForecastingService:
    """Service for calculating 45Q tax credit forecasts."""
    
    def __init__(self):
        self.rag_service = RAGService()
        self.llm_service = LLMService()
    
    async def generate_forecast(self, facility_info: Dict[str, Any], forecasting_data: Dict[str, Any]) -> CreditForecast:
        """Generate a comprehensive credit forecast."""
        
        # Extract key data
        annual_co2_captured = forecasting_data.get("annual_co2_captured", 0)
        capture_efficiency = forecasting_data.get("capture_efficiency", 0.9)
        sequestration_method = forecasting_data.get("sequestration_method", "")
        sequestration_location = forecasting_data.get("sequestration_location", "")
        start_date = forecasting_data.get("start_date", "")
        domestic_content_percentage = forecasting_data.get("domestic_content_percentage")
        energy_community_eligible = forecasting_data.get("energy_community_eligible", False)
        
        # Calculate base credit rate
        base_calculation = self._calculate_base_credits(
            facility_info, annual_co2_captured, sequestration_method
        )
        
        # Calculate bonus credits
        bonus_calculation = self._calculate_bonus_credits(
            domestic_content_percentage, energy_community_eligible, facility_info
        )
        
        # Generate forecast periods
        forecast_periods = self._generate_forecast_periods(
            start_date, annual_co2_captured, base_calculation, bonus_calculation
        )
        
        # Calculate totals
        total_credits_10_years = sum(period.total_credits for period in forecast_periods[:10])
        total_value_10_years = sum(period.total_value for period in forecast_periods[:10])
        total_credits_12_years = sum(period.total_credits for period in forecast_periods[:12])
        total_value_12_years = sum(period.total_value for period in forecast_periods[:12])
        
        # Calculate averages
        average_annual_credits = total_credits_12_years / 12
        average_annual_value = total_value_12_years / 12
        
        # Generate bonus opportunities
        bonus_opportunities = self._identify_bonus_opportunities(
            facility_info, domestic_content_percentage, energy_community_eligible
        )
        
        # Generate assumptions
        assumptions = self._generate_assumptions(
            facility_info, forecasting_data, base_calculation, bonus_calculation
        )
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            facility_info, forecasting_data, forecast_periods
        )
        
        return CreditForecast(
            facility_info=facility_info,
            forecast_periods=forecast_periods,
            total_credits_10_years=total_credits_10_years,
            total_value_10_years=total_value_10_years,
            total_credits_12_years=total_credits_12_years,
            total_value_12_years=total_value_12_years,
            average_annual_credits=average_annual_credits,
            average_annual_value=average_annual_value,
            bonus_opportunities=bonus_opportunities,
            assumptions=assumptions,
            recommendations=recommendations
        )
    
    def _calculate_base_credits(self, facility_info: Dict[str, Any], annual_co2: float, sequestration_method: str) -> CreditCalculation:
        """Calculate base credit rates and amounts."""
        facility_type = facility_info.get("facility_type", "").lower()
        capture_method = facility_info.get("capture_method", "").lower()
        
        # Determine base credit rate based on facility type and year
        if "direct air capture" in facility_type:
            base_rate = 85.0  # $85/ton for DAC
        else:
            base_rate = 60.0  # $60/ton for other facilities
        
        # Adjust for sequestration method
        if "utilization" in sequestration_method.lower():
            # Utilization credits are typically lower
            base_rate *= 0.6
        
        # Calculate annual credits
        annual_credits = annual_co2 * base_rate
        annual_value = annual_credits
        
        return CreditCalculation(
            base_credit_rate=base_rate,
            bonus_multipliers={},
            total_multiplier=1.0,
            effective_credit_rate=base_rate,
            annual_credits=annual_credits,
            annual_value=annual_value
        )
    
    def _calculate_bonus_credits(self, domestic_content: Optional[float], energy_community: bool, facility_info: Dict[str, Any]) -> Dict[str, float]:
        """Calculate bonus credit multipliers."""
        bonus_multipliers = {}
        
        # Domestic content bonus
        if domestic_content and domestic_content >= 40:
            bonus_multipliers["domestic_content"] = 0.1  # 10% bonus
        
        # Energy community bonus
        if energy_community:
            bonus_multipliers["energy_community"] = 0.1  # 10% bonus
        
        # Carbon intensity bonus (simplified calculation)
        facility_type = facility_info.get("facility_type", "").lower()
        if "industrial" in facility_type:
            # Industrial facilities might qualify for carbon intensity bonuses
            bonus_multipliers["carbon_intensity"] = 0.05  # 5% bonus
        
        return bonus_multipliers
    
    def _generate_forecast_periods(self, start_date: str, annual_co2: float, base_calc: CreditCalculation, bonus_multipliers: Dict[str, float]) -> List[ForecastPeriod]:
        """Generate forecast periods for the credit timeline."""
        periods = []
        
        try:
            start_year = datetime.strptime(start_date, "%Y-%m-%d").year
        except ValueError:
            start_year = datetime.now().year
        
        # Calculate total bonus multiplier
        total_bonus = sum(bonus_multipliers.values())
        effective_rate = base_calc.base_credit_rate * (1 + total_bonus)
        
        # Generate periods for 12 years (typical 45Q period)
        for year in range(start_year, start_year + 12):
            # Adjust rates based on year (simplified - actual rates vary)
            year_rate = effective_rate
            if year >= 2033:
                # Rates may change after 2032
                year_rate *= 0.9
            
            # Calculate credits for this year
            total_credits = annual_co2 * year_rate
            bonus_credits = annual_co2 * base_calc.base_credit_rate * total_bonus
            total_value = total_credits
            
            periods.append(ForecastPeriod(
                year=year,
                co2_captured_tons=annual_co2,
                credit_rate=year_rate,
                total_credits=total_credits,
                bonus_credits=bonus_credits,
                total_value=total_value
            ))
        
        return periods
    
    def _identify_bonus_opportunities(self, facility_info: Dict[str, Any], domestic_content: Optional[float], energy_community: bool) -> List[Dict[str, Any]]:
        """Identify potential bonus credit opportunities."""
        opportunities = []
        
        # Domestic content opportunity
        if not domestic_content or domestic_content < 40:
            opportunities.append({
                "type": "domestic_content",
                "description": "Increase domestic content to 40% or more for 10% bonus",
                "potential_bonus": "10% increase in credit rate",
                "requirements": "40% of facility components manufactured in US"
            })
        
        # Energy community opportunity
        if not energy_community:
            opportunities.append({
                "type": "energy_community",
                "description": "Locate facility in energy community for 10% bonus",
                "potential_bonus": "10% increase in credit rate",
                "requirements": "Facility located in designated energy community"
            })
        
        # Carbon intensity opportunity
        facility_type = facility_info.get("facility_type", "").lower()
        if "industrial" in facility_type:
            opportunities.append({
                "type": "carbon_intensity",
                "description": "Optimize carbon intensity for additional bonus",
                "potential_bonus": "5% increase in credit rate",
                "requirements": "Meet carbon intensity thresholds"
            })
        
        return opportunities
    
    def _generate_assumptions(self, facility_info: Dict[str, Any], forecasting_data: Dict[str, Any], base_calc: CreditCalculation, bonus_multipliers: Dict[str, float]) -> Dict[str, Any]:
        """Generate assumptions used in the forecast."""
        return {
            "annual_co2_captured": forecasting_data.get("annual_co2_captured", 0),
            "capture_efficiency": forecasting_data.get("capture_efficiency", 0.9),
            "base_credit_rate": base_calc.base_credit_rate,
            "bonus_multipliers": bonus_multipliers,
            "effective_credit_rate": base_calc.effective_credit_rate,
            "forecast_period": "12 years",
            "rate_assumptions": "Rates based on current 45Q provisions",
            "sequestration_method": forecasting_data.get("sequestration_method", ""),
            "domestic_content": forecasting_data.get("domestic_content_percentage"),
            "energy_community": forecasting_data.get("energy_community_eligible", False)
        }
    
    async def _generate_recommendations(self, facility_info: Dict[str, Any], forecasting_data: Dict[str, Any], forecast_periods: List[ForecastPeriod]) -> List[str]:
        """Generate recommendations for maximizing credits."""
        recommendations = []
        
        # Get RAG-based guidance
        rag_guidance = await self.rag_service.get_credit_calculation_guidance(facility_info)
        
        # Add RAG-based recommendations
        if rag_guidance.get("answer"):
            recommendations.append(f"RAG Guidance: {rag_guidance['answer'][:200]}...")
        
        # Add specific recommendations based on forecast
        total_value = sum(period.total_value for period in forecast_periods)
        
        if total_value > 1000000:  # $1M threshold
            recommendations.append("Consider professional tax consultation for large credit amounts")
        
        # Bonus optimization recommendations
        domestic_content = forecasting_data.get("domestic_content_percentage")
        if not domestic_content or domestic_content < 40:
            recommendations.append("Increase domestic content to 40%+ for 10% bonus credits")
        
        if not forecasting_data.get("energy_community_eligible"):
            recommendations.append("Consider energy community location for additional 10% bonus")
        
        # Documentation recommendations
        recommendations.append("Maintain detailed documentation of CO2 capture and sequestration")
        recommendations.append("Implement monitoring and verification systems")
        recommendations.append("Prepare for IRS compliance requirements")
        
        return recommendations
    
    def generate_timeline_projection(self, forecast_periods: List[ForecastPeriod], initial_investment: float = 0) -> List[TimelineProjection]:
        """Generate timeline projections with cumulative values."""
        projections = []
        cumulative_credits = 0
        cumulative_value = 0
        
        for period in forecast_periods:
            cumulative_credits += period.total_credits
            cumulative_value += period.total_value
            
            # Calculate payback period
            payback_period = None
            roi_percentage = None
            
            if initial_investment > 0:
                if cumulative_value >= initial_investment and payback_period is None:
                    payback_period = period.year
                
                roi_percentage = ((cumulative_value - initial_investment) / initial_investment) * 100
            
            projections.append(TimelineProjection(
                year=period.year,
                cumulative_credits=cumulative_credits,
                cumulative_value=cumulative_value,
                payback_period=payback_period,
                roi_percentage=roi_percentage
            ))
        
        return projections
    
    async def get_detailed_forecast_analysis(self, facility_info: Dict[str, Any], forecasting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed forecast analysis with RAG guidance."""
        # Generate basic forecast
        forecast = await self.generate_forecast(facility_info, forecasting_data)
        
        # Generate timeline projections
        timeline_projections = self.generate_timeline_projection(
            forecast.forecast_periods,
            initial_investment=forecasting_data.get("initial_investment", 0)
        )
        
        # Get RAG-based analysis
        rag_analysis = await self.rag_service.get_credit_calculation_guidance(facility_info)
        
        return {
            "forecast": forecast,
            "timeline_projections": timeline_projections,
            "rag_analysis": rag_analysis,
            "summary": {
                "total_potential_credits": forecast.total_credits_12_years,
                "total_potential_value": forecast.total_value_12_years,
                "average_annual_value": forecast.average_annual_value,
                "bonus_opportunities_count": len(forecast.bonus_opportunities),
                "confidence_score": 0.85
            }
        } 
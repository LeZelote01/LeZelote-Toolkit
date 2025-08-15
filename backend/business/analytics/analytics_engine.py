# Analytics Engine for Business Intelligence
from typing import Optional
from datetime import datetime, date

class AnalyticsEngine:
    """Business intelligence engine for analytics processing"""
    
    def parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
        try:
            # Support 'YYYY-MM-DD' or ISO 'YYYY-MM-DDTHH:MM:SS'
            return datetime.fromisoformat(date_str[:10]).date()
        except:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                return None

    def in_range(self, iso_str: str, start: Optional[date], end: Optional[date]) -> bool:
        """Check if date is within range"""
        if not start and not end:
            return True
        try:
            d = datetime.fromisoformat(str(iso_str)[:10]).date()
        except:
            return True
        if start and d < start:
            return False
        if end and d > end:
            return False
        return True

    def calculate_growth_rate(self, current: float, previous: float) -> float:
        """Calculate growth rate percentage"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)

    def calculate_trend(self, data_points: list) -> str:
        """Determine trend from data points"""
        if len(data_points) < 2:
            return "stable"
        
        increases = 0
        decreases = 0
        
        for i in range(1, len(data_points)):
            if data_points[i] > data_points[i-1]:
                increases += 1
            elif data_points[i] < data_points[i-1]:
                decreases += 1
        
        if increases > decreases:
            return "increasing"
        elif decreases > increases:
            return "decreasing"
        else:
            return "stable"
"""
Takeoff Calculator Module
Calculates project takeoffs and estimates
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json


class Unit(Enum):
    """Measurement units"""
    LINEAR_FOOT = "ft"
    SQUARE_FOOT = "sf"
    CUBIC_YARD = "cy"
    TON = "ton"
    UNIT = "unit"
    GALLON = "gal"


@dataclass
class LineItem:
    """Represents a line item in takeoff"""
    description: str
    quantity: float
    unit: str
    unit_price: float
    
    @property
    def total_price(self) -> float:
        """Calculate total price for this line item"""
        return self.quantity * self.unit_price


@dataclass
class Takeoff:
    """Represents a complete takeoff"""
    project_name: str
    description: str
    line_items: List[LineItem]
    markup_percentage: float = 10.0
    tax_rate: float = 0.0
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal"""
        return sum(item.total_price for item in self.line_items)
    
    @property
    def markup_amount(self) -> float:
        """Calculate markup amount"""
        return self.subtotal * (self.markup_percentage / 100)
    
    @property
    def subtotal_with_markup(self) -> float:
        """Calculate subtotal with markup"""
        return self.subtotal + self.markup_amount
    
    @property
    def tax_amount(self) -> float:
        """Calculate tax amount"""
        return self.subtotal_with_markup * self.tax_rate
    
    @property
    def total_price(self) -> float:
        """Calculate final total price"""
        return self.subtotal_with_markup + self.tax_amount


class TakeoffCalculator:
    """Calculate project takeoffs"""

    def __init__(self):
        self.takeoffs: Dict[str, Takeoff] = {}

    def create_takeoff(self, project_name: str, description: str = "",
                      markup_percentage: float = 10.0, 
                      tax_rate: float = 0.0) -> str:
        """
        Create a new takeoff
        
        Args:
            project_name: Name of the project
            description: Project description
            markup_percentage: Markup percentage (default 10%)
            tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)
            
        Returns:
            Takeoff ID
        """
        takeoff_id = f"takeoff_{len(self.takeoffs) + 1}"
        self.takeoffs[takeoff_id] = Takeoff(
            project_name=project_name,
            description=description,
            line_items=[],
            markup_percentage=markup_percentage,
            tax_rate=tax_rate
        )
        return takeoff_id

    def add_line_item(self, takeoff_id: str, description: str, 
                     quantity: float, unit: str, unit_price: float) -> bool:
        """
        Add a line item to takeoff
        
        Args:
            takeoff_id: ID of the takeoff
            description: Item description
            quantity: Quantity
            unit: Unit of measurement
            unit_price: Price per unit
            
        Returns:
            True if successful, False otherwise
        """
        if takeoff_id not in self.takeoffs:
            return False
        
        item = LineItem(
            description=description,
            quantity=quantity,
            unit=unit,
            unit_price=unit_price
        )
        self.takeoffs[takeoff_id].line_items.append(item)
        return True

    def get_takeoff_summary(self, takeoff_id: str) -> Optional[Dict[str, Any]]:
        """
        Get takeoff summary with calculations
        
        Args:
            takeoff_id: ID of the takeoff
            
        Returns:
            Dictionary with takeoff summary or None
        """
        if takeoff_id not in self.takeoffs:
            return None
        
        takeoff = self.takeoffs[takeoff_id]
        
        return {
            'takeoff_id': takeoff_id,
            'project_name': takeoff.project_name,
            'description': takeoff.description,
            'line_items': [
                {
                    'description': item.description,
                    'quantity': item.quantity,
                    'unit': item.unit,
                    'unit_price': f"${item.unit_price:,.2f}",
                    'total': f"${item.total_price:,.2f}"
                }
                for item in takeoff.line_items
            ],
            'subtotal': f"${takeoff.subtotal:,.2f}",
            'markup_percentage': takeoff.markup_percentage,
            'markup_amount': f"${takeoff.markup_amount:,.2f}",
            'subtotal_with_markup': f"${takeoff.subtotal_with_markup:,.2f}",
            'tax_rate': f"{takeoff.tax_rate * 100:.1f}%",
            'tax_amount': f"${takeoff.tax_amount:,.2f}",
            'total_price': f"${takeoff.total_price:,.2f}",
            'item_count': len(takeoff.line_items)
        }

    def calculate_estimate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate estimate from data
        
        Args:
            data: Dictionary with project info and line items
                  {
                      'project_name': str,
                      'description': str,
                      'markup_percentage': float,
                      'tax_rate': float,
                      'line_items': [
                          {
                              'description': str,
                              'quantity': float,
                              'unit': str,
                              'unit_price': float
                          }
                      ]
                  }
            
        Returns:
            Dictionary with estimate summary
        """
        try:
            # Create takeoff
            takeoff_id = self.create_takeoff(
                project_name=data.get('project_name', 'Unknown Project'),
                description=data.get('description', ''),
                markup_percentage=data.get('markup_percentage', 10.0),
                tax_rate=data.get('tax_rate', 0.0)
            )
            
            # Add line items
            for item in data.get('line_items', []):
                self.add_line_item(
                    takeoff_id,
                    description=item.get('description', ''),
                    quantity=float(item.get('quantity', 0)),
                    unit=item.get('unit', 'unit'),
                    unit_price=float(item.get('unit_price', 0))
                )
            
            # Return summary
            summary = self.get_takeoff_summary(takeoff_id)
            if summary:  # type: ignore
                summary['success'] = True
            return summary or {}  # type: ignore
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'calculation_status': 'failed'
            }

    def get_all_takeoffs(self) -> Dict[str, Any]:
        """Get all takeoffs"""
        return {
            'takeoffs': [
                self.get_takeoff_summary(tid)
                for tid in self.takeoffs.keys()
            ],
            'total_count': len(self.takeoffs)
        }


def calculate_takeoff(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to calculate takeoff
    
    Args:
        data: Dictionary with project and line item data
        
    Returns:
        Dictionary with takeoff calculation results
    """
    calculator = TakeoffCalculator()
    return calculator.calculate_estimate(data)

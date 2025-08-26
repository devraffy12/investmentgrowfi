from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def calculate_daily_profit(amount, rate):
    """Calculate daily profit from amount and rate - uses fixed values for GROWFI plans."""
    try:
        amount = float(amount)
        # Use fixed daily profits for each GROWFI plan
        if amount == 500:  # GROWFI 1
            return 56
        elif amount == 1000:  # GROWFI 2
            return 111
        elif amount == 2200:  # GROWFI 3
            return 269
        elif amount == 3500:  # GROWFI 4
            return 389
        elif amount == 5000:  # GROWFI 5
            return 556
        elif amount == 8000:  # GROWFI 6
            return 889
        else:
            # Fallback to calculation
            return int((amount * float(rate)) / 100)
    except (ValueError, TypeError):
        return 0

@register.filter
def calculate_total_profit(amount, rate, days):
    """Calculate total profit from amount, rate, and days - uses fixed values for GROWFI plans."""
    try:
        amount = float(amount)
        days = float(days)
        
        # Use fixed total revenues for each GROWFI plan
        if amount == 500 and days == 30:  # GROWFI 1
            return 1680
        elif amount == 1000 and days == 30:  # GROWFI 2
            return 3330
        elif amount == 2200 and days == 90:  # GROWFI 3
            return 24210  # This is total revenue, not net profit
        elif amount == 3500 and days == 120:  # GROWFI 4
            return 46680
        elif amount == 5000 and days == 180:  # GROWFI 5
            return 100080
        elif amount == 8000 and days == 180:  # GROWFI 6
            return 100080
        else:
            # Fallback to calculation
            daily_profit = (amount * float(rate)) / 100
            return int(daily_profit * days)
    except (ValueError, TypeError):
        return 0

@register.filter
def calculate_net_profit(amount, rate, days):
    """Calculate net profit - uses fixed values for GROWFI plans."""
    try:
        amount = float(amount)
        days = float(days)
        
        # Use fixed net profits for each GROWFI plan
        if amount == 500 and days == 30:  # GROWFI 1
            return 1680
        elif amount == 1000 and days == 30:  # GROWFI 2
            return 3330
        elif amount == 2200 and days == 90:  # GROWFI 3
            return 16140  # Special case: net profit is different from total revenue
        elif amount == 3500 and days == 120:  # GROWFI 4
            return 46680
        elif amount == 5000 and days == 180:  # GROWFI 5
            return 100080
        elif amount == 8000 and days == 180:  # GROWFI 6
            return 100080
        else:
            # Fallback to calculation
            daily_profit = (amount * float(rate)) / 100
            return int(daily_profit * days)
    except (ValueError, TypeError):
        return 0

@register.filter
def format_currency(value):
    """Format value as currency."""
    try:
        return "{:,.0f}".format(float(value))
    except (ValueError, TypeError):
        return "0"

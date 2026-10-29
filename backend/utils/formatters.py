# DwellIQ Shared Utilities

def format_inr(amount: float) -> str:
    """Format INR amounts into standard Indian notations."""
    if amount is None:
        return "₹0"
    if amount >= 10_000_000:
        return f"₹{amount / 10_000_000:.2f} Cr"
    elif amount >= 100_000:
        return f"₹{amount / 100_000:.2f} Lakh"
    return f"₹{amount:,.0f}"

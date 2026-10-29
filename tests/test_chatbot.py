import pytest
from backend.services.chatbot_service import (
    ask_property_advisor,
    get_ai_service_status,
    SYSTEM_INSTRUCTION,
)


class TestChatbotService:
    def test_ai_status_structure(self):
        status = get_ai_service_status()
        assert "is_live_llm" in status
        assert "provider" in status
        assert "badge_text" in status
        assert "badge_color" in status
        assert "description" in status

    def test_system_instruction_grounding(self):
        assert "You are DwellIQ AI" in SYSTEM_INSTRUCTION
        assert "Never invent listings" in SYSTEM_INSTRUCTION
        assert "Do not claim to be a certified financial" in SYSTEM_INSTRUCTION

    def test_price_explanation_general(self):
        res = ask_property_advisor("Explain how the property estimate is calculated")
        assert "reply" in res
        assert "Random Forest" in res["reply"]
        assert "Carpet Area" in res["reply"]
        assert "source" in res
        assert "timestamp" in res

    def test_price_explanation_with_active_context(self):
        context = {
            "title": "3 BHK in Bandra West",
            "price": 35000000.0,
            "area": 1250.0,
            "bhk": 3,
            "location": "Mumbai",
            "bathrooms": 3,
        }
        res = ask_property_advisor("Explain my property valuation", property_context=context)
        assert "Bandra West" in res["reply"] or "Mumbai" in res["reply"]
        assert "3.50 Cr" in res["reply"]
        assert "sq.ft" in res["reply"]

    def test_affordability_calculation(self):
        res = ask_property_advisor("Can I afford a 80 lakh home?")
        assert "reply" in res
        # Should break down 20% down payment (₹16 Lakh) and monthly EMI
        assert "Down Payment" in res["reply"]
        assert "EMI" in res["reply"]
        assert "FOIR" in res["reply"] or "Income" in res["reply"]

    def test_emi_calculation_from_numbers(self):
        res = ask_property_advisor("Calculate EMI for a 60 lakh loan at 8.5% for 20 years")
        assert "reply" in res
        assert "Monthly EMI" in res["reply"]
        assert "Principal" in res["reply"] or "Total Repayment" in res["reply"]
        assert "calculation_note" in res

    def test_home_buying_checklist(self):
        res = ask_property_advisor("What should I check before buying a flat?")
        assert "reply" in res
        assert "RERA" in res["reply"]
        assert "Encumbrance Certificate" in res["reply"]
        assert "Occupancy Certificate" in res["reply"]

    def test_property_terms_explanation(self):
        res = ask_property_advisor("What is carpet area vs super built-up?")
        assert "reply" in res
        assert "Carpet Area" in res["reply"]
        assert "Super Built-Up" in res["reply"]

    def test_nearby_amenities_inquiry(self):
        res = ask_property_advisor("What are the hospitals near Mumbai?")
        assert "reply" in res
        assert "Hospital" in res["reply"]
        assert "Mumbai" in res["reply"]

    def test_comparison_advice(self):
        res = ask_property_advisor("Compare a 2 BHK in city center vs a 3 BHK in suburbs")
        assert "reply" in res
        assert "Trade-off" in res["reply"] or "Comparison" in res["reply"]

    def test_general_fallback(self):
        res = ask_property_advisor("Hello good morning")
        assert "reply" in res
        assert "Welcome to DwellIQ AI" in res["reply"]

import pytest
from pydantic import ValidationError
from hypothesis import given, strategies as st
from src.models.product import EnrichedProduct

# Hypothesis property-based testing strategy for EnrichedProduct
@given(
    sku=st.text(min_size=1),
    canonical_name=st.text(min_size=1),
    active_ingredients=st.lists(st.text(min_size=1), min_size=1),
    target_biomarkers=st.lists(st.text()),
    mechanisms=st.lists(st.text()),
    contraindications=st.lists(st.text())
)
def test_enriched_product_schema(sku, canonical_name, active_ingredients, target_biomarkers, mechanisms, contraindications):
    product = EnrichedProduct(
        sku=sku,
        canonical_name=canonical_name,
        active_ingredients=active_ingredients,
        target_biomarkers=target_biomarkers,
        mechanisms_of_action=mechanisms,
        contraindications=contraindications
    )
    
    assert product.sku == sku
    assert product.canonical_name == canonical_name
    assert isinstance(product.active_ingredients, list)

def test_enriched_product_validation_failure():
    # Test strict typing failure (missing required fields)
    with pytest.raises(ValidationError):
        EnrichedProduct(sku="123") # Missing canonical_name, etc.

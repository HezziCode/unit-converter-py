# UI components for the converter interface

import streamlit as st

class UIComponents:
    """Handles all UI elements and their rendering"""
    def __init__(self, categories):
        # Initialize with unit categories
        self.categories = categories

    def render_header(self):
        """Render the application header"""
        st.title("🔄 Advanced Unit Converter")
        st.markdown("Convert between different units with high precision.")

    def render_category_selector(self):
        """Render the category selection dropdown"""
        categories_with_icons = [
            f"{self.categories[cat]['icon']} {cat}" 
            for cat in self.categories.keys()
        ]
        selected = st.selectbox("Select Category", categories_with_icons)
        return selected.split(' ')[1]

    def render_unit_selectors(self, category):
        """Render the unit selection dropdowns"""
        col1, col2 = st.columns(2)
        with col1:
            from_unit = st.selectbox("From Unit", self.categories[category]['units'])
        with col2:
            to_unit = st.selectbox("To Unit", self.categories[category]['units'])
        return from_unit, to_unit

    def render_value_input(self):
        """Render the value input field"""
        return st.number_input("Enter Value", value=1.0, format="%f")

    def render_result(self, value, from_unit, to_unit, result):
        """Display the conversion result"""
        st.success(f"{value} {from_unit} = {result} {to_unit}") 
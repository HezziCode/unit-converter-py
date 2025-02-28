# Configuration file defining available unit categories and their units

class UnitCategories:
    """Defines all available unit categories and their corresponding units"""
    @staticmethod
    def get_categories():
        """Return dictionary of all unit categories with their units and icons"""
        return {
            "Length": {
                "units": ["Nanometers", "Micrometers", "Millimeters", "Centimeters", "Meters"],
                "icon": "📏"
            },
            "Weight/Mass": {
                "units": ["Micrograms", "Milligrams", "Grams", "Kilograms"],
                "icon": "⚖️"
            },
            "Temperature": {
                "units": ["Celsius", "Fahrenheit", "Kelvin"],
                "icon": "🌡️"
            },
            "Volume": {
                "units": ["Milliliters", "Liters", "Cubic Centimeters", "Cubic Meters",
                         "Fluid Ounces", "Cups", "Pints", "Quarts", "Gallons"],
                "icon": "🧊"
            },
            "Time": {
                "units": ["Nanoseconds", "Microseconds", "Milliseconds", "Seconds", "Minutes", 
                         "Hours", "Days", "Weeks", "Months", "Years", "Decades", "Centuries"],
                "icon": "⏱️"
            },
            "Area": {
                "units": ["Square Millimeters", "Square Centimeters", "Square Meters", "Hectares", 
                         "Square Kilometers", "Square Inches", "Square Feet", "Square Yards", "Acres", "Square Miles"],
                "icon": "📐"
            },
            "Digital Storage": {
                "units": ["Bits", "Bytes", "Kilobytes", "Megabytes", "Gigabytes", 
                         "Terabytes", "Petabytes"],
                "icon": "💾"
            },
            "Speed": {
                "units": ["Meters per Second", "Kilometers per Hour", "Miles per Hour", 
                         "Knots", "Feet per Second"],
                "icon": "🏃"
            },
            "Pressure": {
                "units": ["Pascal", "Kilopascal", "Bar", "PSI", "Atmosphere", 
                         "Millimeters of Mercury", "Inches of Mercury"],
                "icon": "🌪️"
            },
            "Energy": {
                "units": ["Joules", "Kilojoules", "Calories", "Kilocalories", 
                         "Watt-hours", "Kilowatt-hours", "Electron Volts"],
                "icon": "⚡"
            }
        } 
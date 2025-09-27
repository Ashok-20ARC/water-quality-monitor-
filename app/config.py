# core/config.py

# This file contains the configuration for the sensor network.
# You can add or remove sensors here.

SENSOR_CONFIG = [
    {
        'name': 'pH',
        'unit': '',
        'min_val': 0,
        'max_val': 14,
        'normal_range': (6.5, 8.5)
    },
    {
        'name': 'Temperature',
        'unit': '°C',
        'min_val': -10,
        'max_val': 50,
        'normal_range': (10, 25)
    },
    {
        'name': 'Dissolved_Oxygen',
        'unit': 'mg/L',
        'min_val': 0,
        'max_val': 20,
        'normal_range': (6.5, 8.0)
    },
    {
        'name': 'Turbidity',
        'unit': 'NTU',
        'min_val': 0,
        'max_val': 1000,
        'normal_range': (0, 5)
    }
]

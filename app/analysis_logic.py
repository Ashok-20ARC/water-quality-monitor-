# core/analysis_logic.py

import cv2
import numpy as np
import random
import time
from .config import SENSOR_CONFIG

# --- Image Analysis Logic ---

class ImageAnalyzer:
    def __init__(self, image_stream):
        self.image_stream = image_stream
        self.image = self._load_image()

    def _load_image(self):
        # Read image from in-memory stream
        image_array = np.asarray(bytearray(self.image_stream.read()), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Could not decode image from stream.")
        return image

    def analyze_clarity(self):
        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        clarity_score = np.clip(laplacian_var / 10, 0, 100)
        return clarity_score

    def analyze_color(self):
        avg_color_per_row = np.average(self.image, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        return int(avg_color[0]), int(avg_color[1]), int(avg_color[2]) # BGR

# --- Sensor Network Logic ---

class Sensor:
    def __init__(self, name, unit, min_val, max_val, normal_range):
        self.name = name
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self.normal_range = normal_range

    def read_value(self, is_abnormal=False):
        if is_abnormal:
            if random.choice([True, False]):
                return random.uniform(self.min_val, self.normal_range[0])
            else:
                return random.uniform(self.normal_range[1], self.max_val)
        else:
            return random.uniform(self.normal_range[0], self.normal_range[1])

class SensorNetwork:
    def __init__(self):
        self.sensors = [Sensor(**config) for config in SENSOR_CONFIG]

    def get_readings(self, anomaly_prob=0.1):
        readings = {}
        for sensor in self.sensors:
            is_abnormal = random.random() < anomaly_prob
            value = sensor.read_value(is_abnormal)
            readings[sensor.name] = {
                'value': round(value, 2),
                'unit': sensor.unit,
                'normal_range': sensor.normal_range
            }
        return readings

# --- WQI Calculation Logic ---

def calculate_wqi(image_results, sensor_readings):
    weights = {
        'clarity': 0.3, 'color': 0.2, 'ph': 0.2,
        'temperature': 0.15, 'dissolved_oxygen': 0.15
    }
    total_score = 0

    # Score from Clarity
    clarity_score = image_results.get('clarity_score', 50)
    normalized_clarity = 100 - min(clarity_score, 100)
    total_score += normalized_clarity * weights['clarity']

    # Score from Color
    b, g, r = image_results.get('average_color_bgr', (128, 128, 128))
    color_deviation = ((b - 128)**2 + (g - 128)**2 + (r - 128)**2)**0.5
    normalized_color = 100 - (color_deviation / 222 * 100)
    total_score += normalized_color * weights['color']

    # Score from Sensors
    for sensor_name, data in sensor_readings.items():
        value = data['value']
        normal_min, normal_max = data['normal_range']
        if normal_min <= value <= normal_max:
            sensor_score = 100
        else:
            deviation = min(abs(value - normal_min), abs(value - normal_max))
            sensor_score = max(0, 100 - deviation * 20)
        
        # Match sensor name (case-insensitive) to weight key
        weight_key = sensor_name.lower().replace(' ', '_')
        if weight_key in weights:
             total_score += sensor_score * weights[weight_key]

    return total_score


def perform_full_analysis(image_file):
    """
    Orchestrator function to run the entire analysis pipeline.
    """
    # 1. Image Analysis
    analyzer = ImageAnalyzer(image_file)
    clarity = analyzer.analyze_clarity()
    avg_b, avg_g, avg_r = analyzer.analyze_color()
    image_results = {
        'clarity_score': clarity,
        'average_color_bgr': (avg_b, avg_g, avg_r)
    }

    # 2. Sensor Data Simulation
    network = SensorNetwork()
    sensor_readings = network.get_readings(anomaly_prob=0.1)

    # 3. WQI Calculation
    wqi = calculate_wqi(image_results, sensor_readings)

    # 4. Compile all data
    full_results = {
        'wqi_score': wqi,
        'clarity_score': clarity,
        'avg_color_bgr': f"{avg_b},{avg_g},{avg_r}",
        'ph': sensor_readings.get('pH', {}).get('value'),
        'temperature': sensor_readings.get('Temperature', {}).get('value'),
        'dissolved_oxygen': sensor_readings.get('Dissolved_Oxygen', {}).get('value'),
        'turbidity': sensor_readings.get('Turbidity', {}).get('value'),
    }

    return full_results

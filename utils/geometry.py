"""
Geometry utility functions
"""
import math


def distance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def normalize_vector(dx, dy):
    """Normalize a 2D vector"""
    length = math.sqrt(dx**2 + dy**2)
    if length == 0:
        return 0, 0
    return dx / length, dy / length


def clamp(value, min_value, max_value):
    """Clamp a value between min and max"""
    return max(min_value, min(value, max_value))

"""
geometry.py: Useful geometry functions for the simulator.
"""

import math

def circular_intersection(a_center, a_radius, b_center, b_radius):
    """
    circular_intersection: Returns the two intersection points of two circles.
    Parameters:
        a_center: The center of circle A is a tuple (x, y)
        a_radius: The radius of circle A
        b_center: The center of circle B as a tuple (x, y)
        b_radius: The radius of circle B
    Returns a list of two points, the intersections of the circle, or None is none exist.
    """
    x_A, y_A = a_center
    x_B, y_B = b_center
    try:
        L_C = math.sqrt((x_A - x_B)**2 + (y_A - y_B)**2)
        b = (b_radius**2 - a_radius**2 + L_C**2) / (2 * L_C)
        h = math.sqrt(b_radius**2 - b**2)
        x_P = x_B + b * (x_A - x_B) / L_C
        y_P = y_B + b * (y_A - y_B) / L_C
        x_1 = x_P + h * (y_B - y_A) / L_C
        y_1 = y_P - h * (x_B - x_A) / L_C
        x_2 = x_P - h * (y_B - y_A) / L_C
        y_2 = y_P + h * (x_B - x_A) / L_C
    except ValueError:
        return None
    return [(x_1, y_1), (x_2, y_2)]

def line_extension(endpoint_1, endpoint_2, L):
    """
    line_extension: Given the two endpoints of a line, 
                    finds the endpoint of the line formed by extending line A by L_B from endpoint_2.
    Parameters:
        endpoint_1: The first endpoint of the line.
        endpoint_2: The second endpoint of the line, from which the line will be extended.
        L: The length of the extension
    Returns the point given by extending the line from endpoint_2 by L.
    """
    angle = line_angle(endpoint_1, endpoint_2)
    return (endpoint_2[0] + L * math.cos(angle), endpoint_2[1] + L * math.sin(angle))

def distance(point1, point2):
    """Calculate the distance between two points.
    
    Returns the distance between point1 and point2.
    """
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def line_angle(endpoint1, endpoint2):
    """Finds the slope of the line defined by the two endpoints as an angle.
    
    Returns an angle in radians.
    """
    return math.atan2(endpoint2[1] - endpoint1[1], endpoint2[0] - endpoint1[0])

def law_of_cosines(a, b, gamma):
    """Use the law of cosines to find the third side of a triangle.
    a and b are the other two sides, and gamma is the oposite angle (rad).
    """
    return math.sqrt(a*a + b*b - 2*a*b*math.cos(gamma))

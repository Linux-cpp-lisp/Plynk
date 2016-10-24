from driver import Driver
from plynk import geometry
import math

class Slider(Driver):
    """A slider type driver.
    
    A slider moves a joint back and forth along a straight line.
    
    Attributes:
        label: A user label.
        location: One of the endpoints of the slider's line. The endpoint that the joint starts and returns to.
        endpoint: The other endpoint of the slider. Determines the length of the slider. 
        attachment_joint: The joint the slider moves.
        speed: The percentage of the one back and forth that should be covered over all time.
    """
    def __init__(self, label, location, endpoint, attachment_joint, speed = 1.0):
        Driver.__init__(self, label, location, attachment_joint, speed)
        self.endpoint = endpoint
        
    def point_for_time(self, time):
        length = geometry.distance(self.location, self.endpoint)
        angle = geometry.line_angle(self.location, self.endpoint)
        if(time < 0.5):
            distance = time * 2 * length
        else:
            distance = length - (time - 0.5) * 2 * length
        return (self.location[0] + distance * math.cos(angle), self.location[1] + distance * math.sin(angle))
from driver import Driver
import math

class Crank(Driver):
    """An instance of the `Crank` class represents a rotating drive crank in the linkage mechanism.
    
    Attributes:
        label: A user label.
        location: The center of the crank.
        attachment_joint: The joint the crank is attached to.
        length: The radius of the crank.
        speed: The percentage of a full rotation that the crank should go through in 1 unit of time.
        starting_angle: The angle to start with in radians.
    """
    def __init__(self, label, location, attachment_joint, length, speed = 1.0, starting_angle = 0):
        Driver.__init__(self, label, location, attachment_joint, speed)
        self.starting_angle = starting_angle
        self.length = length
        
    def point_for_time(self, time):
        res = (self.location[0] + self.length * math.cos(self.starting_angle + time * 2 * math.pi),
               self.location[1] + self.length * math.sin(self.starting_angle + time * 2 * math.pi))
        return res
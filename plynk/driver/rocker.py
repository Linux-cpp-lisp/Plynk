from driver import Driver
import math

class Rocker(Driver):
    """A rocker type driver.
    
    Attributes:
        label: A user label.
        location: The center of the rocker.
        attachment_joint: The joint the rocker is attached to.
        length: The radius of the rocker.
        speed: The percentage of the one back and forth that should be covered over all time.
        starting_angle: The angle, in degrees, for the rocker to start at.
        ending_angle: The angle, in degrees, for the rocker to end at.
    """
    def __init__(self, label, location, attachment_joint, length, starting_angle, ending_angle, speed = 1.0):
        Driver.__init__(self, label, location, attachment_joint, speed)
        self.length = length
        self.starting_angle = starting_angle
        self.ending_angle = ending_angle
        
    def point_for_time(self, time):
        if(time < 0.5):
            angle = self.starting_angle + time * 2 * (self.ending_angle - self.starting_angle)
        else:
            angle = self.ending_angle - (time - 0.5) * 2 * (self.ending_angle - self.starting_angle)
        #Convert degrees to radians for the math functions:
        angle = (angle / 360.0) * 2 * math.pi
        return (self.location[0] + self.length * math.cos(angle), self.location[1] + self.length * math.sin(angle))
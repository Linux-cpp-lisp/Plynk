from plynk.joint import Joint
import math

class Driver(object):
    """The abstract superclass representing moving parts of the linkage that drive it, such as cranks and pistons.
    
    Attributes:
        label: A user label.
        location: The location (usually center point) of the driver.
        attachment_joint: The `Joint` that this driver modifies.
        speed: The divisor for the simulation progress. Allows different drivers to move at different speeds.
               For example, a crank with speed 0.5 would make it from 0 degrees to 180 degrees, while one at
               1.0 speed would go from 0 degrees to 360 degrees.
    """
    def __init__(self, label, location, attachment_joint, speed=1.0):
        self.label = label
        self.location = location
        self.attachment_joint = attachment_joint
        self.speed = speed
        
    def update_attachment_point(self, time):
        """Updates attachment_joint to the correct position for `time`.
        Arguments:
            time: A value ranging from 0.0 to 1.0 indicating the current simulated time.
        Returns nothing.
        """
        self.attachment_joint.location = self.point_for_time(math.fmod(time * self.speed, 1.0))
        
    def point_for_time(self, time):
        """Returns the correct position for attachment_joint for `time`.
        Arguments:
            time: A value ranging from 0.0 to 1.0 indicating the current speed-adjusted simulated time.
        Returns an X, Y tuple.
        """
        raise NotImplementedError("Instances of Driver are not meant to be used directly. Use a subclass that implements this method.")
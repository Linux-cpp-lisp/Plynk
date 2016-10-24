import plynk.geometry

class TimedJointsTracker(object):
    """Track any property of one or more joint over time.
    
    Attributes:
        joints: The joints to track.
        attribute: Any function taking a joint and returning a number.
        chooser: If `joints` contains more than one joint, this function decides which of the trackers joints
                 to track at this moment. Not needed if there is only one joint. Takes one argument mapping
                 joints to their attribute values. Returns a joint.
    """
    def __init__(self, joints, attribute, chooser = None):
        self.joints = joints
        self.attribute = attribute
        self.chooser = chooser
        
    def __call__(self, linkage, time):
        if(len(self.joints) > 1):
            return self.attribute(self.chooser({joint : self.attribute(joint) for joint in self.joints}))
        else:
            return self.attribute(self.joints[0])
        
    @staticmethod
    def x_coordinate(joint):
        """Attribute: the x coordinate of a joint"""
        return joint.location[0]
    
    @staticmethod
    def y_coordinate(joint):
        """Attribute: the y coordinate of a joint"""
        return joint.location[1]
    
    @staticmethod
    def least_attribute(joints):
        return min(joints, key=lambda j: joints[j])
    
    @staticmethod
    def greatest_attribute(joints):
        return max(joints, key=lambda j: joints[j])
    
class JointSpeedTracker(object):
    """Track the speed of a joint.
    
    Attributes:
        joint: The joint to track.
        dimension: The dimension in which to track speed. This can be 'x', to track X-speed, 'y' to track Y-speed, or 'xy' to track
                   speed in the Cartesian plane.
    """
    def __init__(self, joint, dimension='xy'):
        self.joint = joint
        self.dimension = dimension
        self.old_location = None
        self.old_time = None
        if not dimension in ['x', 'y', 'xy']:
            raise ValueError("Dimension '%s' is not 'x', 'y', or 'xy'." % dimension)
        
    def __call__(self, linkage, time):
        res = None
        if not (self.old_location == None or self.old_time == None):
            delta_t = time - self.old_time
            delta_l = None
            if self.dimension == 'x':
                delta_l = self.joint.location[0] - self.old_location[0]
            elif self.dimension == 'y':
                delta_l = self.joint.location[1] - self.old_location[1]
            elif self.dimension == 'xy':
                delta_l = plynk.geometry.distance(self.joint.location, self.old_location)
            res = float(delta_l) / delta_t
        self.old_location = self.joint.location
        self.old_time = time
        return res
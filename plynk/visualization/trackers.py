class JointPickerTracker(object):
    """Tracks whichever joint of a set of joints is chosen by a function.
    
    Attributes:
        joints: The joints to choose between.
        picker: A function that takes the list of joints, and returns the chosen one.
    """
    
    def __init__(self, joints, picker):
        self.joints_selector = joints
        self.picker = picker
        self.current_joint = None
        
    def __call__(self, linkage, time):
        joint = self.picker(linkage.js(self.joints_selector), time)
        if not joint == self.current_joint:
            #Insert discontinuity
            self.current_joint = joint
            return None
        else:
            return joint.location
    
    @staticmethod
    def least_y(joints, time):
        return min(joints, key = lambda j: j.location[1])
    
    @staticmethod
    def least_x(joints, time):
        return min(joints, key = lambda j: j.location[0])
    
    @staticmethod
    def greatest_y(joints, time):
        return max(joints, key = lambda j: j.location[1])
    
    @staticmethod
    def greatest_x(joints, time):
        return max(joints, key = lambda j: j.location[0])
    
    
    

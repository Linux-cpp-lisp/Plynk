from joint import Joint

import math

class Bar(object):
    """One bar in the linkage mechanism.
    
    Each `Bar` instance represents one connection between two joints in a linkage.
    
    Attributes:
               label: A user label.
              joints: A list of `Joint` objects representing the attachment joints of this bar.
     segment_lengths: A list of numbers representing the distance between each of the attachment
                      joints in `joints`. The first element is the distance between joints[0] and
                      joints[1], the second joints[1] and joints[2], and so on. Must contain
                      floor(len(joints) / 2.0) elements. The total length of the bar is the sum
                      of these.
    """
    def __init__(self, label, joints, segment_lengths):
        self.label = label
        self.joints = joints
        self.segment_lengths = segment_lengths
        if not len(joints) >= 2:
            raise ValueError("A bar must have at least two joints.")
        if not len(segment_lengths) == len(joints) - 1:
            raise ValueError("Wrong number of segment lengths. Got %s, expected %s." % (len(segment_lengths), len(joints) - 1))
            
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return ("%s: " % self.label) + (" -- %s -- ".join([str(joint) for joint in self.joints])) % tuple(self.segment_lengths)
    
    def known_endpoints(self):
        """Returns a number between indicating how many of the bar's endpoints are known."""
        return sum(joint.is_known() for joint in self.joints)
    
    def origin_distance(self, joint):
        """Find the distance of some joint from the origin joint (the first member of joints)."""
        if(not joint in self.joints):
            raise ValueError("The given joint %s is not in this bar's joint list." % joint)
        distance = 0
        for index, element in enumerate(self.joints):
            if(joint == element):
                break;
            distance += self.segment_lengths[index]
        return distance
    
    def joint_distance(self, joint1, joint2):
        """Find the distance between two joints on the bar."""
        return abs(self.origin_distance(joint1) - self.origin_distance(joint2))
    
    def neighbor_joints(self, joint):
        """Finds the one or two joints directly next to the given joint on the bar."""
        if(not joint in self.joints):
            raise ValueError("The given joint %s is not in this bar's joint list." % joint)
        i = self.joints.index(joint)
        if(i == 0):
            return [self.joints[1]]
        elif(i == len(self.joints) - 1):
            return [self.joints[i - 1]]
        else:
            return [self.joints[i - 1], self.joints[i + 1]]
    
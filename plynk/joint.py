class Joint(object):
    """The Joint class represents one joint in the linkage mechanism.
    
    Each `Joint` represents one fixed or moving point where bars meet
    in the linkage mechansim.
    
    Attributes:
        label: A user label.
        location: The current location of the joint as an X, Y tuple.
        fixed: A boolean that indicates if the joint is fixed in space.
        chooser: A function taking two possible locations for the joint
                 that returns one of them.
    """
    
    def __init__(self, label, location = None, fixed = False, chooser = None):
        self.label = label
        self.fixed = False
        self.location = location
        self.fixed = fixed
        self.chooser = chooser
        
    def __setattr__(self, pname, val):
        if(pname == "location" and self.fixed):
            raise AttributeError("The location of fixed joints cannot be changed.")
        else:
            object.__setattr__(self, pname, val)
            
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        if(self.is_known()):
            return "(%s: %f, %f)" % (self.label, self.location[0], self.location[1])
        else:
            return "(%s: ?)" % self.label
    
    def is_known(self):
        """Returns whether the location of the joint is known."""
        return self.location != None
    
    def set_location(self, location1, location2 = None):
        """If necissary, chooses location1 or location2, and then assigns it as the joint's location.
        
        Parameters:
            location1: A possible location, as an XY-tuple.
            location2: A possible location, as an XY-tuple. If ommited, location1 will be used unconditionally.
            
        Returns nothing.
        """
        if(location2 == None):
            self.location = location1
        elif(self.chooser != None):
            self.location = self.chooser(location1, location2)
        else:
            raise ValueError("Joint %s does not have a chooser function. Calling choose_location is therefore invalid." % self.label)
        
    def reset_fixed_location(self, newloc):
        """Override the assignment guard for location on fixed joints."""
        if not self.fixed:
            raise ValueError("Calling reset_fixed_location on a dynamic joint is meaningless.")
        object.__setattr__(self, "location", newloc)
    
        
def greater_x(point1, point2):
    """Chooses the point with the greater x coordinate."""
    return point1 if point1[0] > point2[0] else point2

def greater_y(point1, point2):
    """Chooses the point with the greater y coordinate."""
    return point1 if point1[1] > point2[1] else point2

def lesser_x(point1, point2):
    """Chooses the point with the lesser x coordinate."""
    return point1 if point1[0] < point2[0] else point2

def lesser_y(point1, point2):
    """Chooses the point with the lesser y coordinate."""
    return point1 if point1[1] < point2[1] else point2
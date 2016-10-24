from plynk import Joint, Bar, Linkage

from numbers import Number

class LinkageBuilder(object):
    def __init__(self):
        self.bar_builders = []
        self.joints = {}
        self.driver_builders = []
        self.linkage = None
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.linkage = self.build()
        
    def __call__(self, jlabel, *args, **kwargs):
        if jlabel in self.joints:
            bb = BarBuilder(start_joint=self.joints[jlabel])
            self.bar_builders.append(bb)
            if not len(args) == 0:
                print "Warning: Attempt to reinitialize joint %s." % jlabel
            if not len(kwargs) == 0:
                print "Warning: Attempt to reinitialize joint %s." % jlabel
            return bb
        else:
            joint = Joint(jlabel, *args, **kwargs)
            self.joints[jlabel] = joint
            bb = BarBuilder(start_joint = joint)
            self.bar_builders.append(bb)
            return bb
        
    def __getitem__(self, label):
        return BuilderLabeler(label)
        
    def driver(self, klass, *args, **kwargs):
        db = DriverBuilder(klass, args, kwargs)
        self.driver_builders.append(db)
        return db
        
    def build(self):
        bbs = [bb for bb in self.bar_builders if not bb.is_one_joint()]
        return Linkage([builder.build() for builder in bbs],
                       [self.joints[k] for k in self.joints],
                       [builder.build() for builder in self.driver_builders])
        
class Labelable(object):
    """Any builder class that can be assigned a label.
    """
    pass

class BuilderLabeler(object):
    def __init__(self, label):
        self.label = label
        
    def __sub__(self, other):
        if not isinstance(other, Labelable):
            raise TypeError("Only Labelable builder objects can be linked to a BuilderLabeler. %s is not labelable." % other)
        other.label = self.label
        return other

class DriverBuilder(Labelable):
    def __init__(self, klass, args, kwargs, label = ""):
        self.klass = klass
        self.args = args
        self.kwargs = kwargs
        self.label = label
        
    def build(self):
        args = []
        for a in self.args:
            if(isinstance(a, BarBuilder) and a.is_one_joint()):
                args.append(a.joints[0])
            else:
                args.append(a)
        return self.klass(self.label, *args, **self.kwargs)
    
class BarBuilder(Labelable):
    def __init__(self, start_joint = None, label = ""):
        self.joints = []
        self.segments = []
        self.next_expected = "joint"
        self.label = label
        if(start_joint != None):
            self.joints.append(start_joint)
            self.next_expected = "len"
    
    def __sub__(self, other):
        other_type = ""
        if(isinstance(other, Number)):
            other_type = "len"
        elif(isinstance(other, Joint) or isinstance(other, BarBuilder)):
            other_type = "joint"
        else:
            raise TypeError("Next bar building value %s is not a length or a joint." % other)
        if(other_type != self.next_expected):
            raise ValueError("Expecting next bar building value to be a %s, got a %s." % (self.next_expected, other_type))
        else:
            if(other_type == "joint"):
                if(isinstance(other, BarBuilder)):
                    self.joints.extend(other.joints)
                    self.segments.extend(other.segments)
                    self.next_expected = other.next_expected
                else:
                    self.joints.append(other)
                    self.next_expected = "len"
            else:
                self.segments.append(other)
                self.next_expected = "joint"
        return self
    
    def is_one_joint(self):
        return len(self.joints) == 1 and len(self.segments) == 0
    
    def __str__(self):
        return "%s expecting %s" % (', '.join([str(s) for s in self.segments]), self.next_expected)
    
    def build(self):
        if self.next_expected == "joint":
            raise ValueError("You cannot build a BarBuilder that is still expecting a joint.\n\
                             BarBuilder %s:\n\
                             Segs: %s\n\
                             Joints: %s" % (self.label, self.segments, self.joints))
        return Bar(self.label, self.joints, self.segments)
    
    
    

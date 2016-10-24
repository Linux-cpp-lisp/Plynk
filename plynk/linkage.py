import geometry, math, re, copy

from bar import Bar, Joint
from driver import Driver

from itertools import repeat, combinations, product, tee, izip

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

class Linkage(object):
    """A `Linkage` represents a linkage mechanism.
    
    A linkage consists of three things: bars, joints, and drivers.
    
    Bars are static connections between two joints. Bars are represented by instances of the `Bar` class.
    
        Note: The joints that the bars reference must not only have the same names as the ones in the
              `joints` list, but must actually be the same object.
    
    Joints are the points where bars meet and where drivers connect to the mechanism.
    
    Drivers are any "motorized" mechanism that moves the mechansim, such as cranks or pistons.
    
        Note: As with bars, the joints referenced by a driver must be the same objects as those in
              the `joints` list.
              
    Linkage objects are stateful for simulation. One method is used to update the values to a certain
    simulator time, and then the data can be accessed and processesed through the properties of the linkage.
              
    Attributes:
           bars: The bars of the linkage. A list of `Bar` objects.
           
         joints: The joints of the linkage. These *must* be the same objects as those refered to by
                 the bars and drivers. A list of `Joint` objects.
                 
        drivers: The drivers of the linage. A list of `Driver` objects.
    """
    def __init__(self, bars, joints, drivers):
        self.supress_validity = True
        
        self.bars = bars
        self.joints = joints
        self.drivers = drivers
        
        self.supress_validity = False
        
        self.cache = {}
        self.cache_accuraccy = 10000
        
        self.validity_check()
        
    def __setattr__(self, aname, value):
        object.__setattr__(self, aname, value)
        if aname in ['bars', 'joints', 'drivers']:
            if(not self.supress_validity):
                self.validity_check()
            self.invalidate_caches()
        
    def invalidate_caches(self):
        """Invalidate cached simulation functions and data."""
        self.simulation_function = None
        self.cache = None
            
    def validity_check(self):
        """Does preliminary checks of validity and joint reference.
        
        Throws ValueError on any problems found, or returns True if none found.
        """
        #-- Validity Checks --
        joint_references = dict(zip(self.joints, repeat(0)))
        #Check that no bars reference unknown joints.
        for bar in self.bars:
            for joint in bar.joints:
                if joint not in self.joints:
                    raise ValueError("Bar %s references a Joint \"%s\" not in the linkage's joint list." % (bar.label, joint.label))
        #Check that no drivers reference unknown joints.
        for d in self.drivers:
            if d.attachment_joint not in self.joints:
                raise ValueError("Driver %s references a Joint \"%s\" not in the linkage's joint list." % (d.label, d.attachment_joint.label))
        return True
            
    def simulate_to_time(self, time):
        """Update the linkages state for simulator time `time`.
        
        Given a simulator time `time`, simulates the positions of all joints for that time and updates
        the state of the linkage to match.
        
        If the current configuration of the linkage is physically impossible, raises `InvalidLinkageError`.
        
        Parameters:
            time: A simulator time between 0 and 1.
            
        Returns nothing, data is contained in the linkage object.
        """
        #Validate the time parameter
        if(not 0 <= time <= 1):
            raise ValueError("Simulator time `time` must be between 0 and 1, cannot be %s" % time)
        cache_time = math.floor(self.cache_accuraccy * time)
        if(self.cache != None and cache_time in self.cache):
            #There's a cache entry, use it:
            for joint in self.cache[cache_time]:
                joint.set_location(self.cache[cache_time][joint])
            return None
        else:
            #No cache entry.
            if self.cache == None:
                self.cache = {}
            if(self.simulation_function == None):
                self.simulation_function = self.generate_simulation_function()
            self.simulation_function(time)
            #Cache the current state:
            cache_state = {}
            for joint in [joint for joint in self.joints if not joint.fixed]:
                cache_state[joint] = joint.location
            self.cache[cache_time] = cache_state
            return None
        
        
    def generate_simulation_function(self, validity_margin = 0.001):
        """Create a simulation function for the current configuration of the linkage.
        
        If the current configuration of the linkage is physically impossible, raises `InvalidLinkageError`.
        
        Returns a function taking a `time` parameter.
        """
        def solver_for_intersection(unknown_joint, known_joints, bars):
            a = known_joints[0]
            b = known_joints[1]
            a_bar = next(bar for bar in bars if a in bar.joints)
            b_bar = next(bar for bar in bars if b in bar.joints)
            def solver(time):
                loc = (geometry.circular_intersection(a.location,
                                                      a_bar.joint_distance(unknown_joint, a),
                                                      b.location,
                                                      b_bar.joint_distance(unknown_joint, b)))
                if(loc == None):
                    raise InvalidLinkageError("No physically possible intersections for joint %s can be found from joints %s an %s using bars %s and %s." %
                                              (unknown_joint, a, b, a_bar.label, b_bar.label))
                unknown_joint.set_location(*loc)
            solver.solver_type = "intersection"
            return solver
        
        def solver_for_joint_on_bar_given_joints(joint, bar, joints):
            def solver(time):
                joint.set_location(geometry.line_extension(joints[0].location,
                                                           joints[1].location,
                                                           bar.origin_distance(joint) - bar.origin_distance(joints[1])))
            solver.solver_type = "extension"
            return solver
        
        #Create a set representing the joints that the algorithm has "solved"
        #up to this point. This starts off as all fixed joints, and all joints attached to drivers.
        solved_joints = set([driver.attachment_joint for driver in self.drivers]) | set([joint for joint in self.joints if joint.fixed])
        
        #A list mapping sets of joints representing the joints that must be known to find another joint using the given solver.
        #The values are tuples of the form (requirement_set, joint, solver) where joint is the joint that will be solved when solver is run.
        requirements_to_functions = []
        
        #Step 1: Find all posible solvers for all unknown points.
        #Now we need to find every way all of the unknown joints could possibly be found.
        for joint in set(self.joints) - solved_joints:
            bars = self.bars_connected_to_joint(joint)
            #Find all linear extension solving posibilities
            for bar in [bar for bar in bars if len(bar.joints) > 2]:
                #If a bar has more than 2 joints, any joint connected to it can be found
                #as soon as two of the others are found.
                
                #Get all the joints except the one we're looking to solve for.
                other_joints = bar.joints[:]
                other_joints.remove(joint)
                #Find all pairs of the other joints, and insert an entry for each.
                for pair in combinations(other_joints, 2):
                    s = (frozenset(pair), joint, solver_for_joint_on_bar_given_joints(joint, bar, other_joints))
                    requirements_to_functions.append(s)
            
            #Find all circular intersection solving possibilities
            if(len(bars) < 2):
                #If there are not two bars connected, we obviously cannot solve by circular intersection.
                continue
            for bar_pair in combinations(bars, 2):
                b1_joints = set(bar_pair[0].joints)
                b2_joints = set(bar_pair[1].joints)
                b1_joints -= set([joint])
                b2_joints -= set([joint])
                for joint_pair in product(b1_joints, b2_joints):
                    requirements_to_functions.append((frozenset(joint_pair), joint, solver_for_intersection(joint, joint_pair, bar_pair)))
        
        #Define the list of functions that will be invoked in order by the final simulation function.
        #When invoked, each function will be passed the current simulated time.
        #This starts as the driver update functions of all the drivers.
        function_list = [driver.update_attachment_point for driver in self.drivers]
        
        #Step 2: Iteration by iteration, find the solvers whose requirements have been met
        #and add them to the list in order.
        while(True):
            round_solved = False
            #Define a mutable copy of the requirements/functions dictionary
            #that can be modified during iteration.
            new_requirements_to_functions = requirements_to_functions[:]
            for solver in requirements_to_functions:
                if(solver[0].issubset(solved_joints)):
                    if not solver[1] in solved_joints:
                        #Indicate that at least one joint has been solved this iteration:
                        round_solved = True
                        #Add the solver function to the function list:
                        function_list.append(solver[2])
                        #Add the solved joint to the solved joints set:
                        solved_joints.add(solver[1])
                        #Remove the function and it's requriements from the requirements/functions dictionary.
                        new_requirements_to_functions.remove(solver)
            #Update the original to the copy.
            requirements_to_functions = new_requirements_to_functions
            #Check if all points have been solved:
            if(solved_joints == set(self.joints)):
                #If they have, just break. The function_list is now complete,
                #and the simulation function just needs to be defined.
                break
            #If we made no progress this round, and the linkage hasen't been solved,
            #whatever joints remain are unsolvable.
            if(not round_solved):
                unsolvable_joints = set(self.joints) - solved_joints
                raise InvalidLinkageError("Some joints cannot be solved because they are ambiguous, or are unconnected to the linkage.\
                                          Unknown joints: %s" % ", ".join([str(joint) for joint in unsolvable_joints]))
                
        def sim_function(time):
            for function in function_list:
                function(time)
            #Do a validity check for elastic bars:
            for bar in self.bars:
                for joints in pairwise(bar.joints):
                    p1 = joints[0].location
                    p2 = joints[1].location
                    real_dist = geometry.distance(p1, p2)
                    dist = bar.joint_distance(joints[0], joints[1])
                    if not abs(dist - real_dist) < validity_margin:
                        raise InvalidLinkageError("Distance constraint of %s units from bar %s between joints %s and %s cannot be satisfied." % (dist, bar.label, joints[0].label, joints[1].label))
                
        return sim_function
        
    def copy(self, shared_joints = [], shared_drivers = [], joint_indic = ''):
        mapping = {}
        shared_joints.extend([d.attachment_joint for d in shared_drivers])
        for j in shared_joints:
            mapping[j] = j
        joints = shared_joints[:]
        for j in set(self.joints) - set(shared_joints):
            newj = copy.deepcopy(j)
            newj.label = newj.label + joint_indic
            joints.append(newj)
            mapping[j] = newj
        bars = []
        for bar in self.bars:
            newbar = copy.deepcopy(bar)
            newjoints = []
            for oldj in bar.joints:
                if oldj in mapping:
                    newjoints.append(mapping[oldj])
                else:
                    newjoints.append(oldj)
            newbar.joints = newjoints
            bars.append(newbar)
        drivers = shared_drivers[:]
        for d in set(self.drivers) - set(shared_drivers):
            newd = copy.deepcopy(d)
            newd.attachment_joint = mapping[d.attachment_joint]
            drivers.append(newd)
        return Linkage(bars, joints, drivers)
        
    def joints_connected_to_joint(self, joint):
        """Find all joints in the linkage connected to the given joint.
        
        Parameters:
            joint: The joint to find joints for.
            
        Returns a list of Joints.
        """
        bars = self.bars_connected_to_joint(joint)
        joints = [bar.joints for bar in bars]
        joints = [joint for joint_list in joints for joint in joint_list]
        return list(set(joints))
        
    def bars_connected_to_joint(self, joint):
        """Find all bars connected to a joint.
        
        Parameters:
            joint: The joint to find joints for
            
        Returns a list of bars.
        """
        return [bar for bar in self.bars if joint in bar.joints]
        
    def translate(self, dx, dy):
        """Translate the linkage by a given transform."""
        for driver in self.drivers:
            driver.location = (driver.location[0] + dx, driver.location[1] + dy)
        for joint in [j for j in self.joints if j.fixed == True]:
            joint.reset_fixed_location((joint.location[0] + dx, joint.location[1] + dy)) 
        
    def j(self, label):
        """Return the joint with the given label.

        If none is found, None is returned.
        
        If more than one joint has the label, it is undefined which is returned.
        """
        return next((j for j in self.joints if j.label == label), None)
    
    def js(self, pattern):
        """Return all joints with labels matching pattern.
        
        pattern is a string to be compiled to a regex.
        """
        return [j for j in self.joints if re.match(pattern, j.label) != None]
    
    def b(self, label):
        """Return the bar with a given label.
        
        If more than one joint has the label, it is undefined which is returned.
        """
        return next(b for b in self.bars if b.label == label)
    
    def bs(self, label):
        """Return all joints with labels matching pattern.
        
        pattern is a string to be compiled to a regex.
        """
        return [b for b in self.bars if re.match(patter, b.label) != None]
    
class InvalidLinkageError(Exception):
    """The given bars result in a physically impossible situation."""
    pass
    

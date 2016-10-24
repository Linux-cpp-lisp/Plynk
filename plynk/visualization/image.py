from matplotlib import pyplot as plt

from plynk.visualization import util

plt.style.use('ggplot')

def linkage_image(linkage,
                  time = 0,
                  size = (5, 5),
                  legend = True,
                  inset = 0.2,
                  dpi = 100,
                  title = "Linkage",
                  track_joints = [],
                  track_functions = [],
                  style = {'joint' : 'ko', 'bar' : 'b-', 'driver' : 'b-', 'tracked' : '--'},
                  frames = 200):
    """Create an image of a linkage at time `time`.
    
    Parameters:
        linkage: The linkage to visualize.
        time: The time to visualize the linkage at.
        size: The size of the figure in inches.
        legend: Whether or not to include a legend.
        inset: The inset of the linkage in the figure.
        track_joints: A list of joints to plot the locations of over time.
                      Each entry is a tuple of a label for the joint, and the joint itself.
        style: A dictionary of matplotlib styles to use for the different elements.
        title: The figure title.
        
    Returns a matplotlib figure.
    """
    fig = plt.figure(figsize=size, dpi=dpi)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title(title)
    ax.axis('equal')
    ax.margins(inset)
    
    joints, = ax.plot([], [], style['joint'])
    bars = [(bar, ax.plot([], [], style['bar'])[0]) for bar in linkage.bars]
    drivers = [(driver, ax.plot([], [], style['driver'])[0]) for driver in linkage.drivers]
    joint_trackers = [(joint[1], ax.plot([], [], style['tracked'], label = joint[0])[0]) for joint in track_joints]
    func_trackers = [(tracker[1], ax.plot([], [], style['tracked'], label = tracker[0])[0]) for tracker in track_functions]
    
    joints.set_zorder(3)
    
    linkage.simulate_to_time(time)
    joints.set_data(*(zip(*[j.location for j in linkage.joints])))
    for e in bars:
        e[1].set_data(*(zip(*[j.location for j in e[0].joints])))
    for e in drivers:
        e[1].set_data(*(zip(*[e[0].location, e[0].attachment_joint.location])))
        
    for i in range(frames):
        linkage.simulate_to_time(i / float(frames))
        for e in joint_trackers:
            new_point = e[0].location
            points = zip(*e[1].get_data())
            points.append(new_point)
            e[1].set_data(*(zip(*points)))
        for e in func_trackers:
            new_point = e[0](linkage, i / float(frames))
            points = zip(*e[1].get_data())
            if new_point == None:
                new_point = (np.nan, np.nan)
            points.append(new_point)
            e[1].set_data(*(zip(*points)))
        
    ax.relim()
    ax.autoscale()
    
    if((len(track_joints) > 0 or len(track_functions) > 0) and legend):
        util.outside_legend(ax, fancybox=True, shadow=True)
    
    return fig

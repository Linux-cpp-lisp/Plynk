from matplotlib import pyplot as plt
from matplotlib import animation

import numpy as np

from plynk.visualization import util

plt.style.use('ggplot')

import math
 
def linkage_animation(linkage,
                      track_joints = [],
                      track_functions = [],
                      track_timed_funcs = [],
                      size = (6, 3),
                      modifier = None,
                      legend = True,
                      columns = 2,
                      title = "Linkage",
                      dpi = 80,
                      frames = 200,
                      repetitions = 2,
                      interval = 10,
                      inset = 0.3,
                      style = {'joint' : 'o', 'bar' : 'b-', 'driver' : 'b-', 'tracked' : ':'}):
    """Create an animation of a linkage and it's properties over time.
    
    Parameters:
        linkage: The linkage to animate. The linkage will be simulated in place.
        track_joints: A list of joints to plot the locations of over time.
                      Each entry is a tuple of a label for the joint, and the joint label.
        track_functions: A list of functions that take the linkage and return a point value for that frame to track.
                         Each entry is a tuple of a label for the function, and the function itself.
        track_time_funcs: A list of functions that produce a value for the linkage at some time value.
                          The function is called with the linkage as the first argument, and the current
                          simulator time as the other, and must return one number, the value for that time.
                          Each entry is a tuple of a label and a function.
        size: The size of each cell.
        title: The title of the linkage.
        legend: Whether or not to include a legend.
        columns: The number of subplot columns.
        dpi: The DPI of the figure/animation.
        modifier: A function called with the linkage, frame number and time that can make modifications to the linkage before it is simulated.
                    Note: This will probably reduce performance by most likley invalidating caches each frame.
                    Note: This function must only depend on the linkage passed to it, and not an external variable,
                            as it will be called with a COPY of the original linkage.
        frames: Frames per repetition.
        repetitions: The number of times to cycle through the animation.
        interval: The number of miliseconds between frames.
        inset: The inset of the animation from the graph edges.
        style: The matplotlib styles to be used. A dictionary mapping 'joint', 'bar', 'tracked', and 'driver' to matplotlib format strings.
        
    Returns a matplotlib FuncAnimation object that can be played, displayed, and saved, and the figure it animated that can be shown.
    """
    #The total number of frames is the number of frames per repetition times repetitions.
    frames = frames * repetitions
    #Solve for the number of rows, based on the number of columns and things:
    rows = round((len(track_timed_funcs) + 1)/float(columns))
    if (len(track_timed_funcs) + 1) < columns:
        columns = (len(track_timed_funcs) + 1)
    #Create the figure:
    fig = plt.figure(figsize=(size[0] * columns, size[1] * rows))
    fig.set_dpi(dpi)
    ax = fig.add_subplot(rows, columns, 1)
    ax.set_title(title)
    ax.axis('equal')

    #If a modifier is present, copy the linkage
    if modifier != None:
        linkage = linkage.copy()

    #Get real joints for tracked_joints
    track_joints = [(e[0], linkage.j(e[1])) for e in track_joints]
    
    #Create the Line2D objects for everything that will be plotted.
    bars = [(bar, ax.plot([], [], style['bar'])[0]) for bar in linkage.bars]
    drivers = [(driver, ax.plot([], [], style['driver'])[0]) for driver in linkage.drivers]
    joint_trackers = [(joint[1], ax.plot([], [], style['tracked'], label = joint[0])[0]) for joint in track_joints]
    func_trackers = [(tracker[1], ax.plot([], [], style['tracked'], label = tracker[0])[0]) for tracker in track_functions]
    joints, = ax.plot([], [], style['joint'])
    
    #Create the subplots and lines for all the timed functions:
    time_functions = []
    for idex, e in enumerate(track_timed_funcs):
        subplt = fig.add_subplot(rows, columns, 2 + idex, xlabel="Simulator Time", ylabel=e[0])
        subplt.set_title(e[0])
        subplt.set_xlim([0, 1])
        #subplt.set_xlabel("Simulator Time")
        #subplt.set_ylabel(e[0])
        line, = subplt.plot([], [], '-')
        time_bar = subplt.axvline(linestyle = '--', color = 'k', alpha = 0.8)
        time_functions.append((e[1], line, time_bar, subplt))
    
    #Construct the list of all graph items being animated:
    graph_items = []
    graph_items.extend([e[1] for e in bars])
    graph_items.extend([e[1] for e in drivers])
    graph_items.extend([e[1] for e in joint_trackers])
    graph_items.extend([e[1] for e in func_trackers])
    graph_items.extend([e[1] for e in time_functions])
    graph_items.extend([e[2] for e in time_functions])
    graph_items.append(joints)
    
    def init():
        #The init function for the animation. Resets everything animated to nothing.
        for item in graph_items:
            item.set_data([], [])
        return graph_items
    
    #Initialize the data
    data = {}
    #For every frame index, create and store the data for everything in graph_items:
    for i in range(frames):
        #Find the simulator time:
        time = math.fmod(i/(float(frames) / repetitions), 1.0)
        #Modify
        if modifier != None:
            modifier(linkage, i, time)
            linkage.invalidate_caches()
        #Simulate the linkage:
        linkage.simulate_to_time(time)
        #Initialize the data for this frame:
        frame_data = dict({})
        for e in bars:
            frame_data[e[1]] = zip(*[j.location for j in e[0].joints])
        for e in drivers:
            frame_data[e[1]] = zip(*[e[0].location, e[0].attachment_joint.location])
        for e in joint_trackers:
            new_point = e[0].location
            points = zip(*(data[i-1][e[1]])) if i != 0 else []
            points.append(new_point)
            frame_data[e[1]] = zip(*points)
        for e in func_trackers:
            new_point = e[0](linkage, time)
            points = zip(*(data[i-1][e[1]])) if i != 0 else []
            if new_point == None:
                new_point = (np.nan, np.nan)
            if(i < (frames / repetitions)):
                points.append(new_point)
            frame_data[e[1]] = zip(*points)
        for e in time_functions:
            points = zip(*(data[i-1][e[1]])) if i != 0 else []
            new_point = (time, e[0](linkage, time))
            if(new_point[1] == None):
                new_point = (new_point[0], np.nan)
            if(i < (frames / repetitions)):
                points.append(new_point)
                points.sort(key = lambda p: p[0])
            frame_data[e[1]] = zip(*points)
            frame_data[e[2]] = ([time, time], [0, 1])
        frame_data[joints] = zip(*[j.location for j in linkage.joints])
        data[i] = frame_data
    
    #The animate function just sets the precomputed data for that frame.
    def animate(i):
        for graph_item in graph_items:
            graph_item.set_data(*data[i][graph_item])
        return graph_items
    
    #Autscale all animated things.
    util.autoscale_animation([ax], init, animate, frames = frames, inset = inset)
    util.autoscale_animation([e[3] for e in time_functions], init, animate, axis='y', frames = frames)
    
    #If a legend is wanted, make one:
    if(legend and (len(joint_trackers) > 0 or len(track_functions) > 0)):
        util.outside_legend(ax, fancybox=True, shadow=True, ncol = int(math.ceil(size[0] / 2.0)))
    
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=frames, interval=interval, blit=True)
    return anim, fig

def linkage_animation_to_file(filename, *args, **kwargs):
    """Creates a linkage animation and saves it to filename. Takes same arguments as linkage_animation.
    Returns nothing.
    """
    anim = linkage_animation(*args, **kwargs)
    save_animation(anim[0], filename, dpi = anim[1].get_dpi())
    return None

def save_animation(animation, filename, codec="qtrle", dpi = 100):
    """Save an animation generated by linkage_animation.
    
    Parameters:
        filename: The filename to save to.
        codec: The codec to use. The tested options are below:
                - libx264: The H.264 codec. Produces very small videos of reasonable quality,
                           but artifacts and bluring are obvious.
                - qtrle (default): The QuickTime RLE Animation codec. Produces nearly lossless
                           quality, and large files, but still smaller than PNG. Optimal.
                - png: The PNG codec. Produces very large completly loseless files. 
        
    Returns nothing.
    """
    #To get reasonable quality, the PNG codec was neccesary, although it makes the files big.
    #For smaller lower quality files, use libx264.
    animation.save(filename, codec=codec, bitrate=-1, dpi = dpi)

from functools import wraps
 
def autoscale_animation(axes, animation_init, animation_func, frames = 200, axis = 'both', inset = 0):
    """Rescale a set of axes to fit the range of an animation on those axes.
    
    Important Note: Animations that are sent to this function have both of their
    animation functions called multipe times, and those functions shouldn't have
    any side effects because of that.
    
    Parameters:
        axes: A list of matplotlib axes that are being animated by the given
              animating functions.
        animation_init: A matplotlib FuncAnimation initialization function.
                        This function is called TWO times: once to initialize the
                        animation, and again to reset it after the work is done.
        animation_func: A matplotlib FuncAnimation animation function. This is called
                        `frames` times.
        axis: The axis dimensions to autoscale. Can be 'both' (default), 'x', or 'y'.
        frames: The nubmber of frames to simulate.
        
    Returns nothing.
    """
    animation_init()
    limlist = [([], []) for ax in axes]
    for i in range(frames):
        graph_items = animation_func(i)
        for idex, ax in enumerate(axes):
            xdat = []
            ydat = []
            for graph_item in [g for g in graph_items if g.get_axes() == ax]:
                xdat.extend(graph_item.get_xdata())
                ydat.extend(graph_item.get_ydata())
            limlist[idex][0].append((min(xdat), max(xdat)))
            limlist[idex][1].append((min(ydat), max(ydat)))
    for idex, ax in enumerate(axes):
        xlim = (min([xlim[0] for xlim in limlist[idex][0]]), max([xlim[1] for xlim in limlist[idex][0]]))
        ylim = (min([ylim[0] for ylim in limlist[idex][1]]), max([ylim[1] for ylim in limlist[idex][1]]))
        xlen = xlim[1] - xlim[0]
        ylen = ylim[1] - ylim[0]
        xlim = (xlim[0] - xlen*inset, xlim[1] + xlen*inset)
        ylim = (ylim[0] - ylen*inset, ylim[1] + ylen*inset)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        
def autoscaled(frames = 200, axis = 'both'):
    """Autoscale an animator. Decorator."""
    def wrap(animator):
        @wraps(animator)
        def inner(*args, **kwargs):
            animation = animator(*args, **kwargs)
            #args[0] is always the axes for an animator.
            autoscale_animation(args[0], animation[0], animation[1], frames = frames, axis = axis)
            return animation
        return inner
    return wrap
        
def compose_animations(animations):
    """Compose multiple function animations into one.
    
    All of the animations will run on the same clock.
    
    Parameters:
        animations: A list of tuples. Each tuple is an animation where the first element
                    is the initialization function of the animation and the second is
                    the animation function.
                    
    Returns a tuple of an init function and an animate function.
    """
    inits = [e[0] for e in animations]
    animates = [e[1] for e in animations]
    def init():
        graph_items = []
        for ifunc in inits:
            graph_items.extend(ifunc())
        return graph_items
    
    def animate(i):
        graph_items = []
        for afunc in animates:
            graph_items.extend(afunc(i))
        return graph_items
    
    return (init, animate)

def outside_legend(ax, **kwargs):
    """Create a legend outside the plot on ax.
    All keyword arguments are passed through to Axes.legend.
    Returns nothing.
    """
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                    box.width, box.height * 0.9])
    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), **kwargs)
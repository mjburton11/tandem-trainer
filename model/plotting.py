from gpkit.small_scripts import unitstr
import numpy as np
import matplotlib.pyplot as plt
from gpkit import Variable
import gpkit

def fix_vars(model, solution, var_names):
    """
    Fixes variables to values found in initial solution

    Arguments
    ---------
    model: Model
    solution: soluation - initial solution with values of vars to be fixed
    var_names: Dict - variable names of vars to be fixed and value of added
                      tolerance
    """
    for name in var_names:
        value = solution(name).magnitude
        model.substitutions.update({name: value + var_names[name]})

def plot_sweep(model, xvarname, xsweep, yvarnames=None, ylim=None, fig=None, axis=None):
    """
    Takes model with sweep input and returns figure with desired output var

    Arguments
    ---------
    model: Model
    xvarname: String - variable name of sweep var
    xsweep: np.array - sweep values
    yvarname: String - variable name of desired output
    ylim: 2D array - plotting limits on y axis; x axis defaults are sweep min
                     and max

    Returns
    -------
    fig, ax: figure and axis of subplot
    """
    if not fig and not axis:
        fig, axis = plt.subplots(len(yvarnames))
        if not isinstance(axis, np.ndarray) == 1:
            axis = [axis]

    if model.varkeys[xvarname].__len__() > 1:
        oldsub = [vk.value for vk in model.varkeys[xvarname]]
        for yvarname, ax in zip(yvarnames, axis):
            ys = []
            for x in xsweep:
                for vk in model.varkeys[xvarname]:
                    model.substitutions.update({vk: x})
                try:
                    sol = model.solve("mosek")
                    ys.append(sol(yvarname).magnitude)
                except RuntimeWarning:
                    ys.append(np.nan)
            ax.plot(xsweep, ys)
            ax.set_ylabel("%s [%s]" % (model[yvarname].descr["label"],
                                       unitstr(model[yvarname].units)))
            ax.set_xlabel("%s [%s]" % (vk.descr["label"], unitstr(vk.units)))

            if ylim:
                ax.set_ylim((ylim[0], ylim[1]))
            ax.grid()

        for vk, os in zip(model.varkeys[xvarname], oldsub):
            model.substitutions.update({vk: os})

    else:
        oldsub = model.substitutions[xvarname]

        model.substitutions.update({xvarname: ("sweep", xsweep)})
        sol = model.solve("mosek", skipsweepfailures=True)

        for yvarname, ax in zip(yvarnames, axis):

            if yvarname:
                if yvarname not in model.substitutions:
                    ax.plot(sol(xvarname), sol(yvarname))
                else:
                    ax.plot(sol(xvarname),
                            [sol(yvarname).magnitude]*len(sol(xvarname)))
                ax.set_ylabel("%s [%s]" % (model[yvarname].descr["label"],
                                           unitstr(model[yvarname].units)))
            else:
                ax.plot(sol(xvarname),
                        sol["sensitivities"]["constants"][xvarname])
                ax.set_ylabel("%s sens" % model[xvarname].descr["label"])

            ax.set_xlabel("%s [%s]" % (model[xvarname].descr["label"],
                                       unitstr(model[xvarname].units)))
            if ylim:
                ax.set_ylim((ylim[0], ylim[1]))

            plt.grid()

        model.substitutions.update({xvarname: oldsub})

    return fig, axis

def plot_mission_var(model, sol, yvarname, ylim=False, yaxis_name=None):
    """
    Plots a mission varible against mission time.

    Arguments
    ---------
    model: must be GasPoweredMALE from gasmale.py
    yvarname: String - variable string name

    Returns:
    fig, ax: matplotlib figure and axis - time not to scale, labeled
             by mission profile inhereint in model.
    """

    y = []
    flightseg = []
    shape = [0]
    for subm in model.submodels:
        if subm.__class__.__name__ == "Mission":
            for i, fs in enumerate(subm.submodels):
                if "/" in yvarname:
                    vname1 = yvarname.split("/")[0]
                    vname2 = yvarname.split("/")[1]
                    value = (sol(fs[vname1])/sol(fs[vname2]))
                    yunits = "%s/%s" % (unitstr(fs[vname1].units),
                                        unitstr(fs[vname2].units))
                    ylabel = yvarname
                    name = vname1
                else:
                    value = sol(fs[yvarname])
                    yunits = unitstr(fs[yvarname].units)
                    ylabel = (fs[yvarname][0].descr["label"] if not
                              isinstance(fs[yvarname], Variable) else
                              fs[yvarname].descr["label"])
                    name = yvarname
                shape.append(shape[i] +
                             (fs[name][0].descr["shape"][0] if not
                              isinstance(fs[name], Variable) else 1))
                flightseg.append(fs.__class__.__name__ + "%s" % fs.num)
                y.append(value.magnitude)

    y = np.hstack(np.array(y))
    shape[2:] = [x-1 for x in shape[2:]]

    # define tick step on plot
    N = range(len(y))

    # create plot
    fig, ax = plt.subplots()
    line, = ax.plot(N, y)

    # label time axis
    ax.xaxis.set_ticks(np.arange(0, len(y) - 1, 1))
    labels = [item.get_text() for item in ax.get_xticklabels()]
    for i, seg in enumerate(flightseg):
        labels[shape[i]] = seg
    ax.set_xticklabels(labels, rotation=-45)

    # mark mission profile changes
    if not ylim:
        ylim = [min(y), max(y)]

    ax.set_ylim([ylim[0], ylim[1]])
    if yaxis_name:
        ax.set_ylabel(yaxis_name)
    else:
        ax.set_ylabel("%s [%s]" % (ylabel, yunits))

    ax.grid()
    for s in shape:
        ax.plot([s, s], [ylim[0], ylim[1]], '--', color='r')

    return fig, ax

def solution_value(eqstr, sol, units, submodel):
    if "/" in eqstr:
        varnames = eqstr.split("/")
        value = (sol(submodel[varnames[0]])/
                 sol(submodel[varnames[1]])).to(units)
    else:
        value = sol(eqstr)

    return value


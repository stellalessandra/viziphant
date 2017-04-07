"""
Simple but highly configurable plotting functions for spiketrains in neo format.
While building on the matplotlib libary the functions lay an emphasis on clear,
pleasant-to-look-at visualizations.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from elephant.statistics import mean_firing_rate
from math import log10, floor


def _round_to_1(x):
    rounded = round(x, -int(floor(log10(abs(x)))))
    return rounded, rounded > x


def _get_attributes(spiketrains, key_list):
    """
    attribute_array is of shape (len(spiketrains), len(key_list))
    and consists of numerical ids for each value of each key for each
    spiketrain.

    Passed spiketrains must be sorted according to key_list.
    key_list must not be empty.
    """

    key_count = len(key_list)
    attribute_array = np.zeros((len(spiketrains), len(key_list)))
    # count all group sizes for all keys in keylist:
    while key_count > 0:
        key_count -= 1
        group_key = key_list[key_count]
        i = 0
        if group_key in spiketrains[i].annotations:
            current_value = spiketrains[i].annotations[group_key]
        else:
            # use placeholder value when key is not in annotations
            # of the current spiketrain
            current_value = '####BLANK####'
        ref_value = current_value
        values = np.array([])
        # count all group sizes for values of current key:
        while i < spiketrains.__len__():
            if not len(values) or current_value not in values:
                values = np.append(values, current_value)
            # count group size for a value of the current key:
            while i < len(spiketrains) and current_value == ref_value:
                attribute_array[i][key_count] = \
                np.where(values == current_value)[0][0]
                i += 1
                if i < len(spiketrains):
                    if group_key in spiketrains[i].annotations:
                        current_value = spiketrains[i].annotations[
                            group_key]
                    else:
                        current_value = '####BLANK####'
            ref_value = current_value
    return attribute_array


def rasterplot(spiketrain_list,
               key_list=[],
               groupingdepth=0,
               spacing=[5,3],
               colorkey=0,
               pophist_mode='color',
               pophistbins=100,
               right_histogram=mean_firing_rate,
               filter_function=None,
               histscale=.1,
               labelkey=None,
               markerargs={'markersize':4,'marker':'.'},
               separatorargs=[{'linewidth':2, 'linestyle':'--', 'color':'0.8'},
                              {'linewidth':1, 'linestyle':'--', 'color':'0.8'}],
               legend=False,
               legendargs={'loc':(.98,1.), 'markerscale':1.5, 'handletextpad':0},
               ax=None,
               style='ticks',
               palette='Set2',
               context='paper',
               colorcodes='colorblind'):

    """
    This function plots the dot display of spiketrains alongside its population
    histogram and the mean firing rate (or a custom function). Visual aids
    are offered such as sorting, grouping and colorcoding on the basis of the
    arrangement in list of spiketrains and spiketrain annotations.

    :param spiketrain_list: list
        List can either contain neo spiketrains or lists of neo spiketrains.
    :param key_list: str | list of str
        Annotation key(s) for which the spiketrains should be ordered.
        When list of keys is given the spiketrains are ordered successively for
        the keys.
        By default the ordering by the given lists of spiketrains have priority.
        This can be bypassed by using an empty string '' as list-key at any
        position in the key_list.
    :param groupingdepth: 0 | 1 | 2
        * 0: No grouping (default)
        * 1: grouping by first key in key_list.
             Note that when list of lists of spiketrains are given the first
             key is by the list identification key ''. If this is unwanted
             the empty string '' can be placed at a different position in
             key_list.
        * 2: additional grouping by second key respectively
        The groups are separated by whitespace specified in the spacing
        parameter and optionally by a line specified by the the separatorargs.
    :param spacing: int | [int] | [int, int]
        Size of whitespace separating the groups in units of spiketrains.
        When groupingdepth == 2 a list of two values can specify the distance
        between the groups in level 1 and level 2. When only one value is given
        level 2 spacing is set to half the spacing of level 1.
        Default: [5, 3]
    :param colorkey: str | int  (default 0)
        Contrasts values of a key by color. The key can be defined by its
        namestring or its position in key_list. Note that position 0 points to
        the list identification key ('') when list of lists of spiketrains are
        given, if not otherwise specified in key_list!
    :param pophist_mode: 'color' (default) | 'total'
         * total: One population histogram for all drawn spiketrains
         * color: Additionally to the total population histogram,
                  a histogram for each colored subset is drawn (see colorkey).
    :param pophistbins: int (default 100)
        Number of bins used for the population histogram.
    :param right_histogram: function
        The function gets ONE neo.SpikeTrain as argument and has to return a
        scalar. For example the functions in the elephant.statistics module can
        be used. (default: mean_firing_rate)
        When a function is applied is is recommended to set the axis label
        accordingly by using the axis handle returned by the function:
        axhisty.set_xlabel('Label Name')
    :param filter_function: function
        The function gets ONE neo.SpikeTrain as argument and if the return is
        Truethy the spiketrain is included and if the return is Falsely it is
        exluded.
    :param histscale: float (default .1)
        Portion of the figure used for the histograms on the right and upper
        side.
    :param labelkey: 0 | 1 | '0+1' (default) | 'annotation key' | None
        * 0, 1: Set label according to first or second key in key_list.
                Note that the first key is by default the list identification
                key ('') when list of lists of spiketrains are given.
        * '0+1': Two level labeling of 0 and 1
        * annotation-key: Labeling each spiketrain with its value for given key
        * None: No labeling
        Note that only groups (-> see groupingdepth) can be labeled as bulks.
        Alternatively you can color for an annotation key and show a legend.
    :param markerargs: dict
        Arguments dictionary is passed on to matplotlib.pyplot.plot()
    :param separatorargs: dict | [dict, dict] | None
        If only one dict is given and groupingdepth == 2 the arguments are
        applied to the separator of both level. Otherwise the arguments are
        of separatorargs[0] are applied to the level 1 and [1] to level 2.
        Arguments dictionary is passed on to matplotlib.pyplot.plot()
        To turn of separators set it to None.
    :param legend: boolean
        Show legend?
    :param legendargs: dict
        Arguments dictionary is passed on to matplotlib.pyplot.legend()
    :param ax: matplotlib axis | None (default)
        The axis onto which to plot. If None a new figure is created.
        When an axis is given, the function can't handle the figure settings.
        Therefore it is recommended to call seaborn.set() with your preferred
        settings before creating your matplotlib figure in order to control
        your plotting layout.
    :param style: str
        seaborn style setting. Default: 'ticks'
    :param palette: string | sequence
        Define the color palette either by its name or use a custom palette in
        a sequence of the form ([r,g,b],[r,g,b],...).
    :param colorcodes: str
        seaborn colorcodes setting. By default this is set to 'colorblind' so
        that any additional drawing into the plot using colorcodes ('r', 'g', ...)
        are coherent with the default color palette ('Set2') of the plot.
    :param context: 'paper'(default) | 'talk' | 'poster'
        seaborn context setting which controls the scaling of labels. For the
        three options the parameters are scaled by .8, 1.3, and 1.6 respectively.
    :return: ax, axhistx, axhisty   <matplotlib axis handle>
        * ax is handle of the dot display plot
        * axhistx is handle of the histogram plot above the the dot display
        * axhisty is handle of the histogram plot on the right hand side
    """

    # Initialize plotting canvas
    sns.set(style=style, palette=palette, context=context)
    sns.set_color_codes(colorcodes)

    if ax is None:
        fig = plt.figure()
        # axis must be created after sns.set() command for style to apply!
        ax = fig.add_subplot(111)

    margin = 1 - histscale
    left, bottom, width, height = ax.get_position()._get_bounds()
    ax.set_position([    left,                  bottom,
                         margin * width,        margin * height])
    axhistx = plt.axes([left,                   bottom + margin * height,
                        margin * width,         histscale * height])
    axhisty = plt.axes([left + margin * width,  bottom,
                        histscale * width,      margin * height])

    sns.despine(ax=axhistx)
    sns.despine(ax=axhisty)

    # Whitespace margin around dot display = 2%
    ws_margin = 0.02

    # Assertions
    assert groupingdepth <= 2, "Grouping is limited to two layers."
    groupingdepth = int(groupingdepth)

    list_key = "%$\@[#*&/!"  # unique key to be added to annotations to store
                             # list ordering information.

    if type(key_list) == 'str':
        key_list = [key_list]

    if '' not in key_list:
        key_list = [list_key] + key_list
    else:
        key_list = [list_key if not key else key for key in key_list]

    if type(spacing) == list:
        if len(spacing) == 1:
            spacing = [spacing[0], spacing[0]/2.]
    else:
        spacing = [spacing, spacing/2.]
    assert spacing[0] >= spacing[1], "For reasonable visual aid spacing[0] must" \
                                   + " be larger than spacing[1]."

    if type(colorkey) == int and len(key_list):
        assert colorkey < len(key_list), "An integer colorkey must refer to a" \
                                       + " position in key_list."
        colorkey = key_list[colorkey]
    else:
        if not colorkey:
            colorkey = list_key
        else:
            assert colorkey in key_list, "colorkey must be in key_list"

    if legend:
        assert len(key_list) > 0, "Legend requires a non empty key_list."

    if labelkey == '':
        labelkey = list_key

    if type(separatorargs) == list:
        if len(separatorargs) == 1:
            separatorargs += separatorargs
        for args in separatorargs:
            assert type(args) == dict, "The parameters must be given as dict."
    else:
        separatorargs = [separatorargs, separatorargs]

    for i, args in enumerate(separatorargs):
        if 'c' in args:
            separatorargs[i]['color'] = args['c']
        elif 'color' not in args:
            separatorargs[i]['color'] = '0.8'

    markerargs['linestyle'] = ''

    # Flatten list of lists while keeping the grouping info in annotations
    if isinstance(spiketrain_list[0], list):
        for list_nbr, st_list in enumerate(spiketrain_list):
            for st in st_list:
                st.annotations[list_key] = "set {}".format(list_nbr)
        spiketrain_list = [st for sublist in spiketrain_list for st in sublist]
    else:
        for st in spiketrain_list:
            st.annotations[list_key] = "set {}".format(0)
        key_list.remove(list_key)
        key_list.append(list_key)

    # Assertions on flattened list
    assert len(key_list) >= groupingdepth, "Can't group more as keys in key_list"

    # Filter spiketrains according to given filter function
    if filter_function is not None:
        filter_index = []
        for st_count, spiketrain in enumerate(spiketrain_list):
            if filter_function(spiketrain):
                filter_index += [st_count]
        spiketrain_list = [spiketrain_list[i] for i in filter_index]

    # Initialize plotting parameters
    t_lims = [(st.t_start, st.t_stop) for st in spiketrain_list]
    tmin = min(t_lims, key=lambda f: f[0])[0]
    tmax = max(t_lims, key=lambda f: f[1])[1]
    period = tmax - tmin
    ax.set_xlim(tmin - ws_margin*period, tmax + ws_margin*period)
    yticks = np.zeros(len(spiketrain_list))

    # Sort spiketrains according to keylist
    def sort_func(x):
        return ['' if key not in x.annotations
                else x.annotations[key] for key in key_list]

    spiketrain_list = sorted(spiketrain_list, key=lambda x: sort_func(x))
    if len(key_list) > 1:
        attribute_array = _get_attributes(spiketrain_list, key_list)
    elif len(key_list) == 1:
        attribute_array = np.zeros((len(spiketrain_list), 2))
        attribute_array[:,0] = _get_attributes(spiketrain_list, key_list)[:,0]
    else:
        attribute_array = np.zeros((len(spiketrain_list), 1))

    # Define colormap
    if not len(key_list):
        nbr_of_colors = 1
        colorkey = None
    else:
        colorkey = np.where(colorkey == np.array(key_list))[0][0]
        nbr_of_colors = int(max(attribute_array[:, colorkey]) + 1)

    colormap = sns.color_palette(palette, nbr_of_colors)

    # Draw population histogram (upper side)
    colorkeyvalues = np.unique(attribute_array[:, colorkey])

    if pophist_mode == 'color' and len(colorkeyvalues)-1:
        if len(sns.color_palette()) < len(colorkeyvalues):
            print "\033[31mWarning: There are more subsets than can be " \
                  "separated by colors in the color palette which might lead "\
                  "to confusion!\033[0m"
        for value in colorkeyvalues:
            idx = np.where(attribute_array[:, colorkey] == value)[0]
            axhistx.hist([stime for strain in [spiketrain_list[i] for i in idx]
                          for stime in strain],
                         pophistbins, histtype='step', linewidth=1,
                         color=colormap[int(value)])

    if len(colorkeyvalues)-1:
        sum_color = separatorargs[0]['color']
    else:
        sum_color = sns.color_palette()[0]

    histout = axhistx.hist([stime for strain in spiketrain_list
                                  for stime in strain],
                           pophistbins, histtype='step', linewidth=1,
                           color=sum_color)

    # Set ticks and labels for population histogram
    max_y = np.max(histout[0])
    axhistx_ydim, up = _round_to_1(max_y)
    if max_y > axhistx.get_ylim()[-1]:
        axhistx.set_ylim(0, max_y)
    if up and axhistx_ydim > max_y:
        axhistx.set_ylim(0, axhistx_ydim)
    axhistx.set_yticks([axhistx_ydim])
    axhistx.set_yticklabels(['{:.0f}'.format(axhistx_ydim)])

    # Legend for colorkey
    if legend:
        __, index = np.unique(attribute_array[:, colorkey], return_index=True)
        legend_labels = [spiketrain_list[i].annotations[key_list[colorkey]]
                         for i in index]
        legend_handles = [0] * len(index)

    # Reshape list into sublists according to groupingdepth
    if groupingdepth > 0:
        value1, index1, counts1 = np.unique(attribute_array[:, 0],
                                            return_index=True,
                                            return_counts=True)
        for v1, i1, c1 in zip(value1, index1, counts1):
            v1 = int(v1)
            spiketrain_list[v1:v1 + c1] = [spiketrain_list[v1:v1 + c1]]
            if groupingdepth > 1:
                __, counts2 = np.unique(attribute_array[i1:i1 + c1, 1],
                                        return_counts=True)
                for v2, c2 in enumerate(counts2):
                    v2 = int(v2)
                    spiketrain_list[v1][v2:v2+c2] = [spiketrain_list[v1][v2:v2+c2]]
            else:
                spiketrain_list[v1] = [spiketrain_list[v1]]
    else:
        spiketrain_list = [[spiketrain_list]]

    # HIERARCHIE:
    # [ [ []..[] ] .... [ []..[] ] ] spiketrain_list
    # [ []..[] ] LIST
    # [] list
    # spiketrain

    # Loop through lists of lists of spiketrains
    for COUNT, SLIST in enumerate(spiketrain_list):

        # Separator depth 1
        if COUNT and separatorargs is not None:
            linepos = ypos + len(spiketrain_list[COUNT-1][-1]) \
                      + spacing[0]/2. - 0.5
            ax.plot(ax.get_xlim(), [linepos] * 2, **separatorargs[0])

        # Loop through lists of spiketrains
        for count, slist in enumerate(SLIST):
            nbr_of_drawn_sts = int(sum([len(sl) for SL in
                                        spiketrain_list[:COUNT] for sl in SL])\
                                 + sum([len(sl) for sl in SLIST[:count]]))

            # Calculate postition of next spiketrain to draw
            prev_spaces = np.sum([len(SLIST_it) - 1
                                  for SLIST_it in spiketrain_list[:COUNT]])
            ypos = nbr_of_drawn_sts \
                 + int(bool(groupingdepth)) * COUNT * spacing[0] \
                 + groupingdepth/2 * count * spacing[1] \
                 + groupingdepth/2 * prev_spaces * spacing[1]

            # Separator depth 2
            if count and separatorargs is not None:
                linepos = ypos - (spacing[1] + 1) / 2.
                ax.plot(ax.get_xlim(), [linepos] * 2, **separatorargs[1])

            # Loop through spiketrains
            for st_count, st in enumerate(slist):
                current_st = nbr_of_drawn_sts + st_count
                annotation_value = int(attribute_array[current_st, colorkey])
                color = colormap[annotation_value]

                # Dot display
                handle = ax.plot(st.times.magnitude,
                                 [st_count + ypos] * st.__len__(), color=color,
                                 **markerargs)
                if legend:
                    legend_handles[annotation_value] = handle[0]

                # Right side histogram bar
                barvalue = right_histogram(st)
                barwidth = .8
                axhisty.barh(bottom=st_count + ypos,
                             width=barvalue,
                             height=barwidth,
                             color=color,
                             edgecolor=color)

            # Append positions of spiketrains to tick list
            ycoords = np.arange(len(slist)) + ypos
            yticks[nbr_of_drawn_sts:nbr_of_drawn_sts+len(slist)] = ycoords

    # Plotting axis
    yrange = yticks[-1] - yticks[0]
    ax.set_ylim(yticks[0] - ws_margin*yrange,
                yticks[-1] + ws_margin*yrange)
    axhistx.set_xlim(ax.get_xlim())
    axhisty.set_ylim(ax.get_ylim())
    ax.set_xlabel('t [{}]'.format(spiketrain_list[0][0][0].units.dimensionality))
    axhistx.get_xaxis().set_visible(False)
    axhisty.get_yaxis().set_visible(False)

    # Set ticks and labels for right side histogram
    axhisty_xdim, up = _round_to_1(axhisty.get_xlim()[-1])
    if up:
        axhistx.set_ylim(0, axhistx_ydim)
    axhisty.set_xticks([axhisty_xdim])
    axhisty.set_xticklabels(['{}'.format(axhisty_xdim)])

    # Y labeling
    if key_list and labelkey in key_list + [0, 1, '0+1']:
        if labelkey == key_list[0]:
            if groupingdepth > 0:
                labelkey = 0
        elif len(key_list) > 1 and labelkey == key_list[1]:
            if groupingdepth > 1:
                labelkey = 1

        if type(labelkey) == int or labelkey == '0+1':
            labelpos = [[] for label_level in range(2)]
            labelname = [[] for label_level in range(2)]

            # Labeling depth 1 + 2
            if groupingdepth:
                values1, index1, counts1 = np.unique(attribute_array[:, 0],
                                                     return_index=True,
                                                     return_counts=True)

                for v1, i1, c1 in zip(values1, index1, counts1):
                    st = spiketrain_list[int(v1)][0][0]
                    if key_list[0] in st.annotations:
                        labelname[0] += [st.annotations[key_list[0]]]
                        if labelkey == '0+1':
                            labelname[0][-1] += ' ' * 5
                    else:
                        labelname[0] += ['']

                    labelpos[0] += [(yticks[i1] + yticks[i1+c1-1])/2.]

                    # Labeling depth 2
                    if groupingdepth / 2 and labelkey and len(key_list) - 1:
                        __, index2, counts2 = np.unique(attribute_array[i1:i1+c1, 1],
                                                        return_index=True,
                                                        return_counts=True)

                        for v2, (i2, c2) in enumerate(zip(index2, counts2)):
                            st = spiketrain_list[int(v1)][int(v2)][0]
                            if key_list[1] in st.annotations:
                                labelname[1] += [st.annotations[key_list[1]]]
                            else:
                                labelname[1] += ['']

                            labelpos[1] += [(yticks[i1+i2] + yticks[i1+i2+c2-1])/2.]

            # Set labels according to labelkey
            if type(labelkey) == int:
                ax.set_yticks(labelpos[1] if labelkey else labelpos[0])
                ax.set_yticklabels(labelname[1] if labelkey else labelname[0])

            elif labelkey == "0+1":
                ax.set_yticks(labelpos[0] + labelpos[1])
                ax.set_yticklabels(labelname[0] + labelname[1])

        else:
            # Annotatation key as labelkey
            labelname = []
            for COUNT, SLIST in enumerate(spiketrain_list):
                for count, slist in enumerate(SLIST):
                    for st_count, st in enumerate(slist):
                        if labelkey in st.annotations:
                            labelname += [st.annotations[labelkey]]
                        else:
                            labelname += ['']
            ax.set_yticks(yticks)
            ax.set_yticklabels(labelname)

    else:
        ax.set_yticks([])
        ax.set_yticklabels([''])

    # Draw legend
    if legend:
        ax.legend(legend_handles, legend_labels, **legendargs)

    # Remove list_key from annotations
    for SLIST in spiketrain_list:
        for slist in SLIST:
            for st in slist:
                st.annotations.pop(list_key, None)

    return ax, axhistx, axhisty

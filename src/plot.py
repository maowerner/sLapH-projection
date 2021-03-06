import matplotlib
# matplotlib.use('QT4Agg')
import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D

import matplotlib.patheffects as PathEffects

import numpy as np
import pandas as pd
from pandas import Series, DataFrame

import itertools as it
import gmpy

import utils

################################################################################
# TODO: Symmetrization and Antisymmetrization. Take negative eigenvalues under
# time reversal into account
# TODO: this does not work if I work with the column indices directly rather
# than the config numbers. Using np.random.randint and iloc should be
# considerably faster


def bootstrap(df, bootstrapsize):
    """
  Apply the bootstrap method to randomly resample gauge configurations

  Parameters
  ----------
  df : pd.DataFrame
      Lattice data with arbitrary rows and columns cnfg x T.
  bootstrapsize : int
      The number of bootstrap samles being drawn from `df`

  Returns
  -------
  boot : pd.DataFrame
      Lattice data with rows like `df` and columns boot x T. The number of
      level0 column entries is `bootstrapsize` and it contains the mean of
      nb_cnfg randomly drawn configurations.
  """
    np.random.seed(1227)
    idx = pd.IndexSlice

    # list of all configuration numbers
    cnfgs = df.columns.levels[0].values
    rnd_samples = np.array(
        [np.random.choice(cnfgs,
                          len(cnfgs) * bootstrapsize)]).reshape((bootstrapsize,
                                                                 len(cnfgs)))
    # writing the mean value in the first sample
    rnd_samples[0] = cnfgs

    # Also I have to use a list comprehension rather than rnd directly...
    boot = pd.concat(
        [df.loc[:, idx[[r for r in rnd]]].mean(axis=1, level=1) for rnd in rnd_samples],
        axis=1,
        keys=range(bootstrapsize))

    return boot


def mean_and_std(df, bootstrapsize):
    """
  Mean and standard deviation over all configurations/bootstrap samples

  Parameters
  ----------
  df : pd.DataFrame
      Table with purely real entries (see Notes) and hierarchical columns where
      level 0 is the gauge configuration/bootrstrap sample number and level 1
      is the lattice time
  bootstrapsize : int
      The number of bootstrap samles being drawn from `df`

  Returns:
  --------
  pd.DataFrame
      Table with identical indices as `df` The column level 0 is replaced by
      mean and std while level 1 remains unchanged

  Notes
  -----
  Must be taken for real and imaginary part seperately because that apparently
  breaks pandas.
  """

    boot = bootstrap(df, bootstrapsize)
    mean = boot[0]
    std = boot.std(axis=1, level=1)

    return pd.concat([mean, std], axis=1, keys=['mean', 'std'])

################################################################################


def plot_gevp_el_ax(data, label_template, scale, ax, multiindex=False):
    """
  Plot all rows of given pd.DataFrame into a single page as seperate graphs

  data : pd.DataFrame

      Table with any quantity as rows and multicolumns where level 0 contains
      {'mean', 'std'} and level 1 contains 'T'

  label_template : string

      Format string that will be used to label the graphs. The format must fit
      the index of `data`
  """

    symbol = Line2D.filled_markers

    rows = data.index.values

    # iterrows() returns a tuple (index, series)
    # index is a string (the index of data must be strings for this to work). In
    # data has a MultiIndex, index is a tuple of strings
    # series contains the mean and std for every timeslice
    for counter, (index, series) in enumerate(data.iterrows()):

        T = series.index.levels[1].values
        mean = series['mean'].values
        std = series['std'].values

        # prepare parameters for plot design
        if len(rows) == 1:
            cmap_brg = ['r']
        else:
            cmap_brg = plt.cm.brg(
                np.asarray(range(len(rows))) * 256 / (len(rows) - 1))
        shift = 2. / 5 / len(rows)

        if multiindex:
            label = label_template.format(*index)
        else:
            label = label_template.format(index)

        # plot
        ax.errorbar(
            T - 1. / 5 + shift * counter,
            mean,
            std,
            fmt=symbol[counter % len(symbol)],
            color=cmap_brg[counter],
            label=label,
            markersize=3. / scale,
            capsize=3. / scale,
            capthick=0.5 / scale,
            elinewidth=0.5 / scale,
            markeredgecolor=cmap_brg[counter],
            linewidth='0.0')


def plot_mean(data, scale, ax):

    symbol = Line2D.filled_markers

    # prepare data to plot
    T = data.index.levels[1].astype(int)
    mean = data['mean'].values
    std = data['std'].values

    # plot
    ax.errorbar(
        T,
        mean,
        std,
        fmt='o',
        color='black',
        label='mean',
        markersize=3. / scale,
        capsize=3. / scale,
        capthick=0.5 / scale,
        elinewidth=0.5 / scale,
        markeredgecolor='black',
        linewidth='0.0')


################################################################################

def average(graphdata, ax, scale=1):
    """
    Create a multipage plot with a page for every element of the rho gevp

    Parameters
    ----------

    gevp_data : pd.DataFrame

        Table with a row for each gevp element (sorted by gevp column running
        faster than gevp row) and hierarchical columns for gauge configuration
        number and timeslice

    bootstrapsize : int

        The number of bootstrap samples being drawn from `gevp_data`.

    pdfplot : mpl.PdfPages object

        Plots will be written to the path `pdfplot` was created with.

    See also
    --------

    utils.create_pdfplot()
    """

    # prepare data to plot
    graphdata = graphdata.T.squeeze()

    # plot
    plot_mean(graphdata, scale, ax)

    return

# TODO: use color for momenta and symbols for rows.


def pcm_and_mu(graphdata, ax, scale=1):

    plot_gevp_el_ax(graphdata, r'$\vec{{P}}_\textnormal{{cm}} = {}$, $\mu = {}$', scale,
                    ax, multiindex=True)

    # This takes the mean over all operators for the mean and std over
    # bootstrapsamples. That is not entirelly correct. The operations should
    # be the over way round. good enough for a consistency check.
    graphdata_mean = graphdata.mean(axis=0)

    plot_mean(graphdata_mean, scale, ax)

    ax.legend(numpoints=1, loc='best', fontsize=6)

    return


def p_and_gammas(data, diagram, bootstrapsize, pdfplot, logscale=True, verbose=False):
    """
    Create a multipage plot with a page for every element of the rho gevp. Each
    page contains one graph for each row of the irrep, summed over all momenta.

    Parameters
    ----------

    plotdata : pd.DataFrame

        Table with physical quantum numbers as rows 'gevp_row' x 'gevp_col' x
        'p_{cm}' x \mu' '\gamma_{so}' x '\gamma_{si}' and columns 'cnfg' x 'T'.
        Contains the linear combinations of correlation functions transforming
        like what the parameters qn_irrep was created with, i.e. the subduced
        data

    diagram : string
        The diagram as it will appear in the plot labels.

    bootstrapsize : int

        The number of bootstrap samples being drawn from `gevp_data`.

    pdfplot : mpl.PdfPages object

        Plots will be written to the path `pdfplot` was created with.

    See also
    --------

    utils.create_pdfplot()
    """

    plotdata_real = mean_and_std(data.apply(np.real), bootstrapsize)
    plotdata_imag = mean_and_std(data.apply(np.imag), bootstrapsize)

    # abs of smallest positive value
    linthreshy = 1e3 * plotdata_real['mean'][plotdata_real['mean'] > 0].min().min()
    # abs of value closest to zero
    #linthreshy = plotdata_real['mean'].iloc[plotdata_real.loc[:,('mean',0)].nonzero()].abs().min().min()

    # create list of gevp elements to loop over
#    plotlabel = list(set([(i[0], i[1], i[2], i[3]) for i in plotdata_real.index.values]))
    # Create unique list of gevp elements to loop over while keeping order intact
    seen = set()
    plotlabel = []
    for item in [(i[0], i[1], i[2], i[3]) for i in plotdata_real.index.values]:
        if item not in seen:
            seen.add(item)
            plotlabel.append(item)

    for graphlabel in plotlabel:

        if verbose:
            print '\tplotting p_cm = ', graphlabel[2], \
                ', \mu = ', graphlabel[3]

        # Select data for plot
        graphdata_real = plotdata_real.xs(
            graphlabel, level=['gevp_row', 'gevp_col', 'p_{cm}', '\mu'])
        graphdata_imag = plotdata_imag.xs(
            graphlabel, level=['gevp_row', 'gevp_col', 'p_{cm}', '\mu'])

        # Prepare Figure
        fig, (ax_r, ax_i) = plt.subplots(1, 2, sharex=True, sharey=True)
        fig.suptitle(r'Gevp Element ${}$ - ${}$, $\vec{{P}}_\textnormal{{cm}} = {}$, $\mu = {}$'.
                     format(graphlabel[0], graphlabel[1], graphlabel[2], graphlabel[3]))

        # Prepare Axes
        ax_r.set_title('Real')
        ax_r.set_xlabel(r'$t/a$', fontsize=12)
        ax_r.set_ylabel(r'$%s(t/a)$' % diagram, fontsize=12)
        ax_r.label_outer()
        if logscale:
            ax_r.set_yscale('symlog', linthreshy=linthreshy)

        # plot
        plot_gevp_el_ax(graphdata_real, 'None', 1, ax_r)
        plot_mean(graphdata_real.mean(axis=0), 1, ax_r)

        # Prepare Axes
        ax_i.set_title('Imag')
        ax_i.set_xlabel(r'$t/a$', fontsize=12)
        ax_i.set_ylabel(r'$%s(t/a)$' % diagram, fontsize=12)
        ax_i.label_outer()
        if logscale:
            ax_r.set_yscale('symlog', linthreshy=linthreshy)
            ax_i.set_yscale('symlog', linthreshy=linthreshy)

        # plot
        plot_gevp_el_ax(graphdata_imag, 'None', 1, ax_i)
        plot_mean(graphdata_imag.mean(axis=0), 1, ax_i)

        # clean up for next plot
        #plt.legend(numpoints=1, loc='best', fontsize=6)
        #fig.legend(numpoints=1, loc='lower center', fontsize=6)
        pdfplot.savefig(fig)
        plt.close(fig)


def for_each_gevp_element(plotting_function, plotdata, bootstrapsize, pdfplot,
                          logscale=False,
                          verbose=False):
    """
    Create a multipage plot with a page for every element of the rho gevp

    Parameters
    ----------

    gevp_data : pd.DataFrame

        Table with a row for each gevp element (sorted by gevp column running
        faster than gevp row) and hierarchical columns for gauge configuration
        number and timeslice

    bootstrapsize : int

        The number of bootstrap samples being drawn from `gevp_data`.

    pdfplot : mpl.PdfPages object

        Plots will be written to the path `pdfplot` was created with.

    See also
    --------

    utils.create_pdfplot()
    """

    plotdata = mean_and_std(plotdata, bootstrapsize)

    # abs of smallest positive value
    linthreshy = plotdata['mean'][plotdata['mean'] > 0].min().min()
    # abs of value closest to zero
    #linthreshy = plotdata['mean'].iloc[plotdata.loc[:,('mean',0)].nonzero()].abs().min().min()

    # create list of gevp elements to loop over
    plotlabel = list(set([(i[0], i[1]) for i in plotdata.index.values]))

    for graphlabel in plotlabel:

        if verbose:
            print '\tplotting ', graphlabel[0], ' - ', graphlabel[1]

        # Prepare Figure
        fig, ax = plt.subplots(1, 1)

        # Prepare Axes
        ax.set_title(r'Gevp Element ${}$ - ${}$'.format(graphlabel[0], graphlabel[1]))
        ax.set_xlabel(r'$t/a$', fontsize=12)
        ax.set_ylabel(r'$C(t/a)$', fontsize=12)
        if logscale:
            ax.set_yscale('symlog', linthreshy=linthreshy)

        # Select data for plot
        graphdata = plotdata.xs(graphlabel, level=['gevp_row', 'gevp_col'])

        plotting_function(graphdata, ax)

        pdfplot.savefig(fig)
        plt.close(fig)

    return


def gevp(plotting_function, plotdata, bootstrapsize,
         pdfplot, logscale=False, verbose=False):
    """
  Create a multipage plot with a page for every element of the rho gevp

  Parameters
  ----------

  plotdata: pd.DataFrame

      Table with a row for each gevp element (sorted by gevp column running
      faster than gevp row) and hierarchical columns for gauge configuration
      number and timeslice

  bootstrapsize : int

      The number of bootstrap samples being drawn from `plotdata`.

  pdfplot : mpl.PdfPages object

      Plots will be written to the path `pdfplot` was created with.

  See also
  --------

  utils.create_pdfplot()
  """

    assert np.all(plotdata.notnull()), 'Gevp contains null entires'
    plotdata = mean_and_std(plotdata, bootstrapsize)

    # abs of smallest positive value
    #linthreshy = plotdata['mean'][plotdata['mean'] > 0].min().min()
    # abs of value closest to zero
    linthreshy = 1e3 * plotdata['mean'].iloc[plotdata.loc[:,
                                                          ('mean', 0)].nonzero()].abs().min().min()

    # Create unique list of gevp elements to loop over while keeping order intact
    seen = set()
    plotlabel = []
    for item in [(i[0], i[1]) for i in plotdata.index.values]:
        if item not in seen:
            seen.add(item)
            plotlabel.append(item)
    assert gmpy.is_square(len(plotlabel)), 'Gevp is not a square matrix'
    gevp_size = int(gmpy.sqrt(len(plotlabel)))

    # Prepare Figure
    fig, axes = plt.subplots(gevp_size, gevp_size, sharex=True, sharey=True)

    for counter, graphlabel in enumerate(plotlabel):

        if verbose:
            print '\tplotting ', graphlabel[0], ' - ', graphlabel[1]

        # Prepare Axes
        ax = axes[counter // gevp_size, counter % gevp_size]
#        ax.set_title(r'Gevp Element ${}$ - ${}$'.format(graphlabel[0], graphlabel[1]))
        ax.set_xlabel(r'$%s$' % graphlabel[1], fontsize=3, rotation=30)
        ax.set_ylabel(r'$%s$' % graphlabel[0], fontsize=3, rotation=30)
        # https://stackoverflow.com/questions/4209467/matplotlib-share-x-axis-but-dont-show-x-axis-tick-labels-for-both-just-one
        ax.label_outer()

        if logscale:
            #            ax.locator_params(axis='y', numticks=3)
            ax.set_yscale('symlog', linthreshy=linthreshy)

        ax.set_xticks([])
#        ax.tick_params(labelleft='off')
        ax.set_yticks([])

        # Select data for plot
        graphdata = plotdata.xs(graphlabel, level=['gevp_row', 'gevp_col'])

        plotting_function(graphdata, ax, scale=gevp_size)
        if ax.legend_:
            ax.legend_.remove()

#    plt.locator_params(axis='y', numticks=2)
    plt.tight_layout(h_pad=0.1, w_pad=0.15)
    pdfplot.savefig(fig)
    plt.close(fig)

    return

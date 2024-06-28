import os
from typing import Dict, Tuple

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import pandas as pd

from eisImport import EisData


def plotNyquist(
    eis: Dict[str, EisData],
    realLabel="Real Impedance (mΩ)",
    imagLabel="Imaginary Impedance (mΩ)",
    ax: Axes | None = None,
    scatter: bool = False,
    limitFrequencyLabels: bool = False,
    saveDir: str | None = None,
    fileName: str | None = None,
    transparent: bool = False,
    title: str | None = None,
    figsize: Tuple[int, int] = (16, 12),
) -> Axes | None:
    """
    Plots the EIS spectral data with a Nyquist scatter plot.

    Args:
        eis (Dict[str, EisData]): A dictionary containing EIS spectral data.
        realLabel (str, optional): Label for the real impedance axis. Defaults to "Real Impedance (mΩ)".
        imagLabel (str, optional): Label for the imaginary impedance axis. Defaults to "Imaginary Impedance (mΩ)".
        ax (Axes | None, optional): The matplotlib Axes object to plot on. Defaults to None.
        scatter (bool, optional): If the plot should be a scatter plot. Defaults to False (line plot).
        limitFrequencyLabels (bool, optional): Add labels to indicate the frequency limits. Defaults to False.
        saveDir (str | None, optional): The directory to save the plot image. Defaults to None.
        fileName (str | None, optional): The filename of the saved plot image. Only effects if saveDir is not None.
        transparent (bool, optional): If the saved plot should be transparent. Defaults to False. Only effects if saveDir is not None.
        title (str | None, optional): The title of the plot. Defaults to None.
        figsize (Tuple[int, int], optional): The size of the plot figure. Defaults to (16, 12).

    Single EIS special effects (`len(eis) == 1`):
    - Title is the spectrum key name.
    - Subtitle with metadata information.
    - Removes the legend.

    Multiple EIS data special effects:
    - Title is the provided title (if provided).
    - Legend is shown.

    Returns:
        Axes | None: The matplotlib Axes object if saveDir is None, otherwise None.

    Raises:
        ValueError: If no EIS data is provided.

    Industry standard Nyquist plot settings:
    - Equal aspect ratio.
    - Inverts the imaginary axis.
    - Zero left limit on the real axis.

    Example usage:
    ```
    eis_data = {
        "Spectrum1": eis_data1,
        "Spectrum2": eis_data2,
    }
    plot = plotNyquist(eis_data, realLabel="Real Impedance (mΩ)", imagLabel="Imaginary Impedance (mΩ)")
    ```
    """

    if len(eis) == 0:
        raise ValueError("No EIS data provided.")

    for spectra in eis:
        plot_func = (
            eis[spectra].data.plot.scatter if scatter else eis[spectra].data.plot.line
        )
        plot: Axes = plot_func(
            x="Zreal1",
            y="Zimg1",
            marker=".",
            ax=ax,
            label=spectra,
        )
        ax = plot
        if limitFrequencyLabels:
            idFreq = [
                eis[spectra].data["ActFreq"].idxmin(),
                eis[spectra].data["ActFreq"].idxmax(),
            ]
            for id in idFreq:
                plot.text(
                    eis[spectra].data["Zreal1"].iloc[id] * 1.01,
                    eis[spectra].data["Zimg1"].iloc[id],
                    f"{eis[spectra].data['ActFreq'].iloc[id]:.0f} Hz",
                    fontsize=8,
                )

    plot.invert_yaxis()
    plot.set_aspect("equal", adjustable="box")
    plot.grid(axis="both")
    plot.set_xlim(left=0)
    plot.set_xlabel(realLabel)
    plot.set_ylabel(imagLabel)

    figure = plot.get_figure()
    assert figure is not None

    figure.set_size_inches(figsize)

    if len(eis) == 1 and title is None:
        title = list(eis.keys())[0]
        assert title is not None
        plot.set_title(title)

        suptitle = f"""
        Measurement ID: {eis[title].metadata['Measurement ID']}
        Start Time: {eis[title].metadata['Start Time']}
        End Time: {eis[title].metadata['End Time']}
        """
        figure.suptitle(
            suptitle,
            ha="left",
            x=0.125,
        )

        plot.legend().remove()
    else:
        plot.legend()
        if title is not None:
            plot.set_title(title)

    if saveDir is not None:
        os.makedirs(saveDir, exist_ok=True)
        savePath = (
            os.path.join(saveDir, f"{spectra}.png")
            if fileName is None
            else os.path.join(saveDir, fileName)
        )

        assert plot.figure is not None
        figure.savefig(
            savePath,
            transparent=transparent,
        )
        plt.close(figure)  # Memory management

        return None
    else:
        return plot


def plotEisTestTemperatureRanges(
    eisObservations: Dict[str, Dict[str, pd.DataFrame]]
) -> plt.Figure:
    fig, ax = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=(16, 32),
        # squeeze=True,
    )
    fig.suptitle("EIS Test Temperatures")
    ax[0].set_title("Batch A")
    ax[1].set_title("Batch B")
    ax[0].grid(True)
    ax[1].grid(True)

    for batch in eisObservations:
        axIndex = 0 if batch == "A" else 1
        for temperature in eisObservations[batch]:
            # Plot a bar chart of ranges "Battery Min Temperature" to "Battery Max Temperature"
            for row in eisObservations[batch][temperature].iterrows():
                try:
                    minTemp = float(row[1]["Battery Min Temperature"])
                    maxTemp = float(row[1]["Battery Max Temperature"])
                except ValueError:
                    continue

                ax[axIndex].barh(
                    y=row[1]["Test"],
                    width=maxTemp - minTemp,
                    left=minTemp,
                )

                if minTemp == maxTemp:
                    # Special case for when minTemp == maxTemp, plot a single point
                    ax[axIndex].scatter(
                        x=minTemp,
                        y=row[1]["Test"],
                    )

    return fig

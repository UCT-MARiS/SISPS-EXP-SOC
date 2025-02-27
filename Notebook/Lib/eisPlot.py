import os
from concurrent import futures

from typing import Dict, Tuple, TypedDict

import darkdetect

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

import pandas as pd
import numpy as np

from .eisImport import EisData
from .eisAnalysis import (
    groupByBatch,
    groupByTemperature,
    groupByBatteryNumber,
    getSoC,
    getPaperLabel,
)


def plotNyquist(
    eis: Dict[str, EisData],
    realLabel=r"Real Impedance $(m\Omega)$",
    imagLabel=r"Imaginary Impedance $(m\Omega)$",
    ax: Axes | None = None,
    scatter: bool = False,
    limitFrequencyLabels: bool = False,
    saveDir: str | None = None,
    fileName: str | None = None,
    transparent: bool = False,
    title: str | None = None,
    figsize: Tuple[int, int] = (16, 12),
    paperMode: bool = False,
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
            label=spectra if not paperMode else f"{getPaperLabel(spectra)}",
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


def plotIndividualNyquist(
    eisData: Dict[str, EisData],
    saveDir,
    scatter=False,
) -> None:
    """
    Plots individual Nyquist plots for each EIS data set in the dictionary.

    Args:
        eisData (dict): A dictionary containing EIS data sets.
        saveDir (str): The directory where the plots will be saved.
        scatter (bool, optional): Whether to include scatter points in the plot. Defaults to False.

    Returns:
        None

    Note:
        - This function is parallelized to speed up the plotting process and is intended for long dictionaries only.
        - If the specified save directory does not exist, it will be created. If it already exists, the function will skip the plotting process (speeds up re-runs).
    """
    if os.path.exists(saveDir) == False:
        with futures.ThreadPoolExecutor() as executor:
            for eis in eisData:
                executor.submit(
                    plotNyquist,
                    {eis: eisData[eis]},
                    saveDir=saveDir,
                    scatter=scatter,
                    transparent=True,
                    limitFrequencyLabels=True,
                )


class EisDataComparison(TypedDict):
    class EisDataNameValue(TypedDict):
        name: str
        value: EisData

    eis1: EisDataNameValue
    eis2: EisDataNameValue


def plotNyquistComparison(
    eis1: EisDataComparison,
    eis2: EisDataComparison,
    mainTitle: str,
    figsize=(8, 5),
) -> Figure:

    fig, axs = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(mainTitle)

    for eis, ax in zip([eis1, eis2], axs):
        plotNyquist(
            {eis["name"]: eis["value"]},
            title=eis["name"],
            ax=ax,
            figsize=(figsize[0] / 2, figsize[1] / 2),
        )

    axs[0].legend().set_visible(False)
    axs[1].legend().set_visible(False)
    axs[1].set_ylabel("")
    fig.tight_layout()

    return fig


def plotEisTestTemperatureRanges(
    eisObservations: Dict[str, Dict[str, pd.DataFrame]],
    saveDir: str | None = None,
    fileName: str | None = None,
    figsize: Tuple[int, int] = (16, 32),
    paperMode: bool = False,
) -> plt.Figure:
    fig, ax = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=figsize,
    )
    if not paperMode:
        fig.suptitle("EIS Test Temperatures")

    ax[0].set_title("Batch A (0 Cycles)")
    ax[1].set_title("Batch B (50 Cycles)")
    ax[0].grid(True)
    ax[1].grid(True)

    for batch in eisObservations:
        axIndex = 0 if batch == "A" else 1
        for temperature in reversed(list(eisObservations[batch])):
            # Plot a bar chart of ranges "Battery Min Temperature" to "Battery Max Temperature"
            for row in eisObservations[batch][temperature].iterrows():
                try:
                    minTemp = float(row[1]["Battery Min Temperature"])
                    maxTemp = float(row[1]["Battery Max Temperature"])
                except ValueError:
                    continue

                y = (
                    (row[1]["Test"])
                    if not paperMode
                    else f"{getPaperLabel(row[1]['Test'])}, {temperature}{'°C' if not temperature[0:2] == 'RT' else ''}"
                )

                # ax[axIndex].barh(
                #     y=y,
                #     width=maxTemp - minTemp,
                #     left=minTemp,
                #     color="black" if darkdetect.isLight() else "lightgrey",
                #     edgecolor="black" if darkdetect.isLight() else "black",
                # )

                tStr = disambiguateLabel(row[1]["Test"]).temperature
                if tStr.startswith("RT"):
                    tStr = "25"

                t = float(tStr)
                meanTemp = (maxTemp + minTemp) / 2

                ax[axIndex].scatter(
                    x=t,
                    y=y,
                    color="black" if darkdetect.isLight() or paperMode else "lightgrey",
                )

                ax[axIndex].errorbar(
                    x=meanTemp,
                    y=y,
                    xerr=[[meanTemp - minTemp], [maxTemp - meanTemp]],
                    markersize=0,
                    color="black" if darkdetect.isLight() or paperMode else "lightgrey",
                )

    if saveDir is not None:
        os.makedirs(saveDir, exist_ok=True)
        savePath = os.path.join(saveDir, fileName)
        fig.savefig(savePath)

    return fig


def plotBode(
    eis: Dict[str, EisData],
    title: str = "Bode Plot",
    **pltParams,
) -> Figure:
    """
    Plots the EIS spectral data with a Bode plot.

    Args:
        eis (Dict[str, EisData]): A dictionary containing EIS spectral data.
        title (str): The title of the plot (placed above ax[0]).
        **pltParams: Additional parameters to pass to each plotting axis.

    Returns:
        Figure: The matplotlib Figure object containing the generated plot.
    """

    fig, ax = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=(12, 8),
    )

    for spectra in eis:
        eis[spectra].data.plot(
            x="ActFreq",
            y="NomVal1",
            marker=".",
            logx=True,
            ax=ax[0],
            ylabel="Magnitude (Ω)",
            label=spectra,
            grid=True,
            **pltParams,
        )
        ax[0].legend(loc="upper left", bbox_to_anchor=(1, 1))
        ax[0].title.set_text(title)

        eis[spectra].data.plot(
            x="ActFreq",
            y="Phase1",
            marker=".",
            logx=True,
            xlabel="Frequency (Hz)",
            ax=ax[1],
            ylabel="Phase (°)",
            legend=False,
            grid=True,
            **pltParams,
        )

    return fig


def plotConstantTempVariedSocBodePerBatch(
    eisByTemp: Dict[str, Dict[str, EisData]],
    temp: str,
    saveDir: str,
    **pltParams,
) -> Dict[str, Figure]:
    batchSplit = groupByBatch(eisByTemp[temp])

    os.makedirs(saveDir, exist_ok=True)

    batchFigures = {}

    for batch in batchSplit:
        fig = plotBode(
            batchSplit[batch],
            title=f"Batch {batch}, {temp}",
            **pltParams,
        )

        batchFigures[batch] = fig

        fig.savefig(
            f"{saveDir}/{batch}{temp}.png",
            transparent=True,
            bbox_inches="tight",
        )

    return batchFigures


def getDcVoltage(eis: EisData) -> float:
    return np.mean([eis.data["U1"][0], eis.data["U2"][0], eis.data["U3"][0]])


def mergeAxisYLim(ax1: Axes, ax2: Axes) -> None:
    """
    Merges the y-axis limits of two matplotlib Axes objects.

    Args:
        ax1 (Axes): The first matplotlib Axes object.
        ax2 (Axes): The second matplotlib Axes object.

    Returns:
        None
    """
    ax1.set_ylim(
        min(ax1.get_ylim()[0], ax2.get_ylim()[0]),
        max(ax1.get_ylim()[1], ax2.get_ylim()[1]),
    )
    ax2.set_ylim(ax1.get_ylim())


from .eisAnalysis import disambiguateLabel


def plotDcVoltageByBattery(
    eis: Dict[str, EisData],
    cellData: Dict[str, Dict[str, float]],
    savePath: str | None = None,
    paperMode: bool = False,
) -> Figure:
    eisByBatch = groupByBatch(eis)

    fig, ax = plt.subplots(
        2,
        1,
        figsize=(12, 8),
        sharex=True,
        sharey=True,
    )

    if not paperMode:
        fig.suptitle("DC Voltage Over SoC by Battery")

    for axis in ax:
        axis.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
        axis.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.2f}V"))

    for batch in eisByBatch:
        eisByTemperature = groupByTemperature(eisByBatch[batch])

        for temperature in eisByTemperature:
            voltageOverCellConcentration = pd.DataFrame(
                {
                    cellData[f"{batch}{disambiguateLabel(spectra).batteryNumber}"][
                        "A"
                    ]: getDcVoltage(eisByTemperature[temperature][spectra])
                    for spectra in eisByTemperature[temperature]
                }.items(),
                columns=["Cell Concentration", "DcVoltage"],
            )

            if paperMode:
                voltageOverCellConcentration["DcVoltage"] /= 6

            # Sort by cell concentration
            voltageOverCellConcentration = voltageOverCellConcentration.sort_values(
                by="Cell Concentration"
            )

            voltageOverCellConcentration.plot(
                x="Cell Concentration",
                y="DcVoltage",
                label=f"{getTemperatureLabel(temperature)}",
                ax=ax[0] if batch == "A" else ax[1],
                marker=".",
                grid=True,
            )

            if paperMode:
                fig.axes[1].set_xlabel(
                    r"Mean Cell Concentration, $A$ (\%w/w)",
                )
                [
                    fig.axes[i].set_ylabel(
                        r"Mean Cell Voltage, $E$ ($V$)",
                    )
                    for i in range(2)
                ]
                fig.axes[0].set_title("0 Cycles")
                fig.axes[1].set_title("50 Cycles")

    if savePath:
        fig.savefig(
            savePath,
            transparent=False,
        )

    return fig


def plotDcVoltageByTemperature(
    eis: Dict[str, EisData],
    savePath: str | None = None,
) -> Figure:
    """
    Plots the DC voltage over temperature for each battery in each batch.

    Args:
        eis (Dict[str, EisData]): A dictionary containing EIS spectral data.
        savePath (str | None): The path to save the plot image. Defaults to None.
    """
    eisByBatch = groupByBatch(eis)

    fig, ax = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle("DC Voltage over Temperature")

    for batch in eisByBatch:
        eisByBattery = groupByBatteryNumber(eisByBatch[batch])

        for battery in eisByBattery:
            voltageOverTemp = pd.DataFrame(
                {
                    spectra.metadata["SetTemperature"] - 273.15: getDcVoltage(spectra)
                    for spectra in eisByBattery[battery].values()
                }.items(),
                columns=["Temperature", "DcVoltage"],
            )

            voltageOverTemp = voltageOverTemp.sort_values(by="Temperature")
            voltageOverTemp.plot(
                x="Temperature",
                y="DcVoltage",
                ax=ax[0] if batch == "A" else ax[1],
                xlabel="Temperature (°C)",
                ylabel="DC Voltage (V)",
                marker=".",
                grid=True,
                label=getSoC(list(eisByBattery[battery].keys())[0]),
            )

    ax[0].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[1].legend(loc="upper left", bbox_to_anchor=(1, 1))
    mergeAxisYLim(ax[0], ax[1])

    if savePath:
        fig.savefig(
            savePath,
            transparent=False,
        )

    return fig


def plotHighFrequencyResistanceVsFreezingFactor(
    fCorrelation,
    paperMode: bool = False,
) -> Figure:
    rHf = [(f, rHf) for f, (rHf, _) in fCorrelation]
    stdRhf = [std for _, (_, std) in fCorrelation]
    fig, ax = plt.subplots()
    ax.scatter(
        *zip(*rHf),
        color="black" if paperMode else None,
    )
    ax.set_xlabel(r"Freezing Factor, $F$")
    ax.set_ylabel(r"High Frequency Resistance, $R_{HF} (m\Omega)$")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid(
        True,
        which="both",
        linestyle="--",
        linewidth=0.5,
    )

    from numpy.polynomial.polynomial import Polynomial

    p = Polynomial.fit(*zip(*rHf), 1)
    x = [min(f for f, _ in rHf), max(f for f, _ in rHf)]
    y = p(x)
    ax.plot(
        x,
        y,
        linestyle="--",
        color="black" if paperMode else None,
    )

    monomial = p.convert()
    a, b = monomial.coef[1], monomial.coef[0]
    r2 = np.corrcoef(*zip(*rHf))[0, 1] ** 2
    ax.text(
        0.05,
        0.85,
        f"$R_{{HF}} = {a:.2f}F + {b:.2f}, (R^2 = {r2:.3f})$",
        transform=ax.transAxes,
        fontsize=12,
    )

    return fig


def getTemperatureLabel(temperature: str) -> str:
    """
    Returns the set temperature label for plotting.
    """
    if temperature.startswith("RT"):
        return "25-28°C"
    else:
        return f"{temperature}°C"

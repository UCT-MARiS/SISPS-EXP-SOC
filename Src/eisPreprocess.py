import copy
from dataclasses import dataclass
import pandas as pd
import regex as re

from eisImport import EisData
from typing import Dict, Optional


def filterNegativeReal(eis: Dict[str, EisData]) -> Dict[str, EisData]:
    """
    Filters points in EIS data where the real impedance is negative (an impossible value).

    Parameters:
    - eis (Dict[str, EisData]): A dictionary containing EIS data, where the keys are spectra names and the values are EisData objects.

    Returns:
    - Dict[str, EisData]: A filtered dictionary of EIS data, where the keys are spectra names and the values are EisData objects.

    """
    eisCopy = copy.deepcopy(eis)  # Prevent modifying the parameter passed by reference
    for spectra in eisCopy:
        spectrum = eisCopy[spectra]
        spectrum.data = spectrum.data[spectrum.data["Zreal1"] > 0]
        numFilteredPoints = len(eis[spectra].data) - len(spectrum.data)
        if numFilteredPoints > 0:
            print(f"Filtered {numFilteredPoints} negative real points from {spectra}")
    return eisCopy


def filterSingleOutlier(eis: Dict[str, EisData]) -> Dict[str, EisData]:
    """
    Filters outlying points in EIS data where the difference between points n and n+1 is greater than that between points n to n+2.

    Parameters:
    - eis (Dict[str, EisData]): A dictionary containing EIS data, where the keys are spectra names and the values are EisData objects.

    Returns:
    - Dict[str, EisData]: A filtered dictionary of EIS data, where the keys are spectra names and the values are EisData objects.

    """
    eisCopy = copy.deepcopy(eis)
    for spectra in eisCopy:
        spectrum = eisCopy[spectra]
        data = spectrum.data

        diff1 = (data["Zreal1"].diff(-1) + 1j * data["Zimg1"].diff(-1)).abs()
        diff2 = (data["Zreal1"].diff(-2) + 1j * data["Zimg1"].diff(-2)).abs()

        # Option context responding Deprecation warning on fillna as at June 2024
        with pd.option_context("future.no_silent_downcasting", True):
            data = data[
                ((diff1 < 2 * diff2) | (diff1.isna()) | (diff2.isna()))
                .shift(1)
                .fillna(True)  # Corrects NaN due to shift, separate to NaN in diff
                .infer_objects()
            ]
        eisCopy[spectra].data = data

        if len(data) < len(eis[spectra].data):

            # Find the frequencies of the dropped points from the ActFreq field
            droppedFrequencies = (
                eis[spectra]
                .data[~eis[spectra].data.index.isin(data.index)]["ActFreq"]
                .tolist()
            )

            print(
                f"Filtered {len(eis[spectra].data) - len(data)} outliers from {spectra} at frequencies {droppedFrequencies}Hz"
            )

    return eisCopy


def renameLabels(eis: Dict[str, EisData]) -> Dict[str, EisData]:
    """
    Renames the labels of the EIS data to a consistent format:

    e.g. `UCT_AST9AH_B01_RT01`
    - `UCT_AST9AH` is a prefix
    - `B01` is the battery number
    - `RT01` is the temperature

    The original labels remain available in the `Comment` field of the `EisData` object.

    Parameters:
    - eis (Dict[str, EisData]): A dictionary containing EIS data, where the keys are spectra names and the values are EisData objects.

    Returns:
    - Dict[str, EisData]: A dictionary containing EIS data, where the keys are spectra names and the values are EisData objects with renamed labels.
    """
    prefix = "UCT_AST9AH_"

    renamedEis = {}
    for spectra in eis:
        battery = re.search(r"(A|B)\d{2}", spectra).group(0)  # type: ignore

        temperature = re.search(r"RT\d?|-40|-30|-20|-10|00|_\+00|_0", spectra).group(0)  # type: ignore
        if temperature == "_+00" or temperature == "_0":
            temperature = "00"
        if temperature == "RT":
            temperature = "RT1"

        runRepetition = re.search(r"(\s\d$)", spectra)

        newSpectraName = prefix + battery + "_" + temperature
        if runRepetition:
            newSpectraName += runRepetition.group(0)

        assert newSpectraName not in renamedEis, f"Duplicate key {newSpectraName}"

        if newSpectraName not in eis:
            print(f"Rename: \u27A4 {spectra:<25} \u27A4 {newSpectraName}")
        else:
            print(f"Unchanged: \u27A4 {newSpectraName}")

        renamedEis[newSpectraName] = eis[spectra]

    return renamedEis


@dataclass
class EisLabelDisambiguation:
    batteryBatch: str
    batteryNumber: str
    temperature: str
    runRepetition: Optional[str] = None


def disambiguateLabel(label: str) -> EisLabelDisambiguation:
    batteryBatchMatch = re.search(r"(A|B)(?>\d{2})", label)
    batteryNumberMatch = re.search(r"(A|B)(\d{2})", label)
    temperatureMatch = re.search(r"RT\d|-40|-30|-20|-10|00", label)
    runRepetitionMatch = re.search(r"(\s\d$)", label)

    assert batteryBatchMatch, f"Invalid label {label}"
    assert batteryNumberMatch, f"Invalid label {label}"
    assert temperatureMatch, f"Invalid label {label}"

    batteryBatch = batteryBatchMatch.group(1)
    batteryNumber = batteryNumberMatch.group(2)
    temperature = temperatureMatch.group(0)
    runRepetition = runRepetitionMatch.group(0) if runRepetitionMatch else None

    return EisLabelDisambiguation(
        batteryBatch,
        batteryNumber,
        temperature,
        runRepetition,
    )

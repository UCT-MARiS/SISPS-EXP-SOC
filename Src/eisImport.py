import os as os
import pandas as pd
from functools import cache

from typing import List, Dict
from dataclasses import dataclass


@cache
def findEisFiles(eisDirectory: str, isAll: bool = False) -> List[str]:
    files = []
    for root, dirs, file in os.walk(eisDirectory):
        for f in file:
            if isAll:
                if f.endswith("_EIS00001.csv") and root.endswith("All"):
                    files.append(os.path.join(root, f))
            else:
                if f.endswith("_EIS00001.csv") and not root.endswith("All"):
                    files.append(os.path.join(root, f))

    return files


def findMainEisFiles(eisDirectory: str) -> List[str]:
    return findEisFiles(eisDirectory, isAll=False)


def findAllEisFiles(eisDirectory: str) -> List[str]:
    return findEisFiles(eisDirectory, isAll=True)


@dataclass
class EisData:
    data: pd.DataFrame
    metadata: Dict[str, str]

    def __repr__(self) -> str:
        return f"EisData: {self.metadata['Comment']}"


@cache
def readEisFile(file: str) -> EisData:
    headerRow = 30
    skipRow = lambda r: (r in range(0, headerRow - 1)) or (
        r in range(headerRow, headerRow + 4)
    )  # Constant offset for all EIS files.

    data = pd.read_csv(
        file,
        skiprows=skipRow,
        usecols=lambda col: col
        not in [
            "Voltage",
            "Current",
            "Cycle",
            "Cycle Level",
            "EisStart",
            "EisFinish",
            "AAcMax",
            "Unnamed: 42",
        ],
    )

    metadata = pd.read_csv(
        file,
        nrows=23,
        skiprows=2,
        sep=",",
        names=["key", "value"],
    )
    metadataDict: Dict = metadata.set_index("key").to_dict()["value"]

    return EisData(data, metadataDict)


@cache
def readEisFiles(files: List[str]) -> Dict[str, EisData]:
    eis = {}
    for file in files:
        eisData = readEisFile(file)
        eis[eisData.metadata["Comment"]] = (
            eisData  # Comment set as unique key during experiment.
        )
    return eis


def readMeasurementsAndObservations(
    file: str,
    discardColumns: list = [],
) -> pd.DataFrame:
    """
    Read the EIS measurements and observations table from the experiment spreadsheet.
    """

    # Raw reading needed to locate sub-tables within sheet.
    rawRead = pd.read_excel(
        file,
        sheet_name="Data",
        header=None,
    )

    # Find the row where ""3. Cooling & EIS" is located. This marks start of the EIS measurements table.

    # Offset from the "3. Cooling & EIS" row to the start of the EIS table.
    START_ROW_OFFSET = 10  # ! This may break if the spreadsheet format changes.

    startRow = rawRead[rawRead[0] == "3. Cooling & EIS"].index[0] + START_ROW_OFFSET
    emptyRows = rawRead[rawRead[0].isnull()].index
    endRow = emptyRows[emptyRows > startRow][0]
    assert (
        endRow - startRow - 1 == 140
    ), f"Expected 140 rows of data, got {endRow - startRow - 1} rows."

    if len(discardColumns) == 0:
        discardedColumns = ["Due"]  # Generally not useful

    eisObservations = pd.read_excel(
        file,
        sheet_name="Data",
        header=startRow,
        nrows=endRow - startRow,
        usecols=lambda col: col not in discardedColumns,
    ).fillna("")

    return eisObservations


def groupMeasurementsAndObservations(
    observations: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """
    Group the measurements and observations table by batch and then temperature of measurement.
    The expected table follows a strict format which this function assumes.
    """

    def groupByTemperature(batchObservations: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Group the batch observations by temperature of measurement.
        """
        assert len(batchObservations) == 70

        temperatureKeys = [
            "RT1",
            "-40",
            "-30",
            "-20",
            "-10",
            "00",
            "RT2",
        ]

        grouped = {
            f"{temperatureKeys[i]}": batchObservations.iloc[i * 10 : (i + 1) * 10]
            for i in range(len(temperatureKeys))
        }
        return grouped

    batchKeys = ["A", "B"]
    grouped = {
        key: groupByTemperature(
            observations[observations["Battery"].apply(lambda x: x[11] == key)]
        )
        for key in batchKeys
    }
    return grouped


def inferObservationTestNames(
    groupedObservations: Dict[str, Dict[str, pd.DataFrame]]
) -> None:
    """
    Infer the test name from the grouped observations and add it as a column to the observations.
    """

    for batch in groupedObservations:
        for temperature in groupedObservations[batch]:
            for row in groupedObservations[batch][temperature].iterrows():
                testName = f"{row[1]['Battery']}_{temperature}"
                groupedObservations[batch][temperature].at[row[0], "Test"] = testName

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

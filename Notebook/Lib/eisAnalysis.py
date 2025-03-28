from typing import Dict

from .eisImport import EisData
from .eisPreprocess import disambiguateLabel

ABSOLUTE_ZERO_CELSIUS = 273.15


def groupByBatch(eisData: Dict[str, EisData]) -> Dict[str, Dict[str, EisData]]:
    """
    Splits EIS data sets by batch number.

    Args:
            eisData (dict): A dictionary containing EIS data sets.

    Returns:
            dict: A dictionary containing EIS data sets split by batch number.
    """
    eisByBatch = {}
    for spectra in eisData:
        disambiguatedLabel = disambiguateLabel(spectra)
        batch = disambiguatedLabel.batteryBatch
        if batch not in eisByBatch:
            eisByBatch[batch] = {}
        eisByBatch[batch][spectra] = eisData[spectra]
    return eisByBatch


def groupByTemperature(eisData: Dict[str, EisData]) -> Dict[str, Dict[str, EisData]]:
    """
    Splits EIS data sets by temperature.

    Args:
            eisData (dict): A dictionary containing EIS data sets.

    Returns:
            dict: A dictionary containing EIS data sets split by temperature.
    """
    eisByTemperature = {}
    for spectra in eisData:
        disambiguatedLabel = disambiguateLabel(spectra)
        temperature = disambiguatedLabel.temperature
        if temperature not in eisByTemperature:
            eisByTemperature[temperature] = {}
        eisByTemperature[temperature][spectra] = eisData[spectra]
    return eisByTemperature


def groupByBatteryNumber(eisData: Dict[str, EisData]) -> Dict[str, Dict[str, EisData]]:
    """
    Splits EIS data sets by battery number.

    Args:
            eisData (dict): A dictionary containing EIS data sets.

    Returns:
            dict: A dictionary containing EIS data sets split by battery number.
    """
    eisByBatteryNumber = {}
    for spectra in eisData:
        disambiguatedLabel = disambiguateLabel(spectra)
        batteryNumber = disambiguatedLabel.batteryNumber
        if batteryNumber not in eisByBatteryNumber:
            eisByBatteryNumber[batteryNumber] = {}
        eisByBatteryNumber[batteryNumber][spectra] = eisData[spectra]
    return eisByBatteryNumber


socMap = {
    "A01": "100%",
    "A02": "93%",
    "A03": "87%",
    "A04": "80%",
    "A05": "73%",
    "A06": "67%",
    "A07": "60%",
    "A08": "53%",
    "A09": "47%",
    "A10": "40%",
    "B01": "100%",
    "B02": "93%",
    "B03": "87%",
    "B04": "80%",
    "B05": "73%",
    "B06": "67%",
    "B07": "60%",
    "B08": "53%",
    "B09": "47%",
    "B10": "40%",
}


def getSoC(spectra: str) -> str:
    """
    Returns the state of charge (SoC) of the battery.

    Args:
            spectra (str): The EIS spectra name.

    Returns:
            str: The state of charge (SoC) of the battery.
    """
    disambiguation = disambiguateLabel(spectra)
    mapIndex = disambiguation.batteryBatch + disambiguation.batteryNumber
    return socMap[mapIndex]


def getPaperLabel(spectra: str) -> str:
    """
    Returns the alternative label for external use.

    Args:
            spectra (str): The EIS spectra name.

    Returns:
            str: The paper label of the battery.
    """
    disambiguation = disambiguateLabel(spectra)
    return f"{disambiguation.batteryBatch}{disambiguation.batteryNumber} ({getSoC(spectra)})"


def getSocByNumber(number: int) -> str:
    """
    Returns the state of charge (SoC) of the battery.

    Args:
            number (int): The number of the battery.

    Returns:
            str: The state of charge (SoC) of the battery.
    """
    mapIndex = "A" + f"{number:02d}"
    return socMap[mapIndex]


def getSocNumeric(spectra: str) -> float:
    """
    Returns the state of charge (SoC) of the battery (0-1).
    """

    return float(getSoC(spectra)[:-1]) / 100


def getTemperatureNumeric(spectra: str) -> float:
    """
    Returns the set temperature of the battery in kelvin.
    """
    disambiguation = disambiguateLabel(spectra)
    if disambiguation.temperature.startswith("RT"):
        return 25.0 + ABSOLUTE_ZERO_CELSIUS
    else:
        return int(disambiguation.temperature) + ABSOLUTE_ZERO_CELSIUS

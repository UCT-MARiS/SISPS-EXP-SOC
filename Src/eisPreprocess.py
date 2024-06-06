from eisImport import EisData
from typing import Dict
import copy


def filterNegativeReal(eis: Dict[str, EisData]) -> Dict[str, EisData]:
    eisCopy = copy.deepcopy(eis)  # Prevent modifying the original data
    for spectra in eisCopy:
        spectrum = eisCopy[spectra]
        spectrum.data = spectrum.data[spectrum.data["Zreal1"] > 0]
    return eisCopy

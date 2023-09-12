import copy
import numpy as np
from REM.analysis import PhaseConstructor, ElementalAnalysesParser, InfoOrganizer
import matplotlib.pyplot as plt


phase_constructor = PhaseConstructor(phases=["CaF2", "CaO", "SiO2",
                                             "Al2O3", "MgO", "Na2O",
                                             "K2O", "FeO", "ZnO"],
                                     ignore=["O", "C"])
phased_data = ElementalAnalysesParser("data/sem.xlsx").phased(phase_constructor)

print(phased_data)
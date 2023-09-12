import copy
import numpy as np
from REM.analysis import PhaseConstructor, ElementalAnalysesParser, InfoOrganizer


phase_constructor = PhaseConstructor(phases=["CaO", "SiO2", "Al2O3", "MgO", "FeO", "ZnO",
                                             "KCl", "NaCl", "K2O", "Na2O", "PbO",
                                             "CuO", "MnO", "S", "Cr2O3"],
                                     ignore=["O", "C"])

phased_data = ElementalAnalysesParser("data/sem.xlsx").phased(phase_constructor)
phased_data.to_excel("results/schlacken_phasenanalysen_gerechnet.xlsx")

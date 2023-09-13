import traceback

import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QShortcut
import sys
from PyQt5.QtCore import Qt

from REM.analysis import PhaseConstructor, ElementalAnalysesParser
from REM.chemical import ELEMENTS, Molecule, Element
from ui import *

class REMPhaseCalculator(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(REMPhaseCalculator, self).__init__(parent)
        self.setupUi(self)
        self.elements_analyses = None

        self.addBtn.clicked.connect(lambda: self.addEntry())
        self.addIgnoreBtn.clicked.connect(lambda: self.addIgnoreEntry())
        self.removeBtn.clicked.connect(self.removeCompoundEntry)
        self.removeIgnoreBtn.clicked.connect(self.removeIgnoreEntry)
        self.loadBtn.clicked.connect(self.pasteClipboardToElementsTable)
        self.saveBtn.clicked.connect(self.calculateCompounds)


        # Create a shortcut for Ctrl+V (Cmd+V on macOS)
        self.shortcut_paste = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_V), self)
        self.shortcut_paste.activated.connect(self.pasteClipboardToElementsTable)

        # Create a shortcut for Ctrl+V (Cmd+V on macOS)
        self.shortcut_copy = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_C), self)
        self.shortcut_copy.activated.connect(self.copy_to_clipboard)

        # Create a shortcut for Ctrl+V (Cmd+V on macOS)
        self.shortcut_calc= QShortcut(QKeySequence(Qt.Key_Space), self)
        self.shortcut_calc.activated.connect(self.calculateCompounds)



    def addEntry(self, text=None):
        try:
            if text is None:
                text = self.compoundLineEdit.text()
            text = text.replace(" ", "")

            if text == "":
                return

            text = text.split(",")
            if type(text) is list:
                for t in text:
                    self.addColumnToCompounds(t)
            else:
                self.addColumnToCompounds(text)

            self.compoundLineEdit.setText("")
        except:
            traceback.print_exc()


    def addIgnoreEntry(self, text=None):
        try:
            if text is None:
                text = str(self.ignoreLineEdit.text())
            text = text.replace(" ", "")

            if text == "":
                return

            text = text.split(",")
            if type(text) is list:
                for t in text:
                    self.addElementToIgnore(t)
            else:
                self.addElementToIgnore(text)

            self.ignoreLineEdit.setText("")
        except:
            traceback.print_exc()

    def addColumnToCompounds(self, compound):
        try:
            Molecule(compound)
            compound = str(compound)

            if compound in self.compounds:
                print(f"{compound} already there")
                return None

            self.compoundListWidget.addItem(compound)
            self.addColumn(compound)
        except Exception as e:
            print(f"{compound} could not be parsed as Compound and was not added.")
            traceback.print_exc()
            return None

    def addElementToIgnore(self, element):
        try:
            element = Element(element)
            element = str(element)

            if element in self.ignores:
                print(f"{element} already there")
                return None

            self.ignoredElementsListWidget.addItem(element)

        except Exception as e:
            print(f"{element} could not be parsed as Compound and was not added.")
            traceback.print_exc()
            return None

    @property
    def compounds(self):
        return [self.compoundListWidget.item(i).text() for i in range(self.compoundListWidget.count())]

    @property
    def ignores(self):
        return [self.ignoredElementsListWidget.item(i).text() for i in range(self.ignoredElementsListWidget.count())]

    def removeCompoundEntry(self):
        try:
            for item in self.compoundListWidget.selectedItems():
                self.compoundListWidget.takeItem(self.compoundListWidget.row(item))
                tableWidget = self.compoundTableWidget
                header = tableWidget.horizontalHeader()

                # Find the index of the column with the header name "CaO"
                column_index = tableWidget.columnCount() - 1  # Default to the last column
                for i in range(tableWidget.columnCount()):
                    if tableWidget.horizontalHeaderItem(i).text() == item:
                        column_index = i
                        break

                tableWidget.removeColumn(column_index)
        except:
            traceback.print_exc()

    def removeIgnoreEntry(self):
        try:
            for item in self.ignoredElementsListWidget.selectedItems():
                self.ignoredElementsListWidget.takeItem(self.ignoredElementsListWidget.row(item))
        except:
            traceback.print_exc()

    def addColumn(self, col):
        current_columns = self.compoundTableWidget.columnCount()
        # Increase column count by one
        self.compoundTableWidget.setColumnCount(current_columns + 1)

        # Set the header for the new column
        header = self.compoundTableWidget.horizontalHeader()
        header.setSectionResizeMode(current_columns, QtWidgets.QHeaderView.Stretch)
        self.compoundTableWidget.setHorizontalHeaderItem(current_columns, QtWidgets.QTableWidgetItem(col))

    def pasteClipboardToElementsTable(self):
        try:
            clipboard = QApplication.clipboard()

            text = clipboard.text()

            rows = text.split("\n")

            for i,row in enumerate(rows):
                rows[i] = row.split("\t")

            df = pd.DataFrame(data=rows[:-1])
            columns = df.iloc[0,0:]
            index = df.iloc[1:,0].tolist()
            df = df.drop([0], axis=0)
            df = df.replace("", "0")


            df.columns = columns
            df = df.reset_index(drop=True)

            # todo drop columns that are not chemical elements
            for i, column in enumerate(df.columns):
                if column not in ELEMENTS:
                    df = df.drop([column], axis=1)

            df.insert(0, "Id", index)

            self.fillTableWithDF(self.elementsTableWidget, df)

            df.index = index
            df = df.iloc[:,1:]

            # todo parse empty cells as zero
            df = df.astype(float)
            self.elements_analyses = ElementalAnalysesParser(df)
        except:
            traceback.print_exc()

    def fillTableWithDF(self, widget, df):
        # clear
        widget.clear()

        # Set the table dimensions
        widget.setRowCount(df.shape[0])
        widget.setColumnCount(df.shape[1])
        # Set the table headers
        widget.setHorizontalHeaderLabels(df.columns)

        # Fill the table with data
        for row_num, row_data in df.iterrows():
            for col_num, col_name in enumerate(df.columns):
                value = row_data[col_name]
                try:
                    item = QTableWidgetItem('' if pd.isna(value) else f"{value*100:.2f}")
                except:
                    item = QTableWidgetItem(value)

                widget.setItem(row_num, col_num, item)


    def copy_to_clipboard(self):
        # Create a sample DataFrame
        # Copy the DataFrame to the clipboard
        self.phased_df.to_clipboard(excel=True)


    def calculateCompounds(self):
        try:
            if type(self.elements_analyses) is not ElementalAnalysesParser:
                return None

            phase_constructor = PhaseConstructor(phases=self.compounds,
                                                 ignore=self.ignores)

            phased_data = self.elements_analyses.phased(phase_constructor)

            self.fillTableWithDF(self.compoundTableWidget, phased_data.df_int_index)
            self.phased_df = phased_data.df
            #phased_data.to_excel("schlacken_phasenanalysen_gerechnet.xls")
        except:
            traceback.print_exc()

    def save(self):
        with open("ignores.txt", "w") as file:
            file.write(",".join(self.ignores))

        with open("compounds.txt", "w") as file:
            file.write(",".join(self.compounds))

    def load(self):
        with open("ignores.txt", "r") as file:
            rd = file.read()
            self.addIgnoreEntry(rd)
        with open("compounds.txt", "r") as file:
            rd = file.read()
            self.addEntry(rd)

# @todo str+v for pasting, str+c for copying

def main():
    app = QApplication(sys.argv)
    form = REMPhaseCalculator()
    app.aboutToQuit.connect(form.save)
    form.load()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()

#MgO, Al2O3, SiO2, S, KCl, Cl, K2O, CaO, Cr2O3, MnO, FeO, Cu2O, ZnO, PbO, Na2O
#SiO2, CaO, Al2O3, MgO, Na2O, S, Cl, Cr2O3, MnO, FeO, Cu, ZnO, PbO
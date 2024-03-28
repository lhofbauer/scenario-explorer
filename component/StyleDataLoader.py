from pathlib import Path
import pandas as pd

# Get the absolute path of the parent directory containing the current script
appdir = str(Path(__file__).parent.parent.resolve())

class ColorMapStyle:
    def __init__(self, appdir = appdir, palette = 'tol-light', 
                 continuous = False, theme = 'default'):
        self.appdir = appdir
        self.palette = palette
        self.continuous = continuous
        self.theme = theme
        self.cp = None
        self.ca = None
        self.cdm = None

    def load_colour_palette(self):
        self.cp = pd.read_csv(f'{self.appdir}/data/colour_palette.csv', index_col=["PALETTE"])
        self.cp = self.cp.loc[self.palette, :]
        self.cp = self.cp.sort_values("PC_CODE")

    def load_colour_allocation(self):
        self.ca = pd.read_csv(f'{self.appdir}/data/colour_allocation.csv', index_col=["THEME"]) 
        naming = pd.read_csv(f'{self.appdir}/data/naming.csv', index_col=["NAME_IN_MODEL"])
        naming = naming["NAME"]
        self.ca["ARTEFACT"] = self.ca["ARTEFACT"].replace(naming)
        self.ca = self.ca.loc[self.theme, :]
        self.ca = self.ca.merge(right=self.cp[["PC_CODE", "COLOUR_CODE"]],
                                how="left", on="PC_CODE")
        self.ca = self.ca.drop("PC_CODE", axis=1)
        self.ca = self.ca.set_index("ARTEFACT")
        self.ca = self.ca["COLOUR_CODE"].to_dict()

    def construct_cdm(self):
        if not self.continuous:
            self.load_colour_palette()
            self.load_colour_allocation()
        else:
            self.ca = list()
            self.ca.append([0, self.cp.loc[self.cp["PC_CODE"] == -1, "COLOUR_CODE"].squeeze()])
            colours = self.cp.loc[self.cp["PC_CODE"] != -1, "COLOUR_CODE"].to_list()
            for s, c in zip(np.linspace(0.001, 1, len(colours)), colours):
                self.ca.append([s, c])
        self.cdm = self.ca
        return self.cdm
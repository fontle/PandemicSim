import json
import tkinter as tk
from tkinter import ttk
import numpy as np
from dataclasses import dataclass


class _RadioFrame(ttk.LabelFrame):
    def __init__(self, root, title: str, options: dict) -> None:
        super().__init__(root, text=title)

        self.options = options

        self.var = tk.StringVar()
        if len(self.options.keys()) > 2:
            middle = len(self.options.keys()) // 2
        else:
            middle = 1
        self.var.set(list(self.options.values())[middle])

        for col, val in enumerate(self.options.keys()):
            button = ttk.Radiobutton(
                self, text=val, value=self.options[val], variable=self.var
            )
            button.grid(column=col, row=0, padx=5)

    def fetch(self):
        """
        Returns the current toggled button
        """
        return self.var.get()


class _Slider(ttk.LabelFrame):
    def __init__(self, root, title: str, from_: int, to: int, default: int) -> None:
        super().__init__(root, text=title)

        self.slider = ttk.Scale(
            self,
            from_=from_,
            to=to,
            orient="horizontal",
            command=lambda _: self.set_label(),
        )
        self.slider.set(default)
        self.slider.grid(row=0, column=0, padx=5, pady=5)

        self.label = ttk.Label(self, text=round(self.slider.get()))
        self.label.grid(row=0, column=1)

    def set_label(self):

        self.label = ttk.Label(self, text=round(self.slider.get()))
        self.label.grid(row=0, column=1)

    def fetch(self) -> int:
        """
        Returns the current value of slider
        """
        return int(round(self.slider.get()))


class _Menu(tk.Tk):
    def __init__(self, config_addr="config.json"):
        super().__init__()

        self.iconphoto(False, tk.PhotoImage(file="icon.png"))
        self.title("Simulation Configuration")

        self.config_addr = config_addr

        with open(self.config_addr, "r") as config_file:
            self.config = json.loads(config_file.read())

        self.theme = self.config["theme"][self.config["app"]["theme"]]
        self.sim_vars = self.config["simulation"]
        self.app_vars = self.config["app"]
        self.path_vars = self.config["pathogen"]

        self.geometry = f'{self.app_vars["sim_size"][0]}x{self.app_vars["sim_size"][1]}'

        self.column0 = tk.Frame(self)
        self.column1 = tk.Frame(self)

        self.column0.grid(row=1, column=0, sticky=tk.N)
        self.column1.grid(row=1, column=1, sticky=tk.N)

        self.theme_chooser = _RadioFrame(
            self, "Simulation Theme", {"Light": "light", "Dark": "dark"}
        )
        self.theme_chooser.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.pathogen_frame = ttk.LabelFrame(self.column0, text="Pathogen")
        self.pathogen_frame.pack(padx=5, pady=5)

        self.lethality = _RadioFrame(
            self.pathogen_frame,
            "Lethality",
            {"Low": "0.001", "Medium": "0.002", "High": "0.005"},
        )
        self.lethality.grid(row=0, column=0, pady=5)

        self.curability = _RadioFrame(
            self.pathogen_frame,
            "Curability",
            {"Low": "0.001", "Medium": "0.0025", "High": "0.005"},
        )
        self.curability.grid(row=1, column=0, pady=5)

        self.catchment = _RadioFrame(
            self.pathogen_frame, "Catchment", {"Low": "1", "Medium": "5", "High": "10"}
        )
        self.catchment.grid(row=2, column=0, pady=5)

        self.infectiousness = _RadioFrame(
            self.pathogen_frame,
            "Infectiousness",
            {"Low": "0.03", "Medium": "0.1", "High": "0.25"},
        )
        self.infectiousness.grid(row=3, column=0, pady=5)

        self.mitigation_frame = ttk.LabelFrame(self.column0, text="Mitigations")
        self.mitigation_frame.pack(padx=5, pady=5)

        self.migrations = _RadioFrame(
            self.mitigation_frame,
            "Migrations",
            {"Low": "0.01", "Medium": "0.05", "High": "0.1"},
        )
        self.migrations.grid(row=0, column=0, padx=5, pady=5)

        self.movements = _RadioFrame(
            self.mitigation_frame,
            "Movements",
            {"Low": "0.01", "Medium": "0.05", "High": "0.1"},
        )
        self.movements.grid(row=1, column=0, padx=5, pady=5)

        self.population = _Slider(self.column1, "Population Size", 1, 2000, 1000)
        self.population.pack(side=tk.TOP, padx=5, pady=5)

        self.layout_frame = ttk.LabelFrame(self.column1, text="Community Layout")
        self.layout_frame.pack(side=tk.TOP, padx=5, pady=10)

        self.rows = _Slider(self.layout_frame, "Rows", 1, 8, 1)
        self.rows.grid(row=0, column=0, padx=5, pady=5)

        self.cols = _Slider(self.layout_frame, "Columns", 1, 8, 1)
        self.cols.grid(row=1, column=0, padx=5, pady=5)

        self.size_frame = ttk.LabelFrame(self.column1, text="Simulation Size")
        self.size_frame.pack(side=tk.TOP, padx=5, pady=0)

        self.width = _Slider(self.size_frame, "Width", 360, 1000, 600)
        self.width.grid(row=0, column=0)

        self.height = _Slider(self.size_frame, "Height", 360, 600, 400)
        self.height.grid(row=1, column=0, padx=5, pady=5)

        self.button_frame = ttk.Frame(self.column0)
        self.button_frame.pack(side=tk.TOP, pady=5)

        self.save_button = ttk.Button(
            self.button_frame, text="Save", command=lambda: self.save()
        )
        self.save_button.grid(row=0, column=0, padx=10)

        self.exit_button = ttk.Button(
            self.button_frame, text="Close", command=lambda: self.exit()
        )
        self.exit_button.grid(row=0, column=1, padx=10)

    def save(self):

        self.config["app"]["theme"] = str(self.theme_chooser.fetch())
        self.path_vars["lethality"] = float(self.lethality.fetch())
        self.path_vars["curability"] = float(self.curability.fetch())
        self.path_vars["catchment"] = float(self.catchment.fetch())
        self.path_vars["infectiousness"] = float(self.infectiousness.fetch())

        self.sim_vars["migration"] = float(self.migrations.fetch())
        self.sim_vars["movement"] = float(self.movements.fetch())

        population_size = self.population.fetch()
        rows = self.rows.fetch()
        cols = self.cols.fetch()

        community_size = population_size // (rows * cols)
        remainder = population_size % (rows * cols)

        layout = []

        # Assigne a weighted probability for a community having different amount of places
        places_choice = [0, 1, 2, 3]
        places_weights = [0.4, 0.4, 0.15, 0.05]
        for _ in range(rows):
            row_layout = []

            for _ in range(cols):
                num_places = np.random.choice(places_choice, p=places_weights)
                row_layout.append([int(community_size), int(num_places)])

            layout.append(row_layout)

        # Add excess population to first community
        layout[0][0][0] += remainder

        self.sim_vars["layout"] = layout
        self.sim_vars["population"] = population_size
        self.sim_vars["susceptible"] = population_size

        # Round width and height to nearest 10 to prevent weird remainders
        width = round(self.width.fetch() / 10) * 10
        height = round(self.height.fetch() / 10) * 10
        self.app_vars["sim_size"] = width, height

    def exit(self):
        self.save()
        self.destroy()


@dataclass
class _Theme:
    appbg: tuple[int, int, int]
    simbg: tuple[int, int, int]
    infected: tuple[int, int, int]
    immune: tuple[int, int, int]
    dead: tuple[int, int, int]
    susceptible: tuple[int, int, int]
    place: tuple[int, int, int]
    route: tuple[int, int, int]
    r_label: tuple[int, int, int]


@dataclass
class _Sim:
    layout: list
    movement: float
    migration: float
    population: int
    dead: int
    immune: int
    susceptible: int
    infected: int


@dataclass
class _App:
    sim_size: tuple[int, int]
    sidebar_width: int
    bar_height: int
    theme: str


@dataclass
class _Pathogen:
    catchment: float
    curability: float
    infectiousness: float
    lethality: float


menu = _Menu()
menu.mainloop()

theme = _Theme(*menu.theme.values())
sim = _Sim(*menu.sim_vars.values())
app = _App(*menu.app_vars.values())
pathogen = _Pathogen(*menu.path_vars.values())
del menu

if __name__ == "__main__":
    print(theme.__dict__)
    print(sim.__dict__)
    print(app.__dict__)
    print(pathogen.__dict__)

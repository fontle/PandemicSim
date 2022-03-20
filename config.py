import json
import tkinter as tk
from tkinter import ttk
import numpy as np

class Config(tk.Tk):

    def __init__(self, config_addr = 'config.json'):
        super().__init__()

        self.iconphoto(False, tk.PhotoImage(file='icon.png'))
        self.title('Simulation Configuration')

        self.config_addr = config_addr
        with open(self.config_addr, 'r') as config_file:
            self.config = json.loads(config_file.read())

        self.theme = self.config['theme'][self.config['app']['theme']]
        self.sim_vars = self.config['simulation']
        self.app_vars = self.config['app']
        self.path_vars = self.config['pathogen']

        self.geometry = f'{self.app_vars["sim_size"][0]}x{self.app_vars["sim_size"][1]}'

        self.column0 = tk.Frame(self)
        self.column1 = tk.Frame(self)

        self.column0.grid(row=1,column=0, sticky=tk.N)
        self.column1.grid(row=1,column=1, sticky=tk.N)

        # Simulation theme chooser
        self.theme_frame = ttk.LabelFrame(self, text='Simulation Theme')
        self.theme_frame.grid(row=0, column=0, padx = 10, pady = 10, columnspan= 2)
        self.theme_var = tk.StringVar()
        self.theme_var.set("dark")

        for col, theme in enumerate(['Light', 'Dark']):

            button = ttk.Radiobutton(self.theme_frame, text=theme, value=theme.lower(), variable=self.theme_var)
            button.grid(column=col, row=0, padx=5)


        self.pathogen_frame = ttk.LabelFrame(self.column0, text = 'Pathogen')
        self.pathogen_frame.pack(padx = 5, pady = 5)


        # Lethality of pathogen chooser
        self.lethality_frame = ttk.LabelFrame(self.pathogen_frame, text='Lethality')
        self.lethality_frame.grid(row = 0, column = 0, padx = 5, pady = 5)
        self.lethality_var = tk.StringVar()
        self.lethality_values = {'Low': 0.00001, 'Medium': 0.001, 'High': 0.05}

        self.lethality_var.set(self.lethality_values['Medium'])

        for col, val in enumerate(self.lethality_values.keys()):

            button = ttk.Radiobutton(self.lethality_frame,
                text=val,
                value=self.lethality_values[val],
                variable=self.lethality_var)
            button.grid(column=col, row=0, padx=5)


        # Curability of pathogen chooser
        self.curability_frame = ttk.LabelFrame(self.pathogen_frame, text='Curability')
        self.curability_frame.grid(row = 1, column = 0, padx = 5, pady = 5)
        self.curability_var = tk.StringVar()
        self.curability_values = {'Low': 0.00001, 'Medium': 0.001, 'High': 0.05}
        self.curability_var.set(self.curability_values['Medium'])

        for col, val in enumerate(self.curability_values.keys()):

            button = ttk.Radiobutton(self.curability_frame,
                text=val,
                value=self.curability_values[val],
                variable=self.curability_var)
            button.grid(column=col, row=0, padx=5)


        # Catchment area of pathogen chooser
        self.catchment_frame = ttk.LabelFrame(self.pathogen_frame, text='Catchment')
        self.catchment_frame.grid(row = 2, column = 0, padx = 5, pady = 5)
        self.catchment_var = tk.StringVar()
        self.catchment_values = {'Low': 1, 'Medium': 5, 'High': 10}
        self.catchment_var.set(self.catchment_values['Medium'])

        for col, val in enumerate(self.catchment_values.keys()):

            button = ttk.Radiobutton(self.catchment_frame,
                text=val,
                value=self.catchment_values[val],
                variable=self.catchment_var)
            button.grid(column=col, row=0, padx=5)


        # Infectiousness of pathogen chooser
        self.infectiousness_frame = ttk.LabelFrame(self.pathogen_frame, text='Infectiousness')
        self.infectiousness_frame.grid(row = 3, column = 0, padx = 5, pady = 5)
        self.infectiousness_var = tk.StringVar()
        self.infectiousness_values = {'Low': 0.03, 'Medium': 0.1, 'High': 0.25}
        self.infectiousness_var.set(self.infectiousness_values['Medium'])

        for col, val in enumerate(self.infectiousness_values.keys()):

            button = ttk.Radiobutton(self.infectiousness_frame,
                text=val,
                value=self.infectiousness_values[val],
                variable=self.infectiousness_var)
            button.grid(column=col, row=0, padx=5)


        self.mitigation_frame = ttk.LabelFrame(self.column0, text = 'Mitigations')
        self.mitigation_frame.pack(padx = 5, pady= 5)

        # Migration chance chooser
        self.migrations_frame = ttk.LabelFrame(self.mitigation_frame, text='Migrations')
        self.migrations_frame.grid(row= 0, column= 0, padx= 5, pady= 5)
        self.migrations_var = tk.StringVar()
        self.migrations_values = {'Low': 0.01, 'Medium': 0.1, 'High': 0.25}
        self.migrations_var.set(self.migrations_values['Medium'])

        for col, val in enumerate(self.migrations_values.keys()):

            button = ttk.Radiobutton(self.migrations_frame,
                text=val,
                value=self.migrations_values[val],
                variable=self.migrations_var)
            button.grid(column=col, row=0, padx=5)


        # Move chance chance chooser
        self.movements_frame = ttk.LabelFrame(self.mitigation_frame, text='Movement Chance')
        self.movements_frame.grid(row= 1, column= 0, padx= 5, pady= 5)
        self.movements_var = tk.StringVar()
        self.movements_values = {'Low': 0.01, 'Medium': 0.05, 'High': 0.15}
        self.movements_var.set(self.movements_values['Medium'])

        for col, val in enumerate(self.movements_values.keys()):

            button = ttk.Radiobutton(self.movements_frame,
                text=val,
                value=self.movements_values[val],
                variable=self.movements_var)
            button.grid(column=col, row=0, padx=5)

        self.population_frame = ttk.LabelFrame(self.column1, text = 'Population Size')
        self.population_frame.pack(side= tk.TOP, padx= 5, pady= 5)

        self.population_slider = ttk.Scale(self.population_frame, from_ = 1, to = 2000, orient = 'horizontal', command=lambda _ :self.set_population_label())
        self.population_slider.set(1000)
        self.population_slider.grid(row = 0, column = 0, padx = 5, pady = 5)

        self.population_label = ttk.Label(self.population_frame, text = round(self.population_slider.get()))
        self.population_label.grid(row = 0, column = 1)


        self.layout_frame = ttk.LabelFrame(self.column1, text = 'Community Layout')
        self.layout_frame.pack(side= tk.TOP, padx = 5, pady = 10)

        self.row_frame = ttk.LabelFrame(self.layout_frame, text = 'Rows')
        self.row_frame.grid(row = 0, column = 0, padx = 5, pady = 5)

        self.row_slider = ttk.Scale(self.row_frame, from_ = 1, to = 8, orient = 'horizontal', command=lambda _ :self.set_row_label())
        self.row_slider.set(1)
        self.row_slider.grid(row = 0, column = 0, padx = 5, pady = 5)

        self.row_label = ttk.Label(self.row_frame, text = round(self.row_slider.get()))
        self.row_label.grid(row = 0, column = 1)

        self.col_frame = ttk.LabelFrame(self.layout_frame, text = 'Columns')
        self.col_frame.grid(row = 1, column = 0, padx = 5, pady = 5)

        self.col_slider = ttk.Scale(self.col_frame, from_ = 1, to = 8, orient = 'horizontal', command=lambda _ :self.set_column_label())
        self.col_slider.set(1)
        self.col_slider.grid(row = 0, column = 0, padx = 5, pady = 5)

        self.col_label = ttk.Label(self.col_frame, text = round(self.col_slider.get()))
        self.col_label.grid(row = 0, column = 1)

        self.save_button = ttk.Button(self, text='Save', command=lambda:self.save())
        self.save_button.grid(row = 2, column = 0, pady = 5)

        self.exit_button = ttk.Button(self, text='Exit', command=lambda:self.exit())
        self.exit_button.grid(row = 2, column = 1)


    def set_row_label(self):

        self.row_label = ttk.Label(self.row_frame, text = round(self.row_slider.get()))
        self.row_label.grid(row = 0, column = 1)


    def set_column_label(self):

        self.col_label = ttk.Label(self.col_frame, text = round(self.col_slider.get()))
        self.col_label.grid(row = 0, column = 1)


    def set_population_label(self):

        self.population_label = ttk.Label(self.population_frame, text = round(self.population_slider.get()))
        self.population_label.grid(row = 0, column = 1)


    def save(self):

        self.config['app']['theme'] = str(self.theme_var.get())

        self.config['pathogen']['lethality'] = float(self.lethality_var.get())
        self.config['pathogen']['curability'] = float(self.curability_var.get())
        self.config['pathogen']['catchment'] = float(self.catchment_var.get())
        self.config['pathogen']['catchment'] = float(self.catchment_var.get())

        self.config['simulation']['migration_chance'] = float(self.migrations_var.get())
        self.config['simulation']['move_chance'] = float(self.movements_var.get())

        population_size = round(self.population_slider.get())
        rows = round(self.row_slider.get())
        cols = round(self.col_slider.get())

        community_size = population_size // (rows * cols)
        remainder = population_size  % (rows * cols)

        layout = []
        places_choice =  [0, 1, 2, 3]
        places_weights = [0.4, 0.4, 0.15, 0.05]

        for row in range(rows):
            row_layout = []
            for community in range(cols):

                num_places = np.random.choice(places_choice, p=places_weights)
                row_layout.append([int(community_size), int(num_places)])

            layout.append(row_layout)

        layout[0][0][0] += remainder

        self.config['simulation']['community_layout'] = layout
        self.config['simulation']['total_population'] = population_size
        self.config['simulation']['susceptible'] = population_size

        with open(self.config_addr, 'w') as config_file:
            config_file.write(json.dumps(self.config))

    def exit(self):
        self.save()
        self.destroy()


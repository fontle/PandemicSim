# Author: Isaac Beight-Welland
# A simple pandemic simulation created in pygame.
# Made for AQA A level Computer Science NEA 2021/22
# pylint: disable=E1101 
import pygame, json, random, time
from dataclasses import dataclass
pygame.font.init()

with open('config.json', 'r') as config_file:
    config = json.loads(config_file.read())

sim_vars = config['simulation'] 
theme = config['theme'][config['app']['theme']]
class Pathogen:

    '''
    Purpose: Class that contains methods for characteristics 
    of pathogen spread.
    '''

    def __init__(self, catchment, infectiousness) -> None:

        self.catchment = catchment # Manhattan Distance Person has to be from other to get infected
        self.infectiousness = infectiousness # Chance person will get infected from other person
        self.lethality = 0.01 # Probabiliy will kill every cycle self.severity = 0.005 # The rate at which lethality changes every cycle
        self.curability = 0.002 # The chance of someone being cured from the disease every cycle


    def infect(self, susceptible, infected) -> None: 
        '''
        Purpose: Given two people who have been in contact;
        returns whether the infected person infects the other 'person'
        Arguments: 
            susceptible: Person()
            infected: Person()
        '''

        if susceptible.infected == True: 
            return

        sx, sy = susceptible.coords
        ix, iy = infected.coords

        if random.random() < self.infectiousness:

            if abs(sx - ix) <= self.catchment and abs(sy - iy) <= self.catchment:
                
                susceptible.infect()


@dataclass
class Render:

    def __alpha_rect(self, surf: pygame.Surface, colour: tuple, rect: tuple) -> None:
        '''
        Creates a rectangle with transparent colour.

        Args:
            surf: pygame.Surface
            colour: (r, g, b, a)
            rect: (x, y, width, height)

        '''

        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, colour, shape_surf.get_rect())
        surf.blit(shape_surf, rect)

    """ 
    def __alpha_circle(self, surf: pygame.Surface, colour: tuple, center: tuple, radius: int) -> None:
        '''
        Creates a circle with transparent colour.

        Args:
            surf: pygame.Surface
            colour: (r, g, b, a)
            center: (x, y)
            radius: int
        '''

        target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.circle(shape_surf, colour, (radius, radius), radius)
        surf.blit(shape_surf, target_rect)

    """

    def __alpha_polygon(self, surf: pygame.Surface, colour: tuple, points: tuple) -> None:
        '''
        Creates transparent polygon with defined number of points.

        Arguments:
            surf: pygame.Surface
            colour: (r, g, b, a)
            points: ((x1, y1), (x2, y2), (x3, y3) ... )
        '''

        lx, ly = zip(*points)
        min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)

        target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.polygon(shape_surf, colour, [(x - min_x, y - min_y) for x, y in points])
        surf.blit(shape_surf, target_rect)


    def normal_speed_symbol(self, surf: pygame.Surface) -> None:
        '''
        Renders normal speed symbol on top left of surface provided.

        Args: 
            surf: pygame.Surface 
        '''
        self.__alpha_polygon(surf, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))
        self.__alpha_polygon(surf, (255, 255, 255, 100), ((30, 10), (50, 20), (30, 30)))


    def fast_symbol(self, surf: pygame.Surface) -> None:
        '''
        Renders fast speed symbol on top left surface provided.

        Args:
            surf: pygame.Surface
        '''
        self.__alpha_polygon(surf, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))
        self.__alpha_polygon(surf, (255, 255, 255, 100), ((30, 10), (50, 20), (30, 30)))
        self.__alpha_polygon(surf, (255, 255, 255, 100), ((50, 10), (70, 20), (50, 30)))


    def slow_symbol(self, surf: pygame.Surface) -> None:
        '''
        Renders slow speed symbol on top left surface provided.

        Args: 
            surf: pygame.Surface
        '''
        self.__alpha_polygon(surf, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))
        

    def pause_symbol(self, surf: pygame.Surface) -> None:
        '''
        Renders slow speed symbol on top left surf provided.

        Args: 
            surf: pygame.Surface
        '''
        width = surf.get_rect().width
        self.__alpha_rect(surf, (180, 180, 180, 4),(width- 20, 10, 10, 30))
        self.__alpha_rect(surf, (180, 180, 180, 4),(width - 37, 10, 10, 30))


class Graph:
    
    '''
    Class that handles graphs in the simulation, capable of line graphs only.

    Args:
        size: (x, y)
        font: pygame.font.SysFont()
        theme: dict that defines the colour palette
        title: str that is shown as caption to graph

    '''

    def __init__(self, size: tuple[int, int], font:pygame.font.SysFont, lines: int, title = ''):

        global theme 

        # Initialise vars
        self.surf = pygame.Surface((size))
        self.font = font
        # Render title in initialisation as will never change
        self.title = self.font.render(title, True, theme['susceptible'])
        # Format dimensions of frame
        self.width, self.height = size
        self.n_buff = self.height // 10

        # Puts graph in line with simulation as uses same buff as community 
        sim_size = config['app']['sim_size']    
        sim_width, sim_height = sim_size
        layout = sim_vars['community_layout']
        self.s_buff = sim_height/(len(layout)*10)

        self.w_buff = 0 
        self.e_buff = self.width // 10
        # Create values to be plotted
        
        self.values = [[] for _ in range(lines)]


    def plot(self, value) -> None:
        '''
        Add values to be plotted to the graph; the value parameter is a multi-dimensional
        array corresponding to the number of lines on the graph. 

        Must have a value for every line, if no new value added to a line, specify with [].

        Args: 
            value: list[list, ...]  
        '''

        for i in range(len(self.values)): 
            self.values[i] += [value[i]]

    def draw(self, *, maximum = 0) -> None:
        '''
        Draws graph and its values onto surface.

        Args:
            maximum: integer, sets the maximum value of the y-axis (optional)
        '''

        global theme 

        self.surf.fill(theme['app_background'])
        self.surf.blit(self.title, (self.w_buff, self.height-self.s_buff))

        # Set maximum value of y-scale
        if maximum == 0:
            # If maximum value not provided then set the highest value in plots as y_max
            self.y_max = max([max(val) for val in self.values if len(val) > 0])

        else: # Max value provided
            self.y_max = maximum

        # Render vertical axis on surface
        self.y_axis = pygame.draw.line(
                self.surf,
                theme['susceptible'],
                (self.w_buff, self.n_buff),
                (self.w_buff, self.height-self.s_buff),
                width=2)

        # The number of pixels between used to delimit the y_axis
        self.y_scale = (self.height-self.n_buff - self.s_buff)/self.y_max

        # Render horizontal axis on surface
        self.x_axis = pygame.draw.line(
            self.surf,
            theme['susceptible'],
            (self.w_buff, self.height - self.s_buff),
            (self.width-self.e_buff, self.height-self.s_buff),
            width=2)

        # The maximum x value of both lines
        self.x_max = max([len(line) for line in self.values])
        # The number of pixels rendered between each item in the list 
        self.x_scale = (self.width-self.e_buff-self.w_buff)/self.x_max

        # Plot points for each line
        for line in self.values:

            x_last = round(self.w_buff + (self.x_scale / 2))
            y_last = round((self.height - self.s_buff) - (self.y_scale * line[0]))
            
            # Draw every plot for specified line
            for point_count, point in enumerate(line):

                x_pos = round(self.w_buff + (self.x_scale * point_count) + (self.x_scale / 2))
                y_pos = round((self.height - self.s_buff) - (self.y_scale * point))

                # Draws line between current and last position
                pygame.draw.line(
                    self.surf,
                    theme['infected'],
                    (x_last, y_last),
                    (x_pos, y_pos),
                    width=2)

                x_last, y_last = x_pos, y_pos

        # Memory management for number of items in values
        if self.x_scale <= 1: 
            for line in self.values: 
                del line[::60]


class Simulation:
    '''
    Controls the main pygame window, has Communnity instances as frames

    Args: 
        config: str path of config.json
    '''

    def __init__(self) -> None:

        global sim_vars, theme

        self.sim_size = (config['app']['sim_size'])
        self.sidebar_size = (config['app']['sidebar_width'], self.sim_size[1])
        self.botbar_size = (self.sim_size[0], config['app']['bar_height'])
        self.controls_size = (config['app']['sidebar_width'], config['app']['bar_height'])
        self.pathogen = Pathogen(5, 1)
        self.communities = self.__calculate_communities()


    def __calculate_communities(self) -> list:
        '''
        Initialises communities according to config file. 

        Returns: 
            list of community objects.
        '''
        communities = []
        sim_width, sim_height = self.sim_size
        layout = sim_vars['community_layout']
        self.y_buffer = sim_height/(len(layout)*10) # The pixels between each row of communities
        height = round((sim_height - (self.y_buffer*(len(layout)+1))) / len(layout))

        # Create each community in grid defined by layout
        for y, cols in enumerate(layout): # y counts how many rows in
            x_buffer = sim_width/(cols*10) # The pixels between each column of communities
            # Round to prevent floating error when dividing
            width = round((sim_width - (x_buffer*(cols+1))) / cols)
            for x in range(cols): # x counts how many columns in
                # Round do prevent float error when dividing
                coords = round((x*(width+x_buffer)+x_buffer)), round(y*(height+self.y_buffer)+self.y_buffer)
                communities.append(Community(coords, (width, height), self.pathogen))

        return communities


    def __pause(self) -> None:
        '''
        Handles the pause state of the simulation.
        '''
        paused = True
        while paused:

            # Render Pause bars
            self.render.pause_symbol(self.window)
            # Event handling for pause menu
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    paused = False
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False

            pygame.display.update()


    def __speed_up(self) -> None:
        pass


    def __slow_down(self) -> None:
        pass


    def __render_sidebar(self) -> None:
        '''
        Controls the rendering of the sidebar in pygame window.
        '''
        infected_label = self.font.render(f'Infected:{sim_vars["infected"]}', True, theme['infected'])
        susceptible_label = self.font.render(f'Susceptible:{sim_vars["susceptible"]}', True, theme['susceptible'])

        self.sidebar_surf.blit(susceptible_label, (0, self.y_buffer))
        self.sidebar_surf.blit(infected_label, (0, self.y_buffer + self.font_size * 1.25))


    def __render_graph(self) -> None:
        '''
        Controls the rendering and updating of the graph object in sidebar. 
        '''
        self.graph.plot([sim_vars['infected'], sim_vars['susceptible']])
        self.graph.draw(maximum=sim_vars['total_population'])
        self.sidebar_surf.blit(self.graph.surf, (0, self.sim_size[1]//2))


    def run(self) -> None:

        '''
        Instantiates pygame window and starts the simulation. 
        '''

        # Create application size defined by config json
        window_size = (self.sim_size[0] + self.sidebar_size[0], self.sim_size[1] + self.botbar_size[1])
        self.window = pygame.display.set_mode(window_size)
        self.render = Render() # Create render methods for standard symbols

        # Create GUI layout
        self.sim_surf= pygame.Surface(self.sim_size)
        self.sidebar_surf = pygame.Surface(self.sidebar_size)
        self.botbar_surf = pygame.Surface(self.botbar_size)
        self.controls_surf = pygame.Surface(self.controls_size)

        # Font Initialisation
        self.font_size = self.sidebar_size[1] // 25
        self.font = pygame.font.SysFont('Calibri', self.font_size)

        # Create graph to be rendered in sidebar
        self.graph = Graph((self.sidebar_size[0], self.sim_size[1]//2), self.font, 2)

        bgcolor = theme['app_background']
        self.running = True
        while self.running:
            
            # Fill backgrounds for re-rendering
            self.sim_surf.fill(bgcolor) 
            self.sidebar_surf.fill(bgcolor) 
            self.controls_surf.fill(bgcolor)
            self.botbar_surf.fill(bgcolor)

            # Update info
            self.__render_sidebar()
            self.__render_graph()

            # Render the canvas of each community and update
            for community in self.communities:
                
                # Perform migration event calculation and migrate people to new communities
                persons_migrated = community.calculate_migrations()

                for person in persons_migrated:
                    new_community = random.choice([c for c in self.communities if c != community])
                    community.population.remove(person)
                    old_coords = [a + b for (a, b) in zip(person.coords, community.coords)]
                    person.set_random_location()
                    new_coords = [a + b for (a, b) in zip(person.coords, community.coords)]
                    pygame.draw.line(self.sim_surf, (255,255,255), old_coords, new_coords,10) 
                    new_community.population.add(person)
    
                community.calculate_infected()
                community.surf.fill(theme['community_background'])
                community.population.draw(community.surf)
                community.population.update()

                self.sim_surf.blit(community.surf, community.coords)

            for event in pygame.event.get():

                # User closed window -> quit application
                if event.type == pygame.QUIT:
                    self.running = False
                # User pressed key -> perform related event
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False
                    if event.key == pygame.K_p:
                        self.__pause()

            # Render all frames to main window
            self.window.blit(self.sim_surf, (0, 0))
            self.window.blit(self.sidebar_surf, (self.sim_size[0], 0))
            self.window.blit(self.controls_surf, (self.sim_size))
            self.window.blit(self.botbar_surf, (0, self.sim_size[1]))
            # Update display
            pygame.display.update()
            time.sleep(0.02)


class Person(pygame.sprite.Sprite):

    def __init__(self, community_size) -> None:

        global sim_vars, theme

        # Initialise sprite to allow rendering
        pygame.sprite.Sprite.__init__(self)

        # Simulation variables
        self.community_size = community_size

        # Person size and surface to be rendered
        self.size = (5,5)
        self.image = pygame.Surface(self.size)
        self.image.fill(theme['susceptible'])

        # Person location
        self.rect = self.image.get_rect()
        self.set_random_location()
        # Person behaviour variables
        self.movement = 2
        self.infected = False


    def infect(self):
        '''
        Infects a person
        '''
        self.infected = True
        self.image.fill(theme['infected'])
        sim_vars['infected'] += 1
        sim_vars['susceptible'] -= 1 

    def set_random_location(self): 
        '''
        Move person to random location in commmunity
        '''
        self.rect.x = random.randint(1,self.community_size[0] - self.size[0])
        self.rect.y = random.randint(1,self.community_size[1] - self.size[1])
        self.coords = self.rect.x, self.rect.y 


    def update(self):
        '''
        Controls movement of the person.
        '''
        new_x = eval(f'{self.rect.x}{random.choice(["+", "-"])}{self.movement}')
        new_y = eval(f'{self.rect.y}{random.choice(["+", "-"])}{self.movement}')
        max_x, max_y = self.community_size
        width, height = self.size
        valid_x, valid_y  = max_x - width, max_y - height
        # If new x coord out of range
        if new_x < 0:
            new_x = 0
        elif new_x > valid_x:
            new_x = valid_x
        # If new y coord out of range
        if new_y < 0:
            new_y = 0
        elif new_y > valid_y:
            new_y = valid_y
        # Coordinates definitely in range
        self.rect.x = new_x
        self.rect.y = new_y
        self.coords = self.rect.x, self.rect.y 


class Community:
    '''
    Is a pygame frame that sits encapsulated within simulation
    '''

    def __init__(self, coords, surf_size, pathogen) -> None:

        global sim_vars, theme

        self.coords = coords
        self.surf_size = surf_size
        self.surf = pygame.Surface(self.surf_size)
        
        self.pathogen = pathogen
        # Create list of people in the community
        self.population = pygame.sprite.Group()
        self.infected = []
        self.susceptible = []

        for _ in range(sim_vars['community_size']):
            self.population.add(Person(self.surf_size))


    def calculate_infected(self):
        '''
        Infects (calls method from Pathogen) every person in proximity
        to an infected person in the community
        '''

        population_list = self.population.sprites()
        infected = [person for person in population_list if person.infected == True]
        susceptible = [person for person in population_list if person not in infected]

        # zombie refering to infected person 
        for zombie in infected: 
            for person in susceptible:
                self.pathogen.infect(person, zombie)

    def calculate_migrations(self): 
        '''
        Manages whether events such as migration occurs.
        '''
        mig_chance = 0.15
        
        # If migration event occurs, ensure at least one person migrates

        if mig_chance < random.random():
            yield random.choice(self.population.sprites())
            # Subsequent people have less and less chance of migrating
            while random.random() < mig_chance:
                yield random.choice(self.population.sprites())
        # If not migration occurs, return empty tuple 
        else: 
            return () 

    
class Test:
    
    class Simulation:

        def run(self):
            # Tests __init__ of simulation class
            simulation = Simulation()
            simulation.communities[0].population.sprites()[0].infect()
            simulation.run()

if __name__ == '__main__':
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        Test.Simulation().run()

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()


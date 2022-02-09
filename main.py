# Author: Isaac Beight-Welland 
# A simple pandemic simulation created in pygame. 
# Made for AQA A level Computer Science NEA 2021/22
import pygame, json, os, render, random, time

pygame.init()
pygame.font.init()

class Pathogen:
    '''
    Purpose: Class that contains methods for characteristics of pathogen spread
    '''

    def __init__(self) -> None:
        pass 


    def infect(self, person, infected) -> bool:
        '''
        Purpose: Given two people who have been in contact;
        returns whether the infected person infects the other 'person'
        ''' 
        pass


class Mitigations:
    '''
    Purpose: Class that contains methods for characteristics of mitigations against
    pathogen spread
    '''
    
    def __init__(self):
        pass

class Render:

    def __alpha_rect(surface: pygame.Surface, colour: tuple, rect: tuple):
        '''
        Creates a rectangle with transparent colour.
        Arguments:
            colour: (r, g, b, a)
            rect: (x, y, width, height)
        '''

        shape_surface = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surface, colour, shape_surface.get_rect())
        surface.blit(shape_surface, rect)


    def __alpha_circle(surface: pygame.Surface, colour: tuple, center: tuple, radius: int):
        '''
        Creates a circle with transparent colour.

        Arguments: 
            colour -- (r, g, b, a)
            center -- (x, y)
        '''

        target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.circle(shape_surf, colour, (radius, radius), radius)
        surface.blit(shape_surf, target_rect)


    def __alpha_polygon(surface: str, colour: tuple, points: tuple):
        '''
        Creates transparent polygon with defined number of points.

        Arguments:
            colour -- (r, g, b, a)
            points -- ((x1, y1), (x2, y2), (x3, y3) ... )
        '''

        lx, ly = zip(*points)
        min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)

        target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.polygon(shape_surf, colour, [
                            (x - min_x, y - min_y) for x, y in points])
        surface.blit(shape_surf, target_rect)


    def normal_speed_symbol(surface: pygame.Surface):
        '''
        Renders normal speed symbol on top left of surface provided.
        '''
        __alpha_polygon(surface, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))
        __alpha_polygon(surface, (255, 255, 255, 100), ((30, 10), (50, 20), (30, 30)))


    def fast_symbol(surface: pygame.Surface):
        '''
        Renders fast speed symbol on top left surface provided.
        '''
        __alpha_polygon(surface, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))
        __alpha_polygon(surface, (255, 255, 255, 100), ((30, 10), (50, 20), (30, 30)))
        __alpha_polygon(surface, (255, 255, 255, 100), ((50, 10), (70, 20), (50, 30)))


    def slow_symbol(surface: pygame.Surface):
        '''
        Renders slow speed symbol on top left surface provided.
        '''
        __alpha_polygon(surface, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))



class Graph(pygame.Surface):

    def __init__(self, size: tuple[int, int], font:int, theme:dict, title = ''):
        
        # Initialise vars 
        self.surf = pygame.Surface((size))
        self.theme = theme
        self.font = font
        # Render title in initialisation as will never change 
        self.title = self.font.render(title, True, self.theme['susceptible'])
        # Format dimensions of frame
        self.width, self.height = size 
        self.n_buff = self.height // 10
        # South buffer must be large to accommodate for title 
        self.s_buff = self.height // 8
        self.w_buff = self.width // 10
        self.e_buff = self.width // 10
        # Create values to be plotted 
        self.values = []


    def plot(self, value, line=0): 
        '''Purpose: Takes single value or multiple, adds to values plotted by draw.'''
        print(value)
        if type(value) is int:
            self.values.append([value])
        elif type(value) is list:
            
            if type(value[0]) is int:
                self.values += [values] 
            elif type(value[0]) is list:
                for i in range(len(value)):
                    try: 
                        self.values[i] += value[i]
                    except IndexError: # Haven't added points to this line yet
                        self.values.append(value[i])
        else:
            raise AttributeError('Received unexpected type when plotting to graph.')
        print(self.values)


    def draw(self, *, maximum = 0):
        '''
        Purpose: Draws graph and its values onto surface
        '''
        self.surf.fill(self.theme['app_background'])
        self.surf.blit(self.title, (self.w_buff, self.height-self.s_buff))

        # Set maximum value of y-scale
        if maximum == 0:
            # If maximum value not provided then set the highest value in plots as y_max
            self.y_max = max([max(val) for val in self.values if len(val) > 0])
            
        else: # Max value provided
            self.y_max = maximum 

        self.y_axis = pygame.draw.line(
                self.surf,
                self.theme['susceptible'],
                (self.w_buff, self.n_buff),
                (self.w_buff, self.height-self.s_buff), 
                width=2)
        
        self.y_scale = (self.height-self.n_buff - self.s_buff)/self.y_max

        self.x_axis = pygame.draw.line(
            self.surf,
            self.theme['susceptible'],  
            (self.w_buff, self.height - self.s_buff), 
            (self.width-self.e_buff, self.height-self.s_buff), 
            width=2)

        self.x_max = max([len(line) for line in self.values])
        self.x_scale = (self.width-self.e_buff-self.w_buff)/self.x_max
        
        # Decreases the values to be rendered, when the length of values greater than width of graph area
        if self.x_scale <= 1:

            # Deletes every 20 items from each line, increasing x_scale to a point greater than 1 
            for line in range(len(self.values)):
                del self.values[line][::20]

        # Plot points for each line
        for line_count, line in enumerate(self.values):

            x_last = round(self.w_buff + (self.x_scale / 2))
            y_last = round((self.height - self.s_buff) - (self.y_scale * line[0]))

            for point_count, point in enumerate(line):
                
                x_pos = round(self.w_buff + (self.x_scale * point_count) + (self.x_scale / 2))
                y_pos = round((self.height - self.s_buff) - (self.y_scale * point))

                # Draws line between current and last position
                pygame.draw.line(
                    self.surf, 
                    self.theme['infected'], 
                    (x_last, y_last), 
                    (x_pos, y_pos), 
                    width=4
                    )

                x_last, y_last = x_pos, y_pos


class Simulation: 
    '''
    Purpose: Controls the main pygame window, has Communnity instances as frames 
    '''

    def __init__(self, config:str) -> None:

        with open(config, 'r') as config_file:
            config = json.loads(config_file.read())

        self.sim_size = (config['app']['sim_size'])
        self.sidebar_size = (config['app']['sidebar_width'], self.sim_size[1])
        self.botbar_size = (self.sim_size[0], config['app']['bar_height']) 
        self.controls_size = (config['app']['sidebar_width'], config['app']['bar_height']) 
        self.theme = config['theme'][config['app']['theme']]
        self.sim_vars = config['simulation']    
        self.communities = self.calculate_communities()
   

    def calculate_communities(self) -> list:

        communities = []
        sim_width, sim_height = self.sim_size
        layout = self.sim_vars['community_layout'] 
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
                communities.append(Community(coords, (width, height), self.sim_vars, self.theme))
                
        return communities


    def __pause(self) -> None:
        pass


    def __speed_up(self) -> None:
        pass


    def __slow_down(self) -> None:
        pass 


    def __render_sidebar(self) -> None:
        '''
        !Warning: This method is PRIVATE and should only be called by the Simulation.run method!

        Purpose: Controls the rendering of the sidebar in pygame window. 
        '''
        infected_label = self.font.render(f'Infected:{10}', True, self.theme['infected'])
        susceptible_label = self.font.render(f'Susceptible:{10}', True, self.theme['susceptible'])
     
        self.sidebar_surf.blit(susceptible_label, (0, self.y_buffer))
        self.sidebar_surf.blit(infected_label, (0, self.y_buffer + self.font_size * 1.25)) 

    def __render_graph(self) -> None:
        self.graph.draw()
        self.sidebar_surf.blit(self.graph.surf, (0, self.sim_size[1]//2))

    def run(self) -> None:
        
        # Create application size defined by config json
        window_size = (self.sim_size[0] + self.sidebar_size[0], self.sim_size[1] + self.botbar_size[1])
        self.window = pygame.display.set_mode(window_size)
        self.sim_surf= pygame.Surface(self.sim_size)
        self.sidebar_surf = pygame.Surface(self.sidebar_size)
        self.botbar_surf = pygame.Surface(self.botbar_size)
        self.controls_surf = pygame.Surface(self.controls_size)
        self.running = True
        bgcolor = self.theme['app_background'] 
        # Font Initialisation
        self.font_size = self.sidebar_size[1] // 25 
        self.font = pygame.font.SysFont('Calibri', self.font_size)
        # Create graph to be rendered in sidebar
        self.graph = Graph((self.sidebar_size[0], self.sim_size[1]//2), self.font, self.theme)
        self.graph.plot([[1,2,3,4,5], [5,4,3,2,1]])
        
        while self.running:
            
            self.sim_surf.fill(bgcolor) # Fill background            
            self.sidebar_surf.fill(bgcolor) # Fill background            
            self.controls_surf.fill(bgcolor)
            self.botbar_surf.fill(bgcolor)

            self.__render_sidebar()
            self.__render_graph()

            # Render the canvas of each community and update
            for community in self.communities:
                community.update()
                self.sim_surf.blit(community.surface, community.coords)

            for event in pygame.event.get():
                # User closed window -> quit application
                if event.type == pygame.QUIT: 
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False

            self.window.blit(self.sim_surf, (0, 0))
            self.window.blit(self.sidebar_surf, (self.sim_size[0], 0))
            self.window.blit(self.controls_surf, (self.sim_size))
            self.window.blit(self.botbar_surf, (0, self.sim_size[1]))
            pygame.display.update() 
            time.sleep(0.02)
             

class Community():
    '''
    Is a pygame frame that sits encapsulated within simulation
    '''
        
    def __init__(self, coords, surface_size, sim_vars, theme) -> None:

        self.coords = coords 
        self.surface_size = surface_size
        self.surface = pygame.Surface(self.surface_size)
        self.sim_vars = sim_vars
        self.theme = theme 
        # Create list of people in the community 
        self.population = pygame.sprite.Group()

        for person in range(self.sim_vars['community_size']):
            self.population.add(Person(self.surface_size, self.sim_vars, self.theme))

    def calculate_infected(self):
        pass


    def update(self) -> None:

        self.surface.fill(self.theme['community_background'])
        self.population.draw(self.surface)
        self.population.update()


class Person(pygame.sprite.Sprite):

    def __init__(self, community_size, sim_vars, theme) -> None:

        # Initialise sprite to allow rendering
        pygame.sprite.Sprite.__init__(self)

        # Simulation variables 
        self.community_size = community_size
        self.sim_vars = sim_vars 
        self.theme = theme

        # Person size and surface to be rendered 
        self.size = (5,5)
        self.image = pygame.Surface(self.size) 
        self.image.fill(self.theme['susceptible']) 

        # Person location 
        self.rect = self.image.get_rect() 
        self.rect.x = random.randint(1,self.community_size[0] - self.size[0])
        self.rect.y = random.randint(1,self.community_size[1] - self.size[1])

        # Person behaviour variables
        self.movement = 2  
        self.infected = False


    def infect(self):
        '''
        Infects a person
        '''
        self.infected = True
        self.image.fill(self.theme['infected'])


    def __update_animation(self):
        pass 


    def __update_movement(self):
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
    
    def update(self):

        self.__update_movement()
        self.__update_animation()
   

class Test:

    class Simulation:

        def init():
            # Tests __init__ of simulation class 
            simulation = Simulation(os.getcwd()+'\\config.json')
            simulation.run() 

if __name__ == '__main__':
    Test.Simulation.init()

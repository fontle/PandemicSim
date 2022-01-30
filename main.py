
import pygame, json, os, render, random, time

class Pathogen:
    '''
    Class that contains methods for characteristics of pathogen spread
    '''

    def __init__(self) -> None:
        pass 


    def infect(self, personn, infected) -> bool:
        '''
        Given two people who have been in contact;
        returns whether the infected person infects the other 'person'
        ''' 
        pass


class Mitigations:
    '''
    Class that contains methods for characteristics of mitigations against
    pathogen spread
    '''
    
    def __init__(self):
        pass


class Simulation: 
    '''
    Controls the main pygame window, has Communnity instances as frames 
    '''

    def __init__(self, config) -> None:

        with open(config, 'r') as config_file:
            config = json.loads(config_file.read())

        self.app_size = tuple(config['app']['window_size'])
        self.theme = config['theme'][config['app']['theme']]
        self.sim_vars = config['simulation']    
        self.communities = self.calculate_communities()
    
    def calculate_communities(self):
        communities = []
        app_width, app_height = self.app_size
        x_buffer = app_width/10 
        y_buffer = app_height/10
        layout = self.sim_vars['community_layout']
        height = app_height/len(layout)
        for y, cols in enumerate(layout):
            width = app_width/cols
            for x in range(cols):
                coords = (x*width+x_buffer, y*height+y_buffer) 
                communities.append(Community(coords, (width, height), self.sim_vars, self.theme))
        return communities

    def pause(self) -> None:
        pass


    def speed_up(self) -> None:
        pass


    def slow_down(self) -> None:
        pass 


    def render_info(self) -> None:
        pass


    def render_graph(self) -> None:
        pass


    def run(self) -> None:
        
        # Create application size defined by config json
        self.window = pygame.display.set_mode(self.app_size)
        self.running = True
        bgcolor = self.theme['app_background'] 

        while self.running:
            
            self.window.fill(bgcolor) # Fill background            

            # Render the canvas of each community and update
            for community in self.communities:
                community.update()
                self.window.blit(community.surface, community.coords)

            for event in pygame.event.get():
                # User closed window -> quit application
                if event.type == pygame.QUIT: 
                    self.running = False

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
            x = random.uniform(1,self.surface_size[0])
            y = random.uniform(1,self.surface_size[1])
            self.population.add(Person((x, y), self.sim_vars, self.theme))

    def calculate_infected(self):
        pass


    def update(self) -> None:

        self.surface.fill(self.theme['community_background'])
        print('1')
        self.population.draw(self.surface)
        self.population.update()


class Person(pygame.sprite.Sprite):

    def __init__(self, coords, sim_vars, theme=None) -> None:

        # If people will be rendered then a colour palette is required 
        if render and theme == None:
            raise AttributeError("No 'theme' attribute provided for person to use")

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((5,5)) # Set size of object that is rendered to window
        self.image.fill(theme['susceptible']) # Set background to colour of uninfected person
        self.rect = self.image.get_rect() # The rectangle object that controlls position of person 
        self.rect.x, self.rect.y = coords
        self.sim_vars = sim_vars # Get simulation variables from config.json  loaded in community
        self.movement = 2  

    def infect(self):
        '''
        Infects a person
        '''
        pass


    def update(self):
        '''
        Controls movement of person: is set to random wihout mitigations. 
        '''
        new_x = eval(f'{self.rect.x}{random.choice(["+", "-"])}{self.movement}')
        new_y = eval(f'{self.rect.y}{random.choice(["+", "-"])}{self.movement}')

        self.rect.x = new_x
        self.rect.y = new_y
   

class Test:

    class Simulation:

        def init():
            # Tests __init__ of simulation class 
            simulation = Simulation(os.getcwd()+'\\config.json')
            simulation.run() 

if __name__ == '__main__':
    Test.Simulation.init()

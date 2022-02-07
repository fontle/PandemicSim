# Author: Isaac Beight-Welland 
# A simple pandemic simulation created in pygame. 
# Made for AQA A level Computer Science NEA 2021/22
import pygame, json, os, render, random, time

pygame.init()
pygame.font.init()


class Pathogen:
    '''
    Class that contains methods for characteristics of pathogen spread
    '''

    def __init__(self) -> None:
        pass 


    def infect(self, person, infected) -> bool:
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

        self.sim_size = (config['app']['sim_size'])
        self.sidebar_size = (config['app']['sidebar_width'], self.sim_size[1])
        self.botbar_size = (self.sim_size[0], config['app']['bar_height']) 
        self.controls_size = (config['app']['sidebar_width'], config['app']['bar_height']) 
        self.theme = config['theme'][config['app']['theme']]
        self.sim_vars = config['simulation']    
        self.communities = self.calculate_communities()
   
    def calculate_communities(self):

        communities = []
        sim_width, sim_height = self.sim_size
        layout = self.sim_vars['community_layout'] 
        y_buffer = sim_height/(len(layout)*10) # The pixels between each row of communities 
        height = round((sim_height - (y_buffer*(len(layout)+1))) / len(layout)) 

        # Create each community in grid defined by layout
        for y, cols in enumerate(layout): # y counts how many rows in 
            x_buffer = sim_width/(cols*10) # The pixels between each column of communities
            width = round((sim_width - (x_buffer*(cols+1))) / cols)  

            for x in range(cols): # x counts how many columns in 
                coords = round((x*(width+x_buffer)+x_buffer)), round(y*(height+y_buffer)+y_buffer) 
                communities.append(Community(coords, (width, height), self.sim_vars, self.theme))
                
        return communities

    def __pause(self) -> None:
        pass


    def __speed_up(self) -> None:
        pass


    def __slow_down(self) -> None:
        pass 


    def __render_info(self) -> None:

        infected_label = self.font.render(f'Infected:{10}', True, self.theme['susceptible'])
        susceptible_label = self.font.render(f'Susceptible:{10}', True, self.theme['susceptible'])
 

    def __render_graph(self) -> None:
        pass


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
        self.font = pygame.font.SysFont('Calibri', 20)

        while self.running:
            
            self.sim_surf.fill(bgcolor) # Fill background            
            self.sidebar_surf.fill(bgcolor) # Fill background            

            # Render the canvas of each community and update
            for community in self.communities:
                community.update()
                self.sim_surf.blit(community.surface, community.coords)

            for event in pygame.event.get():
                # User closed window -> quit application
                if event.type == pygame.QUIT: 
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

    def __init__(self, community_size, sim_vars, theme=None) -> None:

        # If people will be rendered then a colour palette is required 
        if render and theme == None:
            raise AttributeError("No 'theme' attribute provided for person to use")

        self.community_size = community_size
        pygame.sprite.Sprite.__init__(self)
        self.size = (5,5)
        self.image = pygame.Surface(self.size) # Set size of object that is rendered to window
        self.image.fill(theme['susceptible']) # Set background to colour of uninfected person
        self.rect = self.image.get_rect() # The rectangle object that controlls position of person 
        self.rect.x = random.randint(1,self.community_size[0] - self.size[0])
        self.rect.y = random.randint(1,self.community_size[1] - self.size[1])
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
    
   

class Test:

    class Simulation:

        def init():
            # Tests __init__ of simulation class 
            simulation = Simulation(os.getcwd()+'\\config.json')
            simulation.run() 

if __name__ == '__main__':
    Test.Simulation.init()

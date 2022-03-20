# Author: Isaac Beight-Welland
# A simple pandemic simulation created in pygame.
# Made for AQA A level Computer Science NEA 2021/22
# pylint: disable=E1101
import pygame, json, random, time, math, render, config

pygame.init()
pygame.font.init()

class Pathogen:

    '''
    Purpose: Class that contains methods for characteristics
    of pathogen spread.
    '''

    def __init__(self, catchment:float, curability:float, infectiousness:float, lethality:float ) -> None:

        # Manhattan Distance Person has to be from other to get infected
        self.catchment = catchment
        # Chance person will get infected from other person
        self.infectiousness = infectiousness
        # The probability infected would die every cycle
        self.lethality = lethality
        # The rate at which the probability of someone being cured from the disease increases every cycle
        self.curability = curability


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
        if infected.infected == False:
            return

        sx, sy = susceptible.coords
        ix, iy = infected.coords

        if random.random() < self.infectiousness:

            if abs(sx - ix) <= self.catchment and abs(sy - iy) <= self.catchment:
                susceptible.infect()


    def update_health(self, person):
        '''
        Calculates whether an infected person dies or is cured within a cycle.

        Arguments:
            person : Person()
        '''

        if random.random() < self.curability:
            person.cure(True)
            return

        else:
            person.cure_chance += self.curability

        if random.random() < self.lethality:

            person.kill()



class Graph:

    '''
    Class that handles graphs in the simulation, capable of line graphs only.

    Args:
        size: (x, y)
        font: pygame.font.SysFont()
        theme: dict that defines the colour palette
        title: str that is shown as caption to graph

    '''

    def __init__(self, size: tuple[int, int], font:pygame.font.SysFont, title = ''):

        global sim_vars, theme, pathogen

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
        self.values = {
            tuple(theme['infected']) : [sim_vars['infected']],
            tuple(theme['susceptible']) : [sim_vars['susceptible']],
            tuple(theme['dead']) : [sim_vars['dead']],
            tuple(theme['immune']) : [sim_vars['immune']]
        }

    def plot(self) -> None:
        '''
        Add values to be plotted to the graph; the value parameter is a multi-dimensional
        array corresponding to the number of lines on the graph.
        '''
        self.values[tuple(theme['infected'])].append(sim_vars['infected'])
        self.values[tuple(theme['susceptible'])].append(sim_vars['susceptible'])
        self.values[tuple(theme['dead'])].append(sim_vars['dead'])
        self.values[tuple(theme['immune'])].append(sim_vars['immune'])

    def __draw_axis(self):

        self.y_max = sim_vars['total_population']

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
        self.x_max = max([len(line) for line in self.values.values()])
        # The number of pixels rendered between each item in the list
        self.x_scale = (self.width-self.e_buff-self.w_buff)/self.x_max


    def __draw_plots(self):

        # Plot points for each line
        for (line_colour, line_values) in self.values.items():

            x_last = round(self.w_buff + (self.x_scale / 2))
            y_last = round((self.height - self.s_buff) - (self.y_scale * line_values[0]))

            # Draw every plot for specified line
            for point_count, point in enumerate(line_values):

                x_pos = round(self.w_buff + (self.x_scale * point_count) + (self.x_scale / 2))
                y_pos = round((self.height - self.s_buff) - (self.y_scale * point))

                # Draws line between current and last position
                pygame.draw.line(
                    self.surf,
                    line_colour,
                    (x_last, y_last),
                    (x_pos, y_pos),
                    width=2)

                x_last, y_last = x_pos, y_pos


    def draw(self) -> None:
        '''
        Draws graph and its values onto surface.

        Args:
            maximum: integer, sets the maximum value of the y-axis (optional)
        '''

        global theme

        self.surf.fill(theme['app_background'])
        self.surf.blit(self.title, (self.w_buff, self.height-self.s_buff))

        self.__draw_axis()
        self.__draw_plots()


class Simulation:
    '''
    Controls the main pygame window, has Communnity instances as frames

    Args:
        config: str path of config.json
    '''

    def __init__(self) -> None:

        global sim_vars, theme, pathogen

        self.sim_size = (config['app']['sim_size'])
        self.sidebar_size = (config['app']['sidebar_width'], self.sim_size[1])
        self.botbar_size = (self.sim_size[0], config['app']['bar_height'])
        self.controls_size = (config['app']['sidebar_width'], config['app']['bar_height'])
        self.communities = self.__calc_communities()

        # Create application size defined by config json
        window_size = (self.sim_size[0] + self.sidebar_size[0], self.sim_size[1] + self.botbar_size[1])
        self.window = pygame.display.set_mode(window_size)
        pygame.display.set_caption('Pandemic Simulation')
        pygame.display.set_icon(pygame.image.load('icon.png'))

        # Create GUI layout
        self.sim_surf= pygame.Surface(self.sim_size)
        self.sidebar_surf = pygame.Surface(self.sidebar_size)
        self.botbar_surf = pygame.Surface(self.botbar_size)
        self.controls_surf = pygame.Surface(self.controls_size)

        # Font Initialisation
        self.font_size = self.sidebar_size[1] // 25
        self.font = pygame.font.SysFont('Calibri', self.font_size)

        # Create graph to be rendered in sidebar
        self.graph = Graph((self.sidebar_size[0], self.sim_size[1]//2), self.font)

        self.delay = 0.016
        self.speed_states = {
            0.008 : render.fast_symbol,
            0.016: render.normal_speed_symbol,
            0.064: render.slow_symbol}

    def __calc_communities(self) -> list:
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
            x_buffer = sim_width/(len(cols)*10) # The pixels between each column of communities
            # Round to prevent floating error when dividing
            width = round((sim_width - (x_buffer*(len(cols)+1))) / len(cols))
            for x, (pop, places) in enumerate(cols): # x counts how many columns in
                # Round do prevent float error when dividing
                coords = round((x*(width+x_buffer)+x_buffer)), round(y*(height+self.y_buffer)+self.y_buffer)
                communities.append(Community(coords, (width, height), pop, places))

        return communities


    def __pause(self) -> None:
        '''
        Handles the pause state of the simulation.
        '''
        paused = True
        while paused:

            # Render Pause bars
            render.pause_symbol(self.window)

            # Event handling for pause menu
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    paused = False
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        paused = False
                    if event.key == pygame.K_p:
                        paused = False

            pygame.display.update()


    def __render_sidebar(self) -> None:
        '''
        Controls the rendering of the sidebar in pygame window.
        '''

        # Calculate R number
        try:
            r = round(1 + (sim_vars['susceptible'] - sim_vars['infected']) / sim_vars['old_infected'], 2)
        except ZeroDivisionError:
            r = 0
        sim_vars['old_infected'] = sim_vars['infected']

        # Update counter on label
        infected_label = self.font.render(f'Infected:{sim_vars["infected"]}', True, theme['infected'])
        susceptible_label = self.font.render(f'Susceptible:{sim_vars["susceptible"]}', True, theme['susceptible'])
        dead_label = self.font.render(f'Dead:{sim_vars["dead"]}', True, theme['dead'])
        immune_label = self.font.render(f'Immune:{sim_vars["immune"]}', True, theme['immune'])
        r_label = self.font.render(f'R:{r}', True, theme['r_label'])

        # Render changes to surface
        self.sidebar_surf.blit(susceptible_label, (0, self.y_buffer))
        self.sidebar_surf.blit(infected_label, (0, self.y_buffer + self.font_size * 1.25))
        self.sidebar_surf.blit(dead_label, (0,  self.y_buffer + self.font_size * 2.5))
        self.sidebar_surf.blit(immune_label, (0,  self.y_buffer + self.font_size * 3.75))
        self.sidebar_surf.blit(r_label, (0,  self.y_buffer + self.font_size * 5))

    def __render_graph(self) -> None:
        '''
        Controls the rendering and updating of the graph object in sidebar.
        '''

        # Update graph
        self.graph.plot()
        self.graph.draw()
        # Draw updated graph to application
        self.sidebar_surf.blit(self.graph.surf, (0, self.sim_size[1]//2))


    def run(self) -> None:
        '''
        Instantiates pygame window and starts the simulation.
        '''

        self.communities[0].population.sprites()[0].infect()
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

            # Update community and render
            for community in self.communities:

                community.surf.fill(theme['community_background'])

                # Update the population of the community (state and movement)
                community.update()

                # Calculate movements and routing to places
                community.calc_movement_events()
                # Perform migration event calculation and migrate people to new communities
                persons_migrated = community.calc_migration_events()

                # If there is only one community, do not go through with migration process
                valid = [x for x in self.communities if x is not community]
                if len(valid) > 0:

                    for person in persons_migrated:
                        # Migration can occur within a community (ie. Go-to someones house, or cross communities)
                        new_community = random.choice(valid)
                        community.population.remove(person)
                        person.set_random_location()
                        person.community_size = new_community.surf_size
                        new_community.population.add(person)

                # Render places to surface
                community.places.draw(community.surf)
                # Render population to the community surface
                community.population.draw(community.surf)
                # Render community surface to main window
                self.sim_surf.blit(community.surf, community.coords)

            # Event handler
            for event in pygame.event.get():

                # User closed window -> quit application
                if event.type == pygame.QUIT:
                    self.running = False
                # User pressed key -> perform related event
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_p:
                        self.__pause()
                    if event.key == pygame.K_LEFT:

                        if self.delay != 0.064:
                            self.delay = 0.064
                        else:
                            self.delay = 0.016

                    if event.key == pygame.K_RIGHT:

                        if self.delay != 0.008:
                            self.delay = 0.008
                        else:
                            self.delay = 0.016

            # Render all frames to main window
            self.window.blit(self.sim_surf, (0, 0))
            self.window.blit(self.sidebar_surf, (self.sim_size[0], 0))
            self.window.blit(self.controls_surf, (self.sim_size))
            self.window.blit(self.botbar_surf, (0, self.sim_size[1]))
            # Render speed symbol
            self.speed_states[self.delay](self.window)
            # Update display
            pygame.display.update()
            time.sleep(self.delay) # 60 updates a second



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
        self.dead = False
        self.immune = False
        self.infected = False
        self.cure_chance = 0
        self.despawn_time = 300 # Equivalent to 5s at 60hz

        # Route behaviour
        self.dest = None
        # How many cycles the person will stay at the destination
        self.stay_time = 100


    def kill(self):
        '''
        Kills the person from the Simulation
        '''

        # Guard checks to ensure person in killable
        if self.dead == True:
            return
        if self.infected == False:
            return

        # Update person vars
        self.dead = True
        self.infected = False
        self.cure_chance = 0
        self.immune = False
        self.image.fill(theme['dead'])

        # Update sim_vars
        sim_vars['dead'] += 1
        sim_vars['infected'] -= 1


    def infect(self):
        '''
        Infects a person.
        '''
        # Guard checks to ensure person is infectable
        if self.dead == True:
            return
        if self.immune == True:
            return

        self.infected = True
        self.image.fill(theme['infected'])

        sim_vars['infected'] += 1
        sim_vars['susceptible'] -= 1


    def cure(self, immune = False):
        '''
        Cures a person.
        '''
        # Guard checks to ensure person is curable
        if self.dead == True:
            return
        if self.infected == False:
            return

        # Update person state
        self.infected = False

        if immune:
            self.immune = True
            self.image.fill(theme['immune'])
        else:
            self.image.fill(theme['susceptible'])

        # Adjust global counters
        sim_vars['infected'] -= 1
        sim_vars['immune'] += 1


    def set_random_location(self) -> None:
        '''
        Move person to random location in commmunity
        '''
        self.rect.x = random.randint(1,self.community_size[0] - self.size[0])
        self.rect.y = random.randint(1,self.community_size[1] - self.size[1])
        self.coords = self.rect.x, self.rect.y


    def route(self, dest: tuple[int,int], set_home: bool) -> None:

        # Set a home which can be returned to
        if set_home == True:
            self.home = self.coords

        self.dest = dest

        x1, y1 = self.coords
        x2, y2 = self.dest

        i, j = x2 - x1, y2 - y1

        magnitude = math.sqrt(i**2 + j**2)

        try:
            # Vector on which person should move to the destination
            self.vector = (i*self.movement)/magnitude, (j*self.movement)/magnitude
        # Occurs when magnitude is so small float rounds to zero
        # This means person already next to the destination, so do not create route
        except ZeroDivisionError:
            self.dest = None


    def update(self) -> bool:
        '''
        Controls movement of the person.

        Returns -> boolean flag of whether to despawn person
        '''

        # Dead people can do anything so return
        if self.dead == True:
            if self.despawn_time == 0:
                return True
            else:
                self.despawn_time -= 1
                return False

        x,y = self.coords

        if self.dest == None:

            # New coordinates
            nx = eval(f'{x}{random.choice(["+", "-"])}{self.movement}')
            ny = eval(f'{y}{random.choice(["+", "-"])}{self.movement}')
            # Boundaries of community
            mx, my = self.community_size
            # Valid coordinates are the boundaries accounted for size of person
            w, h = self.size
            vx, vy  = mx - w, my - h

            # If new x coord out of range
            if nx < 0:
                nx = 0
            elif nx > vx:
                nx = vx

            # If new y coord out of range
            if ny < 0:
                ny = 0
            elif ny > vy:
                ny = vy

        else:

            # Person arrived at destination

            dx, dy = self.dest # Destination coords

            if abs(dx - x) < 10 and abs(dy - y) < 10:

                # If home doesnt exist and person at destination
                # then person has returned home
                try:
                    if self.stay_time == 0:

                        self.stay_time = 100
                        self.route(self.home, False)

                        del self.home

                    else:
                        self.stay_time -= 1

                except AttributeError:
                    self.dest = None
                    self.stay_time == 100

                nx, ny = dx, dy

            # Add vector to coords
            else:
                x, y = self.coords
                i, j = self.vector
                nx = x + i
                ny = y + j

        # Update position of rect on surface
        self.rect.x = round(nx)
        self.rect.y = round(ny)
        self.coords = nx, ny

        return False


class Place(pygame.sprite.Sprite):

    def __init__(self, community_size):

        global sim_vars, theme

        pygame.sprite.Sprite.__init__(self)

        self.size = (15, 15)
        self.image = pygame.Surface(self.size)
        self.image.fill(theme['place'])
        self.rect = self.image.get_rect()

        self.rect.x = random.randint(1,community_size[0] - self.size[0])
        self.rect.y = random.randint(1,community_size[1] - self.size[1])
        self.coords = (self.rect.x + self.size[0]/2, self.rect.y + self.size[1]/2)


class Community:
    '''
    Is a pygame frame that sits encapsulated within simulation
    '''

    def __init__(self, coords, surf_size, population, places) -> None:

        global sim_vars, theme, pathogen

        self.coords = coords
        self.surf_size = surf_size
        self.surf = pygame.Surface(self.surf_size)

        # Create list of people in the community
        self.population = pygame.sprite.Group()
        for _ in range(population):
            self.population.add(Person(self.surf_size))

        # Create places in community
        self.places = pygame.sprite.Group()

        for place in range(places):
            self.places.add(Place(self.surf_size))

    def update(self):
        '''
        Updates the state (dead, immune, susceptible, or infected)
        of people within the community.
        '''

        population_list = self.population.sprites()
        susceptible = []
        infected = []
        dead = []
        immune = []

        for person in population_list:

            despawn = person.update()

            if person.dead == True:

                dead.append(person)
                if despawn == True:
                    self.population.remove(person)

            elif person.infected == True:
                infected.append(person)

            elif person.immune == True:
                immune.append(person)

            else:
                susceptible.append(person)

            if person.dest != None:
                pygame.draw.line(self.surf, theme['route'], person.coords, person.dest)

        # zombie refering to infected person
        for zombie in infected:
           for person in susceptible:
                pathogen.infect(person, zombie)

           pathogen.update_health(zombie)


    def calc_movement_events(self):
        '''
        Manages whether a person heads to a place in a community
        '''
        if len(self.places) == 0:
            return

        move_chance = sim_vars['move_chance']

        def check(person):
            if person.dead == False and person.dest == None:
                return True

        valid = list(filter(check, self.population.sprites()))

        while (random.random() < move_chance) and len(valid) > 0:
            mover = random.choice(valid)
            mover.route(random.choice(self.places.sprites()).coords, True)
            valid.remove(mover)


    def calc_migration_events(self):
        '''
        Manages whether migrations occur.
        '''

        mig_chance = sim_vars['migration_chance']

        def check(person):
            if person.dead == False and person.dest == None:
                return True

        valid = list(filter(check, self.population.sprites()))

        migrants = []
        while (random.random() < mig_chance) and len(valid) > 0:
            migrant = random.choice(valid)
            migrants.append(migrant)

        return migrants


#def call_stack_statistics():
#
#    import cProfile
#    import pstats
#
#    with cProfile.Profile() as pr:
#        simulation = Simulation()
#        simulation.communities[0].population.sprites()[0].infect()
#        simulation.run()
#
#    stats = pstats.Stats(pr)
#    stats.sort_stats(pstats.SortKey.TIME)


if __name__ == '__main__':
    # User defines config_file

    config.Config().mainloop()

    # Load config and global vars
    with open('config.json', 'r') as config_file:
        config = json.loads(config_file.read())

    sim_vars = config['simulation']
    theme = config['theme'][config['app']['theme']]

    vars = config['pathogen']

    pathogen = Pathogen(
        vars['catchment'],
        vars['curability'],
        vars['infectiousness'],
        vars['lethality'])

    # Start simulation
    simulation = Simulation()
    simulation.run()


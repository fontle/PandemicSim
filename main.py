# Author: Isaac Beight-Welland
# A simple pandemic simulation created in pygame.
# Made for AQA A level Computer Science NEA 2021/22
import pygame, random, time, math, render, config

from dataclasses import dataclass

pygame.init()
pygame.font.init()

class Pathogen:

    '''
    Purpose: Class that contains methods for characteristics
    of pathogen spread.
    '''

    def __init__(self) -> None:

        # Manhattan Distance Person has to be from other to get infected
        self.catchment = config.pathogen.catchment
        # Chance person will get infected from other person
        self.infectiousness = config.pathogen.infectiousness
        # The probability infected would die every cycle
        self.lethality = config.pathogen.lethality
        # The rate at which the probability of someone being cured from the disease increases every cycle
        self.curability = config.pathogen.curability


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
            return
        else:
            person.death_chance += self.lethality


class Graph:

    '''
    Class that handles graphs in the simulation, capable of line graphs only.

    Args:
        size: (x, y)
        font: pygame.font.SysFont()
        title: str that is shown as caption to graph


    Window Constants:
            ^
            |                n_buff
            |
            |          |              /
            |          |    _________/
     height |  w_buff  |   /                e_buff
            |          |  /
            |          | /
            |          |___________________
            |
            ⌄                s_buff
            <------------------------------------------>
                              width
    '''

    def __init__(self, size: tuple[int, int], font:pygame.font.SysFont, title = ''):

        global stats, pathogen

        # Initialise Pygame Vars
        self.surf = pygame.Surface((size))
        self.font = font
        self.title = self.font.render(title, True, config.theme.susceptible)
        self.width, self.height = size

        # Create buffers for rendering
        self.n_buff = self.height // 10
        self.s_buff = config.app.sim_size[1]/(len(config.sim.layout)*10)
        self.w_buff = 0
        self.e_buff = self.width // 10

        # Create values to be plotted
        self.values = {
            tuple(config.theme.infected) : [stats.infected],
            tuple(config.theme.susceptible) : [stats.susceptible],
            tuple(config.theme.dead) : [stats.dead],
            tuple(config.theme.immune) : [stats.immune]
        }

    def plot(self) -> None:
        '''
        Add values to be plotted to the graph; the value parameter is a multi-dimensional
        array corresponding to the number of lines on the graph.
        '''
        self.values[tuple(config.theme.infected)].append(stats.infected)
        self.values[tuple(config.theme.susceptible)].append(stats.susceptible)
        self.values[tuple(config.theme.dead)].append(stats.dead)
        self.values[tuple(config.theme.immune)].append(stats.immune)


    def __draw_axis(self) -> None:

        self.y_max = config.sim.population

        # Render vertical axis on surface
        self.y_axis = pygame.draw.line(
                self.surf,
                config.theme.susceptible,
                (self.w_buff, self.n_buff),
                (self.w_buff, self.height-self.s_buff),
                width=2)

        # The number of pixels between used to delimit the y_axis
        self.y_scale = (self.height-self.n_buff - self.s_buff)/self.y_max

        # Render horizontal axis on surface
        self.x_axis = pygame.draw.line(
            self.surf,
            config.theme.susceptible,
            (self.w_buff, self.height - self.s_buff),
            (self.width-self.e_buff, self.height-self.s_buff),
            width=2)

        # The maximum x value of both lines
        self.x_max = max([len(line) for line in self.values.values()])
        # The number of pixels rendered between each item in the list
        self.x_scale = (self.width-self.e_buff-self.w_buff)/self.x_max


    def __draw_plots(self) -> None:

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
        '''

        self.surf.fill(config.theme.appbg)
        self.surf.blit(self.title, (self.w_buff, self.height-self.s_buff))

        self.__draw_axis()
        self.__draw_plots()

@dataclass
class Stats:
    '''
    Dataclass that controls counters for the simulation
    '''
    infected = config.sim.infected
    susceptible = config.sim.susceptible
    dead = config.sim.dead
    immune = config.sim.immune
    old_infected = 1 # Used to calculate r number


class Simulation:
    '''
    Controls the main pygame window, has Communnity instances as frames

    Args:
        config: str path of config.json
    '''

    def __init__(self) -> None:

        global stats, pathogen

        self.communities = self.__calc_communities()

        # Create application
        window_size = (config.app.sim_size[0] + config.app.sidebar_width, config.app.sim_size[1] + config.app.bar_height)
        self.window = pygame.display.set_mode(window_size)
        pygame.display.set_caption('Pandemic Simulation')
        pygame.display.set_icon(pygame.image.load('icon.png'))

        # Create GUI layout
        self.sim_surf= pygame.Surface(config.app.sim_size)
        self.sidebar_surf = pygame.Surface((config.app.sidebar_width, config.app.sim_size[1]))
        self.botbar_surf = pygame.Surface((config.app.sim_size[0], config.app.bar_height))
        self.controls_surf = pygame.Surface((config.app.sidebar_width, config.app.bar_height))

        # Font Initialisation
        self.font_size = config.app.sim_size[1] // 25
        self.font = pygame.font.SysFont('Calibri', self.font_size)

        # Create graph to be rendered in sidebar
        self.graph = Graph((config.app.sidebar_width, config.app.sim_size[1]//2), self.font)

        # Define the frame rate of simulation, depending on speed
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
        sim_width, sim_height = config.app.sim_size
        layout = config.sim.layout
        self.y_buffer = sim_height/(len(layout)*10) # The pixels between each row of communities
        height = round((sim_height - (self.y_buffer*(len(layout)+1))) / len(layout))

        # Create each community in grid defined by layout
        for y, cols in enumerate(layout):

            x_buffer = sim_width/(len(cols)*10)

            width = round((sim_width - (x_buffer*(len(cols)+1))) / len(cols))
            for x, (pop, places) in enumerate(cols):

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
            r = round(1 + (stats.susceptible - stats.infected) / stats.old_infected, 2)
        except ZeroDivisionError:
            r = 0
        stats.old_infected = stats.infected

        # Update counter on label
        infected_label = self.font.render(f'Infected:{stats.infected}', True, config.theme.infected)
        susceptible_label = self.font.render(f'Susceptible:{stats.susceptible}', True, config.theme.susceptible)
        dead_label = self.font.render(f'Dead:{stats.dead}', True, config.theme.dead)
        immune_label = self.font.render(f'Immune:{stats.immune}', True, config.theme.immune)
        r_label = self.font.render(f'R:{r}', True, config.theme.r_label)

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
        self.sidebar_surf.blit(self.graph.surf, (0, config.app.sim_size[1]//2))


    def run(self) -> None:
        '''
        Instantiates pygame window and starts the simulation.
        '''

        # Infect first person
        self.communities[0].population.sprites()[0].infect()

        self.running = True
        while self.running:

            # Fill backgrounds for re-rendering
            self.sim_surf.fill(config.theme.appbg)
            self.sidebar_surf.fill(config.theme.appbg)
            self.controls_surf.fill(config.theme.appbg)
            self.botbar_surf.fill(config.theme.appbg)

            # Update statistics and graphs
            self.__render_sidebar()
            self.__render_graph()

            # Update community and render
            for community in self.communities:

                community.surf.fill(config.theme.simbg)

                persons_migrated = community.update()

                # If there is only one community, do not go through with migration process
                valid = [x for x in self.communities if x is not community]
                if len(valid) > 0:

                    # Remove migrant from old community and add to new community
                    for person in persons_migrated:
                        community.population.remove(person)
                        person.set_random_location()
                        new_community = random.choice(valid)
                        person.community_size = new_community.surf_size
                        new_community.population.add(person)

                # Draw changes to surface and render to window
                community.places.draw(community.surf)
                community.population.draw(community.surf)
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
            self.window.blit(self.sidebar_surf, (config.app.sim_size[0], 0))
            self.window.blit(self.controls_surf, (config.app.sim_size))
            self.window.blit(self.botbar_surf, (0, config.app.sim_size[1]))
            # Render speed symbol
            self.speed_states[self.delay](self.window)
            # Update display
            pygame.display.update()
            time.sleep(self.delay) # 60 updates a second



class Person(pygame.sprite.Sprite):

    def __init__(self, community_size) -> None:

        global stats

        # Initialise sprite to allow rendering
        pygame.sprite.Sprite.__init__(self)

        # Simulation variables
        self.community_size = community_size

        # Person size and surface to be rendered
        self.size = (5,5)
        self.image = pygame.Surface(self.size)
        self.image.fill(config.theme.susceptible)

        # Person location
        self.rect = self.image.get_rect()
        self.set_random_location()

        # Person behaviour variables
        self.movement = 2
        self.dead = False
        self.immune = False
        self.infected = False
        self.cure_chance = 0
        self.death_chance = 0
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
        self.image.fill(config.theme.dead)

        # Update stats
        stats.dead += 1
        stats.infected -= 1


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
        self.image.fill(config.theme.infected)

        stats.infected += 1
        stats.susceptible -= 1


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
            self.image.fill(config.theme.immune)
        else:
            self.image.fill(config.theme.susceptible)

        # Adjust global counters
        stats.infected -= 1
        stats.immune += 1


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

        pygame.sprite.Sprite.__init__(self)

        self.size = (15, 15)
        self.image = pygame.Surface(self.size)
        self.image.fill(config.theme.place)
        self.rect = self.image.get_rect()

        self.rect.x = random.randint(1,community_size[0] - self.size[0])
        self.rect.y = random.randint(1,community_size[1] - self.size[1])
        self.coords = (self.rect.x + self.size[0]/2, self.rect.y + self.size[1]/2)


class Community:
    '''
    Is a pygame frame that sits encapsulated within simulation
    '''

    def __init__(self, coords, surf_size, population, places) -> None:

        global stats, pathogen

        self.coords = coords
        self.surf_size = surf_size
        self.surf = pygame.Surface(self.surf_size)

        # Create list of people in the community
        self.population = pygame.sprite.Group()
        for _ in range(population):
            self.population.add(Person(self.surf_size))

        # Create places in community
        self.places = pygame.sprite.Group()
        for _ in range(places):
            self.places.add(Place(self.surf_size))

    def update(self) -> list:
        '''
        Updates the state (dead, immune, susceptible, or infected)
        of people within the community.

        Returns:
            A list of people objects to be migrated to another community
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
                pygame.draw.line(self.surf, config.theme.route, person.coords, person.dest)

        # zombie refering to infected person
        for zombie in infected:
           for person in susceptible:
                pathogen.infect(person, zombie)

           pathogen.update_health(zombie)

        self.__calc_movement_events()
        return self.__calc_migration_events()


    def __calc_movement_events(self):
        '''
        Manages whether a person heads to a place in a community
        '''
        if len(self.places) == 0:
            return

        move_chance = config.sim.movement

        def check(person):
            if person.dead == False and person.dest == None:
                return True

        valid = list(filter(check, self.population.sprites()))

        while (random.random() < move_chance) and len(valid) > 0:
            mover = random.choice(valid)
            mover.route(random.choice(self.places.sprites()).coords, True)
            valid.remove(mover)


    def __calc_migration_events(self):
        '''
        Manages whether migrations occur.
        '''

        mig_chance = config.sim.migration

        def check(person):
            if person.dead == False and person.dest == None:
                return True

        valid = list(filter(check, self.population.sprites()))

        migrants = []
        while (random.random() < mig_chance) and len(valid) > 0:
            migrant = random.choice(valid)
            migrants.append(migrant)

        return migrants

def main():

    global pathogen, stats

    pathogen = Pathogen()
    stats = Stats()

    simulation = Simulation()
    simulation.run()


def call_stack_statistics():

    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        main()


    runstats = pstats.Stats(pr)
    runstats.sort_stats(pstats.SortKey.TIME)


if __name__ == '__main__':

    main()


from math import trunc
import pygame
from random import randint


def alpha_rect(surface: pygame.Surface, colour: tuple, rect: tuple):
    '''
    Creates a rectangle with transparent colour.
    Arguments:
        colour: (r, g, b, a)
        rect: (x, y, width, height)
    '''

    shape_surface = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surface, colour, shape_surface.get_rect())
    surface.blit(shape_surface, rect)


def alpha_circle(surface: pygame.Surface, colour: tuple, center: tuple, radius: int):
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


def alpha_polygon(surface: str, colour: tuple, points: tuple):
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
    alpha_polygon(surface, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))
    alpha_polygon(surface, (255, 255, 255, 100), ((30, 10), (50, 20), (30, 30)))

def fast_symbol(surface: pygame.Surface):
    '''
    Renders fast speed symbol on top left surface provided.
    '''
    alpha_polygon(surface, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))
    alpha_polygon(surface, (255, 255, 255, 100), ((30, 10), (50, 20), (30, 30)))
    alpha_polygon(surface, (255, 255, 255, 100), ((50, 10), (70, 20), (50, 30)))


def slow_symbol(surface: pygame.Surface):
    '''
    Renders slow speed symbol on top left surface provided.
    '''
    alpha_polygon(surface, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))


class Graph(pygame.sprite.Sprite):
    '''
    Class that controls the rendering of graphs.

    

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

    def __init__(self, width: int, height: int, values: list, *, title = ''):

        pygame.sprite.Sprite.__init__(self)

        self.values = values 

        # Initialising Pygame Variables
        self.width = width
        self.height = height
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.font = pygame.font.SysFont('Comic Sans MS', 15)

        # Buffer constants for formatting of GUI 
        self.s_buff = 25  # Greater than others to include space for graph's title
        self.w_buff = 10
        self.n_buff = 10
        self.e_buff = 10

        # Initialise Colour Palette and Title
        self.title = title
        self.text = self.font.render(self.title, True, (255, 255, 255))
        self.colours = [(255,0,0), (255,255,255), (0,0,255)]


    def update(self, *, new = None, maximum = 0):

        # Fill background as blank
        self.image.fill((0, 0, 0))
        self.image.blit(self.text, (self.w_buff, self.height-self.s_buff))

        # Set the maximum for the y-scale
        if maximum == 0: 
            self.y_max = max([max(line) for line in self.values if len(line) > 0])
        else: 
            self.y_max = maximum

        # Add new plots if provided by keyword argument
        if new != None:
            for index, line in enumerate(self.values):
                self.values[index] = line + new[index]

        # Re-render the axis and the scales for the axis
        self.y_axis = pygame.draw.line(
            self.image, 
            (255, 255, 255), 
            (self.w_buff, self.n_buff), 
            (self.w_buff, self.height-self.s_buff), 
            width=2
            )

        self.y_scale = (self.height-self.n_buff - self.s_buff)/self.y_max

        self.x_axis = pygame.draw.line(
            self.image, (255, 255, 255), 
            (self.w_buff, self.height - self.s_buff), 
            (self.width-self.e_buff, self.height-self.s_buff), 
            width=2
            )

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
                    self.image, 
                    self.colours[line_count], 
                    (x_last, y_last), 
                    (x_pos, y_pos), 
                    width=4
                    )

                x_last, y_last = x_pos, y_pos



if __name__ == '__main__':
    from time import sleep
    pygame.init()
    pygame.font.init()

    display = pygame.display.set_mode((200, 200))
    surface = pygame.Surface((200, 200))
    myGraph = pygame.sprite.Group()
    myGraph.add(Graph(200, 200, [[x for x in range(501)], [x for x in range(250)]], title='my graph'))
    running = True

    while running:

        myGraph.draw(surface)
        myGraph.update()
        display.blit(surface, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.update()
        sleep(0.08)

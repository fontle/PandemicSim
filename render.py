import pygame

def alpha_rect(surf: pygame.Surface, colour: tuple, rect: tuple) -> None:
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
def alpha_circle(surf: pygame.Surface, colour: tuple, center: tuple, radius: int) -> None:
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

def alpha_polygon(surf: pygame.Surface, colour: tuple, points: tuple) -> None:
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


def normal_speed_symbol(surf: pygame.Surface) -> None:
    '''
    Renders normal speed symbol on top left of surface provided.

    Args:
        surf: pygame.Surface
    '''
    alpha_polygon(surf, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))
    alpha_polygon(surf, (255, 255, 255, 100), ((30, 10), (50, 20), (30, 30)))


def fast_symbol(surf: pygame.Surface) -> None:
    '''
    Renders fast speed symbol on top left surface provided.

    Args:
        surf: pygame.Surface
    '''
    alpha_polygon(surf, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))
    alpha_polygon(surf, (255, 255, 255, 100), ((30, 10), (50, 20), (30, 30)))
    alpha_polygon(surf, (255, 255, 255, 100), ((50, 10), (70, 20), (50, 30)))


def slow_symbol(surf: pygame.Surface) -> None:
    '''
    Renders slow speed symbol on top left surface provided.

    Args:
        surf: pygame.Surface
    '''
    alpha_polygon(surf, (255, 255, 255, 100), ((10, 10), (30, 20), (10, 30)))


def pause_symbol(surf: pygame.Surface) -> None:
    '''
    Renders slow speed symbol on top left surf provided.

    Args:
        surf: pygame.Surface
    '''
    width = surf.get_rect().width
    alpha_rect(surf, (180, 180, 180, 4),(width- 20, 10, 10, 30))
    alpha_rect(surf, (180, 180, 180, 4),(width - 37, 10, 10, 30))


"""
Collision handling module for Pixel Heist game.
"""

import pygame
import math

def check_line_of_sight(start_pos, end_pos, wall_sprites, step=5):
    """
    Check if there's a clear line of sight between two positions.
    
    Args:
        start_pos: Starting position (x, y)
        end_pos: Ending position (x, y)
        wall_sprites: Sprite group containing wall objects
        step: Step size for ray casting
        
    Returns:
        bool: True if there's a clear line of sight, False otherwise
    """
    # Calculate direction vector
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance == 0:
        return True
    
    # Normalize direction
    dx /= distance
    dy /= distance
    
    # Cast ray from start to end
    current_distance = 0
    while current_distance < distance:
        # Calculate current position
        x = start_pos[0] + dx * current_distance
        y = start_pos[1] + dy * current_distance
        
        # Create a small rect for collision checking
        check_rect = pygame.Rect(x - 2, y - 2, 4, 4)
        
        # Check for collision with walls
        for wall in wall_sprites:
            if check_rect.colliderect(wall.rect):
                return False
        
        # Move along the ray
        current_distance += step
    
    return True

def check_rect_collision(rect, sprite_group):
    """
    Check if a rectangle collides with any sprite in a group.
    
    Args:
        rect: Pygame Rect to check
        sprite_group: Sprite group to check against
        
    Returns:
        list: List of sprites that collide with the rect
    """
    collisions = []
    for sprite in sprite_group:
        if rect.colliderect(sprite.rect):
            collisions.append(sprite)
    
    return collisions

def check_circle_collision(center, radius, sprite_group):
    """
    Check if a circle collides with any sprite in a group.
    
    Args:
        center: Center position of the circle (x, y)
        radius: Radius of the circle
        sprite_group: Sprite group to check against
        
    Returns:
        list: List of sprites that collide with the circle
    """
    collisions = []
    for sprite in sprite_group:
        # Get the closest point on the rectangle to the circle center
        closest_x = max(sprite.rect.left, min(center[0], sprite.rect.right))
        closest_y = max(sprite.rect.top, min(center[1], sprite.rect.bottom))
        
        # Calculate distance between the closest point and circle center
        distance = math.sqrt(
            (closest_x - center[0]) ** 2 + 
            (closest_y - center[1]) ** 2
        )
        
        # Check if the distance is less than the radius
        if distance < radius:
            collisions.append(sprite)
    
    return collisions

def check_point_in_rect(point, rect):
    """
    Check if a point is inside a rectangle.
    
    Args:
        point: Point coordinates (x, y)
        rect: Pygame Rect object
        
    Returns:
        bool: True if the point is inside the rect, False otherwise
    """
    return rect.collidepoint(point)

def check_point_in_circle(point, center, radius):
    """
    Check if a point is inside a circle.
    
    Args:
        point: Point coordinates (x, y)
        center: Circle center coordinates (x, y)
        radius: Circle radius
        
    Returns:
        bool: True if the point is inside the circle, False otherwise
    """
    distance = math.sqrt(
        (point[0] - center[0]) ** 2 + 
        (point[1] - center[1]) ** 2
    )
    return distance < radius

def check_point_in_polygon(point, vertices):
    """
    Check if a point is inside a polygon using ray casting algorithm.
    
    Args:
        point: Point coordinates (x, y)
        vertices: List of polygon vertices [(x1, y1), (x2, y2), ...]
        
    Returns:
        bool: True if the point is inside the polygon, False otherwise
    """
    x, y = point
    n = len(vertices)
    inside = False
    
    p1x, p1y = vertices[0]
    for i in range(1, n + 1):
        p2x, p2y = vertices[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

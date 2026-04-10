from typing import Any

from .inventory import Item
import pygame

class Entity:
    def __init__(self, name: str, x: int, y: int, z_index: int = 0, width: int = 32, height: int = 32):
        self.name = name
        self.x = x
        self.y = y
        self.z_index = z_index
        self.width = width
        self.height = height
        self.current_sprite = pygame.Surface((width, height))
        self.current_sprite.fill((255, 0, 255))
        self.metadata: dict[str, Any] = {}

    

    def __repr__(self):
        return f"Entity({self.name}, {self.x}, {self.y}))"
    
    def print_metadata(self):
        print(self.metadata)
    
    def pvt_move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

class LivingEntity(Entity):
    def __init__(self, name: str, x: int, y: int, z_index: int, width: int = 32, height: int = 32, health: int = 100):
        super().__init__(name, x, y, z_index, width, height)
        self.health = health
        self.velocity: list[int] = [0, 0]

    def __repr__(self):
        return f"LivingEntity({self.name}, {self.x}, {self.y}, {self.health})"
    

class Player(LivingEntity):
    def __init__(self, name: str, x: int, y: int, z_index: int, width: int = 32, height: int = 32, health: int = 100, inventory: list[Item] = []):
        super().__init__(name, x, y, z_index, width, height, health)
        self.inventory = inventory
        self.sprite_up = pygame.Surface((width, height))
        self.sprite_down = pygame.Surface((width, height))
        self.sprite_left = pygame.Surface((width, height))
        self.sprite_right = pygame.Surface((width, height))
        # For now we just fill the sprites with different colors, but eventually we will want to load actual images here
        self.sprite_up.fill((127, 127, 0))
        self.sprite_down.fill((0, 255, 0))
        self.sprite_left.fill((0, 255, 255))
        self.sprite_right.fill((22, 98, 122))
        self.current_sprite = self.sprite_down

    def change_sprite_direction(self, direction: str):
        if direction == "up":
            self.current_sprite = self.sprite_up
        elif direction == "down":
            self.current_sprite = self.sprite_down
        elif direction == "left":
            self.current_sprite = self.sprite_left
        elif direction == "right":
            self.current_sprite = self.sprite_right

    def pvt_move(self, dx: int, dy: int):
        super().pvt_move(dx, dy)
        if dx != 0 or dy != 0:
            self.change_sprite_direction("down" if dy > 0 else "up" if dy < 0 else "right" if dx > 0 else "left" if dx < 0 else "down")
            
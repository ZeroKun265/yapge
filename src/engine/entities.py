from typing import Any, Callable
import pygame


class SimpleHitbox:
    def __init__(self, x: int, y: int, width: int, height: int, collide_function: Callable[..., None] | None = None, color: tuple[int, int, int] = (255, 0, 0)):
        self.collide_function = collide_function
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        self.color = color
        
    def check_collision_with_rect(self, parent: Entity, rect: pygame.Rect) -> tuple[bool, SimpleHitbox]:
        # We move the hitbox by the parent's position and then check if it collides with the given rect
        new_self_rect = pygame.Rect(self.x + parent.x, self.y + parent.y, self.rect.width, self.rect.height)
        if new_self_rect.colliderect(rect):
            return True, self
        return False, self
    
    def set_color(self, color: tuple[int, int, int]):
        self.color = color
    
    def set_collide_function(self, func: Callable[..., None]):
        self.collide_function = func

    def set_visible(self, visible: bool):
        self.visible = visible

    def check_collision_with_hitbox(self, parent: Entity, other_entity: Entity, other_hitbox: SimpleHitbox) -> bool:
        # We move the hitbox by the parent's position and then check if it collides with the other hitbox (also moved by the other entity's position)
        if not isinstance(other_hitbox, ComplexHitbox):
            new_other_rect = pygame.Rect(other_hitbox.x + other_entity.x, other_hitbox.y + other_entity.y, other_hitbox.rect.width, other_hitbox.rect.height)
       
            new_self_rect = pygame.Rect(self.x + parent.x, self.y + parent.y, self.rect.width, self.rect.height)    
            if new_self_rect.colliderect(new_other_rect):
                if self.collide_function:
                    self.collide_function(parent, other_entity, self)
                return True
            return False
        else:
            collided = other_hitbox.check_collision_with_hitbox(other_entity, parent, self)
            if collided and self.collide_function:
                self.collide_function(parent, other_entity, self)
            return collided

class ComplexHitbox(SimpleHitbox):
    def __init__(self, hitboxes: list[SimpleHitbox], collide_function: Callable[..., None] | None = None, color: tuple[int, int, int] = (255, 0, 0)):
        self.hitboxes = hitboxes
        self.collide_function = collide_function
        self.visible = False
        self.color = color

    def set_color(self, color: tuple[int, int, int]):
        self.color = color
        for hitbox in self.hitboxes:
            hitbox.set_color(color)

    def check_collision_with_hitbox(self, parent: Entity, other_entity: Entity, other_hitbox: SimpleHitbox) -> bool:
        for hitbox in self.hitboxes:
            if hitbox.check_collision_with_hitbox(parent, other_entity, other_hitbox):
                if self.collide_function:
                    self.collide_function(parent, other_entity, self)
                return True
        return False

    def set_visible(self, visible: bool):
        self.visible = visible
        for hitbox in self.hitboxes:
            hitbox.set_visible(visible)
    
    def set_collide_function(self, func: Callable[..., None]):
        self.collide_function = func

    def check_collision_with_rect(self, parent: Entity, rect: pygame.Rect) -> tuple[bool, SimpleHitbox]:
        for hitbox in self.hitboxes:
            collided, hb = hitbox.check_collision_with_rect(parent, rect)
            if collided:
                if self.collide_function:
                    self.collide_function(parent, None, "entity", (0, 0), hb)
                return True, hb
        return False, self
        

class Entity:
    def __init__(self, name: str, x: int, y: int, z_index: int = 0, width: int = 32, height: int = 32, collider_name: str = "collider"):
        self.name = name
        self.x = x
        self.y = y
        self.z_index = z_index
        self.width = width
        self.height = height
        self.current_sprite = pygame.Surface((width, height))
        self.current_sprite.fill((255, 0, 255))
        self.metadata: dict[str, Any] = {}
        self.hitboxes: dict[str, SimpleHitbox] = {}
        self.collider_name = "collider"

    def set_collider_name(self, name: str):
        self.collider_name = name

    def set_hitbox(self, name: str, hitbox: SimpleHitbox) -> None:
        self.hitboxes[name] = hitbox
    
    def clear_hitboxes(self) -> None:
        self.hitboxes.clear()

    def remove_hitbox(self, name: str) -> None:
        if name in self.hitboxes:
            del self.hitboxes[name]
    
    def is_colliding_with_tile_rect(self, rect: pygame.Rect) -> tuple[bool, SimpleHitbox | None]:
        for key, hitbox in self.hitboxes.items():
            if key != self.collider_name:
                continue
            collided, hb = hitbox.check_collision_with_rect(self, rect)
            if collided:
                return (collided, hb)
        return (False, None)

    def check_entity_collision(self, other: Entity) -> list[str]:
        # Entity collisions happen only if the entities have same hitbox keys and we return a list containing what keys (in common) have collisions
        # So if entity A has hitboxes "main", "area" and "damage" and entity B has hitboxes "main", "area" and "collider"
        # The result will be ["main", "area"]
        # Those hitboxes can be simple or complex, and their collide function is called
        # For complex hitboxes, both the complex funcion and the individual simple hitboxes' ones are called
        common_hitbox_keys = set(self.hitboxes.keys()) & set(other.hitboxes.keys())
        final_collisions: list[str] = []
        for key in common_hitbox_keys:
            entity_hitbox = self.hitboxes[key]
            other_hitbox = other.hitboxes[key]
            if entity_hitbox.check_collision_with_hitbox(self, other, other_hitbox):
                final_collisions.append(key)

        return final_collisions

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
    def __init__(self, name: str, x: int, y: int, z_index: int, width: int = 32, height: int = 32, health: int = 100):
        super().__init__(name, x, y, z_index, width, height, health)
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
            
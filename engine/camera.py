from .map import World, Layer, SimpleBoundingBox, ComplexBoundingBox
import pygame
from .entities import Entity
from functools import singledispatchmethod

class Camera:
    def __init__(self, x: int, y: int, zoom: float = 1.0, width: int = 800, height: int = 600, world: World = World()):
        self.x = x
        self.y = y
        self.zoom = zoom
        self.width = width
        self.height = height
        self.world = world
        self.easing = False
        self.target: Entity | None = None
        self.easing_speed = 0.1
        self.max_offset = 100

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

    def get_position(self):
        return self.x, self.y
    
    @singledispatchmethod
    def set_position(self, arg, b=None) -> None: #type: ignore
        raise TypeError("Base method called, expected an Entity or a tuple of (x, y)")

    @set_position.register(Entity)
    def _(self, entity: Entity):
        self.x = entity.x
        self.y = entity.y

    @set_position.register(tuple)
    def _(self, position: tuple[int, int]):
        self.x = position[0]
        self.y = position[1]
    
    @set_position.register(int)
    def _(self, x: int, y: int):
        self.x = x
        self.y = y

    def set_target(self, entity: Entity, easing: bool = False, centered: bool = False, easing_speed: float = 0.1, max_offset: int = 100):
        self.target = entity
        self.easing = easing
        self.centered = centered
        self.easing_speed = easing_speed
        self.max_offset = max_offset
        
        # Only snap the camera to the target immediately if we are NOT easing
        if not self.easing:
            if centered:
                self.x = entity.x - self.width // 2
                self.y = entity.y - self.height // 2
            else:
                self.x = entity.x
                self.y = entity.y
    
    def render(self, screen: pygame.Surface):
        if self.target is not None:
            target_x = self.target.x - self.width // 2 if self.centered else self.target.x
            target_y = self.target.y - self.height // 2 if self.centered else self.target.y
            
            if self.easing:
                # Move a percentage of the distance towards the target (Linear Interpolation)
                self.x += (target_x - self.x) * self.easing_speed
                self.y += (target_y - self.y) * self.easing_speed
                
                # Enforce the maximum offset bounds (clamping)
                self.x = max(target_x - self.max_offset, min(self.x, target_x + self.max_offset))
                self.y = max(target_y - self.max_offset, min(self.y, target_y + self.max_offset))
            else:
                self.x = target_x
                self.y = target_y
        
        # We get all the tilesets that the camera can see and render them on the screen
        sorted_layers = sorted(self.world.layers, key=lambda layer: layer.z_index)
        sorted_entities = sorted(self.world.entities, key=lambda entity: entity.z_index)
        ## We merge the sorted layers and entities into a single list of renderables, sorted by z_index
        sorted_renderables: tuple[Layer | Entity, ...] = tuple(sorted(sorted_layers + sorted_entities, key=lambda renderable: renderable.z_index))

        for renderable in sorted_renderables:
            if isinstance(renderable, Layer):
                self.render_layer(screen, renderable)
            else:
                pass
                self.render_entity(screen, renderable)
                
    
    def render_entity(self, screen: pygame.Surface, entity: Entity):
        screen.blit(entity.current_sprite, (entity.x - self.x, entity.y - self.y))


    def render_layer(self, screen: pygame.Surface, layer: Layer):
        for y in range(layer.tilemap.height):
            for x in range(layer.tilemap.width):
                tile = layer.tilemap.get_tile(x, y)
                if tile:
                    screen.blit(tile.surface, (x * tile.size - self.x, y * tile.size - self.y))
                    if layer.tilemap.draw_bounding_boxes:
                        # In this case we check if the tile has a bounding box and if it does we draw it in red
                        if tile.bounding_box:
                            bounding_box = tile.bounding_box
                            if isinstance(bounding_box, ComplexBoundingBox):
                                for box in bounding_box.bounding_boxes:
                                    pygame.draw.rect(screen, box.color, (x * tile.size + box.rect.x - self.x, y * tile.size + box.rect.y - self.y, box.rect.width, box.rect.height), 1)
                            else:
                                pygame.draw.rect(screen, bounding_box.color, (x * tile.size + bounding_box.rect.x - self.x, y * tile.size + bounding_box.rect.y - self.y, bounding_box.rect.width, bounding_box.rect.height), 1)

    def __repr__(self):
        return f"Camera(x {self.x}, y {self.y}, zoom {self.zoom}, width {self.width}, height {self.height})"

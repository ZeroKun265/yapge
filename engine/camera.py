from .map import World, Layer
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


    def set_target(self, entity: Entity, easing: bool = False, centered: bool = False):
        if centered:
            self.x = entity.x - self.width // 2
            self.y = entity.y - self.height // 2
        else:
            self.x = entity.x
            self.y = entity.y
        self.target = entity
        self.easing = easing
        self.centered = centered
    
    def render(self, screen: pygame.Surface):
        if not self.easing and self.target is not None and self.centered:
            self.set_position(self.target.x - self.width // 2, self.target.y - self.height // 2)
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
                            pygame.draw.rect(screen, (255, 0, 0), (x * tile.size + bounding_box.x - self.x, y * tile.size + bounding_box.y - self.y, bounding_box.width, bounding_box.height), 1)

    def __repr__(self):
        return f"Camera(x {self.x}, y {self.y}, zoom {self.zoom}, width {self.width}, height {self.height})"


import pygame
from typing import Callable
from .entities import Entity, LivingEntity

class SimpleBoundingBox:
    def __init__(self, x: int, y: int, width: int, height: int, id: int = 0, color: tuple[int, int, int] = (255, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.id = id
        self.color = color
        self.collide_function: Callable[[Entity, 'Tile', str, tuple[int, int], 'SimpleBoundingBox'], None] | None = None

    def on_collide(self, func: Callable[[Entity, 'Tile', str, tuple[int, int], 'SimpleBoundingBox'], None]):
        self.collide_function = func
        return func

    def set_collide_function(self, func: Callable[[Entity, 'Tile', str, tuple[int, int], 'SimpleBoundingBox'], None]):
        self.collide_function = func

    def check_collision(self, entity: Entity, tile: 'Tile', tile_position: tuple[int, int] = (0, 0), move_type:str = "hor"):
        entity_rect = pygame.Rect(entity.x, entity.y, entity.width, entity.height)
        new_self_rect = self.rect.move(tile_position[0] * tile.size, tile_position[1] * tile.size)
        velocity = getattr(entity, 'velocity', (0, 0))
        if entity_rect.colliderect(new_self_rect):
            if self.collide_function:
                self.collide_function(entity, tile, move_type, tile_position, self)
                
            if move_type=="hor":
                if velocity[0] > 0:
                    entity.x = new_self_rect.left - entity.width
                elif velocity[0] < 0:
                    entity.x = new_self_rect.right
                return True
            elif move_type=="ver":
                if velocity[1] > 0:
                    entity.y = new_self_rect.top - entity.height
                elif velocity[1] < 0:
                    entity.y = new_self_rect.bottom
                return True
        return False

class ComplexBoundingBox(SimpleBoundingBox):
    def __init__(self, bounding_boxes: list[SimpleBoundingBox] = []):
        self.bounding_boxes = bounding_boxes

    def check_collision(self, entity: Entity, tile: 'Tile', tile_position: tuple[int, int] = (0, 0), move_type:str = "hor"):
        for box in self.bounding_boxes:
            if box.check_collision(entity, tile, tile_position, move_type):
                return True
        return False        


class Tile:
    def __init__(self, tile_type: str, color: tuple[int, int, int] = (255, 255, 255), size: int = 32, width: int = 1, height: int = 1, bounding_box: SimpleBoundingBox = SimpleBoundingBox(0, 0, 0, 0)):
        self.tile_type = tile_type
        self.color = color # placeholder for now but also could be used for debug visualizations or stuff
        self.surface = pygame.Surface((width * size, height * size))
        self.surface.fill(color)
        self.size = size
        self.width = width
        self.height = height

        self.bounding_box = bounding_box

        # based on the bounding box string, we create a bounding box, we have a few presets:
        # - full_rect means the entire tile is solid
        # - bottom_half means the bottom half of the tile is solid
        # - top_half means the top half of the tile is solid
        # - left_half means the left half of the tile is solid
        # - right_half means the right half of the tile is solid
        # - custom means we use a custom bounding box defined by the user, not yet implemented


    def __repr__(self):
        return f"Tile({self.tile_type})"
    
    def __bool__(self):
        return self.tile_type != ""

    
class TileMap:
    def __init__(self, width: int, height: int, name: str = "TileMap", draw_bounding_boxes: bool = False):
        self.width = width
        self.height = height
        self.name = name
        self.draw_bounding_boxes = draw_bounding_boxes
        self.tiles: list[list[Tile]] = [[Tile("") for _ in range(width)] for _ in range(height)]

    def set_tile(self, x: int, y: int, tile: Tile):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile

    def set_name(self, name: str):
        self.name = name

    def get_tile(self, x: int, y: int):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
    
    def grow(self, new_width: int, new_height: int):
        if new_width > self.width:
            for row in self.tiles:
                row.extend([Tile("") for _ in range(new_width - self.width)])
        if new_height > self.height:
            for _ in range(new_height - self.height):
                self.tiles.append([Tile("") for _ in range(new_width)])
        self.width = new_width
        self.height = new_height

    def __repr__(self):
        return f"TileMap(w {self.width}, h {self.height}, n {self.name})"


class TileMapGenerator: # this could have probably been a function instead of a class but i really got into the Java mindset lol
    def __init__(self, resource_path: str):
        self.resource_path = resource_path

    def generate(self):
        # Symbolo into type, color, size, width, height
        tiletypes: dict[str, tuple[str, tuple[int, int, int], int, int, int]] = {}
        # Symbol to bounding box string
        tile_bounding_boxes: dict[str, SimpleBoundingBox] = {}
        tilemap: TileMap = TileMap(0, 0)
        non_data_lines = 0
        with open(self.resource_path, "r") as f:
            data = f.read()
        for j, line in enumerate(data.splitlines()):
            if line.startswith("DEFINE"):
                # We are at the first line
                _, w, h, n = line.split(" ")
                width = int(w.split("=")[1])
                height = int(h.split("=")[1])
                name = n.split("=")[1]
                tilemap = TileMap(width, height, name)
                non_data_lines += 1
            elif line.startswith("TILE"):
                # We are definint a tile
                _, s, t, c, size, w, h = line.split(" ")
                symbol = s.split("=")[1]
                tile_type = t.split("=")[1]
                cc = c.split("=")[1].split(",")
                color = (int(cc[0]), int(cc[1]), int(cc[2]))
                size = int(size.split("=")[1])
                width = int(w.split("=")[1])
                height = int(h.split("=")[1])
                tiletypes[symbol] = (tile_type, color, size, width, height)
                non_data_lines += 1
            elif line.startswith("BOUNDINGBOX"):

                split_line = line.split(" ")
                box_type = split_line[2]
                symbol = split_line[1]

                size = tiletypes[symbol][2]
                width = tiletypes[symbol][3]
                height = tiletypes[symbol][4]

                # We get the tile's color from tiletypes
                tile_color = tiletypes[symbol][1]
                bb_color = (255 - tile_color[0], 255 - tile_color[1], 255 - tile_color[2])
                
                match box_type:
                    case "full_rect":
                        bounding_box = SimpleBoundingBox(0, 0, width * size, height * size, color=bb_color)
                    case "bottom_half":
                        bounding_box = SimpleBoundingBox(0, size * height // 2, width * size, size * height // 2, color=bb_color)
                    case "top_half":
                        bounding_box = SimpleBoundingBox(0, 0, width * size, size * height // 2, color=bb_color)
                    case "left_half":
                        bounding_box = SimpleBoundingBox(0, 0, size * width // 2, height * size, color=bb_color)
                    case "right_half":
                        bounding_box = SimpleBoundingBox(size * width // 2, 0, size * width // 2, height * size, color=bb_color)
                    case "simple":
                        # _, symbol, type, x, y, w, h
                        # BOUNDINGBOX ^ simple 0.2 0.2 0.6 0.6
                        _, symbol, _, x, y, w, h = split_line[0:7]
                        bounding_box = SimpleBoundingBox(int(float(x)*size) , int(float(y)*size), int(float(w)*size), int(float(h)*size), color=bb_color)
                    case "complex":
                        # BOUNDINGBOX T complex 1:(0,0,0.2,1)-2:(0,0,1,0.2)-3:(0.8, 0, 0.2, 1)
                        _, symbol, _, boxes = split_line[0:4]
                        final_boxes: list[SimpleBoundingBox] = []
                        complex_boxes = boxes.split("-")
                        for i in range(len(complex_boxes)):
                            box = complex_boxes[i]
                            id, params = box.split(":")
                            x, y, w, h = params.strip("()").split(",")
                            final_boxes.append(SimpleBoundingBox(int(float(x)*size) , int(float(y)*size), int(float(w)*size), int(float(h)*size), id=int(id), color=bb_color))
                        
                        bounding_box = ComplexBoundingBox(final_boxes)
                    case _:
                        bounding_box = SimpleBoundingBox(0, 0, 0, 0)
                        print(f"Unknown bounding box type: {box_type}")

                tile_bounding_boxes[symbol] = bounding_box
                non_data_lines += 1
            else:
                # We are at the tilemap data
                for i, char in enumerate(line):
                    if char in tiletypes:
                        tile_type, color, size, width, height = tiletypes[char]
                        tile = Tile(tile_type, color, size, width, height, tile_bounding_boxes.get(char, SimpleBoundingBox(0, 0, 0, 0)))
                        tilemap.set_tile(i, j - non_data_lines, tile)
                
        return tilemap


class Layer: #realistically could just move z_index into the TileMap class and not have a separate Layer class but yeah, maybe in the future this could serve as filters for physics processing or something, who knows
    def __init__(self, z_index: int, tilemap: TileMap = TileMap(0, 0)):
        self.z_index = z_index
        self.tilemap: TileMap = tilemap

class World:
    def __init__(self):
        self.layers: list[Layer] = []
        self.entities: list[Entity] = []

    def add_layer(self, layer: Layer):
        self.layers.append(layer)

    def remove_layer(self, layer: Layer):
        self.layers.remove(layer)
    
    def move_entity(self, entity: Entity, dx: int = 0, dy: int = 0, no_collide: bool = False, use_entity_velocity:bool = True):
        if isinstance(entity, LivingEntity) and use_entity_velocity:
            dx = entity.velocity[0]
            dy = entity.velocity[1]
        
        if no_collide:
            entity.pvt_move(dx, dy)
            return
        else:
            # We move along the x, if the player rect and one tile rect intersect we set them side by side based on speed
            entity.pvt_move(dx, 0)
            for layer in self.layers:
                for y in range(layer.tilemap.height):
                    for x in range(layer.tilemap.width):
                        tile = layer.tilemap.get_tile(x, y)
                        if tile and tile.bounding_box:
                            tile.bounding_box.check_collision(entity, tile, (x, y), move_type="hor")
                            
                            
            # We then move along the y and do the same thing
            entity.pvt_move(0, dy)
            for layer in self.layers:
                for y in range(layer.tilemap.height):
                    for x in range(layer.tilemap.width):
                        tile = layer.tilemap.get_tile(x, y)
                        if tile and tile.bounding_box: 
                            tile.bounding_box.check_collision(entity, tile, (x, y), move_type="ver")
                        
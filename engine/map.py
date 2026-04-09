import pygame
from .entities import Entity

class Tile:
    def __init__(self, tile_type: str, color: tuple[int, int, int] = (255, 255, 255), size: int = 32, width: int = 1, height: int = 1, bounding_box_str: str = ""):
        self.tile_type = tile_type
        self.color = color
        self.surface = pygame.Surface((width * size, height * size))
        self.surface.fill(color)
        self.size = size
        self.width = width
        self.height = height

        # based on the bounding box string, we create a bounding box, we have a few presets:
        # - full_rect means the entire tile is solid
        # - bottom_half means the bottom half of the tile is solid
        # - top_half means the top half of the tile is solid
        # - left_half means the left half of the tile is solid
        # - right_half means the right half of the tile is solid
        # - custom means we use a custom bounding box defined by the user, not yet implemented
        if bounding_box_str == "full_rect":
            self.bounding_box = pygame.Rect(0, 0, width * size, height * size)
        elif bounding_box_str == "bottom_half":
            self.bounding_box = pygame.Rect(0, size * height // 2, width * size, size * height // 2)
        elif bounding_box_str == "top_half":
            self.bounding_box = pygame.Rect(0, 0, width * size, size * height // 2)
        elif bounding_box_str == "left_half":
            self.bounding_box = pygame.Rect(0, 0, size * width // 2, height * size)
        elif bounding_box_str == "right_half":
            self.bounding_box = pygame.Rect(size * width // 2, 0, size * width // 2, height * size)
        else:
            self.bounding_box = None


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


class TileMapGenerator:
    def __init__(self, resource_path: str):
        self.resource_path = resource_path

    def generate(self):
        # Symbolo into type, color, size, width, height
        tiletypes: dict[str, tuple[str, tuple[int, int, int], int, int, int]] = {}
        # Symbol to bounding box string
        tile_bounding_boxes: dict[str, str] = {}
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
                # BOUNDINGBOX - full_rect
                _, symbol, bounding_box_str = line.split(" ")
                tile_bounding_boxes[symbol] = bounding_box_str
                print(f"Set bounding box for symbol {symbol} to {bounding_box_str}")
                non_data_lines += 1

            else:
                # We are at the tilemap data
                for i, char in enumerate(line):
                    if char in tiletypes:
                        tile_type, color, size, width, height = tiletypes[char]
                        tile = Tile(tile_type, color, size, width, height, tile_bounding_boxes.get(char, ""))
                        tilemap.set_tile(i, j - non_data_lines, tile)
                
        return tilemap


class Layer:
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
    
    def move_entity(self, entity: Entity, dx: int, dy: int, no_collide: bool = False):
        if no_collide:
            entity.pvt_move(dx, dy)
            return
        else:
            # We move along the x, if the player rect and one tile rect intersect we set them side by side based on speed
            entity.pvt_move(dx, 0)
            entity_rect = pygame.Rect(entity.x, entity.y, entity.width, entity.height)
            for layer in self.layers:
                for y in range(layer.tilemap.height):
                    for x in range(layer.tilemap.width):
                        tile = layer.tilemap.get_tile(x, y)
                        if tile and tile.bounding_box:
                            tile_rect = pygame.Rect(x * tile.size + tile.bounding_box.x, y * tile.size + tile.bounding_box.y, tile.bounding_box.width, tile.bounding_box.height)
                            if entity_rect.colliderect(tile_rect):
                                if dx > 0:
                                    entity.x = tile_rect.left - entity.width
                                elif dx < 0:
                                    entity.x = tile_rect.right
                                entity_rect.x = entity.x
            # We then move along the y and do the same thing
            entity.pvt_move(0, dy)
            entity_rect = pygame.Rect(entity.x, entity.y, entity.width, entity.height)
            for layer in self.layers:
                for y in range(layer.tilemap.height):
                    for x in range(layer.tilemap.width):
                        tile = layer.tilemap.get_tile(x, y)
                        if tile and tile.bounding_box:
                            tile_rect = pygame.Rect(x * tile.size + tile.bounding_box.x, y * tile.size + tile.bounding_box.y, tile.bounding_box.width, tile.bounding_box.height)
                            if entity_rect.colliderect(tile_rect):
                                if dy > 0:
                                    entity.y = tile_rect.top - entity.height
                                elif dy < 0:
                                    entity.y = tile_rect.bottom
                                entity_rect.y = entity.y
                        
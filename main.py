import engine
import pygame
pygame.init()

def main():    
    # I make a world
    world = engine.map.World()
    # Now i want to make a camera that will then be rendered in the game loop
    camera = engine.camera.Camera(0, 0, 1.0, 800, 600, world)

    # We define the main tilemap and layer and add it to the world
    base_tilemap = engine.map.TileMapGenerator("assets/maps/base.tlmp").generate()

    def on_demo_collide(entity: object, tile: object, move_type: str, tile_pos: tuple[int, int], bbox: object) -> None:
        print("--- COLLISION DETECTED ---")
        print(f"Entity: {entity}")
        print(f"Tile: {tile}")
        print(f"Move Type: {move_type}")
        print(f"Tile Position: {tile_pos}")
        print(f"Bounding Box: {bbox}")

    for y in range(base_tilemap.height):
        for x in range(base_tilemap.width):
            tile = base_tilemap.get_tile(x, y)
            if tile and tile.tile_type == "demo_type" and tile.bounding_box:
                tile.bounding_box.set_collide_function(on_demo_collide)

    base_layer = engine.map.Layer(1, base_tilemap)
    world.add_layer(base_layer)

    # we create a player and add it to the world
    player = engine.entities.Player("Player", x=100, y=100, z_index=100, width=32, height=64)
    world.entities.append(player)

    # boilerplate for the game loop
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True

    camera.set_target(player, easing=True, centered=True, easing_speed=0.08, max_offset=150)  # Set the camera's target to the player


    # something that could probably be moved into the LivingEntity class but for now it is here
    SPEED = 5
    should_no_collide = False
    while running:
        #boilerplate
        clock.tick(60)  # Limit to 60 frames per second
        screen.fill((0, 0, 0))  # Clear the screen with black
        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    base_tilemap.draw_bounding_boxes = not base_tilemap.draw_bounding_boxes
                if event.key == pygame.K_c:
                    should_no_collide = not should_no_collide
            # We handle WASD and calculate a velocity vector
                
        keys = pygame.key.get_pressed()


        player.velocity[0] = (keys[pygame.K_d] - keys[pygame.K_a]) * SPEED
        player.velocity[1] = (keys[pygame.K_s] - keys[pygame.K_w]) * SPEED

        world.move_entity(player, no_collide=should_no_collide)  # Move the player based on velocity

        camera.render(screen)  # Render the camera's view of the world
        pygame.display.flip()  # Update the display

# if name = main boilerplate
if __name__ == "__main__":
    main()
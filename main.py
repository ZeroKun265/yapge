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
    base_layer = engine.map.Layer(1, base_tilemap)
    world.add_layer(base_layer)

    # we create a player and add it to the world
    player = engine.entities.Player("Player", x=100, y=100, z_index=100, width=32, height=64)
    world.entities.append(player)

    # boilerplate for the game loop
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True

    # something that could probably be moved into the LivingEntity class but for now it is here
    SPEED = 5
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
            # We handle WASD and calculate a velocity vector
        
        # This could also live in the LivingEntity class but for now it is here 
        velocity: list[int]= [0, 0]
        keys = pygame.key.get_pressed()


        velocity[0] = (keys[pygame.K_d] - keys[pygame.K_a]) * SPEED
        velocity[1] = (keys[pygame.K_s] - keys[pygame.K_w]) * SPEED

        world.move_entity(player, velocity[0], velocity[1])  # Move the player based on velocity

        camera.set_target(player, easing=True, centered=True, easing_speed=0.08, max_offset=150)  # Set the camera's target to the player

        camera.render(screen)  # Render the camera's view of the world
        pygame.display.flip()  # Update the display

# if name = main boilerplate
if __name__ == "__main__":
    main()
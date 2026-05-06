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

    # def on_demo_collide(entity: object, tile: object, move_type: str, tile_pos: tuple[int, int], bbox: object) -> None:
    #     print("--- COLLISION DETECTED ---")
    #     print(f"Entity: {entity}")
    #     print(f"Tile: {tile}")
    #     print(f"Move Type: {move_type}")
    #     print(f"Tile Position: {tile_pos}")
    #     print(f"Bounding Box: {bbox}")

    # for y in range(base_tilemap.height):
    #     for x in range(base_tilemap.width):
    #         tile = base_tilemap.get_tile(x, y)
    #         if tile and tile.tile_type == "demo_type" and tile.bounding_box:
    #             tile.bounding_box.set_collide_function(on_demo_collide)

    base_layer = engine.map.Layer(1, base_tilemap)
    world.add_layer(base_layer)

    # we create a player and add it to the world
    player = engine.entities.Player("Player", x=100, y=100, z_index=100, width=32, height=64)
    player_hitbox = engine.entities.SimpleHitbox(10, 10, player.width -16, player.height-24)
    player.set_hitbox("collider", player_hitbox)
    world.entities.append(player)

    ball = engine.entities.LivingEntity("Ball", x=250, y=200, z_index=50, width=32, height=32)
    ball_hitbox_1 = engine.entities.SimpleHitbox(1, 1, 20, 10)
    ball_hitbox_2 = engine.entities.SimpleHitbox(1, 21, 10, 10)
    ball_hitbox = engine.entities.ComplexHitbox([ball_hitbox_1, ball_hitbox_2])
    ball.set_hitbox("collider", ball_hitbox)

    ball2 = engine.entities.LivingEntity("Ball2", x=300, y=200, z_index=50, width=32, height=32)
    ball2_hitbox = engine.entities.SimpleHitbox(1, 1, 32, 32)
    ball2.set_hitbox("collider", ball2_hitbox)

    def player_collision_function(entity: object, other: object, hitbox: object) -> None:
        if other is ball:
            print("Player collided with the ball!")
        if other is ball2:
            print("Player collided with the ball2!")


    player.hitboxes["collider"].set_collide_function(player_collision_function)

    world.entities.append(ball)
    world.entities.append(ball2)
    

    # boilerplate for the game loop
    simplescreen = engine.screen.SimpleScreen((800, 600), window_size=(1200,  900), scale_with_desktop=False, flags=pygame.NOFRAME)


    clock = pygame.time.Clock()
    running = True

    camera.set_target(player, easing=True, centered=True, easing_speed=0.08, max_offset=150)  # Set the camera's target to the player


    # something that could probably be moved into the LivingEntity class but for now it is here
    SPEED = 5
    should_no_collide = False

    while running:
        #boilerplate
        clock.tick(60)  # Limit to 60 frames per second
        simplescreen.screen.fill((16, 16, 16))  # Clear the screen with black
        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    base_tilemap.draw_bounding_boxes = not base_tilemap.draw_bounding_boxes
                if event.key == pygame.K_c:
                    should_no_collide = not should_no_collide
                if event.key == pygame.K_b:
                    for entity in world.entities:
                        for hitbox in entity.hitboxes.values():
                            hitbox.set_visible(not hitbox.visible)
                if event.key == pygame.K_m:
                    if simplescreen.window_size == (800, 600):
                        simplescreen.resize_window((400, 300))
                    else:
                        simplescreen.resize_window((800, 600))
            # We handle WASD and calculate a velocity vector
                
        keys = pygame.key.get_pressed()


        player.velocity[0] = (keys[pygame.K_d] - keys[pygame.K_a]) * SPEED
        player.velocity[1] = (keys[pygame.K_s] - keys[pygame.K_w]) * SPEED

        ball.velocity[0] = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * SPEED
        ball.velocity[1] = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * SPEED
        world.move_entity(ball)    


        world.move_entity(player, no_collide=should_no_collide)  # Move the player based on velocity
        

        camera.render(simplescreen.screen)  # Render the camera's view of the world
        hudsurface = pygame.Surface(simplescreen.window_size, pygame.SRCALPHA)  # Create a transparent surface for the HUD
        pygame.draw.rect(hudsurface, (0, 255, 0), (10, 10, 100, 20))  # Draw a simple health bar on the HUD
        simplescreen.update(hudsurface)  # Update the display

# if name = main boilerplate
if __name__ == "__main__":
    main()
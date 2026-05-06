import src.engine as engine
import pygame
import sys
pygame.init()

should_ball_turn = False
did_player_hit_ball = False
score = 0

def main():    
    # We make the world
    world = engine.map.World()
    base_tilemap = engine.map.TileMapGenerator("demos/pong/map.tlmp").generate()
    base_layer = engine.map.Layer(1, base_tilemap)
    world.add_layer(base_layer)
    # We make a camera that will then be rendered in the game loop
    camera = engine.camera.Camera(0, 0, 1.0, 800, 600, world)

    # we create the plyers and add them to the world
    player1 = engine.entities.Player("Player", x=25, y=25, z_index=100, width=32, height=96)
    player1_hitbox = engine.entities.SimpleHitbox(0, 0, player1.width, player1.height)
    player1.set_hitbox("collider", player1_hitbox)
    player1.current_sprite = pygame.Surface((player1.width, player1.height))
    player1.current_sprite.fill((255, 255, 255))
    world.entities.append(player1)

    player1.sprite_down = pygame.Surface((player1.width, player1.height))
    player1.sprite_down.fill((255, 255, 255))
    player1.sprite_up = pygame.Surface((player1.width, player1.height))
    player1.sprite_up.fill((255, 255, 255))

    player2 = engine.entities.Player("Player", x=725, y=25, z_index=100, width=32, height=96)
    player2_hitbox = engine.entities.SimpleHitbox(0, 0, player2.width, player2.height)
    player2.set_hitbox("collider", player2_hitbox)
    player2.current_sprite = pygame.Surface((player2.width, player2.height))
    player2.current_sprite.fill((255, 255, 255))
    world.entities.append(player2)

    player2.sprite_down = pygame.Surface((player2.width, player2.height))
    player2.sprite_down.fill((255, 255, 255))
    player2.sprite_up = pygame.Surface((player2.width, player2.height))
    player2.sprite_up.fill((255, 255, 255))

   
    # We create the ball and add it to the world
    ball = engine.entities.LivingEntity("Ball2", x=300, y=200, z_index=50, width=32, height=32)
    ball_hitbox = engine.entities.SimpleHitbox(0, 0, 32, 32)
    ball.set_hitbox("collider", ball_hitbox)
    ball.current_sprite = pygame.Surface((ball.width, ball.height))
    ball.current_sprite.fill((255, 255, 255))
    world.entities.append(ball)    

    # This function is called when the ball collides with the player
    def player_collision_function(entity: object, other: object, hitbox: object) -> None:
        if other is ball:
            global did_player_hit_ball
            did_player_hit_ball = True

    player1.hitboxes["collider"].set_collide_function(player_collision_function)
    player2.hitboxes["collider"].set_collide_function(player_collision_function)

    # ...and this one when it collides with a wall
    def on_wall_collide(entity: object, tile: object, move_type: str, tile_pos: tuple[int, int], bbox: object) -> None:
        if move_type == "hor":
            sys.exit("Game Over! Final Score: " + str(score))
        if entity is ball:
            global should_ball_turn
            should_ball_turn = True
            
    
    # We set the collide function for all wall tiles
    for y in range(base_tilemap.height):
        for x in range(base_tilemap.width):
            tile = base_tilemap.get_tile(x, y)
            if tile and tile.tile_type == "wall" and tile.bounding_box:
                tile.bounding_box.set_collide_function(on_wall_collide)


    # we make the screen and the game loop boilerplate
    simplescreen = engine.screen.SimpleScreen((800, 600), window_size=(800,  600), scale_with_desktop=False)


    clock = pygame.time.Clock()
    running = True

    SPEED = 500
    while running:
        # We handle the velocity flipping and score here because race conditions
        global should_ball_turn
        global did_player_hit_ball
        if should_ball_turn:
            ball.velocity[1] *= -1
            should_ball_turn = False
        if did_player_hit_ball:
            ball.velocity[0] *= -1
            did_player_hit_ball = False
            global score
            score += 1
            ball.x = player1.x + player1.width if ball.velocity[0] > 0 else player2.x - ball.width
            print("Score: " + str(score))

        #boilerplate
        dt = clock.tick(60)/1000  # Limit to 60 frames per second
        simplescreen.screen.fill((0, 0, 0))  # Clear the screen with black
        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    for entity in world.entities:
                        for hitbox in entity.hitboxes.values():
                            hitbox.set_visible(not hitbox.visible)
                if event.key == pygame.K_SPACE:
                    # we can start the game with space
                    ball.velocity[0] = 5
                    ball.velocity[1] = 5
                if event.key == pygame.K_m:
                    if simplescreen.window_size == (800, 600):
                        simplescreen.resize_window((1200, 900))
                    elif simplescreen.window_size == (1200, 900):
                        simplescreen.resize_window((400, 300))
                    elif simplescreen.window_size == (400, 300):
                        simplescreen.resize_window((800, 600))
            # We handle WASD and calculate a velocity vector

        # We get the input, update the player's velocity and move all entities        
        keys = pygame.key.get_pressed()


        player1.velocity[1] = int((keys[pygame.K_s] - keys[pygame.K_w]) * SPEED * dt)
        player2.velocity[1] = int((keys[pygame.K_DOWN] - keys[pygame.K_UP]) * SPEED * dt)

        world.move_entity(player1)
        world.move_entity(player2)
        world.move_entity(ball)  # Move the player based on velocity
        

        camera.render(simplescreen.screen)  # Render the camera's view of the world
        simplescreen.update()  # Update the display

# if name = main boilerplate
if __name__ == "__main__":
    main()
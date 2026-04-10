# yapge

Read the description if you're curious

the engine itself is just the engine folder, main.py is basically just a test file for now, and so is the assets folder

there is no docs, this is probably not gonna go very far anyways, the code is i think pretty readable, type hinting is strictl enforced so no doubts there

This is more a learning opportunity  for me to play around with large codebases, typehinting and architecture design, buw who knows maybe it could be used in the future.. if that ever happens, LDM studio has and always will have a perpetual license to use this ;)

##  TODO
- Hitbox resource
- Check collision entity-entity
- window creation and other boilerplate simplification


### Boilerplate simplification
Something like this AI code
```python
import engine
import pygame
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 1. Store your game objects as class attributes using 'self.'
        self.world = engine.map.World()
        self.player = engine.entities.Player("Player", x=100, y=100, z_index=100, width=32, height=64)
        self.world.entities.append(self.player)
        
        self.camera = engine.camera.Camera(0, 0, 1.0, 800, 600, self.world)
        self.camera.set_target(self.player, easing=True, centered=True, easing_speed=0.08, max_offset=150)
        
        self.base_tilemap = engine.map.TileMapGenerator("assets/maps/base.tlmp").generate()
        self.world.add_layer(engine.map.Layer(1, self.base_tilemap))
        
        self.SPEED = 5
        self.should_no_collide = False

        # 2. Set the initial state
        self.state = self.menu_state 

    def menu_state(self, events):
        """State for the main menu"""
        self.screen.fill((50, 50, 50)) # Grey background for menu
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Press ENTER to start! Change state to play_state
                    self.state = self.play_state

    def play_state(self, events):
        """State for actual gameplay"""
        self.screen.fill((0, 0, 0)) # Black background for play
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.base_tilemap.draw_bounding_boxes = not self.base_tilemap.draw_bounding_boxes
                if event.key == pygame.K_c:
                    self.should_no_collide = not self.should_no_collide

        # WASD movement using self.player
        keys = pygame.key.get_pressed()
        self.player.velocity[0] = (keys[pygame.K_d] - keys[pygame.K_a]) * self.SPEED
        self.player.velocity[1] = (keys[pygame.K_s] - keys[pygame.K_w]) * self.SPEED

        # Move and Render
        self.world.move_entity(self.player, no_collide=self.should_no_collide)
        self.camera.render(self.screen)
        
        # Example of how you would trigger a lose screen:
        # if self.player.health <= 0:
        #     self.state = self.lose_screen

    def run(self):
        """The main game loop"""
        while self.running:
            events = pygame.event.get()
            
            # 3. Call whatever state function is currently active
            self.state(events)
            
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Create an instance of the game and run it
    my_game = Game()
    my_game.run()
```

But with many functions that are called at various points of the loop so you can "mixin intercept"


## Projects
In order to test the usability of the engine, especially at the begining of development, at some points the versions will be freezed as releases and used to develop some test apps or games, here are the list of them
### PONG!
Not yet completed, needed to complete it:
- Entity to Entity collision with custom func calling (like box)

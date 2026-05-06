import pygame

class SimpleScreen:
    def __init__(self, game_size: tuple[int, int], flags: int = 0, window_size: tuple[int, int] = (0,0), scale_with_desktop: bool = True):
        self.size = game_size
        if window_size == (0,0) and not scale_with_desktop:
            self.window_size = game_size
        elif window_size == (0,0) and scale_with_desktop:
            desktop_height = pygame.display.get_desktop_sizes()[0][1]
            self.window_size = (int(desktop_height/2)*game_size[0]//game_size[1], int(desktop_height/2)) 
        else:
            self.window_size = window_size
        print(f"Initialized SimpleScreen with game size {game_size} and window size {self.window_size}")
        self.window = pygame.display.set_mode(self.window_size, flags)
        self.screen = pygame.Surface(game_size)
    
    def resize_window(self, new_size: tuple[int, int]):
        self.window_size = new_size
        self.window = pygame.display.set_mode(new_size)

    def update(self, hud_surface: pygame.Surface | None = None):
        scaled_screen = pygame.transform.scale(self.screen, self.window_size)  # Scale the screen to fit the window
        self.window.blit(scaled_screen, (0, 0))  # Draw the scaled screen
        if hud_surface is not None:
            self.window.blit(hud_surface, (0, 0))  # Draw the HUD
        pygame.display.flip()  # Update the display
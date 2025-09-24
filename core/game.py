import pygame

class Game:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.state = None  # Estado atual (menu, gameplay, etc.)

    def change_state(self, new_state):
        """Muda o estado atual do jogo (ex: Menu -> Gameplay)."""
        self.state = new_state

    def run(self):
        """Executa o loop de um frame."""
        if self.state is not None:
            self.state.handle_events()
            self.state.update()
            self.state.draw()
        pygame.display.flip()
        self.clock.tick(60)

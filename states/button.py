import pygame

class ImageButton:
    def __init__(self, image_path, pos, scale=1.0):
        self.image = pygame.image.load(image_path).convert_alpha()
        
        # Redimensiona (caso precise)
        if scale != 0.5:
            w, h = self.image.get_size()
            self.image = pygame.transform.scale(self.image, (int(w * scale), int(h * scale)))
        
        self.rect = self.image.get_rect(center=pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

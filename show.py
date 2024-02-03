import sys
import pygame
import threading

from funcs import blitRotate, rectRotated

pygame.init()


class Screen(threading.Thread):
    def __init__(self):
        super().__init__()

        self.WIDTH, self.HEIGHT = 903, 1021
        self.FPS = 60

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()

        self.stop_flag = False

        self.standIMG = pygame.transform.scale(pygame.image.load('img\\stand.png').convert_alpha(), (self.WIDTH, self.HEIGHT))

    def set_obj(self, radar, sputnik):
        self.radar, self.sputnik = radar, sputnik
        self.radarIMG = pygame.transform.scale(pygame.image.load('img\\radar.png').convert_alpha(),
                                               (self.radar.size_x, self.radar.size_y))
        self.sputnikIMG = pygame.transform.scale(pygame.image.load('img\\sputnik.png').convert_alpha(),
                                                 (self.sputnik.size_x, self.sputnik.size_y))

    def get_size(self):
        return self.WIDTH, self.HEIGHT

    def get_FPS(self):
        return self.FPS

    def stop(self):
        self.stop_flag = True

    def run(self):
        while not self.stop_flag:
            self.screen.fill(0)

            self.screen.blit(self.standIMG, (0, 0))
            blitRotate(self.screen, self.radarIMG, (self.radar.x, self.radar.y), (self.radar.size_x / 2 - 20, self.radar.size_y / 2), self.radar.a)
            rectRotated(self.screen, (255, 0, 0), (self.radar.x, self.radar.y), (self.radar.size_x / 2 - 20, self.radar.size_y / 2), self.radar.a)
            self.screen.blit(self.sputnikIMG, (self.sputnik.x, self.sputnik.y))
            pygame.draw.rect(self.screen, (255, 0, 0), (0, self.sputnik.centre, self.WIDTH, 2))

            pygame.display.update()
            self.clock.tick(self.FPS)

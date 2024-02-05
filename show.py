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

    def set_obj(self, radar, sputnik, barrier, mirror):
        self.radar, self.sputnik, self.barrier, self.mirror = radar, sputnik, barrier, mirror
        self.radarIMG = pygame.transform.scale(pygame.image.load('img\\radar.png').convert_alpha(),
                                               (self.radar.size_x, self.radar.size_y))
        self.sputnikIMG = pygame.transform.scale(pygame.image.load('img\\sputnik.png').convert_alpha(),
                                                 (self.sputnik.size_x, self.sputnik.size_y))
        self.barrierIMG = pygame.image.load('img\\barrier.png').convert_alpha()
        self.barriers = []
        self.mirrorIMG = pygame.image.load('img\\mirror.png').convert_alpha()
        self.mirrors = []

    def get_size(self):
        return self.WIDTH, self.HEIGHT

    def get_FPS(self):
        return self.FPS

    def stop(self):
        self.stop_flag = True

    def run(self):
        barrier = None
        mirror = None
        while not self.stop_flag:
            self.screen.fill(0)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not barrier and not mirror:
                    barrier = self.barrier()
                    barrier.set_y(pygame.mouse.get_pos()[1])
                if event.type == pygame.MOUSEMOTION and barrier:
                    barrier.set_size_y(abs(pygame.mouse.get_pos()[1] - barrier.get_y()))
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and barrier:
                    self.barriers.append(barrier)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and not mirror and not barrier:
                    mirror = self.mirror()
                    mirror.set_xy(*pygame.mouse.get_pos())
                if event.type == pygame.MOUSEMOTION and mirror:
                    mirror.set_size_x(abs(pygame.mouse.get_pos()[0] - mirror.get_x()))
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and mirror:
                    self.mirrors.append(mirror)

                if event.type == pygame.MOUSEBUTTONUP:
                    barrier = None
                    mirror = None
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                    self.stop()

            self.screen.blit(self.standIMG, (0, 0))
            blitRotate(self.screen, self.radarIMG, (self.radar.x, self.radar.y), (self.radar.size_x / 2 - 20, self.radar.size_y / 2), self.radar.a)
            rectRotated(self.screen, (255, 0, 0), (self.radar.x, self.radar.y), (self.radar.size_x / 2 - 20, self.radar.size_y / 2), self.radar.a)
            self.screen.blit(self.sputnikIMG, (self.sputnik.x, self.sputnik.y))
            pygame.draw.rect(self.screen, (255, 0, 0), (0, self.sputnik.centre, self.WIDTH, 2))

            if barrier:
                self.screen.blit(pygame.transform.scale(self.barrierIMG, barrier.get_size()), (barrier.x, barrier.y))
            for b in self.barriers:
                self.screen.blit(pygame.transform.scale(self.barrierIMG, b.get_size()), (b.x, b.y))
            if mirror:
                self.screen.blit(pygame.transform.scale(self.mirrorIMG, mirror.get_size()), (mirror.x, mirror.y))
            for m in self.mirrors:
                self.screen.blit(pygame.transform.scale(self.mirrorIMG, m.get_size()), (m.x, m.y))

            pygame.display.update()
            self.clock.tick(self.FPS)

        self.stop_flag = False

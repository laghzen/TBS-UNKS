# здесь подключаются модули
import pygame
import sys
import asyncio

from client2server import server
from funcs import blitRotate, rectRotated
from tracker import tracker

WIDTH, HEIGHT = 1304 // 2, 1477 // 2
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

c2s = server()
c2s.set_size(WIDTH, HEIGHT)

radar = c2s.radar
sputnik = c2s.sputnik

tracklog = open('tracklog.log', 'wb')
tracker = tracker()

standIMG = pygame.transform.scale(pygame.image.load('img\\stand.png').convert_alpha(), (c2s.WIDTH, c2s.HEIGHT))
radarIMG = pygame.transform.scale(pygame.image.load('img\\radar.png').convert_alpha(), (radar.size_x, radar.size_y))
sputnikIMG = pygame.transform.scale(pygame.image.load('img\\sputnik.png').convert_alpha(),
                                    (sputnik.size_x, sputnik.size_y))


async def core():
    time = 0
    while True:

        clock.tick(FPS)
        time += 1 / FPS
        if time >= 60 * 4.5:
            sys.exit()

        screen.fill(0)

        radar.updata()
        sputnik.updata(time)

        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        screen.blit(standIMG, (0, 0))
        blitRotate(screen, radarIMG, (radar.x, radar.y), (radar.size_x // 2, radar.size_y // 2), radar.a)
        rectRotated(screen, (255, 0, 0), (radar.x, radar.y), (radar.size_x // 2, radar.size_y // 2), radar.a)
        screen.blit(sputnikIMG, (sputnik.x, sputnik.y))
        pygame.draw.rect(screen, (255, 0, 0), (0, sputnik.centre, 593, 2))

        pygame.display.update()
        await asyncio.sleep(1/120)


async def main():
    task1 = loop.create_task(core())
    task2 = loop.create_task(tracker.run(tracklog))

    await asyncio.wait([task1, task2])

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
except:
    pass

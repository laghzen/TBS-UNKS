import pygame


def blitRotate(surf, image, pos, originPos, angle):
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    rotated_offset = offset_center_to_pivot.rotate(-angle)

    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    surf.blit(rotated_image, rotated_image_rect)

def rectRotated(surf, color, pos, originPos, angle):
    s = pygame.Surface((1304//2, 1477//2))
    s = s.convert_alpha()
    s.fill((0, 0, 0, 0))

    pygame.draw.rect(s, color, (0, originPos[1]-5, 1304, 2))

    blitRotate(surf, s, (pos[0], pos[1]), (originPos[0], originPos[1]), angle)


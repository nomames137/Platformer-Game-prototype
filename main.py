import pygame
import time
import random

pygame.init()

pygame.display.set_caption("The random game")

WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

BG = pygame.transform.scale(pygame.image.load("space.jpg"), (WIDTH, HEIGHT))

PLAYER_WIDTH  = 40
PLAYER_HEIGHT = 40

clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 30)

# ── stałe fizyki ──────────────────────────────────────────────
GROUND         = HEIGHT - PLAYER_HEIGHT
JUMP_VEL       = -17    # prędkość startowa skoku (ujemna = w górę)
GRAVITY        = 0.9    # normalna grawitacja
GRAVITY_LIGHT  = 0.5    # grawitacja gdy trzymasz spację i jedziesz w górę
VELOCITY       = 10     # prędkość pozioma
MOMENTUM       = 0.5

# ──── przeszkody ─────────────────────────────────────────────────────────
class Player:
    def __init__(self, player_x, player_y):
        self.player_x = player_x
        self.player_y = player_y
        pass

class Obstacle:
    def __init__(self, obs_x, obs_y, obs_height, obs_width, color):
        self.obs_x = obs_x
        self.obs_y = obs_y
        self.obs_height = obs_height
        self.obs_width = obs_width
        self.color = color
        pass


        



# ─────────────────────────────────────────────────────────────
def to_cartesian(pos):
    x, y = pos
    return x - WIDTH // 2, HEIGHT // 2 - y

def cursor():
    mouse_pos       = pygame.mouse.get_pos()
    x_cart, y_cart  = to_cartesian(mouse_pos)

    pygame.draw.circle(WIN, (255, 0, 0), mouse_pos, 5)

    text = font.render(f"X: {x_cart}, Y: {y_cart}", True, (255, 255, 255))
    WIN.blit(text, (10, 10))

    pygame.draw.line(WIN, (100, 100, 100), (WIDTH  // 2, 0),      (WIDTH  // 2, HEIGHT))
    pygame.draw.line(WIN, (100, 100, 100), (0,           HEIGHT // 2), (WIDTH, HEIGHT // 2))

def draw(player):
    WIN.blit(BG, (0, 0))
    pygame.draw.rect(WIN, 'red', player)



def shoot():
    pass

def change_color():
    pass

def ability():
    pass

# ─────────────────────────────────────────────────────────────

def main():
    running = True

    player_x   = 10
    player_y   = float(GROUND)   # gracz startuje na ziemi
    player     = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)

    vel_x      = 0.0
    vel_y      = 0.0
    on_wall    = False
    on_ground  = True
    is_jumping = False
    mov_left, mov_right = False, False

    circles = []

    while running:
        # ── zdarzenia ─────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and on_ground:
                    vel_y      = JUMP_VEL   # jednorazowy impuls
                    on_ground  = False
                    is_jumping = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    is_jumping = False       # puszczenie = koniec wydłużenia
                # if event.key == pygame.K_a and mov_left:
                #     vel_x += MOMENTUM
                #     player_x -= vel_x
                #     if vel_x >= VELOCITY:
                #         vel_x = 0
                #         mov_left = False

                # if event.key == pygame.K_d and mov_right:
                #     vel_x -= MOMENTUM
                #     player_x += vel_x
                #     if vel_x <= VELOCITY:
                #         vel_x = 0
                #         mov_right = False


            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    circles.append(pygame.mouse.get_pos())

        # ── ruch poziomy ──────────────────────────────────────
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            # vel_x = max(vel_x - MOMENTUM, -VELOCITY)   # przyspiesz w lewo
            vel_x = -VELOCITY
            mov_left = True
            mov_right = False
            # if on_wall:

        elif keys[pygame.K_d]:
            # vel_x = min(vel_x + MOMENTUM, VELOCITY)    # przyspiesz w prawo
            vel_x = VELOCITY
            mov_right = True
            mov_left = False
        else:
            # zwalnianie po puszczeniu
            if vel_x > 0 and not on_ground:
                vel_x = max(vel_x - MOMENTUM, 0)
            elif vel_x < 0 and not on_ground:
                vel_x = min(vel_x + MOMENTUM, 0)
            elif on_ground:
                vel_x = 0

        player_x += vel_x
        # if keys[pygame.K_a]:
        #     player_x -= VELOCITY
        #     mov_left = True
        #     mov_right = False
        # if keys[pygame.K_d]:
        #     player_x += VELOCITY
        #     mov_left = False
        #     mov_right = True

        player_x = max(0, min(WIDTH - PLAYER_WIDTH, player_x))

        # -- momentum w powietrzu ---------------------

        # if is_jumping and 

        # ── on_wall ─────────────────────────

       

        # ── fizyka skoku / grawitacja ─────────────────────────
        if is_jumping and vel_y < 0:
            # trzymasz spację i jedziesz w górę → wolniejsza grawitacja
            vel_y += GRAVITY_LIGHT
        else:
            vel_y += GRAVITY

        player_y += vel_y

        # kolizja z podłożem
        if player_y >= GROUND:
            player_y   = GROUND
            vel_y      = 0.0
            on_ground  = True
            is_jumping = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                vel_y      = JUMP_VEL
                on_ground  = False
                is_jumping = True

        # ── aktualizuj rect ───────────────────────────────────
        player.x = int(player_x)
        player.y = int(player_y)

        # ── rysowanie ─────────────────────────────────────────
        draw(player)
        cursor()
        for pos in circles:
            pygame.draw.circle(WIN, (255, 0, 0), pos, 10)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()

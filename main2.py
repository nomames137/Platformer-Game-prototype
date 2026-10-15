import pygame
import random

pygame.init()

pygame.display.set_caption("The random game Claude")

WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

BG = pygame.transform.scale(pygame.image.load("space.jpg"), (WIDTH, HEIGHT))

PLAYER_WIDTH  = 40
PLAYER_HEIGHT = 40

WALL_HEIGHT = 150
WALL_WIDTH = 80
FLOOR_HEIGHT = 40
FLOOR_WIDTH = 200

clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 30)

# ── stałe fizyki ──────────────────────────────────────────────
GROUND        = HEIGHT - PLAYER_HEIGHT

JUMP_VEL      = -18
GRAVITY       = 0.9
GRAVITY_LIGHT = 0.5
VELOCITY      = 10
MOMENTUM      = 0.4


# ── klasy ─────────────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vel_x      = 0.0
        self.vel_y      = 0.0
        self.hp         = 5
        self.on_ground  = True
        self.is_jumping = False
        self.mov_left   = False
        self.mov_right  = False
        self.hit_wall   = False
        self.rect = pygame.Rect(int(x), int(y), PLAYER_WIDTH, PLAYER_HEIGHT)


    def handle_horizontal(self, keys):
        if keys[pygame.K_a]:
            self.vel_x     = -VELOCITY
            self.mov_left  = True
            self.mov_right = False
        elif keys[pygame.K_d]:
            self.vel_x     = VELOCITY
            self.mov_right = True
            self.mov_left  = False
        else:
            if self.vel_x > 0 and not self.on_ground:
                self.vel_x = max(self.vel_x - MOMENTUM, 0)
            elif self.vel_x < 0 and not self.on_ground:
                self.vel_x = min(self.vel_x + MOMENTUM, 0)
            elif self.on_ground:
                self.vel_x = 0

        self.x += self.vel_x
        self.x  = max(0, min(WIDTH - PLAYER_WIDTH, self.x))

    def jump(self):
        self.vel_y      = JUMP_VEL
        self.on_ground  = False
        self.is_jumping = True

    def apply_physics(self, keys):
        self.on_ground = False
        # grawitacja
        if self.on_ground:
            self.vel_y = 0
            self.is_jumping = False
        elif not self.on_ground and not self.is_jumping:
            self.vel_y += GRAVITY
            self.y += self.vel_y
            
            self.on_ground = False
        if self.is_jumping and self.vel_y < 0:
            self.vel_y += GRAVITY
            self.y += self.vel_y
            
            
        elif self.vel_y > 0:
            self.is_jumping = False
        elif self.vel_y > 0 and self.on_ground:
            self.vel_y = 0
            self.is_jumping = False
        elif self.vel_y > 0:
            self.is_jumping = False

        # kolizja z podłożem
        if self.y >= GROUND:
            self.y          = GROUND
            self.vel_y      = 0.0
            self.on_ground  = True
            self.is_jumping = False
            # bunny hop — trzymasz spację przy lądowaniu
            if keys[pygame.K_SPACE] and self.on_ground:
                self.jump()

    def apply_collisions(self, obstacle_x, obstacle_y, obstacle_w, obstacle_h, keys):
        # Granice gracza
        player_left   = self.x
        player_right  = self.x + PLAYER_WIDTH
        player_top    = self.y
        player_bottom = self.y + PLAYER_HEIGHT

        # Granice ściany
        obstacle_left   = obstacle_x
        obstacle_right  = obstacle_x + obstacle_w
        obstacle_top    = obstacle_y
        obstacle_bottom = obstacle_y + obstacle_h

        # Sprawdź czy w ogóle zachodzi kolizja (AABB)
        if (player_right > obstacle_left and
            player_left  < obstacle_right and
            player_bottom > obstacle_top and
            player_top   < obstacle_bottom):

            overlap_left   = player_right - obstacle_left
            overlap_right  = obstacle_right   - player_left
            overlap_top    = player_bottom - obstacle_top
            overlap_bottom = obstacle_bottom   - player_top
            
            # Tylko strony zgodne z kierunkiem ruchu są kandydatami
            candidates = {}
            if self.vel_x > 0:
                candidates['left']  = overlap_left
            elif self.vel_x < 0:
                candidates['right'] = overlap_right
            elif self.vel_y >= 0 and self.on_ground:
                # stoi przy ścianie - użyj pozycji żeby określić stronę poziomą
                player_cx = self.x + PLAYER_WIDTH / 2
                wall_cx   = obstacle_x + obstacle_w / 2
                if player_cx <= wall_cx:
                    candidates['left']  = overlap_left
                else:
                    candidates['right'] = overlap_right
            if self.vel_y >= 0:
                candidates['top']    = overlap_top
            if self.vel_y <= 0:
                candidates['bottom'] = overlap_bottom

            if not candidates:
                return

            side = min(candidates, key=candidates.get)

            if side == 'left':
                self.x = obstacle_left - PLAYER_WIDTH
            elif side == 'right':
                self.x = obstacle_right
            elif side == 'top':
                self.y = obstacle_top - PLAYER_HEIGHT
                self.vel_y = 0
                self.on_ground = True
                self.is_jumping = False
                # if (player_right < obstacle_left) or (player_left > obstacle_right):
                #     self.on_ground = False
                if keys[pygame.K_SPACE] and self.on_ground:
                    self.jump()
            elif side == 'bottom':
                self.y          = obstacle_bottom
                self.vel_y      = 0.0
                self.is_jumping = False
            
            

    def update_rect(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self):
        if self.on_ground:
            pygame.draw.rect(WIN, 'green', self.rect)
        else:
            pygame.draw.rect(WIN, 'red', self.rect)

class Obstacle:
    class Floor:
        def __init__(self, x, y):
            self.width = FLOOR_WIDTH
            self.height = FLOOR_HEIGHT
            self.color = 'yellow'
            self.rect  = pygame.Rect(x, y, self.width, self.height)
        def draw(self):
            pygame.draw.rect(WIN, self.color, self.rect)

    class Wall:
        def __init__(self, x, y):
            self.width = WALL_WIDTH
            self.height = WALL_HEIGHT
            self.color = 'blue'
            self.rect  = pygame.Rect(x, y, self.width, self.height)
        def draw(self):
            pygame.draw.rect(WIN, self.color, self.rect)


# ── helpers ───────────────────────────────────────────────────
def to_cartesian(pos):
    x, y = pos
    return x - WIDTH // 2, HEIGHT // 2 - y

def cursor():
    mouse_pos      = pygame.mouse.get_pos()
    x_cart, y_cart = to_cartesian(mouse_pos)
    pygame.draw.circle(WIN, (255, 0, 0), mouse_pos, 5)
    text = font.render(f"X: {x_cart}, Y: {y_cart}", True, (255, 255, 255))
    WIN.blit(text, (10, 10))
    pygame.draw.line(WIN, (100, 100, 100), (WIDTH // 2, 0),  (WIDTH // 2, HEIGHT))
    pygame.draw.line(WIN, (100, 100, 100), (0, HEIGHT // 2), (WIDTH, HEIGHT // 2))

def generate_map(count=10):
    obstacles = []
    x, y = 300, HEIGHT - 200  # start
    for _ in range(count):
        obstacles.append((x, y, FLOOR_WIDTH, FLOOR_HEIGHT))
        # następna platforma: skok w prawo i trochę w górę/dół
        x += random.randint(150, 280)   # gap poziomy
        y += random.randint(-120, 80)   # zmiana wysokości
        y  = max(200, min(HEIGHT - 100, y))  # clamp żeby nie wychodziło poza ekran
    return obstacles

wall_x = 200
wall_y = HEIGHT - WALL_HEIGHT

floor_x = 500
floor_y = HEIGHT - WALL_HEIGHT
floor = Obstacle.Floor(floor_x, floor_y)
wall = Obstacle.Wall(wall_x, wall_y)

obstacles = [
    (floor_x, floor_y, FLOOR_WIDTH, FLOOR_HEIGHT),
    (wall_x,  wall_y,  WALL_WIDTH,  WALL_HEIGHT),
]
# ── pętla główna ──────────────────────────────────────────────
def main():
    generate_map()
    running = True
    player  = Player(10, GROUND)
    circles = []

    while running:
        # ── zdarzenia ─────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.on_ground:
                    player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player.is_jumping = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    circles.append(pygame.mouse.get_pos())

        # ── update ────────────────────────────────────────────
        keys = pygame.key.get_pressed()

        
        
        player.handle_horizontal(keys)
        player.apply_physics(keys)
        for obstacle in obstacles:
            player.apply_collisions(obstacle[0], obstacle[1], obstacle[2], obstacle[3], keys)
        player.update_rect()

        # ── rysowanie ─────────────────────────────────────────
        WIN.blit(BG, (0, 0))
        player.draw()
        wall.draw()
        floor.draw()
        cursor()
        for pos in circles:
            pygame.draw.circle(WIN, (255, 0, 0), pos, 10)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()

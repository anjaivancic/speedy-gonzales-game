import pygame

# se obrne slika ko greš v drugo stran
# pixel perfect collisions
# animacija ob zmagi - fireworks al neki
# restart če zgubiš


# initializing the gamee + basic setup
pygame.init()

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
GRID_SIZE = 60
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("The Speedy Gonzales Game")
clock = pygame.time.Clock()

# imports, baby (raw string reši moj problem "invalid escape sequence" al neki, idk man - "don't touch it if it works"?)
font = pygame.font.Font(r"MiA_game\files\font.otf", 20)

score_sound = pygame.mixer.Sound(r"MiA_game\files\score.mp3")
win_sound = pygame.mixer.Sound(r"MiA_game\files\win.mp3")
win_sound.set_volume(0.3)
game_music = pygame.mixer.Sound(r"MiA_game\files\background.mp3")
game_music.set_volume(0.5)
ouch_sound = pygame.mixer.Sound(r"MiA_game\files\ouch2.mp3")
ouch_sound.set_volume(0.5)
loss_sound = pygame.mixer.Sound(r"MiA_game\files\loss.mp3")
loss_sound.set_volume(1.5)

player_image = pygame.image.load(r"MiA_game\files\speedygonzales2.png").convert_alpha()
maze_image = pygame.image.load(r"MiA_game\files\wall3.png").convert_alpha()
kudos_image = pygame.image.load(r"MiA_game\files\kudos2.png").convert_alpha()
enemy_image = pygame.image.load(r"MiA_game\files\kneepain.png").convert_alpha()

game_music.play(loops=-1)


class Maze:
    def __init__(self):
        self.maze = [
            "11111111111111111111",  # 1 = wall, 0 = path
            "10000000000000000001",
            "10111111101111111001",
            "10100000000000101011",
            "10101111111110101001",
            "10100010000000101101",
            "10111010111110100001",
            "10001010100000101011",
            "10101010101010101001",
            "11111111111111111111",
        ]
        self.wall_rects = []
        self.image = maze_image
        self.image = pygame.transform.smoothscale(self.image, (GRID_SIZE, GRID_SIZE))
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.build_maze()  # tle sam enkrat zgradim maze, da se ne dela to vsak frame (been there, done that lol, rookie mistake)

    def build_maze(self):
        for y, row in enumerate(self.maze):  # vsako vrstico oštevilčimo
            for x, tile in enumerate(row):  # vsak element v vrstici
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                if tile == "1":  # wall
                    self.wall_rects.append(rect)
                    self.background.blit(self.image, rect)
                    pygame.draw.rect(self.background, "#292929", rect, width=2)
                else:
                    pygame.draw.rect(self.background, "#7a91ae", rect)

    def draw_maze(
        self,
    ):  # s to funkcijo narišem že zgrajen maze (background) vsak frame (called in the main loop)
        display_surface.blit(self.background, (0, 0))


class Player:
    def __init__(self, maze):
        self.image = player_image
        self.image = pygame.transform.smoothscale(self.image, (30, 50))
        self.rect = self.image.get_rect(center=(90, 90))
        self.speed = 300  # najhitrejša miška v Mehiki!
        self.maze = maze

    def update(self, dt):
        keys = pygame.key.get_pressed()
        dx = (
            (
                (keys[pygame.K_RIGHT] or keys[pygame.K_d])
                - (keys[pygame.K_LEFT] or keys[pygame.K_a])
            )
            * self.speed
            * dt
        )
        dy = (
            (
                (keys[pygame.K_DOWN] or keys[pygame.K_s])
                - (keys[pygame.K_UP] or keys[pygame.K_w])
            )
            * self.speed
            * dt
        )

        new_rect = self.rect.move(dx, 0)  # good logic to not get stuck on a wall
        if not self.collision_with_wall(new_rect):
            self.rect = new_rect

        new_rect = self.rect.move(0, dy)
        if not self.collision_with_wall(new_rect):
            self.rect = new_rect

    def collision_with_wall(self, rect):
        return any(
            rect.colliderect(wall) for wall in self.maze.wall_rects
        )  # returns True if we collide with ANY (it's right there in the name of the function, darling) rectangle from the list


class Light:
    def __init__(self):
        self.darkness = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
        )  # scralpha for transparency

    def draw_light(self):
        self.darkness.fill(
            (20, 20, 20, 253)
        )  # zadnja št je alpha value za transparency
        self.light_radius = 120

        pygame.draw.circle(
            self.darkness, (0, 0, 0, 0), player.rect.center, self.light_radius
        )  # transparent circle, zadnja št = 0
        display_surface.blit(self.darkness, (0, 0))


class Kudos:
    def __init__(self):
        self.image = kudos_image
        self.image = pygame.transform.smoothscale(self.image, (30, 30))
        self.count = 0

        self.positions = [
            (90, 510),
            (210, 450),
            (330, 510),
            (450, 510),
            (570, 510),
            (270, 330),
            (810, 510),
            (930, 210),
            (1110, 510),
            (1110, 150),
        ]
        self.rects = [
            self.image.get_rect(center=position) for position in self.positions
        ]

    def draw_kudos(self):
        for rect in self.rects:
            display_surface.blit(self.image, rect)

    def check_collection(self):
        collected = []

        for rect in self.rects:
            if player.rect.colliderect(rect):
                collected.append(rect)
                score_sound.play()
                self.count += 1

        for rect in collected:
            self.rects.remove(rect)


class Enemy:
    def __init__(self):
        self.image = enemy_image
        self.image = pygame.transform.smoothscale(self.image, (30, 40))

        # static enemies:
        self.positions = [(210, 510), (1110, 90)]
        self.rects = [
            self.image.get_rect(center=position) for position in self.positions
        ]

        # moving enemies:
        self.moving_positions = [(570, 90), (630, 450)]
        self.moving_rects = [
            self.image.get_rect(center=position) for position in self.moving_positions
        ]
        self.moving_dxs = [3, -3]
        self.moving_active = [True, True]

    def draw_enemy(self):  # static
        for rect in self.rects:
            display_surface.blit(self.image, rect)

    def move(self, bounds_list):  # moving
        for i, rect in enumerate(self.moving_rects):
            if self.moving_active[i]:
                x_min, x_max = bounds_list[i]
                if (
                    rect.left + self.moving_dxs[i] < x_min
                    or rect.right + self.moving_dxs[i] > x_max
                ):
                    self.moving_dxs[i] *= -1
                rect.x += self.moving_dxs[i]
                display_surface.blit(self.image, rect)

    def check_collision(self):
        collisions = []

        # static
        for rect in self.rects:
            if rect.colliderect(player.rect):
                collisions.append(rect)
                player.speed -= 100
                ouch_sound.play()

        for rect in collisions:
            self.rects.remove(rect)

        # moving
        for i, rect in enumerate(self.moving_rects):
            if self.moving_active[i] and rect.colliderect(player.rect):
                player.speed -= 100
                self.moving_active[i] = False
                ouch_sound.play()


class Message:
    def __init__(self):
        self.greeting = "Welcome to The Speedy Gonzales Game!\n\nYou are Speedy Gonzales, obviously.\nAnd what's the goal? Collect all kudos and you will recieve a secret message.\nBeware of your enemy though - knee pain will significantly reduce your speed.\n\nPress any key to start."
        self.final_message = "Wiii, you did it! Congratulations, you just became the KOM - king of my_heart <3"
        self.loss = "Oh naur, it looks like knee pain won this time.\nIt's so intense you can't move anymore.\nGame over! Take time to recover."

    def show_message(self, message):
        text_surf = font.render(
            message,
            True,
            "#FFFFFF",
        )
        text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        box_rect = text_rect.inflate(50, 30)  # a bigger text box
        pygame.draw.rect(display_surface, "#D15D0BFF", box_rect)
        pygame.draw.rect(display_surface, "#FFFFFF", box_rect, width=2)

        display_surface.blit(text_surf, text_rect)


# stvar k jo zmer pozabm nrdit potem k ustvarm class :) haha
maze = Maze()
player = Player(maze)
kudos = Kudos()
message = Message()
enemy = Enemy()
light = Light()


greeting = True
running = True
win = False
loss = False


# main loop
while running:
    dt = clock.tick(60) / 1000  # delta time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if greeting and event.type == pygame.KEYDOWN:
            greeting = False

    maze.draw_maze()
    player.update(dt)
    display_surface.blit(player.image, player.rect)
    kudos.draw_kudos()
    enemy.draw_enemy()
    enemy.move([(420, 720), (540, 840)])
    kudos.check_collection()
    enemy.check_collision()
    light.draw_light()

    if greeting:
        message.show_message(message.greeting)

    if kudos.count == len(kudos.positions):
        if not win:
            win_sound.play()
            win = True
        message.show_message(message.final_message)

    if player.speed <= 0:
        if not loss:
            loss_sound.play()
            loss = True
        message.show_message(message.loss)

    pygame.display.update()

pygame.quit()

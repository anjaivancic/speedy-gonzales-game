import pygame

# izboljšave:
# slika od playerja se obrne, ko greš v drugo stran
# pixel perfect collisions
# animacija ob zmagi - fireworks ipd
# restart logic, če zgubiš

class Maze:
    def __init__(self, game):
        self.game = game
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
        self.image = game.maze_image
        self.image = pygame.transform.smoothscale(
            self.image, (game.GRID_SIZE, game.GRID_SIZE)
        )
        self.background = pygame.Surface((game.WINDOW_WIDTH, game.WINDOW_HEIGHT))
        self.build_maze()  # tle sam enkrat zgradim maze, da se ne dela to vsak frame (been there, done that lol, rookie mistake)

    def build_maze(self):
        for y, row in enumerate(self.maze):  # vsako vrstico oštevilčimo
            for x, tile in enumerate(row):  # vsak element v vrstici
                rect = pygame.Rect(
                    x * self.game.GRID_SIZE,
                    y * self.game.GRID_SIZE,
                    self.game.GRID_SIZE,
                    self.game.GRID_SIZE,
                )
                if tile == "1":  # wall
                    self.wall_rects.append(rect)
                    self.background.blit(self.image, rect)
                    pygame.draw.rect(self.background, "#292929", rect, width=2)
                else:
                    pygame.draw.rect(self.background, "#7a91ae", rect)

    def draw_maze(
        self,
    ):  # s to funkcijo narišem že zgrajen maze (background) vsak frame (called in the main loop)
        game.display_surface.blit(self.background, (0, 0))


class Player:
    def __init__(self, game, maze):
        self.game = game
        self.image = game.player_image
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
    def __init__(self, game):
        self.game = game
        self.darkness = pygame.Surface(
            (game.WINDOW_WIDTH, game.WINDOW_HEIGHT), pygame.SRCALPHA
        )  # scralpha for transparency

    def draw_light(self):
        self.darkness.fill(
            (20, 20, 20, 253)
        )  # zadnja št je alpha value za transparency
        self.light_radius = 120

        pygame.draw.circle(
            self.darkness, (0, 0, 0, 0), game.player.rect.center, self.light_radius
        )  # transparent circle, zadnja št = 0
        game.display_surface.blit(self.darkness, (0, 0))


class Kudos:
    def __init__(self, game):
        self.game = game
        self.image = game.kudos_image
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
            game.display_surface.blit(self.image, rect)

    def check_collection(self):
        collected = []

        for rect in self.rects:
            if game.player.rect.colliderect(rect):
                collected.append(rect)
                game.score_sound.play()
                self.count += 1

        for rect in collected:
            self.rects.remove(rect)


class Enemy:
    def __init__(self, game):
        self.game = game
        self.image = game.enemy_image
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
            game.display_surface.blit(self.image, rect)

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
                game.display_surface.blit(self.image, rect)

    def check_collision(self):
        collisions = []

        # static
        for rect in self.rects:
            if rect.colliderect(game.player.rect):
                collisions.append(rect)
                game.player.speed -= 100
                game.ouch_sound.play()

        for rect in collisions:
            self.rects.remove(rect)

        # moving
        for i, rect in enumerate(self.moving_rects):
            if self.moving_active[i] and rect.colliderect(game.player.rect):
                game.player.speed -= 100
                self.moving_active[i] = False
                game.ouch_sound.play()


class Message:
    def __init__(self, game):
        self.game = game
        self.greeting = "Welcome to The Speedy Gonzales Game!\n\nYou are Speedy Gonzales, obviously.\nAnd what's the goal? Collect all kudos and you will recieve a secret message.\nBeware of your enemy though - knee pain will significantly reduce your speed.\n\nPress any key to start. And enjoy the journey for it won't be a long one."
        self.final_message = "Wiii, you did it! Congratulations, you just became the KOM - king of my_heart <3"
        self.loss = "Oh naur, it looks like knee pain won this time.\nIt's so bad you can't move anymore.\nGame over! Take time to recover.\n(Or run the code again cause I have no restart logic hahaha.)"

    def show_message(self, message):
        text_surf = game.font.render(
            message,
            True,
            "#FFFFFF",
        )
        text_rect = text_surf.get_rect(
            center=(game.WINDOW_WIDTH // 2, game.WINDOW_HEIGHT // 2)
        )

        box_rect = text_rect.inflate(50, 30)  # a bigger text box
        pygame.draw.rect(game.display_surface, "#A24A0BFF", box_rect)
        pygame.draw.rect(game.display_surface, "#FFFFFF", box_rect, width=2)

        game.display_surface.blit(text_surf, text_rect)

class Game:
    def __init__(self):
        # initializing the gamee + basic setup
        pygame.init()

        self.WINDOW_WIDTH = 1200
        self.WINDOW_HEIGHT = 600
        self.GRID_SIZE = 60
        self.display_surface = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("The Speedy Gonzales Game")
        self.clock = pygame.time.Clock()

        # imports, baby (raw string reši problem "invalid escape sequence ...", ampak boljš je, če daš poševnice v drugo stran)
        self.font = pygame.font.Font("files/font.otf", 20)
        self.score_sound = pygame.mixer.Sound("files/score.mp3")
        self.win_sound = pygame.mixer.Sound("files/win.mp3")
        self.loss_sound = pygame.mixer.Sound("files/loss.mp3")
        self.ouch_sound = pygame.mixer.Sound("files/ouch2.mp3")
        self.game_music = pygame.mixer.Sound("files/background.mp3")

        self.win_sound.set_volume(0.3)
        self.loss_sound.set_volume(1.5)
        self.ouch_sound.set_volume(0.5)
        self.game_music.set_volume(0.5)
        self.game_music.play(loops=-1)

        self.player_image = pygame.image.load(
            "files/speedygonzales2.png"
        ).convert_alpha()
        self.maze_image = pygame.image.load("files/wall3.png").convert_alpha()
        self.kudos_image = pygame.image.load(
            "files/kudos2.png"
        ).convert_alpha()
        self.enemy_image = pygame.image.load(
            "files/kneepain.png"
        ).convert_alpha()

        self.maze = Maze(self)
        self.player = Player(self, self.maze)
        self.kudos = Kudos(self)
        self.enemy = Enemy(self)
        self.message = Message(self)
        self.light = Light(self)

        self.greeting = True
        self.running = True
        self.win = False
        self.loss = False


    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.greeting and event.type == pygame.KEYDOWN:
                    self.greeting = False

            self.maze.draw_maze()
            self.player.update(dt)
            self.display_surface.blit(self.player.image, self.player.rect)
            self.kudos.draw_kudos()
            self.enemy.draw_enemy()
            self.enemy.move([(420, 720), (540, 840)])
            self.kudos.check_collection()
            self.enemy.check_collision()
            self.light.draw_light()

            if self.greeting:
                self.message.show_message(self.message.greeting)

            # win
            if self.kudos.count == len(self.kudos.positions):
                if not self.win:
                    self.win_sound.play()
                    self.win = True
                self.message.show_message(self.message.final_message)

            # loss
            if self.player.speed <= 0:
                if not self.loss:
                    self.loss_sound.play()
                    self.loss = True
                self.message.show_message(self.message.loss)

            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()

import pygame
import random
import asyncio

class Coin:
    def __init__(self, image, screen_height):
        self.image = image
        self.x = random.randint(120 - image.get_width(), 820 - image.get_width() - 120)
        self.y = random.randint(-200, -10)
        self.speed = 1
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.screen_height = screen_height

    def move(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def off_screen(self):
        return self.y + self.image.get_height() >= self.screen_height


class Monster:
    def __init__(self, image, screen_height, screen_width, monster_delay):
        self.image = image
        self.y = screen_height - self.image.get_height()
        self.speed = 2
        self.direction = random.choice([-1, 1])  # Randomly choose direction
        self.x = -self.image.get_width() if self.direction == 1 else screen_width  # Set x coordinate based on direction
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.screen_width = screen_width
        self.monster_delay = monster_delay

    def move(self):
        if self.direction == 1:  # Move right
            self.x += self.speed
        else:  # Move left
            self.x -= self.speed
        self.rect.x = self.x

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def off_screen(self):
        return not (-self.image.get_width() < self.x < self.screen_width)


class Peli:
    def __init__(self):
        pygame.init()

        # Screen
        self.screen_width = 820
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Coins & Creatures")
        self.clock = pygame.time.Clock()

        # Robot image
        self.robot_image = pygame.image.load("robo.png")
        self.robot_rect = self.robot_image.get_rect()
        self.robot_rect.center = (self.screen_width // 2, self.screen_height - self.robot_rect.height // 2)

        # Robot movement
        self.robot_moving_left = False
        self.robot_moving_right = False
        self.robot_isJumping = False
        self.robot_jumpCount = 10

        # Coins
        self.coin_image = pygame.image.load("kolikko.png")
        self.coins = []
        self.coin_delay = 3500
        self.last_coin_spawn_time = pygame.time.get_ticks()

        # Monsters
        self.monster_image = pygame.image.load("hirvio.png")
        self.monsters = []
        self.last_monster_spawn_time = pygame.time.get_ticks()

        # Fonts
        self.font_small = pygame.font.Font("Roboto-Regular.ttf", 18)
        self.font_medium = pygame.font.Font("Jaro-Regular-VariableFont_opsz.ttf", 24)
        self.font_large = pygame.font.Font("Jaro-Regular-VariableFont_opsz.ttf", 36)
        self.font_xlarge = pygame.font.Font("Jaro-Regular-VariableFont_opsz.ttf", 60)

        # Misc
        self.points = 0
        self.star_positions = [(random.randint(0, self.screen_width), random.randint(0, self.screen_height // 3)) for _ in range(30)]
        self.game_over = False
        self.death_by_monster = False
        self.coin_dropped = False

    # HELPER METHODS

    def draw_text(self, text, position, font, center=True):
        text_surface = font.render(text, True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=position if center else position)
        if not center:
            text_rect = position
        self.screen.blit(text_surface, text_rect)

    def vertical_gradient(self, top_color, bottom_color):
        height = self.screen_height
        for y in range(height):
            color = (
                top_color[0] * (1 - y / height) + bottom_color[0] * (y / height),
                top_color[1] * (1 - y / height) + bottom_color[1] * (y / height),
                top_color[2] * (1 - y / height) + bottom_color[2] * (y / height)
            )
            pygame.draw.rect(self.screen, color, pygame.Rect(0, y, self.screen_width, 1))

    def draw_stars(self):
        for position in self.star_positions:
            star = self.font_small.render('*', True, (255, 255, 255))
            self.screen.blit(star, position)

    # ROBOT METHODS & EVENT HANDLER

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.robot_moving_left = True
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.robot_moving_right = True
                elif event.key == pygame.K_SPACE:
                    if not self.robot_isJumping:
                        self.robot_isJumping = True
                        self.robot_jumpCount = 10
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.robot_moving_left = False
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.robot_moving_right = False

    def move_robot(self):
        if self.robot_moving_left:
            self.robot_rect.x -= 3
        if self.robot_moving_right:
            self.robot_rect.x += 3
        if self.robot_isJumping:
            if self.robot_jumpCount >= -10:
                self.robot_rect.y -= (self.robot_jumpCount * abs(self.robot_jumpCount)) * 0.3
                self.robot_jumpCount -= 0.5
            else:
                self.robot_isJumping = False
                self.robot_rect.y = self.screen_height - self.robot_rect.height

        self.robot_rect.x = max(0, min(self.robot_rect.x, self.screen_width - self.robot_rect.width))

    # COIN METHODS

    def create_coins(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_coin_spawn_time >= self.coin_delay:
            self.coins.append(Coin(self.coin_image, self.screen_height))
            self.last_coin_spawn_time = current_time

    def move_coins(self):
        for coin in self.coins:
            coin.move()
            if coin.off_screen():
                self.game_over = True
                self.coin_dropped = True

    def draw_coins(self):
        for coin in self.coins:
            coin.draw(self.screen)

    def check_coin_collision(self):
        for coin in self.coins:
            if self.robot_rect.colliderect(coin.rect):
                self.coins.remove(coin)
                self.points += 1

    # MONSTER METHODS

    def create_monsters(self):
        current_time = pygame.time.get_ticks()
        monster_delay = max(1200, 8000 - ((self.points // 3) * 400))  # Adjust delay on every * points
        if current_time - self.last_monster_spawn_time >= monster_delay:
            self.monsters.append(Monster(self.monster_image, self.screen_height, self.screen_width, monster_delay))
            self.last_monster_spawn_time = current_time

    def move_monsters(self):
        for monster in self.monsters:
            monster.move()
            if monster.off_screen():
                self.monsters.remove(monster)

    def draw_monsters(self):
        for monster in self.monsters:
            monster.draw(self.screen)

    def check_monster_collision(self):
        for monster in self.monsters:
            if self.robot_rect.colliderect(monster.rect.inflate(-25, -5)):
                self.game_over = True
                self.death_by_monster = True

  # SCREENS

    async def starting_screen(self):
        while True:
            self.screen.fill((0, 0, 0))
            self.draw_text("Coins & Creatures", (self.screen_width // 2, 100), self.font_xlarge)
            self.draw_text("Collect coins and avoid monsters", (self.screen_width // 2, 150), self.font_medium)
            self.draw_text("But beware: the more coins you collect the harder it gets", (self.screen_width // 2, 200), self.font_medium)
            self.draw_text("Use LEFT and RIGHT arrow keys (or A & D) to move", (self.screen_width // 2, 400), self.font_small)
            self.draw_text("SPACE to jump", (self.screen_width // 2, 430), self.font_small)
            self.draw_text("Press SPACE to start", (self.screen_width // 2, 550), self.font_small)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return
            await asyncio.sleep(0)

    async def game_over_screen(self):
        while True:
            self.screen.fill((0, 0, 0))
            self.draw_text("Game Over", (self.screen_width // 2, 100), self.font_xlarge)
            if self.death_by_monster:
                self.draw_text("Mauled by a monster!", (self.screen_width // 2, 150), self.font_medium)
            else:
                self.draw_text("You missed a coin...", (self.screen_width // 2, 150), self.font_medium)
            self.draw_text(f"Points: {self.points}", (self.screen_width // 2, 350), self.font_large)
            self.draw_text("Press R to restart", (self.screen_width // 2, 400), self.font_small)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        return
            await asyncio.sleep(0)

    # RESET GAME

    def reset_game(self):
        self.last_coin_spawn_time = pygame.time.get_ticks()
        self.last_monster_spawn_time = pygame.time.get_ticks()
        self.robot_moving_left = False
        self.robot_moving_right = False
        self.robot_isJumping = False
        self.game_over = False
        self.points = 0
        self.monsters = []
        self.coins = []
        self.robot_rect.center = (self.screen_width // 2, self.screen_height - self.robot_rect.height // 2)
        self.death_by_monster = False
        self.coin_dropped = False

    async def game_loop(self):
        await self.starting_screen()
        self.reset_game()

        while not self.game_over:
            self.handle_events()
            self.move_robot()
            self.create_monsters()
            self.move_monsters()
            self.check_monster_collision()
            self.check_coin_collision()
            self.create_coins()
            self.move_coins()

            self.vertical_gradient((0, 0, 0), (0, 0, 255))
            self.draw_stars()
            self.draw_coins()
            self.draw_text(f"Points: {self.points}", (self.screen_width - 165, 5), self.font_large, center=False)

            self.screen.blit(self.robot_image, self.robot_rect)
            self.draw_monsters()

            pygame.display.flip()
            self.clock.tick(60)
            await asyncio.sleep(0)

            if self.game_over:
                await self.game_over_screen()



game = Peli()
asyncio.run(game.game_loop())
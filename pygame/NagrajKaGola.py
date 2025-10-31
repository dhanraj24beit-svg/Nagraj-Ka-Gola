import pygame
import random
import os

pygame.mixer.init()
pygame.init()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600


class SnakeGame:
    def __init__(self):
        self.game_window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nagraj ka gola")

        # Background
        self.bgimg = pygame.image.load("snake.jpg")
        self.bgimg = pygame.transform.scale(self.bgimg, (SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()

        # Fonts
        self.font = pygame.font.SysFont(None, 55)
        self.font_small = pygame.font.SysFont(None, 35)

        # Clock
        self.clock = pygame.time.Clock()

        # Highscore file
        if not os.path.exists("highscore.txt"):
            with open("highscore.txt", "w") as f:
                f.write("0")
        self.highscore = self.get_highscore()

    # ------------------------ HIGH SCORE ------------------------
    def get_highscore(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def update_highscore(self, score):
        if score > self.highscore:
            self.highscore = score
            with open("highscore.txt", "w") as f:
                f.write(str(score))

    # ------------------------ DRAW TEXT ------------------------
    def draw_text(self, text, color, x, y, small=False):
        font = self.font_small if small else self.font
        screen_text = font.render(text, True, color)
        self.game_window.blit(screen_text, [x, y])

    def display_stats(self, score, level, lives):
        stats_text = f"SCORE: {score}    HIGH SCORE: {self.highscore}    LEVEL: {level}    LIVES: {lives}"
        screen_text = self.font_small.render(stats_text, True, RED)
        self.game_window.blit(screen_text, [10, 10])

    # ------------------------ SNAKE DRAW ------------------------
    def plot_snake(self, snake_list, snake_size, color=BLACK):
        for x, y in snake_list:
            pygame.draw.rect(self.game_window, color, [x, y, snake_size, snake_size])

    # ------------------------ WELCOME ------------------------
    def welcome(self):
        exit_game = False
        while not exit_game:
            self.game_window.fill((233, 210, 229))
            self.game_window.blit(self.bgimg, (0, 0))
            self.draw_text("Welcome to Nagraj House", BLACK, 260, 250)
            self.draw_text("Press Space Bar To Play", BLACK, 232, 290)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    try:
                        pygame.mixer.music.load("snake.mp3")
                        pygame.mixer.music.play()
                    except:
                        pass
                    self.gameloop()

            pygame.display.update()
            self.clock.tick(60)

    # ------------------------ FOOD GENERATION ------------------------
    def generate_food(self, blocks, snake_size):
        while True:
            food_x = random.randint(20, SCREEN_WIDTH - snake_size - 20)
            food_y = random.randint(20, SCREEN_HEIGHT - snake_size - 20)
            collision = False
            for bx, by, bw, bh in blocks:
                if bx < food_x + snake_size and bx + bw > food_x and by < food_y + snake_size and by + bh > food_y:
                    collision = True
                    break
            if not collision:
                return food_x, food_y

    # ------------------------ ENEMY AI ------------------------
    def move_enemy_towards_food(self, ex, ey, food_x, food_y, velocity):
        """Simple AI: move enemy snake toward the food."""
        if abs(ex - food_x) > abs(ey - food_y):
            if ex < food_x:
                ex += velocity
            else:
                ex -= velocity
        else:
            if ey < food_y:
                ey += velocity
            else:
                ey -= velocity
        return ex, ey

    # ------------------------ GAME LOOP ------------------------
    def gameloop(self):
        exit_game = False
        game_over = False

        # Player snake attributes
        snake_x, snake_y = 45, 55
        velocity_x, velocity_y = 0, 0
        init_velocity = 5
        snake_size = 20
        snake_list = []
        snake_length = 1

        score = 0
        level = 1
        last_level = 1
        lives = 1
        fps = 60

        # Enemy snake (only active at level 3)
        enemy_active = False
        enemy_x, enemy_y = 800, 500
        enemy_velocity = 3
        enemy_list = []
        enemy_length = 1
        enemy_score = 0

        # Function to make obstacle blocks
        def create_blocks(level):
            num_blocks = level * 3
            block_size = snake_size + 10
            new_blocks = []
            for _ in range(num_blocks):
                x = random.randint(20, SCREEN_WIDTH - block_size)
                y = random.randint(20, SCREEN_HEIGHT - block_size)
                new_blocks.append([x, y, block_size, block_size])
            return new_blocks

        blocks = create_blocks(level)
        food_x, food_y = self.generate_food(blocks, snake_size)

        # Big food vars
        big_food_active = False
        big_food_timer = 0
        big_food_x, big_food_y = 0, 0
        big_food_radius = 15

        # Level 3 variables
        level3_started = False
        winner = None

        while not exit_game:
            if game_over:
                self.game_window.fill(WHITE)
                self.draw_text("Game Over! Press Enter To Replay", RED, 100, 250)
                self.draw_text(f"HIGH SCORE : {self.highscore}", RED, 300, 300)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit_game = True
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.__init__()
                        self.gameloop()
                        return
            else:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit_game = True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RIGHT:
                            velocity_x = init_velocity
                            velocity_y = 0
                        if event.key == pygame.K_LEFT:
                            velocity_x = -init_velocity
                            velocity_y = 0
                        if event.key == pygame.K_UP:
                            velocity_y = -init_velocity
                            velocity_x = 0
                        if event.key == pygame.K_DOWN:
                            velocity_y = init_velocity
                            velocity_x = 0

                # Move player
                snake_x += velocity_x
                snake_y += velocity_y

                # Level update
                if score >= 100:
                    level = 3
                elif score >= 50:
                    level = 2
                else:
                    level = 1

                if level > last_level:
                    blocks = create_blocks(level)
                    try:
                        pygame.mixer.music.load("levelup.mp3")
                        pygame.mixer.music.play()
                    except:
                        pass
                    big_food_active = True
                    big_food_timer = pygame.time.get_ticks()
                    big_food_x, big_food_y = self.generate_food(blocks, big_food_radius * 2)

                # -------- LEVEL 3: Activate enemy --------
                if level == 3 and not level3_started:
                    enemy_active = True
                    score = 0
                    enemy_score = 0
                    snake_list, enemy_list = [], []
                    snake_length = enemy_length = 1
                    snake_x, snake_y = 100, 100
                    enemy_x, enemy_y = 700, 500
                    try:
                        pygame.mixer.music.load("levelup.mp3")
                        pygame.mixer.music.play()
                    except:
                        pass
                    level3_started = True
                    winner = None
                    food_x, food_y = self.generate_food(blocks, snake_size)

                last_level = level
                fps = 60 + (level - 1) * 20

                # Draw background
                self.game_window.fill(WHITE)
                self.game_window.blit(self.bgimg, (0, 0))

                # Display stats
                if level < 3:
                    self.display_stats(score, level, lives)
                else:
                    self.draw_text(f"YOU: {score}    ENEMY: {enemy_score}", RED, 260, 10, small=True)

                # Draw normal food
                pygame.draw.rect(self.game_window, RED, [food_x, food_y, snake_size, snake_size])

                # Draw blocks
                for block in blocks:
                    pygame.draw.rect(self.game_window, YELLOW, block)

                # Big food draw
                if big_food_active:
                    current_time = pygame.time.get_ticks()
                    if current_time - big_food_timer <= 6000:
                        pygame.draw.circle(
                            self.game_window,
                            GREEN,
                            (big_food_x + big_food_radius, big_food_y + big_food_radius),
                            big_food_radius,
                        )
                        if abs(snake_x - big_food_x) < big_food_radius + snake_size and abs(snake_y - big_food_y) < big_food_radius + snake_size:
                            lives += 1
                            big_food_active = False
                    else:
                        big_food_active = False

                # Update snake list
                head = [snake_x, snake_y]
                snake_list.append(head)
                if len(snake_list) > snake_length:
                    del snake_list[0]

                # Enemy movement
                if enemy_active:
                    enemy_x, enemy_y = self.move_enemy_towards_food(enemy_x, enemy_y, food_x, food_y, enemy_velocity)
                    enemy_head = [enemy_x, enemy_y]
                    enemy_list.append(enemy_head)
                    if len(enemy_list) > enemy_length:
                        del enemy_list[0]

                # Food collision
                if abs(snake_x - food_x) < 15 and abs(snake_y - food_y) < 15:
                    score += 10
                    snake_length += 3
                    food_x, food_y = self.generate_food(blocks, snake_size)
                if enemy_active and abs(enemy_x - food_x) < 15 and abs(enemy_y - food_y) < 15:
                    enemy_score += 10
                    enemy_length += 3
                    food_x, food_y = self.generate_food(blocks, snake_size)

                # Winner check (only level 3)
                if level3_started:
                    if score >= 100:
                        winner = "YOU WIN!"
                    elif enemy_score >= 100:
                        winner = "ENEMY WINS!"
                    if winner:
                        self.game_window.fill(WHITE)
                        self.draw_text(winner, RED, 300, 250)
                        self.draw_text("Press Enter to Play Again", BLACK, 220, 300)
                        pygame.display.update()
                        try:
                            pygame.mixer.music.load("expo.mp3")
                            pygame.mixer.music.play()
                        except:
                            pass
                        waiting = True
                        while waiting:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    exit_game = True
                                    waiting = False
                                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                                    self.__init__()
                                    self.gameloop()
                                    return

                # Collision checks
                collision = False
                if head in snake_list[:-1]:
                    collision = True
                if snake_x < 0 or snake_x >= SCREEN_WIDTH or snake_y < 0 or snake_y >= SCREEN_HEIGHT:
                    collision = True
                for bx, by, bw, bh in blocks:
                    if bx < snake_x + snake_size and bx + bw > snake_x and by < snake_y + snake_size and by + bh > snake_y:
                        collision = True

                if collision:
                    if lives > 1:
                        lives -= 1
                        snake_x, snake_y = 45, 55
                        velocity_x = velocity_y = 0
                        snake_list = []
                        snake_length = 1
                    else:
                        game_over = True
                        self.update_highscore(score)
                        try:
                            pygame.mixer.music.load("expo.mp3")
                            pygame.mixer.music.play()
                        except:
                            pass

                # Draw snakes
                self.plot_snake(snake_list, snake_size, BLACK)
                if enemy_active:
                    self.plot_snake(enemy_list, snake_size, BLUE)

            pygame.display.update()
            self.clock.tick(fps)

        pygame.quit()
        quit()


if __name__ == "__main__":
    game = SnakeGame()
    game.welcome()

import pygame
import random
import os
import math

# -------------------- INITIALIZATION --------------------
pygame.init()
pygame.mixer.init()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Screen
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
GAME_WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Nagraj ka Gola")

# Background
bgimg = pygame.image.load("snake.jpg")
bgimg = pygame.transform.scale(bgimg, (SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 50)

# Highscore setup
if not os.path.exists("hiscore.txt"):
    with open("hiscore.txt", "w") as f:
        f.write("0")

# -------------------- UTILITY --------------------
def text_screen(text, color, x, y, size=50):
    font_local = pygame.font.SysFont(None, size)
    screen_text = font_local.render(text, True, color)
    GAME_WINDOW.blit(screen_text, [x, y])

# -------------------- CLASSES --------------------
class Snake:
    def __init__(self, x, y, size, snake_type=1):
        self.x = x
        self.y = y
        self.size = size
        self.velocity_x = 0
        self.velocity_y = 0
        self.body = []
        self.length = 1
        self.snake_type = snake_type
        self.lives = 1

    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

    def grow(self, amount=5):
        self.length += amount

    def reset_length(self):
        self.length = 1

    def draw(self, frame_count):
        for i, (x, y) in enumerate(self.body):
            color = self.get_color(frame_count, i)
            pygame.draw.rect(GAME_WINDOW, color, [x, y, self.size, self.size])

    def get_color(self, frame_count, i):
        t = self.snake_type
        if t == 1:
            return BLACK
        elif t == 2:
            return (
                int(128 + 127 * math.sin((frame_count + i) * 0.15)),
                int(128 + 127 * math.sin((frame_count + i) * 0.2)),
                int(128 + 127 * math.sin((frame_count + i) * 0.25)),
            )
        else:
            return BLACK

    def update_body(self):
        head = [self.x, self.y]
        self.body.append(head)
        if len(self.body) > self.length:
            del self.body[0]

    def check_self_collision(self):
        return [self.x, self.y] in self.body[:-1]

class Food:
    def __init__(self, snake_size):
        self.size = snake_size
        self.x = random.randint(20, SCREEN_WIDTH - 40)
        self.y = random.randint(20, SCREEN_HEIGHT - 40)
        self.big_food_active = False
        self.big_food_frame = 0
        self.big_food_size = snake_size * 2
        self.big_food_x = 0
        self.big_food_y = 0
        self.big_food_eaten = False
        self.eaten_count = 0  # Count normal foods eaten

    def respawn(self):
        self.x = random.randint(20, SCREEN_WIDTH - 40)
        self.y = random.randint(20, SCREEN_HEIGHT - 40)

    def draw(self):
        pygame.draw.rect(GAME_WINDOW, RED, [self.x, self.y, self.size, self.size])

    def check_collision(self, snake_x, snake_y):
        return abs(snake_x - self.x) < self.size and abs(snake_y - self.y) < self.size

    def spawn_big_food(self, snake):
        # Show big food every 5 normal foods eaten
        if self.eaten_count != 0 and self.eaten_count % 5 == 0 and not self.big_food_active and not self.big_food_eaten:
            self.big_food_x = random.randint(50, SCREEN_WIDTH - 50)
            self.big_food_y = random.randint(50, SCREEN_HEIGHT - 50)
            self.big_food_active = True
            self.big_food_frame = 0

    def draw_big_food(self, snake):
        if self.big_food_active:
            self.big_food_frame += 1
            glow = int(128 + 127 * math.sin(self.big_food_frame * 0.15))
            color = (255, glow, 0)
            pygame.draw.rect(GAME_WINDOW, color, [self.big_food_x, self.big_food_y, self.big_food_size, self.big_food_size])

            # Collision with snake
            if (snake.x + snake.size > self.big_food_x and snake.x < self.big_food_x + self.big_food_size and
                snake.y + snake.size > self.big_food_y and snake.y < self.big_food_y + self.big_food_size):
                snake.lives += 1
                self.big_food_active = False
                self.big_food_eaten = True
                self.eaten_count = 0  # Reset count after big food

class Block:
    def __init__(self, num_blocks, size):
        self.size = size
        self.blocks = self.generate_blocks(num_blocks)

    def generate_blocks(self, num):
        return [[random.randint(50, SCREEN_WIDTH - 70), random.randint(50, SCREEN_HEIGHT - 70)] for _ in range(num)]

    def draw(self):
        for bx, by in self.blocks:
            pygame.draw.rect(GAME_WINDOW, YELLOW, [bx, by, self.size, self.size])

    def check_collision(self, snake_x, snake_y, snake_size):
        for bx, by in self.blocks:
            if (snake_x + snake_size > bx and snake_x < bx + self.size and
                snake_y + snake_size > by and snake_y < by + self.size):
                return True
        return False

class EnemySnake(Snake):
    def __init__(self, x, y, size, speed):
        super().__init__(x, y, size, snake_type=2)
        self.speed = speed
        self.velocity_x = speed
        self.velocity_y = 0

    def move_enemy(self):
        # Simple AI: bounce off walls
        self.x += self.velocity_x
        self.y += self.velocity_y
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.size:
            self.velocity_x *= -1
        if self.y <= 0 or self.y >= SCREEN_HEIGHT - self.size:
            self.velocity_y *= -1
        # Randomly change direction
        if random.randint(0, 50) == 0:
            self.velocity_x = random.choice([-self.speed, 0, self.speed])
            self.velocity_y = random.choice([-self.speed, 0, self.speed])

# -------------------- GAME CLASS --------------------
class Game:
    def __init__(self):
        self.exit_game = False
        self.game_over = False
        self.score = 0
        self.level = 1
        self.init_velocity = 5
        self.fps = 60
        self.frame_count = 0
        self.snake = Snake(45, 55, 20)
        self.food = Food(self.snake.size)
        self.block = Block(self.level, 30)
        self.enemy = None  # Enemy snake will appear in level 3

        with open("hiscore.txt", "r") as f:
            self.hiscore = int(f.read())

        self.level_up_sound = pygame.mixer.Sound("levelup.mp3") if os.path.exists("levelup.mp3") else None

    def welcome(self):
        while not self.exit_game:
            GAME_WINDOW.fill((233, 210, 229))
            GAME_WINDOW.blit(bgimg, (0, 0))
            text_screen("Welcome to Nagraj House", BLACK, 260, 250)
            text_screen("Press Space Bar To Play", BLACK, 250, 300)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if os.path.exists("snake.mp3"):
                        pygame.mixer.music.load("snake.mp3")
                        pygame.mixer.music.play(-1)
                    self.game_loop()
            pygame.display.update()
            clock.tick(60)

    def update_score(self):
        if self.score > self.hiscore:
            self.hiscore = self.score

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_game = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.snake.velocity_x = self.init_velocity
                    self.snake.velocity_y = 0
                elif event.key == pygame.K_LEFT:
                    self.snake.velocity_x = -self.init_velocity
                    self.snake.velocity_y = 0
                elif event.key == pygame.K_UP:
                    self.snake.velocity_y = -self.init_velocity
                    self.snake.velocity_x = 0
                elif event.key == pygame.K_DOWN:
                    self.snake.velocity_y = self.init_velocity
                    self.snake.velocity_x = 0

    def check_collisions(self):
        if (self.snake.x <= 0 or self.snake.x >= SCREEN_WIDTH - self.snake.size or
            self.snake.y <= 0 or self.snake.y >= SCREEN_HEIGHT - self.snake.size or
            self.snake.check_self_collision() or
            self.block.check_collision(self.snake.x, self.snake.y, self.snake.size)):
            self.snake.lives -= 1
            if self.snake.lives <= 0:
                self.game_over = True
            else:
                self.snake.reset_length()
                self.snake.x = 45
                self.snake.y = 55
                self.snake.velocity_x = 0
                self.snake.velocity_y = 0

        if self.enemy:
            if (self.enemy.x <= 0 or self.enemy.x >= SCREEN_WIDTH - self.enemy.size or
                self.enemy.y <= 0 or self.enemy.y >= SCREEN_HEIGHT - self.enemy.size or
                self.enemy.check_self_collision()):
                self.enemy.velocity_x *= -1
                self.enemy.velocity_y *= -1

    def game_loop(self):
        while not self.exit_game:
            self.frame_count += 1
            if self.game_over:
                with open("hiscore.txt", "w") as f:
                    f.write(str(self.hiscore))
                GAME_WINDOW.fill(WHITE)
                GAME_WINDOW.blit(bgimg, (0, 0))
                text_screen("Game Over! Press Enter To Replay", RED, 150, 250)
                text_screen(f"Your Score: {self.score} | High Score: {self.hiscore}", BLACK, 200, 310)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.exit_game = True
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.__init__()
                        self.welcome()
                continue

            self.handle_events()
            self.snake.move()
            if self.enemy:
                self.enemy.move_enemy()

            # Food collision
            if self.food.check_collision(self.snake.x, self.snake.y):
                self.score += 10
                self.food.respawn()
                self.snake.grow()
                self.food.eaten_count += 1
                if self.score % 50 == 0:
                    self.level += 1
                    self.init_velocity += 1
                    if self.level_up_sound:
                        self.level_up_sound.play()
                    self.block.blocks.extend(self.block.generate_blocks(1))
                    if self.level <= 2:
                        self.snake.snake_type = self.level

                # Level 3: spawn enemy
                if self.level == 3 and self.enemy is None:
                    self.enemy = EnemySnake(800, 500, self.snake.size, self.init_velocity - 1)

                self.update_score()

            # Big food
            self.food.spawn_big_food(self.snake)
            self.food.draw_big_food(self.snake)

            # Draw everything
            GAME_WINDOW.fill(WHITE)
            GAME_WINDOW.blit(bgimg, (0, 0))
            text_screen(f"SCORE: {self.score}  HISCORE: {self.hiscore}  LEVEL: {self.level}  LIVES: {self.snake.lives}", RED, 5, 5)

            self.food.draw()
            self.block.draw()
            self.snake.update_body()
            self.snake.draw(self.frame_count)
            if self.enemy:
                self.enemy.update_body()
                self.enemy.draw(self.frame_count)

            self.check_collisions()

            # Check win condition in level 3
            if self.level == 3 and self.enemy:
                if self.score >= 200:
                    text_screen("You Win!", GREEN, 350, 250, 60)
                    pygame.display.update()
                    pygame.time.delay(3000)
                    self.game_over = True
                elif self.enemy.length >= 30:  # Enemy reaching length 30 as example
                    text_screen("Enemy Wins!", RED, 350, 250, 60)
                    pygame.display.update()
                    pygame.time.delay(3000)
                    self.game_over = True

            pygame.display.update()
            clock.tick(self.fps)

        pygame.quit()
        quit()

# -------------------- START GAME --------------------
if __name__ == "__main__":
    game = Game()
    game.welcome()

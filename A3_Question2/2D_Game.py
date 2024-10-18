import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle")

# Load and scale images
def load_scale_image(path, scale_factor):
    img = pygame.image.load(path).convert_alpha()
    new_size = (int(WIDTH * scale_factor), int(WIDTH * scale_factor))
    return pygame.transform.scale(img, new_size)

hero_img = load_scale_image("hero.png", 0.05)  # Green tank
enemy_img = load_scale_image("enemy.png", 0.05)  # Purple tank
boss_img = load_scale_image("boss.png", 0.15)  # Red tank
bullet_img = load_scale_image("bullet.png", 0.02)
background = pygame.image.load("background.webp").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Power-up images
x2_img = load_scale_image("x2.png", 0.05)
health_img = load_scale_image("first_aid.png", 0.05)
invincibility_img = load_scale_image("invinsibility.png", 0.05)
ammo_img = load_scale_image("ammo_box.png", 0.05)

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

class Tank(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.bullets = 50

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self):
        if self.shoot_cooldown == 0 and self.bullets > 0:
            self.shoot_cooldown = 30
            self.bullets -= 1
            return Bullet(self.rect.centerx, self.rect.centery, 5, self.rect.right < WIDTH // 2)
        return None

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw_health_bar(self, surface):
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, self.rect.width, 5))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, self.rect.width * health_ratio, 5))

class Player(Tank):
    def __init__(self, x, y):
        super().__init__(hero_img, x, y, 3)
        self.score = 0
        self.lives = 3
        self.invincible = False
        self.invincible_timer = 0
        self.score_multiplier = 1
        self.score_multiplier_timer = 0

    def update(self):
        super().update()
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        if self.score_multiplier > 1:
            self.score_multiplier_timer -= 1
            if self.score_multiplier_timer <= 0:
                self.score_multiplier = 1

class Enemy(Tank):
    def __init__(self, x, y):
        super().__init__(enemy_img, x, y, 1)
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.shoot_chance = 0.01  # Base shooting chance

    def update(self):
        super().update()
        self.rect.x -= self.speed
        if self.rect.right < 0:  # If enemy moves off screen, reset position
            self.rect.left = WIDTH  # Reposition enemy at the right of the screen
            self.rect.y = random.randint(0, HEIGHT - self.rect.height)

        if random.random() < self.shoot_chance:
            return self.shoot()
        return None

class Boss(Tank):
    def __init__(self, x, y):
        super().__init__(boss_img, x, y, 1)
        self.health = 3000
        self.max_health = 3000
        self.rapid_fire = False
        self.rapid_fire_timer = 0

    def update(self):
        super().update()
        if self.rapid_fire:
            self.rapid_fire_timer -= 1
            if self.rapid_fire_timer <= 0:
                self.rapid_fire = False
                self.shoot_cooldown = 120  # 2 seconds cooldown
        
        if not self.rapid_fire and self.shoot_cooldown == 0:
            self.rapid_fire = True
            self.rapid_fire_timer = 60  # 1 second of rapid fire

        if self.rapid_fire and self.shoot_cooldown == 0:
            self.shoot_cooldown = 5
            return self.shoot()

        self.rect.y += math.sin(pygame.time.get_ticks() * 0.002) * 2
        return None

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, moving_right):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.moving_right = moving_right

    def update(self):
        self.rect.x += self.speed if self.moving_right else -self.speed
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_up_type):
        super().__init__()
        self.type = power_up_type
        if power_up_type == "x2":
            self.image = x2_img
        elif power_up_type == "health":
            self.image = health_img
        elif power_up_type == "invincibility":
            self.image = invincibility_img
        elif power_up_type == "ammo":
            self.image = ammo_img
        self.rect = self.image.get_rect(center=(x, y))
        self.duration = random.randint(300, 600)  # 5-10 seconds at 60 FPS

    def update(self):
        self.rect.y += 1
        if self.rect.top > HEIGHT:
            self.kill()

def spawn_enemy():
    return Enemy(WIDTH, random.randint(0, HEIGHT - enemy_img.get_height()))

def spawn_power_up():
    x = random.randint(50, WIDTH - 50)
    y = 0
    power_up_type = random.choice(["x2", "health", "invincibility", "ammo"])
    return PowerUp(x, y, power_up_type)

def show_victory_screen():
    font = pygame.font.Font(None, 74)
    text = font.render("Level Complete!", True, GREEN)
    continue_text = font.render("Click to Continue", True, RED)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
    return True

def show_game_over(screen, score, high_score):
    font = pygame.font.Font(None, 74)
    text = font.render("Game Over", True, WHITE)
    thank_you_text = font.render("Thank you for playing!", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(thank_you_text, (WIDTH // 2 - thank_you_text.get_width() // 2, HEIGHT // 2 + 50))
    
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, GREEN)
    high_score_text = font.render(f"High Score: {high_score}", True, RED)
    restart_text = font.render("Press R to Restart", True, GREEN)
    
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 100))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 150))

def draw_progress_bar(screen, progress, max_progress):
    bar_width = 30
    bar_height = 200
    bar_x = 50
    bar_y = 200

    progress_ratio = progress / max_progress
    progress_height = bar_height * progress_ratio

    # Draw the background of the progress bar
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

    # Draw the filled part of the progress bar
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y + bar_height - progress_height, bar_width, progress_height))

def main():
    clock = pygame.time.Clock()
    player = Player(WIDTH // 4, HEIGHT // 2)
    all_sprites = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    power_ups = pygame.sprite.Group()
    
    score = 0
    high_score = 0
    level = 1
    boss = None
    enemies_killed = 0  # Track number of enemies killed for the progress bar
    
    font = pygame.font.Font(None, 36)

    game_over = False
    running = True

    # Dictionary that defines the properties for each level
    level_config = {
        1: {"enemy_count": 10, "enemy_speed": 1, "enemy_shoot_chance": 0.01},
        2: {"enemy_count": 20, "enemy_speed": 1.5, "enemy_shoot_chance": 0.02},
        3: {"enemy_count": 30, "enemy_speed": 2, "enemy_shoot_chance": 0.03},  # Example, final boss stage will follow
        "boss_level": {"boss_health": 3000, "boss_rapid_fire_duration": 60, "boss_speed": 2},
    }

    def start_level(level_number):
        """Sets up the enemy count needed to progress the level."""
        nonlocal enemies_killed, max_enemies, boss
        boss = None  # Reset boss if it exists
        enemies_killed = 0  # Reset enemies killed counter
        if level_number in level_config:
            max_enemies = level_config[level_number]["enemy_count"]
        else:
            max_enemies = 0  # No enemies for undefined levels

    def all_enemies_defeated():
        """Returns True if the required number of enemies have been shot down."""
        return enemies_killed >= max_enemies

    max_enemies = 10
    start_level(level)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Restart the game
                    player = Player(WIDTH // 4, HEIGHT // 2)
                    all_sprites = pygame.sprite.Group(player)
                    enemies = pygame.sprite.Group()
                    bullets = pygame.sprite.Group()
                    power_ups = pygame.sprite.Group()
                    score = 0
                    level = 1
                    boss = None
                    game_over = False
                    start_level(1)

        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT] or keys[pygame.K_d] - keys[pygame.K_a],
                        keys[pygame.K_DOWN] - keys[pygame.K_UP] or keys[pygame.K_s] - keys[pygame.K_w])

            if keys[pygame.K_SPACE]:
                bullet = player.shoot()
                if bullet:
                    bullets.add(bullet)
                    all_sprites.add(bullet)

            # Ensure there are always enemies on screen
            if len(enemies) < 5 and not boss:
                enemy = spawn_enemy()
                enemy.speed = level_config[level]["enemy_speed"]
                enemy.shoot_chance = level_config[level]["enemy_shoot_chance"]
                enemies.add(enemy)
                all_sprites.add(enemy)

            # Spawn power-ups
            if random.random() < 0.005:
                power_up = spawn_power_up()
                power_ups.add(power_up)
                all_sprites.add(power_up)

            # Update all sprites
            all_sprites.update()

            # Enemy shooting
            for enemy in enemies:
                enemy_bullet = enemy.update()
                if enemy_bullet:
                    bullets.add(enemy_bullet)
                    all_sprites.add(enemy_bullet)

            # Boss shooting
            if boss:
                boss_bullet = boss.update()
                if boss_bullet:
                    bullets.add(boss_bullet)
                    all_sprites.add(boss_bullet)

            # Collision detection
            for bullet in bullets:
                if bullet.moving_right:  # Player's bullet
                    hit_enemies = pygame.sprite.spritecollide(bullet, enemies, True)
                    for enemy in hit_enemies:
                        score += 100 * player.score_multiplier
                        enemies_killed += 1  # Only count enemies when shot down
                        bullet.kill()

                    if boss and bullet.rect.colliderect(boss.rect):
                        boss.health -= 10
                        bullet.kill()
                        if boss.health <= 0:
                            boss.kill()
                            boss = None
                            score += 1000 * player.score_multiplier
                            if level < 3:
                                level += 1
                                if show_victory_screen():
                                    start_level(level)
                                else:
                                    running = False
                            else:
                                game_over = True
                else:  # Enemy's bullet
                    if not player.invincible and bullet.rect.colliderect(player.rect):
                        player.health -= 10
                        bullet.kill()
                        if player.health <= 0:
                            player.lives -= 1
                            if player.lives <= 0:
                                game_over = True
                                if score > high_score:
                                    high_score = score
                            else:
                                player.health = player.max_health

            # Power-up collection
            power_up_hits = pygame.sprite.spritecollide(player, power_ups, True)
            for power_up in power_up_hits:
                if power_up.type == "x2":
                    player.score_multiplier = 2
                    player.score_multiplier_timer = power_up.duration
                elif power_up.type == "health":
                    player.health = min(player.health + 20, player.max_health)
                elif power_up.type == "invincibility":
                    player.invincible = True
                    player.invincible_timer = power_up.duration
                elif power_up.type == "ammo":
                    player.bullets = min(player.bullets + 20, player.max_health)

            # Level progression: check if the required number of enemies are shot down
            if all_enemies_defeated() and not boss:
                if level == 3:
                    # Trigger boss level after level 3
                    boss = Boss(WIDTH, HEIGHT // 2)
                    all_sprites.add(boss)
                else:
                    if show_victory_screen():
                        level += 1
                        start_level(level)
                    else:
                        running = False

        # Draw the game
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        # Draw health bars
        for sprite in all_sprites:
            if isinstance(sprite, Tank):
                sprite.draw_health_bar(screen)

        # Draw UI elements
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        bullets_text = font.render(f"Bullets: {player.bullets}", True, WHITE)
        next_level_text = font.render(f"Next: {level+1 if level < 3 else 'Boss'}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(level_text, (WIDTH - 100, 10))
        screen.blit(bullets_text, (10, 90))
        screen.blit(next_level_text, (WIDTH - 150, 50))

        # Draw Progress Bar
        draw_progress_bar(screen, enemies_killed, max_enemies)

        # Handle game over state
        if game_over:
            show_game_over(screen, score, high_score)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

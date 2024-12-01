import pygame
import random
import sys
import os
import math

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH = 800
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Classic Arcade Shooter")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (147, 0, 211)

# Load images
def create_player_ship():
    surface = pygame.Surface((64, 64), pygame.SRCALPHA)
    
    # Main body (triangle shape)
    points = [(32, 10), (10, 54), (54, 54)]
    pygame.draw.polygon(surface, BLUE, points)
    
    # Cockpit
    pygame.draw.circle(surface, WHITE, (32, 35), 8)
    
    # Wings
    pygame.draw.polygon(surface, PURPLE, [(10, 54), (32, 30), (54, 54)])
    
    # Thrusters
    pygame.draw.rect(surface, RED, (20, 54, 8, 6))
    pygame.draw.rect(surface, RED, (36, 54, 8, 6))
    
    return surface

def create_enemy_ship(color1=RED, color2=PURPLE):
    surface = pygame.Surface((48, 48), pygame.SRCALPHA)
    
    # Main body (octagon)
    points = []
    center = (24, 24)
    radius = 20
    for i in range(8):
        angle = math.pi/8 + (i * math.pi/4)
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(surface, color1, points)
    
    # Inner details
    pygame.draw.circle(surface, color2, (24, 24), 12)
    pygame.draw.circle(surface, WHITE, (24, 24), 6)
    
    # Side cannons
    pygame.draw.rect(surface, color2, (2, 20, 8, 8))
    pygame.draw.rect(surface, color2, (38, 20, 8, 8))
    
    return surface

def create_laser():
    surface = pygame.Surface((8, 24), pygame.SRCALPHA)
    
    # Laser beam
    pygame.draw.rect(surface, YELLOW, (0, 0, 8, 24))
    
    # Glow effect
    pygame.draw.rect(surface, WHITE, (2, 0, 4, 24))
    
    return surface

def create_boss_laser():
    surface = pygame.Surface((12, 32), pygame.SRCALPHA)
    
    # Main beam
    pygame.draw.rect(surface, RED, (0, 0, 12, 32))
    # Core
    pygame.draw.rect(surface, WHITE, (4, 0, 4, 32))
    
    return surface

# Create game images
PLAYER_IMG = create_player_ship()
ENEMY_IMG = create_enemy_ship()
ENEMY_IMG2 = create_enemy_ship(GREEN, BLUE)
LASER_IMG = create_laser()
BOSS_LASER_IMG = create_boss_laser()

# Player
player_width = 64
player_height = 64
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 20
player_speed = 6

# Laser
laser_width = 8
laser_height = 24
laser_speed = 10
lasers = []

# Enemy
enemy_width = 48
enemy_height = 48
enemy_speed = 2
enemies = []
enemy_spawn_delay = 45  # Spawn enemies faster
enemy_timer = 0

# Boss
boss = None
boss_health = 0
boss_entry_pos = 0
boss_lasers = []
boss_shoot_timer = 0

# Level configurations
LEVEL_CONFIGS = {
    1: {"enemy_speed": 2, "spawn_delay": 60, "enemies_to_clear": 20, "boss_health": 5, "boss_shoot_delay": 60},
    2: {"enemy_speed": 3, "spawn_delay": 45, "enemies_to_clear": 30, "boss_health": 8, "boss_shoot_delay": 45},
    3: {"enemy_speed": 4, "spawn_delay": 30, "enemies_to_clear": 40, "boss_health": 10, "boss_shoot_delay": 30}
}

# Score and UI
score = 0
font = pygame.font.Font(None, 48)  # Bigger font
high_score = 0

# Background stars (more stars and different sizes)
stars = []
for _ in range(150):  # More stars
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    speed = random.randint(1, 3)  # Different star speeds
    size = random.randint(1, 3)   # Different star sizes
    stars.append([x, y, speed, size])

# Animation variables
animation_frame = 0
ANIMATION_SPEED = 6

# Game state
class GameState:
    MENU = 0
    PLAYING = 1
    LEVEL_COMPLETE = 2
    GAME_OVER = 3

# Game variables
current_level = 1
enemies_destroyed = 0
lives = 3
game_state = GameState.MENU
level_start_timer = 0
LEVEL_START_DELAY = 180  # 3 seconds at 60 FPS

# Create heart image for lives
def create_heart():
    surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(surface, RED, (5, 10), 5)
    pygame.draw.circle(surface, RED, (15, 10), 5)
    pygame.draw.polygon(surface, RED, [(10, 18), (0, 8), (20, 8)])
    return surface

HEART_IMG = create_heart()

# Boss ship
def create_boss_ship():
    surface = pygame.Surface((96, 96), pygame.SRCALPHA)
    
    # Main body
    pygame.draw.rect(surface, RED, (18, 18, 60, 60))
    pygame.draw.circle(surface, PURPLE, (48, 48), 35)
    
    # Cannons
    pygame.draw.rect(surface, RED, (0, 30, 20, 15))
    pygame.draw.rect(surface, RED, (76, 30, 20, 15))
    
    # Details
    pygame.draw.circle(surface, WHITE, (48, 48), 15)
    pygame.draw.rect(surface, PURPLE, (38, 78, 20, 15))
    
    return surface

BOSS_IMG = create_boss_ship()

# Explosion animation
class Explosion:
    def __init__(self, x, y, size=1):
        self.x = x
        self.y = y
        self.size = size
        self.frame = 0
        self.frames = 12
        self.particles = []
        self.colors = [RED, YELLOW, WHITE]
        
        # Create random particles
        for _ in range(20 * size):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8) * size
            color = random.choice(self.colors)
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'color': color,
                'size': random.randint(2, 4) * size
            })
    
    def update(self):
        self.frame += 1
        for p in self.particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['size'] *= 0.9
    
    def draw(self, surface):
        for p in self.particles:
            size = int(p['size'])
            if size > 0:
                pygame.draw.circle(surface, p['color'], 
                                (int(p['x']), int(p['y'])), size)
    
    def is_finished(self):
        return self.frame >= self.frames

# Add explosions list to track active explosions
explosions = []

# Game loop
clock = pygame.time.Clock()
running = True

def reset_level():
    global enemies, lasers, enemies_destroyed, boss, boss_health, boss_lasers, boss_shoot_timer, explosions
    enemies.clear()
    lasers.clear()
    boss_lasers.clear()
    explosions.clear()
    enemies_destroyed = 0
    boss = None
    boss_shoot_timer = 0
    if current_level in LEVEL_CONFIGS:
        boss_health = LEVEL_CONFIGS[current_level]["boss_health"]

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == GameState.MENU:
                    game_state = GameState.PLAYING
                    reset_level()
                elif game_state == GameState.GAME_OVER:
                    # Reset game
                    score = 0
                    current_level = 1
                    lives = 3
                    game_state = GameState.PLAYING
                    reset_level()

    if game_state == GameState.PLAYING:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed
        if keys[pygame.K_SPACE]:
            # Shoot laser
            if not lasers or lasers[-1][1] < player_y - 30:  # Rate limiting
                laser_x = player_x + player_width // 2 - laser_width // 2
                laser_y = player_y
                lasers.append([laser_x, laser_y])

        # Update game objects
        for star in stars:
            star[1] = (star[1] + star[2]) % HEIGHT

        # Update lasers
        for laser in lasers[:]:
            laser[1] -= laser_speed
            if laser[1] < -laser_height:
                lasers.remove(laser)

        # Update boss lasers
        for boss_laser in boss_lasers[:]:
            boss_laser[1] += laser_speed  # Boss lasers move downward
            if boss_laser[1] > HEIGHT:
                boss_lasers.remove(boss_laser)

            # Check collision with player
            boss_laser_rect = pygame.Rect(boss_laser[0], boss_laser[1], 12, 32)
            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            if boss_laser_rect.colliderect(player_rect):
                boss_lasers.remove(boss_laser)
                lives -= 1
                # Add big explosion for player hit
                explosions.append(Explosion(player_x + player_width//2, 
                                         player_y + player_height//2, 2))
                if lives <= 0:
                    # Add multiple explosions for game over
                    for _ in range(5):
                        ex = random.randint(0, WIDTH)
                        ey = random.randint(0, HEIGHT)
                        explosions.append(Explosion(ex, ey, 3))
                    game_state = GameState.GAME_OVER

        # Spawn and update enemies
        if not boss:
            enemy_timer += 1
            if enemy_timer >= LEVEL_CONFIGS[current_level]["spawn_delay"]:
                enemy_x = random.randint(0, WIDTH - enemy_width)
                enemy_type = random.choice([ENEMY_IMG, ENEMY_IMG2])
                enemies.append([enemy_x, -enemy_height, enemy_type])
                enemy_timer = 0

            for enemy in enemies[:]:
                enemy[1] += LEVEL_CONFIGS[current_level]["enemy_speed"]
                if enemy[1] > HEIGHT:
                    enemies.remove(enemy)
                    lives -= 1
                    if lives <= 0:
                        game_state = GameState.GAME_OVER
        else:
            # Boss movement
            if boss[1] < 50:  # Boss entry
                boss[1] += 2
            else:  # Boss pattern
                boss[0] = WIDTH//2 + math.sin(animation_frame * 0.02) * (WIDTH//3)
                
                # Boss shooting
                boss_shoot_timer += 1
                if boss_shoot_timer >= LEVEL_CONFIGS[current_level]["boss_shoot_delay"]:
                    boss_shoot_timer = 0
                    
                    # Different shooting patterns for each level
                    if current_level == 1:
                        # Single straight shot
                        boss_lasers.append([boss[0] + 48 - 6, boss[1] + 96])
                    elif current_level == 2:
                        # Double shot
                        boss_lasers.append([boss[0] + 20, boss[1] + 96])
                        boss_lasers.append([boss[0] + 76, boss[1] + 96])
                    else:
                        # Triple spread shot
                        for i in range(3):
                            laser_x = boss[0] + 48 - 6 + (i - 1) * 30
                            laser_y = boss[1] + 96
                            velocity_x = (i - 1) * 2  # Add horizontal movement
                            boss_lasers.append([laser_x, laser_y, velocity_x])

        # Update spread shot lasers
        if boss and current_level == 3:
            for boss_laser in boss_lasers:
                if len(boss_laser) > 2:  # Check if it's a spread shot
                    boss_laser[0] += boss_laser[2]  # Apply horizontal movement

        # Check collisions
        for laser in lasers[:]:
            laser_rect = pygame.Rect(laser[0], laser[1], laser_width, laser_height)
            
            if boss:
                boss_rect = pygame.Rect(boss[0], boss[1], 96, 96)
                if laser_rect.colliderect(boss_rect):
                    if laser in lasers:
                        lasers.remove(laser)
                    boss_health -= 1
                    if boss_health <= 0:
                        boss = None
                        score += 1000
                        current_level += 1
                        if current_level > 3:
                            game_state = GameState.GAME_OVER
                        else:
                            game_state = GameState.LEVEL_COMPLETE
                            level_start_timer = LEVEL_START_DELAY
            else:
                for enemy in enemies[:]:
                    enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_width, enemy_height)
                    if laser_rect.colliderect(enemy_rect):
                        if laser in lasers:
                            lasers.remove(laser)
                        if enemy in enemies:
                            enemies.remove(enemy)
                            enemies_destroyed += 1
                            score += 100
                            # Add explosion for destroyed enemy
                            explosions.append(Explosion(enemy[0] + enemy_width//2,
                                                     enemy[1] + enemy_height//2))
                            
                            # Check if we should spawn boss
                            if enemies_destroyed >= LEVEL_CONFIGS[current_level]["enemies_to_clear"]:
                                boss = [WIDTH//2 - 48, -96]  # Spawn boss above screen
                                boss_health = LEVEL_CONFIGS[current_level]["boss_health"]

    # Clear screen
    window.fill((0, 0, 20))

    # Draw stars
    for star in stars:
        pygame.draw.circle(window, WHITE, (int(star[0]), int(star[1])), star[3])

    if game_state == GameState.MENU:
        # Draw menu
        title_font = pygame.font.Font(None, 74)
        menu_font = pygame.font.Font(None, 48)
        
        title = title_font.render("SPACE SHOOTER", True, WHITE)
        start_text = menu_font.render("Press SPACE to Start", True, WHITE)
        
        window.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        window.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
    elif game_state == GameState.PLAYING:
        # Draw game objects
        if animation_frame % ANIMATION_SPEED < ANIMATION_SPEED // 2:
            pygame.draw.rect(window, YELLOW, (player_x + 20, player_y + 60, 8, random.randint(4, 8)))
            pygame.draw.rect(window, YELLOW, (player_x + 36, player_y + 60, 8, random.randint(4, 8)))
        
        window.blit(PLAYER_IMG, (player_x, player_y))

        for laser in lasers:
            window.blit(LASER_IMG, (laser[0], laser[1]))

        if boss:
            window.blit(BOSS_IMG, (boss[0], boss[1]))
            # Draw boss health bar
            health_width = (boss_health / LEVEL_CONFIGS[current_level]["boss_health"]) * 96
            pygame.draw.rect(window, RED, (boss[0], boss[1] - 10, health_width, 5))
            
            # Draw boss lasers
            for boss_laser in boss_lasers:
                window.blit(BOSS_LASER_IMG, (boss_laser[0], boss_laser[1]))
        else:
            for enemy in enemies:
                angle = math.sin(animation_frame * 0.1) * 15
                rotated_enemy = pygame.transform.rotate(enemy[2], angle)
                enemy_rect = rotated_enemy.get_rect(center=(enemy[0] + enemy_width//2, enemy[1] + enemy_height//2))
                window.blit(rotated_enemy, enemy_rect.topleft)

        # Draw UI
        score_text = font.render(f"SCORE: {score}", True, WHITE)
        level_text = font.render(f"LEVEL: {current_level}", True, WHITE)
        window.blit(score_text, (10, 10))
        window.blit(level_text, (10, 50))
        
        # Draw lives
        for i in range(lives):
            window.blit(HEART_IMG, (WIDTH - 30 - i * 25, 10))
            
        # Draw enemies left
        if not boss:
            enemies_left = LEVEL_CONFIGS[current_level]["enemies_to_clear"] - enemies_destroyed
            enemies_text = font.render(f"Enemies Left: {enemies_left}", True, WHITE)
            window.blit(enemies_text, (WIDTH//2 - enemies_text.get_width()//2, 10))

        # Update and draw explosions
        for exp in explosions[:]:
            exp.update()
            if exp.is_finished():
                explosions.remove(exp)
            else:
                exp.draw(window)

    elif game_state == GameState.LEVEL_COMPLETE:
        # Draw level complete
        font = pygame.font.Font(None, 74)
        text = font.render(f"LEVEL {current_level} COMPLETE!", True, WHITE)
        window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
        level_start_timer -= 1
        if level_start_timer <= 0:
            game_state = GameState.PLAYING
            reset_level()

    elif game_state == GameState.GAME_OVER:
        # Draw game over
        font = pygame.font.Font(None, 74)
        text = font.render("GAME OVER", True, RED)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        restart_text = font.render("Press SPACE to Restart", True, WHITE)
        
        window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//3))
        window.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        window.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 2*HEIGHT//3))

    # Update animation frame
    animation_frame += 1

    # Update display
    pygame.display.flip()
    clock.tick(60)

    # Check for boss defeat
    if boss and boss_health <= 0:
        # Add big explosion for boss defeat
        for _ in range(8):
            ex = boss[0] + random.randint(0, 96)
            ey = boss[1] + random.randint(0, 96)
            explosions.append(Explosion(ex, ey, 2))
        boss = None
        score += 1000
        current_level += 1
        if current_level > 3:
            # Victory explosions
            for _ in range(10):
                ex = random.randint(0, WIDTH)
                ey = random.randint(0, HEIGHT)
                explosions.append(Explosion(ex, ey, 2))
            game_state = GameState.GAME_OVER
        else:
            game_state = GameState.LEVEL_COMPLETE
            level_start_timer = LEVEL_START_DELAY

pygame.quit()
sys.exit()

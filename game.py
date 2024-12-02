import pygame
import random
import sys
import os
import math
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Load sounds
shoot_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'shoot.wav'))
explosion_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'explosion.wav'))
powerup_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'powerup.wav'))

# Set up the game window
WIDTH = 800
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Classic Arcade Shooter")

# Create retro-style fonts
def create_retro_font(size):
    try:
        return pygame.font.Font(os.path.join('assets', 'fonts', 'arcade.ttf'), size)
    except:
        # Fallback to built-in font with pixel-style
        return pygame.font.Font(None, size)

# Initialize fonts with different sizes
LARGE_FONT = create_retro_font(64)  # For title
MEDIUM_FONT = create_retro_font(32)  # For menu items
SMALL_FONT = create_retro_font(24)   # For score and lives

# Colors (classic arcade neon colors)
WHITE = (255, 255, 255)
NEON_RED = (255, 50, 50)
NEON_BLUE = (50, 50, 255)
NEON_GREEN = (50, 255, 50)
NEON_PINK = (255, 50, 255)
NEON_YELLOW = (255, 255, 50)

# Player dimensions
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40

def draw_player(surface, x, y, shield_active):
    # Vector style spaceship (Asteroids/Defender style)
    points = [
        (x + PLAYER_WIDTH//2, y),  # Nose
        (x, y + PLAYER_HEIGHT),    # Left
        (x + PLAYER_WIDTH//2, y + PLAYER_HEIGHT - 10),  # Indent
        (x + PLAYER_WIDTH, y + PLAYER_HEIGHT)  # Right
    ]
    # Outline
    pygame.draw.lines(surface, NEON_BLUE, True, points, 2)
    
    # Thruster animation (classic vector style)
    if pygame.time.get_ticks() % 200 < 100:  # Blink every 200ms
        thrust_points = [
            (x + PLAYER_WIDTH//2 - 10, y + PLAYER_HEIGHT),
            (x + PLAYER_WIDTH//2, y + PLAYER_HEIGHT + 15),
            (x + PLAYER_WIDTH//2 + 10, y + PLAYER_HEIGHT)
        ]
        pygame.draw.lines(surface, NEON_YELLOW, False, thrust_points, 2)
    
    # Shield (vector circle)
    if shield_active:
        shield_radius = max(PLAYER_WIDTH, PLAYER_HEIGHT) * 0.75
        for i in range(8):  # Draw 8 segments for vector look
            start_angle = i * math.pi / 4
            end_angle = (i + 1) * math.pi / 4
            start_pos = (x + PLAYER_WIDTH//2 + shield_radius * math.cos(start_angle),
                        y + PLAYER_HEIGHT//2 + shield_radius * math.sin(start_angle))
            end_pos = (x + PLAYER_WIDTH//2 + shield_radius * math.cos(end_angle),
                      y + PLAYER_HEIGHT//2 + shield_radius * math.sin(end_angle))
            pygame.draw.line(surface, NEON_PINK, start_pos, end_pos, 2)

def draw_enemy(surface, x, y, enemy_type, flash=False):
    color = WHITE if flash else NEON_RED
    if enemy_type == "normal":
        # Space Invaders / Galaxian style enemy
        size = 30
        # Body outline
        points = [
            (x + size//2, y),          # Top
            (x, y + size//2),          # Left
            (x, y + size),             # Bottom Left
            (x + size, y + size),      # Bottom Right
            (x + size, y + size//2),   # Right
            (x + size//2, y)           # Back to Top
        ]
        pygame.draw.lines(surface, color, True, points, 2)
        
        # "Antenna" details
        pygame.draw.line(surface, color, (x + size//4, y + size//2), 
                        (x + size//4, y + size//4), 2)
        pygame.draw.line(surface, color, (x + 3*size//4, y + size//2), 
                        (x + 3*size//4, y + size//4), 2)
    else:  # Boss
        color = WHITE if flash else NEON_PINK
        width = 96
        height = 96
        
        # Main hull (geometric shapes)
        points = [
            (x + width//4, y),             # Top Left
            (x + 3*width//4, y),           # Top Right
            (x + width, y + height//2),    # Middle Right
            (x + 3*width//4, y + height),  # Bottom Right
            (x + width//4, y + height),    # Bottom Left
            (x, y + height//2),            # Middle Left
        ]
        pygame.draw.lines(surface, color, True, points, 2)
        
        # Interior details
        pygame.draw.line(surface, color, (x + width//4, y), 
                        (x + width//4, y + height), 2)
        pygame.draw.line(surface, color, (x + 3*width//4, y), 
                        (x + 3*width//4, y + height), 2)

def draw_laser(surface, x, y, width):
    # Vector style laser (line with glow)
    pygame.draw.line(surface, NEON_GREEN, (x + width//2, y), 
                    (x + width//2, y + 20), 4)
    # Glow effect
    pygame.draw.line(surface, WHITE, (x + width//2, y), 
                    (x + width//2, y + 20), 2)

def draw_explosion(surface, x, y, frame):
    # Vector style explosion (expanding lines)
    size = frame * 3
    color = NEON_YELLOW if frame % 2 == 0 else NEON_RED
    points = []
    for i in range(8):
        angle = i * math.pi / 4
        end_x = x + size * math.cos(angle)
        end_y = y + size * math.sin(angle)
        points.append((x, y))
        points.append((end_x, end_y))
    
    # Draw explosion lines
    for i in range(0, len(points), 2):
        pygame.draw.line(surface, color, points[i], points[i+1], 2)

def draw_score(surface, score, x, y):
    # Classic arcade style scoring (right aligned, leading zeros)
    score_text = f"{score:08d}"  # 8 digits with leading zeros
    text_surface = SMALL_FONT.render(score_text, True, NEON_GREEN)
    surface.blit(text_surface, (x, y))

# Add new colors and constants
POWER_UP_COLORS = [(255, 223, 0), (0, 255, 255), (255, 0, 255), (0, 255, 0)]  # Gold, Cyan, Magenta, Green

# Add power-ups list and variables
power_ups = []
SCORE_MULTIPLIER = 1
MAX_MULTIPLIER = 8
MULTIPLIER_DURATION = 300  # 5 seconds at 60 FPS
multiplier_timer = 0
rapid_fire = False
rapid_fire_timer = 0
shield_active = False
shield_timer = 0
double_laser = True  # Always true now
double_laser_timer = 0

# Player
player_x = WIDTH // 2 - PLAYER_WIDTH // 2
player_y = HEIGHT - PLAYER_HEIGHT - 20
player_speed = 6
player_crash_speed = 0
is_crashing = False
crash_recovery_timer = 0
CRASH_RECOVERY_TIME = 120  # 2 seconds at 60 FPS

# Laser
laser_width = 8
laser_height = 24
double_laser_width = 16  # Wider laser for double shot
laser_speed = 10
lasers = []

# Enemy
enemy_width = 48
enemy_height = 48
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
def get_level_config(level):
    # Base configurations
    base_config = {
        "spawn_delay": max(10, 45 - (level - 1) * 5),  # Gets faster but not below 10
        "enemy_speed": min(10, 2 + (level - 1)),       # Gets faster but caps at 10
        "enemy_health": 1 + (level - 1) // 2,          # +1 health every 2 levels
        "boss_health": 100 + (level - 1) * 50          # +50 health per level
    }
    return base_config

# Enemy class to track health
class Enemy:
    def __init__(self, x, y, type, health):
        self.x = x
        self.y = y
        self.type = type
        self.health = health
        self.hit_timer = 0
        
    def draw(self, surface):
        if self.hit_timer > 0:
            # Flash white when hit
            pygame.draw.rect(surface, (255, 255, 255), 
                           (self.x, self.y, enemy_width, enemy_height))
            self.hit_timer -= 1
        else:
            surface.blit(self.type, (self.x, self.y))
            
    def take_damage(self):
        self.health -= 1
        self.hit_timer = 5  # Flash for 5 frames
        return self.health <= 0

# Score and UI
score = 0
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
lives = 3  # Start with 3 lives
game_state = GameState.MENU
level_start_timer = 0
LEVEL_START_DELAY = 180  # 3 seconds at 60 FPS

# Create heart image for lives
def create_heart():
    surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(surface, NEON_RED, (5, 10), 5)
    pygame.draw.circle(surface, NEON_RED, (15, 10), 5)
    pygame.draw.polygon(surface, NEON_RED, [(10, 18), (0, 8), (20, 8)])
    return surface

HEART_IMG = create_heart()

# Boss ship
def create_boss_ship():
    surface = pygame.Surface((96, 96), pygame.SRCALPHA)
    
    # Main body
    pygame.draw.rect(surface, NEON_RED, (18, 18, 60, 60))
    pygame.draw.circle(surface, NEON_PINK, (48, 48), 35)
    
    # Cannons
    pygame.draw.rect(surface, NEON_RED, (0, 30, 20, 15))
    pygame.draw.rect(surface, NEON_RED, (76, 30, 20, 15))
    
    # Details
    pygame.draw.circle(surface, WHITE, (48, 48), 15)
    pygame.draw.rect(surface, NEON_PINK, (38, 78, 20, 15))
    
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
        self.colors = [NEON_RED, NEON_YELLOW, WHITE]
        
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

# Crash effect class for dramatic player death
class CrashEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.duration = 60  # 1 second at 60 FPS
        self.shake_amount = 20
    
    def update(self):
        self.frame += 1
        return self.frame < self.duration
    
    def draw(self, surface):
        # Screen shake only
        shake_x = random.randint(-self.shake_amount, self.shake_amount)
        shake_y = random.randint(-self.shake_amount, self.shake_amount)
        
        # Store and apply screen shake
        current_state = surface.copy()
        surface.blit(current_state, (shake_x, shake_y))

crash_effect = None

# Add explosions list to track active explosions
explosions = []

# Add power-up class
class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type  # 0: Score Multiplier, 1: Rapid Fire, 2: Shield, 3: Double Laser
        self.width = 20
        self.height = 20
        self.speed = 2
        self.color = POWER_UP_COLORS[power_type]
        self.pulse = 0
        
    def update(self):
        self.y += self.speed
        self.pulse = (self.pulse + 1) % 60
        return self.y < HEIGHT
        
    def draw(self, surface):
        # Draw the main power-up box
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw pulsing glow effect
        glow_size = abs(math.sin(self.pulse * 0.1)) * 10  # Pulsing size
        
        # Draw multiple rectangles with decreasing opacity for glow effect
        for i in range(3):
            glow_rect = (
                self.x - i * 2 - glow_size/2,
                self.y - i * 2 - glow_size/2,
                self.width + i * 4 + glow_size,
                self.height + i * 4 + glow_size
            )
            glow_alpha = 128 // (i + 1)  # Decreasing alpha
            glow_surface = pygame.Surface((glow_rect[2], glow_rect[3]), pygame.SRCALPHA)
            glow_color = (*self.color, glow_alpha)  # Create RGBA color
            pygame.draw.rect(glow_surface, glow_color, (0, 0, glow_rect[2], glow_rect[3]))
            surface.blit(glow_surface, (glow_rect[0], glow_rect[1]))

# Add reset_level function
def reset_level():
    global player_x, player_y, enemies, lasers, boss, boss_health, boss_lasers, power_ups
    global SCORE_MULTIPLIER, multiplier_timer, rapid_fire, rapid_fire_timer, shield_active, shield_timer, double_laser, double_laser_timer
    
    # Reset player position
    player_x = WIDTH // 2 - PLAYER_WIDTH // 2
    player_y = HEIGHT - PLAYER_HEIGHT - 20
    
    # Clear all game objects
    enemies = []
    lasers = []
    power_ups = []
    
    # Reset boss
    boss = None
    boss_health = 100
    boss_lasers = []
    
    # Reset power-ups
    SCORE_MULTIPLIER = 1
    multiplier_timer = 0
    rapid_fire = False
    rapid_fire_timer = 0
    shield_active = False
    shield_timer = 0
    double_laser = True  # Always true now
    double_laser_timer = 0

# Game loop
clock = pygame.time.Clock()
running = True
last_shot = 0

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:  # Close game when X is pressed
                running = False
            if event.key == pygame.K_SPACE and game_state == GameState.MENU:
                game_state = GameState.PLAYING
                reset_level()
            elif event.key == pygame.K_r and game_state == GameState.GAME_OVER:
                game_state = GameState.PLAYING
                reset_level()
                score = 0
                lives = 3
                current_level = 1

    if game_state == GameState.MENU:
        # Clear screen
        window.fill((0, 0, 20))

        # Draw stars
        for star in stars:
            pygame.draw.circle(window, WHITE, (int(star[0]), int(star[1])), star[3])

        # Draw title with retro font
        title = LARGE_FONT.render("SPACE SHOOTER", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//3))
        window.blit(title, title_rect)
        
        # Draw "Press SPACE to Start" with medium font
        start_text = MEDIUM_FONT.render("PRESS SPACE TO START", True, 
                                      (255, 255, 255) if int(pygame.time.get_ticks()/500) % 2 else (100, 100, 100))
        start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT*2//3))
        window.blit(start_text, start_rect)
    elif game_state == GameState.PLAYING:
        # Clear screen
        window.fill((0, 0, 20))

        # Draw stars
        for star in stars:
            pygame.draw.circle(window, WHITE, (int(star[0]), int(star[1])), star[3])

        # Draw the player
        draw_player(window, player_x, player_y, shield_active)
        
        # Draw enemies
        for enemy in enemies:
            draw_enemy(window, enemy.x, enemy.y, "normal", enemy.hit_timer > 0)
        
        # Draw boss
        if boss:
            draw_enemy(window, boss[0], boss[1], "boss", boss_shoot_timer > 0)
        
        # Draw lasers
        for laser in lasers:
            draw_laser(window, laser[0], laser[1], 16)
        
        # Draw explosions
        for explosion in explosions[:]:
            draw_explosion(window, explosion.x, explosion.y, explosion.frame)
        
        # Draw UI
        draw_score(window, score, 10, 10)
        
        level_text = SMALL_FONT.render(f"LEVEL {current_level}", True, NEON_BLUE)
        level_rect = level_text.get_rect(midtop=(WIDTH//2, 10))
        window.blit(level_text, level_rect)
        
        lives_text = SMALL_FONT.render(f"LIVES: {lives}", True, NEON_YELLOW)
        lives_rect = lives_text.get_rect(topright=(WIDTH-10, 10))
        window.blit(lives_text, lives_rect)

        # Draw lives
        for i in range(lives):
            window.blit(HEART_IMG, (WIDTH - 30 - i * 25, 10))

        # Draw enemies left
        if not boss:
            enemies_left = get_level_config(current_level)["spawn_delay"]
            enemies_text = SMALL_FONT.render(f"Enemies Left: {enemies_left}", True, WHITE)
            enemies_rect = enemies_text.get_rect(topright=(WIDTH-10, 50))
            window.blit(enemies_text, enemies_rect)

        # Spawn power-ups randomly
        if random.random() < 0.002:  # 0.2% chance each frame
            power_type = random.choice([0, 1, 2])  # Only spawn score multiplier, rapid fire, and shield
            x = random.randint(20, WIDTH - 20)
            power_ups.append(PowerUp(x, -20, power_type))

        # Update power-ups
        for power_up in power_ups[:]:
            if not power_up.update():
                power_ups.remove(power_up)
            else:
                # Check collision with player
                power_rect = pygame.Rect(power_up.x - power_up.width/2, 
                                       power_up.y - power_up.height/2,
                                       power_up.width, power_up.height)
                player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
                
                if power_rect.colliderect(player_rect):
                    if power_up.type == 0:  # Score multiplier
                        SCORE_MULTIPLIER = min(MAX_MULTIPLIER, SCORE_MULTIPLIER * 2)
                        multiplier_timer = MULTIPLIER_DURATION
                    elif power_up.type == 1:  # Rapid fire
                        rapid_fire = True
                        rapid_fire_timer = 300  # 5 seconds
                    elif power_up.type == 2:  # Shield
                        shield_active = True
                        shield_timer = 300  # 5 seconds
                    powerup_sound.play()  # Play sound when collecting powerup
                    power_ups.remove(power_up)

        # Update timers
        if multiplier_timer > 0:
            multiplier_timer -= 1
            if multiplier_timer <= 0:
                SCORE_MULTIPLIER = 1
                
        if rapid_fire_timer > 0:
            rapid_fire_timer -= 1
            if rapid_fire_timer <= 0:
                rapid_fire = False
                
        if shield_timer > 0:
            shield_timer -= 1
            if shield_timer <= 0:
                shield_active = False
                
        # Draw power-ups
        for power_up in power_ups:
            power_up.draw(window)

        # Draw active power-ups status
        if SCORE_MULTIPLIER > 1:
            mult_text = SMALL_FONT.render(f"{SCORE_MULTIPLIER}x", True, POWER_UP_COLORS[0])
            window.blit(mult_text, (WIDTH - 50, 40))
            
        if rapid_fire:
            rapid_text = SMALL_FONT.render("RAPID", True, POWER_UP_COLORS[1])
            window.blit(rapid_text, (WIDTH - 60, 60))
            
        if shield_active:
            shield_text = SMALL_FONT.render("SHIELD", True, POWER_UP_COLORS[2])
            window.blit(shield_text, (WIDTH - 60, 80))
            # Draw shield effect
            shield_radius = max(PLAYER_WIDTH, PLAYER_HEIGHT) * 0.7
            shield_color = (128, 128, 255, 128)
            pygame.draw.circle(window, shield_color, 
                             (int(player_x + PLAYER_WIDTH/2), 
                              int(player_y + PLAYER_HEIGHT/2)), 
                             int(shield_radius), 2)

    elif game_state == GameState.LEVEL_COMPLETE:
        # Clear screen
        window.fill((0, 0, 20))

        # Draw stars
        for star in stars:
            pygame.draw.circle(window, WHITE, (int(star[0]), int(star[1])), star[3])

        # Draw level complete message with large font
        level_text = LARGE_FONT.render(f"LEVEL {current_level} COMPLETE!", True, (0, 255, 0))
        level_rect = level_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        window.blit(level_text, level_rect)

        level_start_timer -= 1
        if level_start_timer <= 0:
            game_state = GameState.PLAYING
            reset_level()

    elif game_state == GameState.GAME_OVER:
        # Clear screen
        window.fill((0, 0, 20))

        # Draw stars
        for star in stars:
            pygame.draw.circle(window, WHITE, (int(star[0]), int(star[1])), star[3])

        # Draw "GAME OVER" with large font
        game_over = LARGE_FONT.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over.get_rect(center=(WIDTH//2, HEIGHT//3))
        window.blit(game_over, game_over_rect)
        
        # Draw final score with medium font
        score_text = MEDIUM_FONT.render(f"SCORE: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        window.blit(score_text, score_rect)
        
        # Draw restart instruction with medium font
        restart = MEDIUM_FONT.render("PRESS R TO RESTART", True, 
                                   (255, 255, 255) if int(pygame.time.get_ticks()/500) % 2 else (100, 100, 100))
        restart_rect = restart.get_rect(center=(WIDTH//2, HEIGHT*2//3))
        window.blit(restart, restart_rect)

    # Update display
    pygame.display.flip()
    clock.tick(60)

    # Update game objects
    if game_state == GameState.PLAYING:
        # Update crash animation
        if is_crashing:
            # Simple up and down movement
            player_y += player_crash_speed
            player_crash_speed += 0.5  # Gravity
            
            # Bounce off bottom of screen
            if player_y > HEIGHT - PLAYER_HEIGHT:
                player_crash_speed = -player_crash_speed * 0.5
                player_y = HEIGHT - PLAYER_HEIGHT
                
                # Only recover if we still have lives
                crash_recovery_timer -= 1
                if crash_recovery_timer <= 0:
                    is_crashing = False
                    player_crash_speed = 0

        # Get keyboard input and allow movement/shooting all the time
        keys = pygame.key.get_pressed()

        # Always allow shooting
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks()
            if rapid_fire:
                if not lasers or current_time - last_shot > 100:  # Faster shooting
                    # Two wide lasers with more spacing
                    laser_x1 = player_x + 5  # Left laser
                    laser_x2 = player_x + PLAYER_WIDTH - 21  # Right laser
                    laser_y = player_y + 10
                    lasers.append([laser_x1, laser_y])
                    lasers.append([laser_x2, laser_y])
                    shoot_sound.play()
                    last_shot = current_time
            else:
                if not lasers or lasers[-1][1] < player_y - 30:
                    # Two wide lasers with more spacing
                    laser_x1 = player_x + 5  # Left laser
                    laser_x2 = player_x + PLAYER_WIDTH - 21  # Right laser
                    laser_y = player_y + 10
                    lasers.append([laser_x1, laser_y])
                    lasers.append([laser_x2, laser_y])
                    shoot_sound.play()

        # Always allow movement
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - PLAYER_WIDTH:
            player_x += player_speed

        # Update stars
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
            player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
            
            if boss_laser_rect.colliderect(player_rect) and not is_crashing:
                if not shield_active:
                    boss_lasers.remove(boss_laser)
                    lives -= 1  # Reduce lives by 1
                    # Crash effect
                    is_crashing = True
                    crash_recovery_timer = CRASH_RECOVERY_TIME
                    player_crash_speed = -10
                    crash_effect = CrashEffect(player_x + PLAYER_WIDTH//2, player_y + PLAYER_HEIGHT//2)
                    explosion_sound.play()
                    if lives <= 0:
                        # Multiple explosions for game over
                        for _ in range(8):
                            ex = random.randint(0, WIDTH)
                            ey = random.randint(0, HEIGHT)
                            explosions.append(Explosion(ex, ey, 3))
                            explosion_sound.play()
                        game_state = GameState.GAME_OVER
                else:
                    boss_lasers.remove(boss_laser)
                    # Shield hit effect
                    shield_timer = max(60, shield_timer)  # At least 1 more second

        # Spawn and update enemies
        if not boss:
            enemy_timer += 1
            if enemy_timer >= get_level_config(current_level)["spawn_delay"]:
                enemy_x = random.randint(0, WIDTH - enemy_width)
                enemy_type = random.choice([ENEMY_IMG, ENEMY_IMG2])
                enemy_health = get_level_config(current_level)["enemy_health"]
                enemies.append(Enemy(enemy_x, -enemy_height, enemy_type, enemy_health))
                enemy_timer = 0

            for enemy in enemies[:]:
                enemy.y += get_level_config(current_level)["enemy_speed"]
                if enemy.y > HEIGHT:
                    enemies.remove(enemy)
                    if not shield_active:  # Only lose life if not shielded
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
                if boss_shoot_timer >= get_level_config(current_level)["boss_health"]:
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
            laser_rect = pygame.Rect(laser[0], laser[1], double_laser_width, laser_height)
            
            if boss:
                boss_rect = pygame.Rect(boss[0], boss[1], 96, 96)
                if laser_rect.colliderect(boss_rect):
                    lasers.remove(laser)
                    boss_health -= 10
                    explosions.append(Explosion(laser[0], laser[1], 1))
                    explosion_sound.play()
                    if boss_health <= 0:
                        explosions.append(Explosion(boss[0] + 48, boss[1] + 48, 3))
                        explosion_sound.play()
                        boss = None
                        current_level += 1  # Keep going up in levels
                        game_state = GameState.LEVEL_COMPLETE
                    continue

            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy_width, enemy_height)
                if laser_rect.colliderect(enemy_rect):
                    lasers.remove(laser)
                    if enemy.take_damage():  # Only remove enemy if health reaches 0
                        enemies.remove(enemy)
                        score += 10 * SCORE_MULTIPLIER
                        explosions.append(Explosion(enemy.x + enemy_width//2, 
                                                 enemy.y + enemy_height//2))
                        explosion_sound.play()
                    break
    # Update animation frame
    animation_frame += 1

    # Check for boss defeat
    if boss and boss_health <= 0:
        # Add big explosion for boss defeat
        for _ in range(8):
            ex = boss[0] + random.randint(0, 96)
            ey = boss[1] + random.randint(0, 96)
            explosions.append(Explosion(ex, ey, 2))
            explosion_sound.play()
        boss = None
        score += 1000
        current_level += 1  # Keep going up in levels
        game_state = GameState.LEVEL_COMPLETE
        level_start_timer = LEVEL_START_DELAY

pygame.quit()
sys.exit()

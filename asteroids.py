#!/usr/bin/env python3
"""
Asteroids Game
A Python implementation of the classic Atari Asteroids game from 1979.

Copyright © 2023 Arne Damvin. All rights reserved.
"""
import math
import random
import pygame
import os
from pygame.math import Vector2

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT_NAME = 'arial'

# Vector constants
UP = Vector2(0, -1)

# Game settings
ACCELERATION = 0.05
SHIP_MAX_SPEED = 5
BULLET_SPEED = 10
BULLET_LIFETIME = 1000  # ms
ASTEROID_SPEED_RANGE = (0.5, 2.0)
INITIAL_ASTEROIDS = 4
UFO_SPAWN_CHANCE = 0.002  # chance per frame
UFO_SHOOT_INTERVAL = 2000  # ms

class GameObject:
    """Base class for all game objects."""
    
    def __init__(self, position, velocity=Vector2(0, 0), rotation=0):
        self.position = Vector2(position)
        self.velocity = Vector2(velocity)
        self.rotation = rotation
        self.points = []  # Points for vector drawing
        self.radius = 1  # Collision radius
        
    def update(self):
        # Update position based on velocity
        self.position += self.velocity
        
        # Wrap around screen edges
        self.position.x %= WIDTH
        self.position.y %= HEIGHT
        
    def draw(self, surface):
        # Transform points based on position and rotation
        transformed_points = []
        for point in self.points:
            # Rotate point
            angle = math.radians(self.rotation)
            rotated_x = point[0] * math.cos(angle) - point[1] * math.sin(angle)
            rotated_y = point[0] * math.sin(angle) + point[1] * math.cos(angle)
            
            # Translate to position
            transformed_points.append((
                rotated_x + self.position.x,
                rotated_y + self.position.y
            ))
        
        # Draw the lines connecting points
        if len(transformed_points) > 1:
            pygame.draw.lines(surface, WHITE, True, transformed_points, 1)
    
    def collides_with(self, other):
        """Check if this object collides with another."""
        distance = self.position.distance_to(other.position)
        return distance < (self.radius + other.radius)


class Ship(GameObject):
    """Player's spaceship."""
    
    def __init__(self, position):
        super().__init__(position, Vector2(0, 0), 0)
        self.direction = Vector2(UP)
        self.thrusting = False
        self.shooting_cooldown = 0
        self.radius = 15
        self.lives = 3
        self.invincible = False
        self.invincibility_time = 0
        self.blink_counter = 0
        
        # Define ship shape (triangle with thruster)
        self.points = [
            (0, -20),  # Nose
            (-12, 12),  # Left back
            (0, 6),     # Thruster indent
            (12, 12)    # Right back
        ]
        
        # Thruster points - only visible when thrusting
        self.thruster_points = [
            (-6, 12),  # Left thruster edge
            (0, 20),   # Thruster flame
            (6, 12)    # Right thruster edge
        ]
    
    def update(self):
        # Apply rotation to direction vector - FIX: correctly set direction based on rotation
        angle_rad = math.radians(self.rotation)
        self.direction = Vector2(math.sin(angle_rad), -math.cos(angle_rad))
        
        # Apply thrust if key is held
        if self.thrusting:
            self.velocity += self.direction * ACCELERATION
            
            # Limit maximum speed
            if self.velocity.length() > SHIP_MAX_SPEED:
                self.velocity.scale_to_length(SHIP_MAX_SPEED)
        
        # Update cooldown
        if self.shooting_cooldown > 0:
            self.shooting_cooldown -= 1
            
        # Update invincibility
        if self.invincible:
            self.invincibility_time -= 1
            self.blink_counter = (self.blink_counter + 1) % 10  # Used for blinking effect
            
            if self.invincibility_time <= 0:
                self.invincible = False
                
        super().update()
    
    def draw(self, surface):
        # Skip drawing every other few frames if invincible (creates blinking effect)
        if self.invincible and self.blink_counter < 5:
            return
            
        super().draw(surface)
        
        # Draw thruster if thrusting
        if self.thrusting:
            # Transform thruster points
            transformed_points = []
            for point in self.thruster_points:
                # Rotate point
                angle = math.radians(self.rotation)
                rotated_x = point[0] * math.cos(angle) - point[1] * math.sin(angle)
                rotated_y = point[0] * math.sin(angle) + point[1] * math.cos(angle)
                
                # Translate to position
                transformed_points.append((
                    rotated_x + self.position.x,
                    rotated_y + self.position.y
                ))
            
            # Draw thruster flame
            pygame.draw.polygon(surface, WHITE, transformed_points, 1)
    
    def shoot(self):
        """Create a bullet fired from the ship."""
        if self.shooting_cooldown > 0:
            return None
        
        # Set cooldown
        self.shooting_cooldown = 10
        
        # Calculate bullet starting position at ship's nose
        # The ship's nose is at (0, -20) rotated by the ship's rotation
        angle = math.radians(self.rotation)
        nose_x = 0 * math.cos(angle) - (-20) * math.sin(angle)
        nose_y = 0 * math.sin(angle) + (-20) * math.cos(angle)
        bullet_pos = self.position + Vector2(nose_x, nose_y)
        
        # Ensure the bullet direction is based on the ship's current rotation
        # This creates a unit vector pointing in the direction of the ship's nose
        bullet_direction = Vector2(math.sin(angle), -math.cos(angle))
        
        # Create bullet with the correct direction vector and the ship's velocity
        return Bullet(bullet_pos, bullet_direction, self.velocity)
    
    def hyperspace(self):
        """Teleport to a random location with a chance of destruction."""
        # 1/6 chance of death when using hyperspace
        self.position = Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        self.velocity = Vector2(0, 0)
        return random.random() > 5/6  # True means destroyed


class Bullet(GameObject):
    """Bullets fired by the ship or UFOs."""
    
    def __init__(self, position, direction, shooter_velocity, from_ufo=False):
        # Bullets inherit shooter's velocity and add their own speed in the direction
        velocity = shooter_velocity + direction * BULLET_SPEED
        super().__init__(position, velocity)
        self.lifetime = BULLET_LIFETIME
        self.radius = 1
        self.from_ufo = from_ufo
        
        # Bullets are just a point
        self.points = [(0, 0), (1, 1)]  # Small line to be visible
    
    def update(self):
        super().update()
        self.lifetime -= 16.67  # Approximately milliseconds per frame at 60fps
        
    def is_expired(self):
        return self.lifetime <= 0


class Asteroid(GameObject):
    """Asteroids that float around and can be destroyed."""
    
    SIZES = {
        "large": {"radius": 40, "score": 20},
        "medium": {"radius": 20, "score": 50},
        "small": {"radius": 10, "score": 100}
    }
    
    def __init__(self, position, size="large"):
        # Random velocity
        speed = random.uniform(*ASTEROID_SPEED_RANGE)
        angle = random.uniform(0, 2 * math.pi)
        velocity = Vector2(math.cos(angle), math.sin(angle)) * speed
        
        super().__init__(position, velocity, random.randint(0, 360))
        
        self.size = size
        self.radius = self.SIZES[size]["radius"]
        self.rotation_speed = random.uniform(-2, 2)
        self.score = self.SIZES[size]["score"]
        
        # Generate asteroid shape
        self.points = self._generate_shape()
    
    def _generate_shape(self):
        """Generate a random asteroid shape."""
        points = []
        num_vertices = random.randint(7, 12)
        for i in range(num_vertices):
            angle = i * (2 * math.pi / num_vertices)
            
            # Add some randomness to the radius
            offset = random.uniform(0.8, 1.2)
            x = math.cos(angle) * self.radius * offset
            y = math.sin(angle) * self.radius * offset
            
            points.append((x, y))
        return points
    
    def update(self):
        super().update()
        self.rotation += self.rotation_speed
    
    def split(self):
        """Split asteroid into smaller pieces."""
        if self.size == "large":
            return [
                Asteroid(self.position + Vector2(5, 5), "medium"),
                Asteroid(self.position + Vector2(-5, -5), "medium")
            ]
        elif self.size == "medium":
            return [
                Asteroid(self.position + Vector2(5, 0), "small"),
                Asteroid(self.position + Vector2(0, 5), "small")
            ]
        else:
            return []  # Small asteroids don't split


class UFO(GameObject):
    """Enemy UFOs that shoot at the player."""
    
    def __init__(self, size="small"):
        # Start at one edge of the screen
        side = random.choice(["left", "right"])
        if side == "left":
            x = 0
            velocity = Vector2(random.uniform(1, 2), 0)
        else:
            x = WIDTH
            velocity = Vector2(random.uniform(-2, -1), 0)
        
        y = random.randint(50, HEIGHT - 50)
        super().__init__((x, y), velocity)
        
        self.size = size
        self.radius = 15 if size == "small" else 30
        self.score = 1000 if size == "small" else 200
        self.last_shot_time = 0
        
        # Define UFO shape
        if size == "small":
            self.points = [
                (-5, -2), (5, -2),  # Top line
                (8, 0), (5, 2), (-5, 2), (-8, 0), (-5, -2),  # Bottom shape
                (-5, -2), (-3, -4), (3, -4), (5, -2)  # Cockpit
            ]
        else:
            self.points = [
                (-10, -3), (10, -3),  # Top line
                (15, 0), (10, 3), (-10, 3), (-15, 0), (-10, -3),  # Bottom shape
                (-10, -3), (-5, -7), (5, -7), (10, -3)  # Cockpit
            ]
    
    def update(self):
        super().update()
        
        # Check if UFO has left the screen horizontally
        if (self.velocity.x > 0 and self.position.x > WIDTH + 20) or \
           (self.velocity.x < 0 and self.position.x < -20):
            return False  # Signal to remove UFO
        
        # Randomly change y direction
        if random.random() < 0.02:
            self.velocity.y = random.uniform(-1, 1)
            
        # Keep in vertical bounds
        if self.position.y < 50:
            self.velocity.y = abs(self.velocity.y)
        elif self.position.y > HEIGHT - 50:
            self.velocity.y = -abs(self.velocity.y)
            
        return True
    
    def shoot(self, target_position):
        """Shoot at target (player)."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < UFO_SHOOT_INTERVAL:
            return None
            
        self.last_shot_time = current_time
        
        # Calculate direction to player
        direction = (target_position - self.position).normalize()
        
        # Small UFOs are more accurate
        if self.size == "large":
            # Add some randomness for large UFOs
            angle = random.uniform(-0.5, 0.5)  # radians
            direction = direction.rotate(angle * 180 / math.pi)
            
        return Bullet(self.position, direction, self.velocity, from_ufo=True)


class Game:
    """Main game controller."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Asteroids")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        
        # Initialize game objects
        self.reset_game()
        
        # Initialize sounds
        self.load_sounds()
        
        # Initialize fonts
        self.font_sm = pygame.font.SysFont(FONT_NAME, 20)
        self.font_md = pygame.font.SysFont(FONT_NAME, 32)
        self.font_lg = pygame.font.SysFont(FONT_NAME, 50)

    def load_sounds(self):
        """Load game sounds."""
        self.shoot_sound = pygame.mixer.Sound("sounds/fire.wav")
        self.explosion_sound = pygame.mixer.Sound("sounds/explode.wav")
        self.thrust_sound = pygame.mixer.Sound("sounds/thrust.wav")
        self.ufo_sound = pygame.mixer.Sound("sounds/saucer.wav")
        self.hyperspace_sound = pygame.mixer.Sound("sounds/hyperspace.wav")
        
        # Set volume
        for sound in [self.shoot_sound, self.explosion_sound, 
                      self.thrust_sound, self.ufo_sound, self.hyperspace_sound]:
            sound.set_volume(0.5)
    
    def load_high_score(self):
        """Load high score from file."""
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f:
                    return int(f.read().strip())
        except:
            # If there's an error reading the file, return 0
            pass
        return 0
    
    def save_high_score(self):
        """Save high score to file."""
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            # If there's an error saving the file, just continue
            pass
    
    def reset_game(self):
        """Reset the game state."""
        # Save high score if needed
        if self.game_over and self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            
        self.ship = Ship((WIDTH // 2, HEIGHT // 2))
        self.asteroids = []
        self.bullets = []
        self.ufos = []
        self.score = 0
        self.game_over = False
        self.level = 1
        
        # Generate initial asteroids
        self.create_asteroids(INITIAL_ASTEROIDS)
    
    def create_asteroids(self, count):
        """Create a number of asteroids."""
        for _ in range(count):
            # Make sure asteroids don't spawn too close to the player
            while True:
                pos = Vector2(
                    random.randint(0, WIDTH),
                    random.randint(0, HEIGHT)
                )
                # Ensure minimum distance from ship
                if pos.distance_to(self.ship.position) > 200:
                    break
            
            self.asteroids.append(Asteroid(pos))
    
    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # Hyperspace
                elif event.key == pygame.K_h and not self.game_over:
                    self.hyperspace_sound.play()
                    if self.ship.hyperspace():  # True if ship was destroyed
                        self.ship_destroyed()
                
                # Restart game if game over
                elif event.key == pygame.K_RETURN and self.game_over:
                    self.reset_game()
        
        # Handle continuous key presses
        if not self.game_over:
            keys = pygame.key.get_pressed()
            
            # Rotation - fixed to match standard controls
            if keys[pygame.K_LEFT]:
                self.ship.rotation -= 5  # Rotate counterclockwise (negative rotation)
            if keys[pygame.K_RIGHT]:
                self.ship.rotation += 5  # Rotate clockwise (positive rotation)
            
            # Thrust
            self.ship.thrusting = keys[pygame.K_UP]
            if self.ship.thrusting and not pygame.mixer.get_busy():
                self.thrust_sound.play(-1)  # Loop
            elif not self.ship.thrusting:
                self.thrust_sound.stop()
            
            # Shooting
            if keys[pygame.K_SPACE]:
                bullet = self.ship.shoot()
                if bullet:
                    self.bullets.append(bullet)
                    self.shoot_sound.play()
    
    def update(self):
        """Update game objects."""
        if self.game_over:
            return
            
        # Update ship
        self.ship.update()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            
            # Remove expired bullets
            if bullet.is_expired():
                self.bullets.remove(bullet)
        
        # Update asteroids
        for asteroid in self.asteroids:
            asteroid.update()
            
            # Check collision with ship (only if not invincible)
            if not self.game_over and not self.ship.invincible and asteroid.collides_with(self.ship):
                self.ship_destroyed()
                break
                
            # Check collisions with bullets
            for bullet in self.bullets[:]:
                if asteroid.collides_with(bullet) and not bullet.from_ufo:
                    self.bullets.remove(bullet)
                    self.destroy_asteroid(asteroid)
                    break
        
        # Update UFOs
        for ufo in self.ufos[:]:
            if not ufo.update():  # UFO has left the screen
                self.ufos.remove(ufo)
                continue
                
            # UFOs shoot at player
            bullet = ufo.shoot(self.ship.position)
            if bullet:
                self.bullets.append(bullet)
                self.shoot_sound.play()
                
            # Check collision with ship (only if not invincible)
            if not self.game_over and not self.ship.invincible and ufo.collides_with(self.ship):
                self.ship_destroyed()
                self.ufos.remove(ufo)
                break
                
            # Check collisions with player bullets
            for bullet in self.bullets[:]:
                if ufo.collides_with(bullet) and not bullet.from_ufo:
                    self.bullets.remove(bullet)
                    self.explosion_sound.play()
                    self.score += ufo.score
                    self.ufos.remove(ufo)
                    break
        
        # Check UFO bullets hitting player (only if not invincible)
        for bullet in self.bullets[:]:
            if bullet.from_ufo and not self.game_over and not self.ship.invincible and bullet.collides_with(self.ship):
                self.bullets.remove(bullet)
                self.ship_destroyed()
                break
        
        # Spawn UFOs randomly
        if random.random() < UFO_SPAWN_CHANCE and len(self.ufos) < 1:
            size = "small" if random.random() < 0.4 else "large"
            self.ufos.append(UFO(size))
            self.ufo_sound.play(-1)  # Loop the sound
            
        # Check if all asteroids are destroyed
        if len(self.asteroids) == 0:
            self.level += 1
            self.create_asteroids(INITIAL_ASTEROIDS + self.level)
    
    def destroy_asteroid(self, asteroid):
        """Destroy an asteroid and add new ones if it splits."""
        self.explosion_sound.play()
        self.score += asteroid.score
        
        # Remove the asteroid and add split parts if any
        self.asteroids.remove(asteroid)
        split_asteroids = asteroid.split()
        self.asteroids.extend(split_asteroids)
    
    def ship_destroyed(self):
        """Handle ship destruction."""
        self.explosion_sound.play()
        self.thrust_sound.stop()
        self.ufo_sound.stop()
        
        self.ship.lives -= 1
        
        if self.ship.lives <= 0:
            self.game_over = True
            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score
                # Save high score to file
                self.save_high_score()
        else:
            # Reset ship position and velocity
            self.ship.position = Vector2(WIDTH // 2, HEIGHT // 2)
            self.ship.velocity = Vector2(0, 0)
            self.ship.rotation = 0
            
            # Make ship invincible for 3 seconds (180 frames at 60fps)
            self.ship.invincible = True
            self.ship.invincibility_time = 180
            
            # Clear bullets and UFOs
            self.bullets.clear()
            self.ufos.clear()
    
    def draw(self):
        """Draw everything to the screen."""
        self.screen.fill(BLACK)
        
        # Draw ship
        if not self.game_over:
            self.ship.draw(self.screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Draw asteroids
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # Draw UFOs
        for ufo in self.ufos:
            ufo.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw game over message
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_hud(self):
        """Draw heads-up display."""
        # Score
        score_text = self.font_md.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # High score
        high_score_text = self.font_sm.render(f"High Score: {self.high_score}", True, WHITE)
        self.screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))
        
        # Level
        level_text = self.font_sm.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 10))
        
        # Lives - text
        lives_text = self.font_sm.render(f"Lives:", True, WHITE)
        self.screen.blit(lives_text, (10, HEIGHT - 30))
        
        # Lives - ship icons
        for i in range(self.ship.lives):
            # Draw small ship icons
            ship_points = [
                (0, -8),    # Nose
                (-5, 5),    # Left back
                (0, 2),     # Thruster indent
                (5, 5)      # Right back
            ]
            
            # Position for each ship icon
            x_pos = 70 + (i * 30)
            y_pos = HEIGHT - 20
            
            # Draw the small ship
            transformed_points = []
            for point in ship_points:
                transformed_points.append((
                    point[0] + x_pos,
                    point[1] + y_pos
                ))
            
            pygame.draw.lines(self.screen, WHITE, True, transformed_points, 1)
    
    def draw_game_over(self):
        """Draw game over message."""
        game_over_text = self.font_lg.render("GAME OVER", True, WHITE)
        press_key_text = self.font_md.render("Press ENTER to play again", True, WHITE)
        
        self.screen.blit(
            game_over_text, 
            (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50)
        )
        self.screen.blit(
            press_key_text, 
            (WIDTH // 2 - press_key_text.get_width() // 2, HEIGHT // 2 + 20)
        )
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.clock.tick(FPS)
            self.handle_input()
            self.update()
            self.draw()
        
        # Save high score when exiting
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()


# Run the game
if __name__ == "__main__":
    # Try to create sounds directory if it doesn't exist
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
        
    # Create empty sound files if they don't exist
    for sound_file in ["fire.wav", "explode.wav", "thrust.wav", "saucer.wav", "hyperspace.wav"]:
        sound_path = os.path.join("sounds", sound_file)
        if not os.path.exists(sound_path):
            try:
                # Create an empty WAV file
                with open(sound_path, "w") as f:
                    pass
            except:
                print(f"Warning: Could not create sound file {sound_path}")
    
    game = Game()
    game.run()
    
    pygame.quit() 
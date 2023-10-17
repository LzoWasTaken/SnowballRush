"""
Purpose: snowball_rush.py is a game where the player (a snowperson) must catch snowballs to prevent
themselves from melting, while avoiding rocks that take away their lives.

Author: Lzo 
Creation Date: 1/1/2022
"""
import pygame, random

# Initialize pygame
pygame.init()

# Set a display surface
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snowball Rush")

# Set FPS and clock
FPS = 60
clock = pygame.time.Clock()

# Set background music
background_music = pygame.mixer.music.load("background_music.mp3")

# Define classes
class Player(pygame.sprite.Sprite):
    """A class to represent the player, a snowperson"""
    def __init__(self):
        """Initializes the player"""
        super().__init__()
        # Set image 
        self.image = pygame.image.load("snowperson.png")
        self.rect = self.image.get_rect()
        self.rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT - 32)

        # Set player values
        self.velocity = 10
        self.temp = -500
        self.lives = 3

        # Set player sounds
        self.snowball_collision_sound = pygame.mixer.Sound("snowball_collision_sound.wav")
        self.rock_collision_sound = pygame.mixer.Sound("rock_collision_sound.wav")
        self.level_up_sound = pygame.mixer.Sound("level_up_sound.wav")
        self.game_over_sound = pygame.mixer.Sound("game_over_sound.wav")

    def reset(self, all=False):
        """Resets the player"""
        self.rect.centerx = WINDOW_WIDTH//2
        if all:
            self.temp = -500
            self.lives = 3


    def update(self):
        """Updates the player."""
        keys = pygame.key.get_pressed()

        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.velocity
            
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.velocity
        

class Projectile(pygame.sprite.Sprite):
    """A parent class to the two falling projectiles (rocks and snowballs)"""
    def __init__(self, velocity):
        """Initializes the projectile"""
        super().__init__()
        self.velocity = velocity 

    def update(self):
        self.rect.y += self.velocity

class Rock(Projectile):
    """A class to represent the falling rocks"""
    def __init__(self, velocity, x, y, damage):
        """Initalizes the rock"""
        super().__init__(velocity)
        self.image = pygame.image.load("rock.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.damage = damage

class Snowball(Projectile):
    """A class to represent the falling snowballs"""
    def __init__(self, velocity, x, y, healability):
        super().__init__(velocity)
        self.image = pygame.image.load("snowball.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.healability = healability

class Game:
    """A class to help better manage the game."""
    def __init__(self, rock_group, snowball_group, player, main_game_loop):

        # Set the main loop
        self.main_game_loop = main_game_loop
    
        # Set projectile groups and player sprites
        self.rock_group = rock_group
        self.snowball_group = snowball_group
        self.player = player 

        # Set font 
        self.title_font = pygame.font.Font("font.ttf", 40)
        self.regular_font = pygame.font.Font("font.ttf", 30)

        # Set game values
        self.rock_damage = 3
        self.rocks_thrown = 0
        self.rocks_to_be_thrown = 10
        self.rock_velocity = 10
        self.rock_threshold = WINDOW_HEIGHT

        self.snowball_velocity = 7
        self.snowball_health_increase = 2
        
        self.melt_rate = 0.1
        self.can_throw_new_rock = True

        # Set colours
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        self.level = 1

    def update(self):
        """Updates the game"""
        # Decrement the player's 
        self.player.temp += self.melt_rate 

        self.check_collisions()
        self.check_game_over()
        self.generate_projectiles()

    def draw(self):
        """Draws the HUD"""
        # Set the text
        title_text = self.title_font.render("Snowball Rush", True, self.WHITE)
        title_rect = title_text.get_rect()
        title_rect.center = (WINDOW_WIDTH//2, 30)

        temp_text = self.regular_font.render(f"Temp {int(self.player.temp)}°C", True, self.WHITE)
        temp_rect = temp_text.get_rect()
        temp_rect.center = (85, 30)

        lives_text = self.regular_font.render(f"Lives {self.player.lives}", True, self.WHITE)
        lives_rect = lives_text.get_rect()
        lives_rect.center = (525, 30)

        level_text = self.regular_font.render(f"Level: {self.level}", True, self.WHITE)
        level_rect = level_text.get_rect()
        level_rect.center = (WINDOW_WIDTH//2, 80)

        # Draw the HUD
        pygame.draw.rect(display_surface, self.BLACK, (0, 0, WINDOW_WIDTH, 100))
        pygame.draw.line(display_surface, self.WHITE, (0, 100), (WINDOW_WIDTH, 100))
        display_surface.blit(title_text, title_rect)
        display_surface.blit(temp_text, temp_rect)
        display_surface.blit(lives_text, lives_rect)
        display_surface.blit(level_text, level_rect)

    def check_collisions(self):
        """Checks for collisions between the user and projectiles."""

        if pygame.sprite.spritecollide(self.player, self.snowball_group, True):
            self.player.snowball_collision_sound.play()
            self.player.temp = -273.15

        if pygame.sprite.spritecollide(self.player, self.rock_group, True):
            self.player.rock_collision_sound.play()
            self.player.lives -= 1

    def generate_projectiles(self):
        """Generates both snowballs and rocks"""
        self.remove_unnecessary_projectiles()

        self.can_throw_new_rock = True
        for rock in self.rock_group:
            if rock.rect.y < self.rock_threshold:
                self.can_throw_new_rock = False
                break

        if self.can_throw_new_rock:
            self.rocks_thrown += 1

            if self.rocks_thrown >= self.rocks_to_be_thrown:
                if not self.rock_group and not self.snowball_group:
                    self.level_up()
            else:
                # Generate rock
                self.rock_group.add(Rock(self.rock_velocity, random.randint(32, WINDOW_WIDTH - 32), -100, self.rock_damage))
    
                # Generate snowballs
                snowball_x = random.randint(64, WINDOW_WIDTH - 64)
                snowball_relative_x = random.choice([50, -50])

                snowball_1 = Snowball(self.snowball_velocity + 2, snowball_x, -100, self.snowball_health_increase)
                snowball_2 = Snowball(self.snowball_velocity, snowball_x + snowball_relative_x, -100, self.snowball_health_increase)
                self.snowball_group.add(snowball_1, snowball_2)                

    def level_up(self):
        """Increases the game level"""
        self.player.level_up_sound.play()
        self.level += 1 
        self.player.reset(False)
        self.rocks_thrown = 0
        self.rocks_to_be_thrown += 5

        # Ensure that the melt rate does not exceed a certain limit. 
        self.melt_rate += 0.1
        if self.melt_rate > 2:
            self.melt_rate = 2

        # Ensure that the rock threshold does not exceed a certain limit. 
        self.rock_threshold -= 100
        if self.rock_threshold < 150:
            self.rock_threshold = 150

        self.pause_game(f"You've made it to level {self.level}!", "Press 'Enter' to resume the game")
    
    def pause_game(self, main_text, sub_text): 
        """Temporaraily pauses the game"""
        
        # Set the text
        main_text = self.regular_font.render(main_text, True, self.WHITE)
        main_rect = main_text.get_rect()
        main_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100)

        sub_text = self.regular_font.render(sub_text, True, self.WHITE) 
        sub_rect = sub_text.get_rect()
        sub_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100)

        # Fill the display and blit the text
        display_surface.fill(self.BLACK)

        display_surface.blit(main_text, main_rect)
        display_surface.blit(sub_text, sub_rect)

        pygame.display.update()

        is_paused = True 
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_paused = False
                    self.main_game_loop.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        is_paused = False

    def remove_unnecessary_projectiles(self):
        """Removes projectiles when they move out off of the display surface"""
        # Remove unnecessary snowballs
        for snowball in self.snowball_group:
            if snowball.rect.y > WINDOW_HEIGHT:
                self.snowball_group.remove(snowball)

        # Remove unncessary rocks 
        for rock in self.rock_group:
            if rock.rect.y > WINDOW_HEIGHT:
                self.rock_group.remove(rock)
    
    def reset_game(self):
        """Resets the entire game"""
        # Resets the player
        self.player.reset(True)

        # Rests game values
        self.melt_rate = 0.1
        self.level = 1
        self.rock_damage = 3
        self.rocks_thrown = 0
        self.rocks_to_be_thrown = 10
        self.rock_velocity = 10
        self.rock_threshold = WINDOW_HEIGHT

        self.snowball_velocity = 7
        self.snowball_health_increase = 2

        # Empty the projectile groups
        for rock in self.rock_group:
            self.rock_group.remove(rock)

        for snowball in self.snowball_group:
            self.snowball_group.remove(snowball)

    def check_game_over(self):
        """Check for a game over condition"""
        if self.player.lives <= 0 or self.player.temp >= 10:
            pygame.mixer.music.stop()

            if self.player.lives <= 0:
                self.pause_game("You lost all of your lives! Game Over!", "Press 'Enter' to play again.")
            else:
                self.pause_game("Your temperature exceeded 10°C! Game Over!", "Press 'Enter' to play again.")
            
            self.reset_game()
            pygame.mixer.music.play(-1, 0.0)

class MainLoop:
    """A class to run the game"""
    def __init__(self):
        """Initializes the main loop"""
        self.running = True

    def run(self, player_group, snowball_group, rock_group, game, clock, FPS):
        """Runs the main game loop"""
        # Main game loop
        while self.running:
            for event in pygame.event.get():
                # Check if the user wants to quit
                if event.type == pygame.QUIT:
                    self.running = False 

            # Fill the display
            display_surface.fill((0, 0, 0))

            # Update and draw the plyaer group
            player_group.update()
            player_group.draw(display_surface)

            # Update and draw the snowball group
            snowball_group.update()
            snowball_group.draw(display_surface)

            # Update and draw the rock group
            rock_group.update()
            rock_group.draw(display_surface)

            # Update and draw the game
            game.update()
            game.draw()

            # Update the display and tick the clock
            pygame.display.update()
            clock.tick(FPS)
                

# Set player group
player_group = pygame.sprite.Group()
player = Player()
player_group.add(player)

# Set rock group
rock_group = pygame.sprite.Group()

# Set snowball group
snowball_group = pygame.sprite.Group()

# Set the main game loop
main_game_loop = MainLoop()

# Set game object
game = Game(rock_group, snowball_group, player, main_game_loop)

# Play background music
pygame.mixer.music.play(-1, 0.0)

# Show title screen
game.pause_game("Welcome to Snowball Rush!", "Press 'Enter' to play!")

# The main game loop
main_game_loop.run(player_group, snowball_group, rock_group, game, clock, FPS)


# End the game
pygame.quit()

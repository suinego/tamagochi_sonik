import sys
import pygame
import random
import os
from dataclasses import dataclass
from typing import Callable, Optional

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 150, 255)

@dataclass
class Food:
    name: str
    health_effect: int
    happiness_effect: int

    def feed_pet(self, pet) -> None:
        pet.hunger += 20
        pet.health = min(pet.health + self.health_effect, 100)
        pet.happiness = min(pet.happiness + self.happiness_effect, 100)

@dataclass
class Pet:
    name: str
    type: str
    gender: str
    health: int = 100
    hunger: int = 100
    happiness: int = 100
    energy: int = 100
    is_sick: bool = False

    def __init__(
    self, 
    name: str, 
    type: str, 
    gender: str, 
    health: int = 100, 
    hunger: int = 100, 
    happiness: int = 100, 
    energy: int = 100, 
    is_sick: bool = False
    ) -> None:  
        self.name = name
        self.type = type
        self.gender = gender
        self.health = health
        self.hunger = hunger
        self.happiness = happiness
        self.energy = energy
        self.is_sick = is_sick
        self.last_update_time = pygame.time.get_ticks()

    def feed(self, food: Food) -> None:
        food.feed_pet(self)
        self.hunger = min(self.hunger + 20, 100)
        self.health = min(self.health, 100)
        self.happiness = min(self.happiness, 100)

    def play(self):
        if self.energy >= 10:
            self.happiness = min(self.happiness + 15, 100)
            self.energy = max(self.energy - 10, 0)
        else:
            self.happiness = max(self.happiness - 5, 0)

    def sleep(self):
        self.energy = min(self.energy + 30, 100)

    def heal(self):
        if self.is_sick:
            self.health = min(self.health + 20, 100)
            self.is_sick = False


    def update_status(self) -> bool:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > 4000:
            self.hunger = max(self.hunger - 5, 0)
            self.energy = max(self.energy - 5, 0)
            self.happiness = max(self.happiness - 2, 0)

            if random.randint(0, 100) < 5:
                self.is_sick = True

            self.last_update_time = current_time

        if self.health <= 0 or self.hunger <= 0 or self.happiness <= 0 or self.energy <= 0:            
            return False
        return True
    
class Game:
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    def __init__(self):
        self.pet = None
        self.is_running = True
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Тамагочи")
        self.background_game = pygame.image.load(os.path.join("data", "background.jpg"))
        self.background_game = pygame.transform.scale(self.background_game, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background_intro = pygame.image.load(os.path.join("data", "intro.jpg"))
        self.background_intro = pygame.transform.scale(self.background_intro, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.selected_pet_image = None
        self.pet_type = "Cat"
        self.gender = "Male"
        self.pet_images = {
            "male_cat": pygame.image.load("data/malecat.png").convert_alpha(),
            "female_cat": pygame.image.load("data/pngegg.png").convert_alpha(),
            "male_dog": pygame.image.load("data/maledog.png").convert_alpha(),
            "female_dog": pygame.image.load("data/femaledog.png").convert_alpha(),
}

    def create_pet(self, name: str, pet_type: str, gender: str) -> None:
        self.pet = Pet(name=name, type=pet_type, gender=gender)
        
    def render_text(self, text: str, x: int, y: int, size: int = 36, color: tuple[int, int, int] = BLACK) -> None:
        font = pygame.font.Font(None, size)
        rendered_text = font.render(text, True, color)
        self.screen.blit(rendered_text, (x, y))

    def render_status(self):
        self.render_text(f"Health: {self.pet.health}", 20, 20)
        self.render_text(f"Hunger: {self.pet.hunger}", 20, 60)
        self.render_text(f"Happiness: {self.pet.happiness}", 20, 100)
        self.render_text(f"Energy: {self.pet.energy}", 20, 140)

    def draw_button(self, text: str, x: int, y: int, width: int, height: int, callback: Optional[Callable] = None) -> None:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        normal_color = (255, 182, 193)
        hover_color = (255, 105, 180)
        color = normal_color
        if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
            color = hover_color
            if mouse_click[0] and callback:
                callback()
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=10)
        self.render_text(text, x + 10, y + 10, size=24, color=BLACK)

    def feed_pet(self):
        food = Food(name="Apple", health_effect=5, happiness_effect=10)
        self.pet.feed(food)

    def play_with_pet(self):
        self.pet.play()

    def let_pet_sleep(self):
        self.pet.sleep()

    def heal_pet(self):
        self.pet.heal()

    def end_game(self):
        self.is_running = False
        pygame.quit()
        sys.exit()

    def game_loop(self):
        clock = pygame.time.Clock()
        while self.is_running:
            self.screen.blit(self.background_game, (0, 0))
            self.render_status()
            self.draw_button("Feed", 20, 200, 100, 50, self.feed_pet)
            self.draw_button("Play", 20, 260, 100, 50, self.play_with_pet)
            self.draw_button("Sleep", 20, 320, 100, 50, self.let_pet_sleep)
            self.draw_button("Heal", 20, 380, 100, 50, self.heal_pet)

            if self.selected_pet_image:
                self.screen.blit(self.selected_pet_image, (300, 100))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.end_game()

            if not self.pet.update_status():
                self.render_text(f"{self.pet.name} умер...", 20, 500, size=48, color=(255, 0, 0))
                pygame.display.flip()
                pygame.time.wait(3000)
                self.end_game()

            pygame.display.flip()
            clock.tick(60)

    def select_type(self, pet_type: str) -> None:
        self.pet_type = pet_type
        self.update_pet_image()

    def select_gender(self, gender: str) -> None:
        self.gender = gender
        self.update_pet_image()

    def update_pet_image(self):
        if hasattr(self, "pet_type") and hasattr(self, "gender"):
            key = f"{self.gender.lower()}_{self.pet_type.lower()}"
            self.selected_pet_image = self.pet_images.get(key)

    def start_game(self, name, pet_type, gender):
        if name:
            self.create_pet(name, pet_type, gender)
            self.game_loop()

    def intro_screen(self):
        clock = pygame.time.Clock()
        input_active = False
        name = ""
        pet_type = self.pet_type
        gender = self.gender

        while True:
            self.screen.blit(self.background_intro, (0, 0))
            self.render_text("Enter Pet Name:", 20, 20, size=36)
            pygame.draw.rect(self.screen, GRAY, (20, 80, 300, 50))
            self.render_text(name, 30, 90, size=36)

            self.render_text("Select Pet Type:", 20, 160, size=36)
            self.draw_button("Cat", 20, 220, 100, 50, lambda: self.select_type("Cat"))
            self.draw_button("Dog", 130, 220, 100, 50, lambda: self.select_type("Dog"))

            self.render_text("Select Gender:", 20, 300, size=36)
            self.draw_button("Male", 20, 360, 100, 50, lambda: self.select_gender("Male"))
            self.draw_button("Female", 130, 360, 100, 50, lambda: self.select_gender("Female"))

            self.draw_button("Start Game", 20, 460, 150, 50, lambda: self.start_game(name, pet_type, gender))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.end_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if 20 <= pygame.mouse.get_pos()[0] <= 320 and 80 <= pygame.mouse.get_pos()[1] <= 130:
                        input_active = True
                elif event.type == pygame.KEYDOWN and input_active:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode

            pygame.display.flip()
            clock.tick(60)

def main():
    game = Game()
    game.intro_screen()

if __name__ == "__main__":
    main()

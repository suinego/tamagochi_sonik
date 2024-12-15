import unittest
import pygame
from unittest.mock import patch, MagicMock
from main import Pet, Food, Game


class TestGameLogic(unittest.TestCase):

    def setUp_2(self):
        pygame.init()
        patcher_pygame_display = patch("pygame.display.set_mode", MagicMock(return_value=pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))))
        patcher_pygame_image = patch("pygame.image.load", MagicMock(return_value=MagicMock(spec=pygame.Surface)))
        patcher_pygame_font = patch("pygame.font.Font", MagicMock())
    
        self.mock_display = patcher_pygame_display.start()
        self.mock_image = patcher_pygame_image.start()
        self.mock_font = patcher_pygame_font.start()

        self.addCleanup(patcher_pygame_display.stop)
        self.addCleanup(patcher_pygame_image.stop)
        self.addCleanup(patcher_pygame_font.stop)
        self.game = Game()

    def setUp(self):
        self.pet = Pet(name="Azat", type="Cat", gender="Male")
        self.game = Game()
        self.game.pet = self.pet
        
    def test_pet_initialization(self):
        self.assertEqual(self.pet.health, 100)
        self.assertEqual(self.pet.hunger, 100)
        self.assertEqual(self.pet.happiness, 100)
        self.assertEqual(self.pet.energy, 100)

    def test_pet_feed(self):
        food = Food(name="Apple", health_effect=5, happiness_effect=10)
        self.pet.feed(food)
        self.assertEqual(self.pet.hunger, 100)
        self.assertEqual(self.pet.health, 100)
        self.assertEqual(self.pet.happiness, 100)
        
    def test_pet_feed_invalid_food(self):
        invalid_food = Food(name="kaka", health_effect=0, happiness_effect=0)
        self.pet.feed(invalid_food)
        self.assertEqual(self.pet.hunger, 100)
        self.assertEqual(self.pet.health, 100)
        self.assertEqual(self.pet.happiness, 100)

    def test_pet_play(self):
            self.pet.energy = 20
            self.pet.play()
            self.assertEqual(self.pet.happiness, 100)
            self.assertEqual(self.pet.energy, 10)
            
    def test_game_play_multiple_times(self):
        initial_energy = self.pet.energy
        self.pet.play()
        self.assertEqual(self.pet.energy, initial_energy - 10)
        self.pet.play()
        self.assertEqual(self.pet.energy, initial_energy - 20)


    def test_pet_update_status(self):
        self.pet.hunger = 10
        with patch('pygame.time.get_ticks', return_value=self.pet.last_update_time + 4001):
            updated = self.pet.update_status()
            self.assertTrue(updated)
            self.assertEqual(self.pet.hunger, 5)

    def test_pet_sleep(self):
        self.pet.energy = 10
        self.pet.sleep()
        self.assertEqual(self.pet.energy, 40)

    def test_pet_sleep_2(self):
        self.pet.energy = 70
        self.pet.sleep()
        self.assertEqual(self.pet.energy, 100)
        
    def test_sleep_pet_3(self):
        pet = Pet(name="Jan", type="Dog", gender="Male", energy=30)
        pet.sleep()
        self.assertEqual(pet.energy, 60)

    def test_pet_death_health(self):
        self.pet.health = 0
        self.assertFalse(self.pet.update_status())

    def test_pet_death_hunger(self):
        self.pet.hunger = 0
        self.assertFalse(self.pet.update_status())

    def test_pet_death_happiness(self):
        self.pet.happiness = 0
        self.assertFalse(self.pet.update_status())

    def test_pet_death_energy(self):
        self.pet.energy = 0
        self.assertFalse(self.pet.update_status())

    def test_pet_update_status_timing(self):
        initial_time = self.pet.last_update_time
        with patch('pygame.time.get_ticks', return_value=initial_time + 4001):
            self.assertTrue(self.pet.update_status())
            self.assertEqual(self.pet.last_update_time, initial_time + 4001)
            self.assertEqual(self.pet.hunger, 95) 
            self.assertEqual(self.pet.energy, 95)
            self.assertEqual(self.pet.happiness, 98) 
        with patch('pygame.time.get_ticks', return_value=initial_time + 4001 + 4001):
            self.assertTrue(self.pet.update_status())
            self.assertEqual(self.pet.last_update_time, initial_time + 4001 + 4001)
            self.assertEqual(self.pet.hunger, 90)      
            self.assertEqual(self.pet.energy, 90)       
            self.assertEqual(self.pet.happiness, 96)

    def test_pet_energy(self):
        self.pet.energy = 10
        self.pet.play()
        self.assertEqual(self.pet.energy, 0)

    def test_pet_100(self):
        self.pet.happiness = 95
        self.pet.play()
        self.assertEqual(self.pet.happiness, 100)

    def test_pet_health_100(self):
        self.pet.health = 98
        food = Food(name="Apple", health_effect=5, happiness_effect=10)
        self.pet.feed(food)
        self.assertEqual(self.pet.health, 100)

    def test_pet_hunge_100(self):
        self.pet.hunger = 90
        food = Food(name="Apple", health_effect=5, happiness_effect=10)
        self.pet.feed(food)
        self.assertEqual(self.pet.hunger, 100)

    def test_pet_heal_sick(self):
        self.pet.is_sick = True
        self.pet.health = 80
        self.pet.heal()
        self.assertEqual(self.pet.health, 100)
        self.assertFalse(self.pet.is_sick)

    def test_pet_heal(self):
        self.pet.is_sick = False
        self.pet.health = 80
        self.pet.heal()
        self.assertEqual(self.pet.health, 80)
        self.assertFalse(self.pet.is_sick)

    def test_pet_sick(self):
        self.pet.is_sick = False
        with patch('random.randint', return_value=3):
            with patch('pygame.time.get_ticks', return_value=self.pet.last_update_time + 4001):
                self.assertTrue(self.pet.update_status())
                self.assertTrue(self.pet.is_sick)

    def test_pet_no_sick(self):
        self.pet.is_sick = False
        with patch('random.randint', return_value=10):
            with patch('pygame.time.get_ticks', return_value=self.pet.last_update_time + 4001):
                self.assertTrue(self.pet.update_status())
                self.assertFalse(self.pet.is_sick)
                
    def test_draw_button(self):
        callback_mock = MagicMock()
        self.game = Game()
        with patch("pygame.mouse.get_pos", return_value=(30, 210)), \
             patch("pygame.mouse.get_pressed", return_value=(1, 0, 0)):
            self.game.draw_button("Test", 20, 200, 100, 50, callback=callback_mock)
        callback_mock.assert_called_once()
    
    def test_game_draw_button_multiple_positions(self):
        callback_mock = MagicMock()
        self.game = Game()
        with patch("pygame.mouse.get_pos", return_value=(50, 250)), \
             patch("pygame.mouse.get_pressed", return_value=(1, 0, 0)):
            self.game.draw_button("Test Button", 20, 200, 100, 50, callback=callback_mock)
        callback_mock.assert_called_once()
        with patch("pygame.mouse.get_pos", return_value=(10, 10)):
            self.game.draw_button("Test Button", 20, 200, 100, 50, callback=callback_mock)
        callback_mock.assert_called_once()
    
    ''' def test_start_game(self):
        with patch.object(Game, 'create_pet') as mock_create_pet, \
             patch.object(Game, 'game_loop') as mock_game_loop:
            self.game.start_game(name="Charlie", pet_type="Cat", gender="Male")
            mock_create_pet.assert_called_once_with(name="Charlie", pet_type="Cat", gender="Male")
            mock_game_loop.assert_called_once() '''
    
    @patch("pygame.quit")
    @patch("sys.exit")
    def test_end_game(self, mock_quit, mock_exit):
        game = Game()
        game.is_running = True
        game.end_game()
        self.assertFalse(game.is_running)
        mock_quit.assert_called_once()
        mock_exit.assert_called_once()

    '''def test_image(self, mock_load):
        mock_image = MagicMock()
        mock_load.return_value = mock_image
        game = Game()
        game.pet_images = {
            "male_cat": mock_image,
            "female_cat": mock_image
        }
        game.pet_type = "Cat"
        game.update_pet_image()
        self.assertIsNone(game.selected_pet_image) '''
    
    '''    def test_update_pet_image(self):
        self.game.pet_type = "Cat"
        self.game.gender = "Male"
        self.game.update_pet_image()
        self.assertEqual(self.game.selected_pet_image, self.game.pet_images.get("malecat"))

        self.game.pet_type = "Dog"
        self.game.gender = "Female"
        self.game.update_pet_image()
        self.assertEqual(self.game.selected_pet_image, self.game.pet_images.get("femaledog"))
        '''
    @patch('pygame.font.Font')
    @patch('pygame.display.set_mode', return_value=MagicMock(spec=pygame.Surface))
    @patch('pygame.image.load', return_value=MagicMock(spec=pygame.Surface))
    
    def test_render_text(self, MockImage, MockDisplay, MockFont):
        mock_font = MagicMock()
        MockFont.return_value = mock_font
        mock_rendered_text = MagicMock()
        mock_font.render.return_value = mock_rendered_text
        mock_screen = MagicMock(spec=pygame.Surface)
        self.game.screen = mock_screen
        self.game.render_text("Sonik!", 100, 150, 24, (255, 0, 0))
        MockFont.assert_called_once_with(None, 24)
        mock_font.render.assert_called_once_with("Sonik!", True, (255, 0, 0))
        mock_screen.blit.assert_called_once_with(mock_rendered_text, (100, 150))
        
    
    


if __name__ == "__main__":
    unittest.main()
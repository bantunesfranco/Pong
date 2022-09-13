import sys, os, random, pygame

class Block(pygame.sprite.Sprite):
	def __init__(self, path, x_pos, y_pos):
		super().__init__()

		self.image = pygame.image.load(path)
		self.rect = self.image.get_rect(center = (x_pos, y_pos))

class Paddle(Block):
	def __init__(self, path, x_pos, y_pos, velocity):
		super().__init__(path, x_pos, y_pos)
		
		self.velocity = velocity
		self.movement = 0

	def on_screen(self):
		if self.rect.top < 0:
			self.rect.top = 0
		if self.rect.bottom > HEIGHT:
			self.rect.bottom = HEIGHT

	def update(self, ball_group):
		if self == player:
			self.rect.y += self.movement
		if self == opponent:
			if random.choice((1, -1)) == 1:
				if self.rect.top < ball_group.sprite.rect.top:
					self.rect.y += self.velocity
			else:
				if self.rect.top < ball_group.sprite.rect.bottom:
					self.rect.y += self.velocity

			if random.choice((1, -1)) == 1:
				if self.rect.bottom > ball_group.sprite.rect.bottom:
					self.rect.y -= self.velocity
			else:
				if self.rect.bottom > ball_group.sprite.rect.top:
					self.rect.y -= self.velocity
		self.on_screen()

class Ball(Block):
	def __init__(self, path, x_pos, y_pos, x_velocity, y_velocity, paddles):
		super().__init__(path, x_pos, y_pos)
		
		self.x_velocity = x_velocity * random.choice((1, -1))
		self.y_velocity = y_velocity * random.choice((1, -1))
		self.paddles = paddles
		self.active = False
		self.score_time = 0

	def update(self):
		if self.active:
			self.rect.y += self.y_velocity
			self.rect.x += self.x_velocity
			self.collisions()
		else:
			self.restart_counter()
	
	def collisions(self):
		if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
			pygame.mixer.Sound.play(bounce_sound)
			self.y_velocity *= -1
		
		if pygame.sprite.spritecollide(self, self.paddles, False):
			pygame.mixer.Sound.play(bounce_sound)
			collision_paddle = pygame.sprite.spritecollide(self, self.paddles, False)[0].rect
			if abs(self.rect.right - collision_paddle.left) < 10 and self.x_velocity > 0:
				self.x_velocity *= -1
			if abs(self.rect.left - collision_paddle.right) < 10 and self.x_velocity < 0:
				self.x_velocity *= -1
			if abs(self.rect.top - collision_paddle.bottom) < 10 and self.y_velocity < 0:
				self.rect.top = collision_paddle.bottom
				self.y_velocity *= -1
			if abs(self.rect.bottom - collision_paddle.top) < 10 and self.y_velocity > 0:
				self.rect.bottom = collision_paddle.top
				self.y_velocity *= -1

	def reset_ball(self):
		self.active = False
		self.x_velocity *= random.choice((1, -1))
		self.y_velocity *= random.choice((1, -1))
		self.rect.center = (WIDTH/2, HEIGHT/2)
		self.score_time = pygame.time.get_ticks()
		pygame.mixer.Sound.play(score_sound)
	
	def restart_counter(self):
		current_time = pygame.time.get_ticks()
		countdown_time = 3

		if current_time - self.score_time <= 700:
			countdown_time = 3
		if 700 < current_time - self.score_time <= 1400:
			countdown_time = 2
		if 1400 < current_time - self.score_time <= 2100:
			countdown_time = 1
		if current_time - self.score_time >= 2100:
			self.active = True

		time_counter = game_font.render(str(countdown_time), True, accent_color)
		time_counter_pos = time_counter.get_rect(center = (WIDTH/2, HEIGHT/2 + 50))
		pygame.draw.rect(screen, bg_color, time_counter_pos)
		screen.blit(time_counter,time_counter_pos)

class GameManager:
	
	def __init__(self,ball_group,paddle_group):
		self.player_score = 0
		self.opponent_score = 0
		self.ball_group = ball_group
		self.paddle_group = paddle_group
		self.easy = 1
		self.normal = 2
		self.hard = 3

	def run_game(self):
		# Drawing the game objects
		self.paddle_group.draw(screen)
		self.ball_group.draw(screen)

		# Updating the game objects
		self.paddle_group.update(self.ball_group)
		self.ball_group.update()
		self.reset_ball()
		self.draw_score()

	def set_difficulty(self):
		if self == easy:
			ball.x_velocity = 3
			ball.y_velocity = 3
			player.velocity = 4
			opponent.velocity = 4
			print("Easy mode")
		if self == normal:
			ball.x_velocity = 4
			ball.y_velocity = 4
			player.velocity = 6
			opponent.velocity = 6
			print("Normal Mode")
		if self == hard:
			ball.x_velocity = 6
			ball.y_velocity = 6
			player.velocity = 8
			opponent.velocity = 8
			print("Hard Mode")

	def reset_paddle(self):
		player.rect.y = HEIGHT/2 - 60
		opponent.rect.y = HEIGHT/2 - 60

	def reset_ball(self):
		if self.ball_group.sprite.rect.right >= WIDTH:
			self.opponent_score += 1
			self.ball_group.sprite.reset_ball()
		if self.ball_group.sprite.rect.left <= 0:
			self.player_score += 1
			self.ball_group.sprite.reset_ball()

	def reset_score(self):
		self.opponent_score = 0 
		self.player_score = 0

	def reset_game(self):
		self.reset_score()
		self.ball_group.sprite.reset_ball()
		self.reset_paddle()

	def draw_score(self):
		playerScore = game_font.render(str(self.player_score), True, accent_color)
		opponentScore = game_font.render(str(self.opponent_score), True, accent_color)

		player_score_rect = playerScore.get_rect(midleft = (WIDTH / 2 + 40, HEIGHT/2))
		opponent_score_rect = opponentScore.get_rect(midright = (WIDTH / 2 - 40, HEIGHT/2))

		screen.blit(playerScore, player_score_rect)
		screen.blit(opponentScore, opponent_score_rect)

class Button():
	def __init__(self, order, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.order = order
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			pygame.mixer.Sound.play(bounce_sound)
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

# General setup
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
clock = pygame.time.Clock()

# Main Window
WIDTH = 1280
HEIGHT = 960
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pong')

# Global Variables
bg_color = pygame.Color(10, 10, 10)
accent_color = (230, 230, 230)
menu_font = pygame.font.Font('freesansbold.ttf', 128)
submenu_font = pygame.font.Font('freesansbold.ttf',64)
game_font = pygame.font.Font('freesansbold.ttf', 32)
bounce_sound = pygame.mixer.Sound("bounce.ogg")
bounce_sound.set_volume(0.25)
score_sound = pygame.mixer.Sound("score.ogg")
score_sound.set_volume(0.25)

middle_strip = pygame.Rect(WIDTH/2 - 2, 0, 4, HEIGHT)

# Game objects
player = Paddle('Paddle.png', 20, HEIGHT/2, 6)
opponent = Paddle('Paddle.png', WIDTH - 20, HEIGHT/2, 6)
paddle_group = pygame.sprite.Group()
paddle_group.add(player)
paddle_group.add(opponent)

ball = Ball('Ball.png', WIDTH/2, HEIGHT/2, 4, 4, paddle_group)
ball_sprite = pygame.sprite.GroupSingle()
ball_sprite.add(ball)

game_manager = GameManager(ball_sprite,paddle_group)

easy = game_manager.easy
normal = game_manager.normal
hard = game_manager.hard


def play():

	while True:
		# Background Stuff
		screen.fill(bg_color)
		pygame.draw.rect(screen, accent_color, middle_strip)
		mouse_pos = pygame.mouse.get_pos()

		back_button = Button(1, image = None, pos = (50, HEIGHT - 25 ), text_input = "Back", font = game_font, base_color = (200, 200, 200), hovering_color = (255, 255, 255))
		back_button.changeColor(mouse_pos)
		back_button.update(screen)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if back_button.checkForInput(mouse_pos):
					game_manager.reset_game()
					menu()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					game_manager.reset_game()
					menu()
				if event.key == pygame.K_UP:
					player.movement -= player.velocity
				if event.key == pygame.K_DOWN:
					player.movement += player.velocity
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_UP:
					player.movement += player.velocity
				if event.key == pygame.K_DOWN:
					player.movement -= player.velocity

		# Run the game
		game_manager.run_game()

		# Rendering
		pygame.display.flip()
		pygame.display.update()
		clock.tick(120)

def options():
	while True:

		# Background Stuff
		screen.fill(bg_color)
		mouse_pos = pygame.mouse.get_pos()

		# Menu Window
		menu_text = submenu_font.render("Select difficulty :", True, accent_color)
		menu_rect = menu_text.get_rect(center = (WIDTH / 2, 250))
		screen.blit(menu_text, menu_rect)

		easy_button = Button(1, image = None, pos = (WIDTH/2, HEIGHT/2 - 80 ), text_input = "Easy", font = submenu_font, base_color = (200, 200, 200), hovering_color = (255, 255, 255))
		normal_button = Button(2, image = None, pos = (WIDTH/2, HEIGHT/2 + 20 ), text_input = "Normal", font = submenu_font, base_color = (200, 200, 200), hovering_color = (255, 255, 255))
		hard_button = Button(3, image = None, pos = (WIDTH/2, HEIGHT/2 + 120 ), text_input = "Hard", font = submenu_font, base_color = (200, 200, 200), hovering_color = (255, 255, 255))
		back_button = Button(4, image = None, pos = (WIDTH/2, HEIGHT/2 + 320 ), text_input = "Back", font = submenu_font, base_color = (200, 200, 200), hovering_color = (255, 255, 255))
		buttons = [easy_button, normal_button, hard_button, back_button]

		for button in buttons:
			button.changeColor(mouse_pos)
			button.update(screen)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					pass
				if event.key == pygame.K_DOWN:
					pass
				if event.key == pygame.K_RETURN:
					pass
				if event.key == pygame.K_ESCAPE:
					menu()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if back_button.checkForInput(mouse_pos):
					menu()
				if easy_button.checkForInput(mouse_pos):
					GameManager.set_difficulty(easy)
				if normal_button.checkForInput(mouse_pos):
					GameManager.set_difficulty(normal)
				if hard_button.checkForInput(mouse_pos):
					GameManager.set_difficulty(hard)

		pygame.display.flip()
		pygame.display.update()

def menu():

	while True:
		# Background Stuff
		screen.fill(bg_color)
		mouse_pos = pygame.mouse.get_pos()

		# Menu Window
		menu_text = menu_font.render("PONG", True, accent_color)
		menu_rect = menu_text.get_rect(center = (WIDTH / 2, 200))
		screen.blit(menu_text, menu_rect)

		play_button = Button(1, image = None, pos = (WIDTH/2, HEIGHT/2 - 20 ), text_input ="Play", font = submenu_font, base_color = (200, 200, 200), hovering_color = (255, 255, 255))
		options_button = Button(2, image = None, pos = (WIDTH/2, HEIGHT/2 + 80), text_input ="Options", font = submenu_font, base_color = (200, 200, 200), hovering_color = (255, 255, 255))
		quit_button = Button(3, image = None, pos = (WIDTH/2, HEIGHT/2 + 180), text_input ="Quit", font = submenu_font, base_color = (200, 200, 200), hovering_color = (255, 255, 255))
		buttons = [play_button, options_button, quit_button]

		for button in buttons:
			button.changeColor(mouse_pos)
			button.update(screen)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					pass
				if event.key == pygame.K_DOWN:
					pass
				if event.key == pygame.K_RETURN:
					pass
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if play_button.checkForInput(mouse_pos):
					play()
				if options_button.checkForInput(mouse_pos):
					options()
				if quit_button.checkForInput(mouse_pos):
					pygame.quit()
					sys.exit()

		pygame.display.flip()
		pygame.display.update()

if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	menu()
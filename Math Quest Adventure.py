import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1200
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Math Quest Adventure")

#Define game variables
tile_size = 50
game_over = 0
quiz_active = False  #New variable to track if a quiz is active
selected_enemy = None  #To keep track of the enemy involved in the collision
question = ""
correct_answer = 0
answer_options = []
answer_buttons = []  #List to hold answer button instances
main_menu = True
score = 0  #Initialize the score variable
boss_defeated = False
level_complete = False
entering_name = True  #New flag for entering name
player_name = ""  #Variable to store the player's name
operation_menu = False  #New variable to track if the operation menu is active
selected_operation = None  #Store the selected operation
mouse_pressed = False  #Variable to track if the mouse is currently pressed

#Load fonts
retro_font = pygame.font.Font('Retro.ttf', 40)
score_font = pygame.font.Font('Retro.ttf', 25)

#Load images
bg_img = pygame.image.load('images/background.jpeg')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))
restart_img = pygame.image.load('images/restart.png')
start_img = pygame.image.load('images/start.png')
exit_img = pygame.image.load('images/exit.png')
addition_img = pygame.image.load('images/addition.png')
addition_img = pygame.transform.scale(addition_img, (100, 100))
subtraction_img = pygame.image.load('images/subtraction.png')
subtraction_img = pygame.transform.scale(subtraction_img, (100, 100))
multiplication_img = pygame.image.load('images/multiplication.png')
multiplication_img = pygame.transform.scale(multiplication_img, (100, 100))
division_img = pygame.image.load('images/division.png')
division_img = pygame.transform.scale(division_img, (100, 100))

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        #Get mouse position
        pos = pygame.mouse.get_pos()

        #Check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        
        #Draw button
        screen.blit(self.image, self.rect)

        return action

class AnswerButton():
    def __init__(self, x, y, width, height, text, is_correct):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (70, 130, 180)  #Steel Blue
        self.hover_color = (100, 149, 237)  #Cornflower Blue
        self.text = text
        self.is_correct = is_correct
        self.font = pygame.font.Font('Retro.ttf', 30)  #Use Retro.ttf for answer buttons

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        else:
            color = self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)  #White border

        #Render text
        text_surf = self.font.render(str(self.text), True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

#Function to create the player character
class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 10

        if game_over == 0 and not quiz_active:  #Allow movement only if not in quiz

            #Get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                self.vel_y = -12
                self.jumped = True
            if not key[pygame.K_SPACE]:
                self.jumped = False
            if key[pygame.K_LEFT] or key[pygame.K_a]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            elif key[pygame.K_RIGHT] or key[pygame.K_d]:
                dx += 5
                self.counter += 1
                self.direction = 1
            else:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index] 
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #Handle animation
            if self.counter > 0:
                if self.counter >= walk_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images_right):
                        self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index] 
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #Add gravity
            self.vel_y += 1
            if self.vel_y > 5:
                self.vel_y = 5
            dy += self.vel_y

            #Check for collision
            self.in_air = True
            for tile in world.tile_list:
                #Check for collision in X-Axis
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0            
                #Check for collision in Y-Axis
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #Check if below the ground i.e. jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #Check if above the ground i.e. falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            #**Boundary checks to keep player within screen limits**
            #Horizontal boundary check (left and right edges)
            if self.rect.x + dx < 0:  #Prevent moving beyond the left edge
                dx = -self.rect.x
            if self.rect.x + dx + self.width > screen_width:  #Prevent moving beyond the right edge
                dx = screen_width - self.rect.x - self.width

            #Vertical boundary check (top and bottom of the screen)
            if self.rect.y + dy < 0:  #Prevent jumping above the top edge
                dy = -self.rect.y
            if self.rect.y + dy + self.height > screen_height:  #Prevent falling below the bottom edge
                dy = screen_height - self.rect.y - self.height
                self.in_air = False  #The player is on the ground

            #Check for collision with enemies
            collided_enemies = pygame.sprite.spritecollide(self, enemy_group, False)
            if collided_enemies and not quiz_active:
                selected_enemy = collided_enemies[0]  #Select the first collided enemy
                start_quiz(selected_enemy)  #Function to initiate quiz

            #Update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
        
        #Draw player onto screen
        screen.blit(self.image, self.rect)
        
        return game_over
    
    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1,9):
            img_right = pygame.image.load(f'images/player{num}.png')
            img_right = pygame.transform.scale(img_right, (90, 90))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('images/dead.png')
        self.dead_image = pygame.transform.scale(self.dead_image, (90, 90))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

#Function to create the world data by putting tiles in each grid location
class World():
    def __init__(self, data):
        self.tile_list = []

        #Load blocks
        grass_img = pygame.image.load('images/grass.png')
        dirt_img = pygame.image.load('images/dirt.jpeg')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    enemy = Slime(col_count * tile_size, row_count * tile_size + 20)
                    enemy_group.add(enemy)
                if tile == 4:
                    enemy = Werewolf(col_count * tile_size, row_count * tile_size - 40)
                    enemy_group.add(enemy)
                if tile == 5:
                    enemy = Boss(col_count * tile_size, row_count * tile_size - 100)
                    enemy_group.add(enemy)
                col_count += 1
            row_count += 1

    def draw(self):
         for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Slime(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/slime.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Werewolf(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/werewolf.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Boss(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/boss.png')
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

#Function to start a quiz with different difficulties
def start_quiz(enemy):
    global quiz_active, question, correct_answer, answer_options, answer_buttons, selected_enemy
    quiz_active = True
    selected_enemy = enemy

    #Variables to store the question and answer options
    a, b, c = 0, 0, 0

    #Adjust difficulty and question generation based on enemy type
    if isinstance(enemy, Slime) or isinstance(enemy, Werewolf):
        #Slime and Werewolf: 2-number equations
        a = random.randint(1, 20) if isinstance(enemy, Slime) else random.randint(1, 50)
        b = random.randint(1, 20) if isinstance(enemy, Slime) else random.randint(1, 50)  #Avoid division by zero

        #Generate question based on selected operation
        if selected_operation == "addition":
            correct_answer = a + b
            question = f"What is {a} + {b}?"
        elif selected_operation == "subtraction":
            correct_answer = a - b
            question = f"What is {a} - {b}?"
        elif selected_operation == "multiplication":
            a = random.randint(1, 5) if isinstance(enemy, Slime) else random.randint(1, 10)
            b = random.randint(1, 5) if isinstance(enemy, Slime) else random.randint(1, 10)
            correct_answer = a * b
            question = f"What is {a} * {b}?"
        elif selected_operation == "division":
            b = random.randint(1, 20) if isinstance(enemy, Slime) else random.randint(1, 20)  #Reassign to avoid zero
            a = random.randint(b, 100) if isinstance(enemy, Slime) else random.randint(b, 100)  #Ensure a is divisible by b
            correct_answer = a // b
            question = f"What is {a} ÷ {b}?"

    elif isinstance(enemy, Boss):
        #Boss: 3-number equations
        a = random.randint(1, 50)
        b = random.randint(1, 50)
        c = random.randint(1, 50)

        #Generate question based on selected operation
        if selected_operation == "addition":
            correct_answer = a + b + c
            question = f"What is {a} + {b} + {c}?"
        elif selected_operation == "subtraction":
            correct_answer = a - b - c
            question = f"What is {a} - {b} - {c}?"
        elif selected_operation == "multiplication":
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            c = random.randint(1, 10)
            correct_answer = a * b * c
            question = f"What is {a} * {b} * {c}?"
        elif selected_operation == "division":
            b = random.randint(1, 10)
            c = random.randint(1, 10)
            a = random.randint(b * c, 100)  #Ensure a is divisible by both b and c
            correct_answer = a // b // c
            question = f"What is {a} ÷ {b} ÷ {c}?"

    #Generate three unique wrong answers based on the correct answer
    wrong_answers = set()
    while len(wrong_answers) < 3:
        wrong = random.randint(max(0, correct_answer - 10), correct_answer + 10)
        if wrong != correct_answer and wrong >= 0:
            wrong_answers.add(wrong)
    answer_options = list(wrong_answers)
    answer_options.append(correct_answer)
    random.shuffle(answer_options)

    #Create answer buttons
    answer_buttons = []
    button_width = 200
    button_height = 60
    start_x = (screen_width - (button_width * 2 + 50)) // 2
    start_y = screen_height // 2 + 50

    for i in range(4):
        x = start_x + (i % 2) * (button_width + 50)
        y = start_y + (i // 2) * (button_height + 20)
        is_correct = answer_options[i] == correct_answer
        btn = AnswerButton(x, y, button_width, button_height, answer_options[i], is_correct)
        answer_buttons.append(btn)

#Function to display the quiz on screen
def draw_quiz():
    #Draw semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))  #Black overlay
    screen.blit(overlay, (0,0))

    #Draw question
    text_surf = retro_font.render(question, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
    screen.blit(text_surf, text_rect)

    #Draw answer buttons
    for btn in answer_buttons:
        btn.draw(screen)

#Function to display the death screen on screen
def draw_death_screen():
    #Draw semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(180)  #Transparency level
    overlay.fill((0, 0, 0))  #Black overlay
    screen.blit(overlay, (0, 0))

    #Draw "You died" text
    death_font = pygame.font.Font('Retro.ttf', 64)  #Use the same font for consistency
    death_text = death_font.render("You Died", True, (255, 0, 0))  #Red text for emphasis
    death_rect = death_text.get_rect(center=(screen_width // 2, screen_height // 2 - 100))  #Center it
    screen.blit(death_text, death_rect)

    #Draw restart button
    restart_button.draw()

def display_score():
    score_text = score_font.render(f"Final Score: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2))  #Center it on the screen
    screen.blit(score_text, score_rect)
    pygame.display.update()  #Update the display to show the score

def complete_score():
    score_text = score_font.render(f"Your Score: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))  #Center it on the screen
    screen.blit(score_text, score_rect)
    pygame.display.update()  #Update the display to show the score

def draw_name_input_screen():
    #Draw black overlay
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.fill((0, 0, 0))  #Solid black overlay
    screen.blit(overlay, (0, 0))

    #Draw prompt for player to enter their name
    prompt_text = retro_font.render("Enter your name:", True, (255, 255, 255))
    screen.blit(prompt_text, (screen_width // 2 - prompt_text.get_width() // 2, screen_height // 2 - 100))

    #Draw the name that the player is typing
    name_surface = retro_font.render(player_name, True, (255, 255, 255))
    screen.blit(name_surface, (screen_width // 2 - name_surface.get_width() // 2, screen_height // 2))

    #Draw a prompt to continue after entering the name
    continue_prompt = score_font.render("Press Enter to continue", True, (200, 200, 200))
    screen.blit(continue_prompt, (screen_width // 2 - continue_prompt.get_width() // 2, screen_height // 2 + 100))

#Create buttons for math choices
addition_button = Button(screen_width // 2 - 350, screen_height // 2 + 25, addition_img)
subtraction_button = Button(screen_width // 2 - 150, screen_height // 2 + 25, subtraction_img)
multiplication_button = Button(screen_width // 2 + 50, screen_height // 2 + 25, multiplication_img)
division_button = Button(screen_width // 2 + 250, screen_height // 2 + 25, division_img)

#Add a variable to track selected math operation
selected_operation = "addition"

#World data
world_data = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 4, 0, 0, 0, 0, 5, 0, 0, 0],
[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

player = Player(100, screen_height - 180)

enemy_group = pygame.sprite.Group()

world = World(world_data)

#Create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

#Create Title
title_font = pygame.font.Font('Retro.ttf', 64)  #Load the Retro font at size 64
title_text = "Math Quest Adventure"  #Title text
title_surf = title_font.render(title_text, True, (58, 174, 216))  #Render title text
title_rect = title_surf.get_rect(center=(screen_width // 2, screen_height // 2 - 180))  #Center it


run = True
while run:

    clock.tick(fps)

    screen.blit(bg_img, (0,0))
        
    if entering_name:
            draw_name_input_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(player_name) > 0:  #Proceed to main menu if name is entered
                        entering_name = False
                        main_menu = True
                    elif event.key == pygame.K_BACKSPACE:  #Handle backspace
                        player_name = player_name[:-1]
                    else:
                        player_name += event.unicode  #Append typed characters to the player's name

    elif main_menu:
        screen.blit(title_surf, title_rect) 
        if player_name:
            player_name_text = retro_font.render(f"Hello {player_name}", True, (113, 47, 121))
            screen.blit(player_name_text, (screen_width // 2 - player_name_text.get_width() // 2, 200))
        if start_button.draw():
            main_menu = False
            mouse_pressed = True  #Indicate that a mouse button was pressed
        if exit_button.draw():
            run = False

    elif mouse_pressed:
        if pygame.mouse.get_pressed()[0] == 0:  #Check if the left mouse button is released
            mouse_pressed = False  #Reset the mouse_pressed flag
            operation_menu = True  #Move to the operation menu only after the release
    
    elif operation_menu:
    #Draw operation selection buttons
        if addition_button.draw():
            selected_operation = "addition"
            operation_menu = False  #Proceed to game
        if subtraction_button.draw():
            selected_operation = "subtraction"
            operation_menu = False
        if multiplication_button.draw():
            selected_operation = "multiplication"
            operation_menu = False
        if division_button.draw():
            selected_operation = "division"
            operation_menu = False
        #Optionally, display instructions on the screen
        operation_text = retro_font.render("Choose a Math Operation", True, (255, 255, 255))
        screen.blit(operation_text, (screen_width // 2 - operation_text.get_width() // 2, screen_height // 2 - 100))
        
    else:
        world.draw()
        enemy_group.draw(screen)

        if not quiz_active:
            game_over = player.update(game_over)

        #If player has died
        if game_over == -1:
            draw_death_screen()  #Draw the death screen

        else:
            #Handle player score display
            score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(topright=(screen_width - 20, 20))  #Put score on top right corner
            screen.blit(score_text, score_rect)

            #If a quiz is active, draw the quiz overlay
            if quiz_active:
                draw_quiz()

                #Handle answer button clicks
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for btn in answer_buttons:
                            if btn.is_clicked(event):
                                if btn.is_correct:
                                    #Correct answer: remove the enemy and deactivate quiz
                                    enemy_group.remove(selected_enemy)
                                    #Increment score based on enemy type
                                    if isinstance(selected_enemy, Slime):
                                        score += 10
                                    elif isinstance(selected_enemy, Werewolf):
                                        score += 20
                                    elif isinstance(selected_enemy, Boss):
                                        score += 50
                                        boss_defeated = True
                                    quiz_active = False
                                    selected_enemy = None
                                else:
                                    #Wrong answer: player dies
                                    game_over = -1
                                    quiz_active = False  #Deactivate quiz

        #Handle event processing outside the quiz and death conditions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        if quiz_active == False and boss_defeated:
            level_complete = True  #Set level complete to True
        
        #If player has died, check for restart button clicks
        if game_over == -1:
            display_score()  #Display score before reset
            if restart_button.draw():
                player.reset(100, screen_height - 180)
                game_over = 0
                score = 0

    if level_complete:
        font = pygame.font.Font('Retro.ttf', 74)  #Adjust font size as necessary
        text = font.render("Level complete!", True, (241, 143, 1))  #White text
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 170))  #Center the text
        screen.blit(text, text_rect)  #Draw text
        complete_score()  #Display score

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
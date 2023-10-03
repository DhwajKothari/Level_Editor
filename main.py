import pygame
import button
import csv
import pickle

pygame.init()

clock = pygame.time.Clock()
FPS = 60


# Game Window
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 400
LOWER_MARGIN = 100
SIDE_MARGIN = 200
#game window
# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 640
# LOWER_MARGIN = 100
# SIDE_MARGIN = 300


screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')

#define game variables
level = 0
ROWS = 16
MAX_COLS = 200
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1
bg_img_repeat = 4
current_tile = 0

#load images
pine1_img = pygame.image.load('images/Background/pine1_edited.png').convert_alpha()
pine2_img = pygame.image.load('images/Background/pine2_edited.png').convert_alpha()
mountain_img = pygame.image.load('images/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('images/Background/sky_cloud.png').convert_alpha()

img_list = []
for i in range(TILE_TYPES):
    img = pygame.image.load(f'images/tile/{i}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

save_img = pygame.image.load('images/save_btn.png').convert_alpha()
load_img = pygame.image.load('images/load_btn.png').convert_alpha()

#define colours
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)
#define font
font = pygame.font.SysFont('Futura', 30)

# create empty world
world_list = [[-1 for i in range(MAX_COLS) ] for j in range(ROWS)]

# create starting ground
for i in range(MAX_COLS):
    world_list[-1][i] = 0

#create function for drawing background
def draw_bg():
	screen.fill(GREEN)
	width = sky_img.get_width()
	for x in range(bg_img_repeat):
		screen.blit(sky_img, ((x * width) - scroll * 0.5, -60))
		screen.blit(mountain_img, ((x * width) - scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 100))
		screen.blit(pine1_img, ((x * width) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 60))
		screen.blit(pine2_img, ((x * width) - scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

# White line grid for guiding level creation
def draw_grid():
    # draw vertical line
    for col in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (col * TILE_SIZE  - scroll, 0), (col * TILE_SIZE  - scroll, SCREEN_HEIGHT))
    # draw horizontal line
    for row in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, row * TILE_SIZE), (SCREEN_WIDTH, row * TILE_SIZE))

# Draw Tiles
def draw_world():
    for y, row in enumerate(world_list):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x*TILE_SIZE - scroll, y*TILE_SIZE))

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

#create buttons
save_button = button.Button(SCREEN_WIDTH + 10, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
load_button = button.Button(SCREEN_WIDTH + 100, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)
# make a button list
button_list = []
button_row = 0
button_col = 0
for i in range(TILE_TYPES):
    tile_button = button.Button(SCREEN_WIDTH + (50 * button_col) + 20, 50 * button_row + 20, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

run = True

while run:
    
    clock.tick(FPS)
    draw_bg()
    draw_grid()
    draw_world()

    draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('Press UP or DOWN to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)

    # save and load level data
    if save_button.draw(screen):
        # save level data
        with open(f'level{level}_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for row in world_list:
                writer.writerow(row)
    
    if load_button.draw(screen):
        # load saved level data
        # reset scroll back to start 
        scroll = 0
        with open(f'level{level}_data.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for y, row in enumerate(reader):
                for x, tile in enumerate(row):
                    world_list[y][x] = int(tile)
    
    # here load is O(n^2) which can be converted to O(n) using pickle
    """Pickle files are more efficient and can preserve 
    the data types of the objects, making them a better option 
    for working with large datasets or complex data structures."""
        # Save data
            #pickle_out = open(f'level{level}_data', 'wb')
            #pickle.dump(world_data, pickle_out)
            #pickle_out.close()

        # Load Data
            #world_data = []
            #pickle_in = open(f'level{level}_data', 'rb')
            #world_data = pickle.load(pickle_in)

    #draw tile panel and tiles
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    # choose a tile
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count

    # highlight the selected tile
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 2)

    # scroll the map
    if scroll_left and scroll>0:
        scroll -= 5 * scroll_speed
    if scroll_right and scroll < (MAX_COLS * TILE_SIZE - SCREEN_WIDTH):
        scroll += 5 * scroll_speed

    # Add new tile to the screen
    # get mouse position
    mouse_pos = pygame.mouse.get_pos()
    x = (mouse_pos[0] + scroll) // TILE_SIZE
    y = mouse_pos[1] // TILE_SIZE

    # check that coordinates are within game screen
    if mouse_pos[0] < SCREEN_WIDTH and mouse_pos[1] < SCREEN_HEIGHT:
        # update the tile value
        if pygame.mouse.get_pressed()[0]: #get_pressed[0] check for left click
            if world_list[y][x] != current_tile:
                world_list[y][x] = current_tile
        
        if pygame.mouse.get_pressed()[2]: #get_pressed[0] check for right click
                world_list[y][x] = -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level>0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()
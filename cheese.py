import pygame
import random
import math

BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,255)
RED = (255,0,0)
GREEN = (0,255,100)
DOK_SKIN = (248, 240, 219)
DOK_SHADE = (204, 174, 142)
DOK_TRENCH = (207, 207, 207)
DOK_EYES = (3, 227, 255)
#python cheese.py

# PLAYER CLASS
class Player(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        
        self.name = "Kim Dokja"
        self.width = width
        self.height = height
        self.health = 100
        self.max_health = 100
        self.kills = 0
        self.eaten = 0
        self.x_speed = 0
        self.y_speed = 0
        # create the rect manually by kims dimensions
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        # prevent weird bug where starting too close to the 'edge' of screen would allow 
        # player to break through barrier. Dont set closer than 101, 101
        self.rect.x = 105
        self.rect.y = 105
        ############
        self.level = 1
        self.rat_num = 2 # how many rats will spawn in the level
        self.sword_available = False
        self.has_sword = False
        # reference to the Sword class
        self.sword = None
        # amount that the floor blocks should move by the next time they're drawn
        self.move_floor_x = 0
        self.move_floor_y = 0
        # Track players movement status in all directions
        self.is_moving_l = False
        self.is_moving_r = False
        self.is_moving_up = False
        self.is_moving_d = False
        # keep track of previous position so we can return player there if a barrier is hit
        self.old_x = 105
        self.old_y = 105
        
    def draw(self, screen):
        eye_size = 10
        #body
        pygame.draw.ellipse(screen, DOK_TRENCH, [self.rect.x,self.rect.y+40,50,50])
        pygame.draw.rect(screen, DOK_TRENCH, [self.rect.x,self.rect.y+65,50,30])
        #hands
        pygame.draw.ellipse(screen, DOK_SKIN, [self.rect.x-20,self.rect.y+60,20,20])
        pygame.draw.ellipse(screen, DOK_SKIN, [self.rect.x+50,self.rect.y+60,20,20])
        pygame.draw.ellipse(screen, DOK_SHADE, [self.rect.x+50,self.rect.y+60,20,20],1)
        pygame.draw.ellipse(screen, DOK_SHADE, [self.rect.x-20,self.rect.y+60,20,20],1)
        #feet
        pygame.draw.rect(screen, BLACK, [self.rect.x-5,self.rect.y+100,20,10])
        pygame.draw.rect(screen, BLACK, [self.rect.x+30,self.rect.y+100,20,10])
        
        #head
        pygame.draw.ellipse(screen, DOK_SKIN, [self.rect.x,self.rect.y,50,50])
        pygame.draw.ellipse(screen, DOK_SHADE, [self.rect.x,self.rect.y,50,50], 1)
        pygame.draw.ellipse(screen, BLACK, [self.rect.x+10, self.rect.y+20,eye_size,eye_size])
        pygame.draw.ellipse(screen, BLACK, [self.rect.x+30, self.rect.y+20,eye_size,eye_size])
        pygame.draw.polygon(screen, BLACK, [(self.rect.x,self.rect.y),(self.rect.x+15,self.rect.y-7),(self.rect.x+25,self.rect.y-8),(self.rect.x+35,self.rect.y-7), 
                            (self.rect.x+50, self.rect.y), (self.rect.x+55, self.rect.y+10),
                            (self.rect.x+55, self.rect.y+20),(self.rect.x+45, self.rect.y+15),(self.rect.x+40,self.rect.y+20), (self.rect.x+30, self.rect.y+10),
                            (self.rect.x+25,self.rect.y+20),(self.rect.x+20,self.rect.y+12),(self.rect.x+10,self.rect.y+22),(self.rect.x+5,self.rect.y+10),(self.rect.x-5,self.rect.y+20)])
       
        # add on the sword if it is held
        if self.has_sword and self.sword.is_swinging:
           self.draw_sword_swinging(screen)
        elif self.has_sword and not self.sword.is_swinging:
           self.draw_sword(screen)
            
    # pass the environment so we can use its properties
    # instead of set number boundaries, the edges of the screen will change once pushed by the player
    def move(self, Mgr):
        move_x = 0
        move_y = 0 # temporary variables to pass to Mgr.move_floor()

       # print("rect x: "+str(self.rect.x) + ", old x: "+str(self.old_x))

        # Return early if player is attempting to move against a barrier (wood wall)
        for bar in Mgr.barriers:
            if self.rect.colliderect(bar) and self.rect.x < bar.x:
                self.rect.x = self.old_x
                self.rect.y = self.old_y
        
        if self.rect.x <= 100 and self.is_moving_l: # only move floor while player IS STILL MOVING
            move_x = 3
        if self.rect.x >= 550 and self.is_moving_r:
            move_x = -3
        if self.rect.y < 100 and self.is_moving_up:
            move_y = 3
        if self.rect.y > 290 and self.is_moving_d:
            move_y = -3 

        # if there is no change move like normal
        if move_x == 0 and move_y == 0:
            # save old coordinates 
            self.old_x = self.rect.x
            self.old_y = self.rect.y 
            self.rect.x += self.x_speed
            self.rect.y += self.y_speed
        # allow for left/right movement even if the other direction is occupied
        elif move_x == 0 and move_y != 0:
            self.old_x = self.rect.x # Save old x /y here too whenever they are changing
            self.rect.x += self.x_speed
            Mgr.move_floor(Mgr.floor_blocks, move_x, move_y)
            Mgr.move_objects(Mgr.all_blocks, move_x, move_y)
        elif move_x != 0 and move_y == 0:
            self.old_y = self.rect.y
            self.rect.y += self.y_speed
            Mgr.move_floor(Mgr.floor_blocks, move_x, move_y)
            Mgr.move_objects(Mgr.all_blocks, move_x, move_y)
        else:
            # move floor, cheese, and rats
            Mgr.move_floor(Mgr.floor_blocks, move_x, move_y)
            Mgr.move_objects(Mgr.all_blocks, move_x, move_y)
    
    def pick_up_sword(self, screen, sword):
        self.has_sword = True
        self.sword = sword
    
    def draw_sword(self, screen):
        self.sword.image = pygame.image.load("sword_idle.png").convert()
        self.sword.image.set_colorkey(BLACK)
        self.sword.rect = self.sword.image.get_rect()
        
        self.sword.rect.x = self.rect.x+50
        self.sword.rect.y = self.rect.y-20
        screen.blit(self.sword.image, self.sword.rect)
        
    def draw_sword_swinging(self, screen):
        # Load new image for sword
        self.sword.image = pygame.image.load("sword_hit.png").convert()
        self.sword.image.set_colorkey(BLACK)
        self.sword.rect = self.sword.image.get_rect()
        
        self.sword.rect.x = self.rect.x+50
        self.sword.rect.y = self.rect.y+60
        screen.blit(self.sword.image, self.sword.rect)
                            
# CHEESE CLASS
class Cheese(pygame.sprite.Sprite): # size is 50x50
    def __init__(self, color, w, h):
        super().__init__()
        
        self.image = pygame.image.load("cheeseImg.png").convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        
# RAT CLASS
class Rat(pygame.sprite.Sprite): # 80 x 40
    def __init__(self, color, w, h):
        super().__init__()
        
        self.image = pygame.image.load("rat.png").convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.speed_x = 0
        self.speed_y = 0
        self.move_counter = 50 # rat cooldown counter (in use)
        self.jerk_counter = 0 # rat strange movement counter (in use)
        self.move_duration = 0 # rat moving counter (in use)
        self.moving = False
        #--------------------------------------------
        self.recent_x = [] # hold recent x positions
        self.recent_y = [] # hold recent y positions
        self.curr_pos_x = 0 # hold current rewrite position in x list
        self.curr_pos_y = 0 # hold current rewrite position in y list
        self.pause_length = 50 # controls how long rat waits before moving
        self.duration = 20 # controls how long rat moves for
        self.jerk_cooldown = random.randrange(50, 150) # controls how long rat waits before random movement
        self.jerking = False
        self.jerk_speed_x = 0
        self.jerk_speed_y = 0
    
    def update(self, x, y): # pass speeds as parameters to move rat
        self.rect.x += x
        self.rect.y += y
        # Set speed to zero if rat reaches a boundary
        if self.rect.x > 620 or self.rect.x < 0:
            self.reset_pos() # send them back to the rat hole if they go offscreen
        if self.rect.y > 460 or self.rect.y < 0:
            self.reset_pos()
            
    # move rat in small increments toward desired object (kim or cheese)
    def inch(self, goal):
        update_x = 0
        update_y = 0
        
        # Dont move if rat is jerking
        if self.jerking:
            return
        
        # if rat ready to move and hasn't been moving for too long
        if self.move_counter == self.pause_length and self.move_duration < self.duration:
            # move rats TOWARD x and y coordinates of their goal
            if goal.rect.x > self.rect.x:
                update_x = self.get_boost(False)
            elif goal.rect.x < self.rect.x:
                update_x = self.get_boost(True)
            if goal.rect.y > self.rect.y:
                update_y = self.get_boost(False)
            elif goal.rect.y < self.rect.y:
                update_y = self.get_boost(True)
                
            self.update(update_x, update_y)
            self.move_duration += 1
            
            # add recent positions using function so we can check if stuck
            # coord, list, position
            #self.curr_pos_x = self.add_to_list(self.rect.x, self.recent_x, self.curr_pos_x)
            #self.curr_pos_y = self.add_to_list(self.rect.y, self.recent_y, self.curr_pos_y)
                
        # if rat has been moving and its done
        elif self.move_counter == self.pause_length and self.move_duration >= self.duration:
            self.move_counter = 0
            self.move_duration = 0 # reset movement
            
        # if rat is not moving increment the move counter
        else:
            self.move_counter += 1
                
    def follow(self, player):
        update_x = 0
        update_y = 0
        
        if player.rect.x > self.rect.x:
            update_x = abs(self.speed_x)
        if player.rect.x < self.rect.x:
            update_x = abs(self.speed_x)*-1
        if player.rect.y > self.rect.y:
            update_y = abs(self.speed_y)
        if player.rect.y < self.rect.y:
            update_y = abs(self.speed_y)*-1
            
        self.update(update_x, update_y)
        # add new coordinates to the recent list so we can check if stuck
        # coord, list, position
        self.curr_pos_x = self.add_to_list(self.rect.x, self.recent_x, self.curr_pos_x)
        self.curr_pos_y = self.add_to_list(self.rect.y, self.recent_y, self.curr_pos_y)
        
    # Force rat to move randomly
    def jerk(self):
        # decide jerk speed
        if self.jerk_counter == self.jerk_cooldown and not self.jerking:
            self.jerking = True
            self.jerk_speed_x = random.randrange(-3, 3)
            self.jerk_speed_y = random.randrange(-3, 3)
            
        # if rat is ready to jerk and hasnt been moving for too long
        if self.jerk_counter == self.jerk_cooldown and self.move_duration < self.duration:
            self.update(self.jerk_speed_x, self.jerk_speed_y)
            self.move_duration += 1
        # if rat has jerked for enough time reset everything
        elif self.jerk_counter == self.jerk_cooldown and self.move_duration >= self.duration:
            self.jerk_counter = 0
            self.move_duration = 0
            self.jerking = False
        # if rat is not jerking
        else:
            self.jerk_counter += 1
    
    # add an x or y coordinate to the most recent list (rewrite if filled list to 10)
    def add_to_list(self, coord, List, position):
        if len(List) == 10:
            List.pop(position)
            List.insert(position, coord)
            
            #increment (or reset) position in list
            if position == 9:
                position = 0
            else:
                position += 1
                
        else:
            List.append(coord)
            
        return position
        
    # check if rat has been stuck in one position for too long
    def fix_stuck(self):
        # if rat has been bouncing or stuck in one spot
        if len(self.recent_x) == 10 or len(self.recent_y) == 10:
            if max(self.recent_x) - min(self.recent_x) <= 5:
                self.kill()
            
    # boost in negative(up/left) or positive(down/right) direction        
    def get_boost(self, is_neg): 
        if is_neg:
            boost = random.randrange(-3, -1)
        else:
            boost = random.randrange(1, 3)
        return boost
        
    # reset rat to random position on right side of screen
    def reset_pos(self):
        self.rect.x = 620
        self.rect.y = random.randrange(0, 460)
        
    def reset_speed(self):
        self.speed_x = 0
        self.speed_y = 0
        
class Sword(pygame.sprite.Sprite): # 23 x 100 idle, 100 x 23 swinging
    def __init__(self, color, w, h):
        super().__init__()
        
        self.name = "Unbreakable Faith"
        self.is_swinging = False
        self.image = pygame.image.load("sword_idle.png").convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
 
# regular floor background blocks 
class Floor(pygame.sprite.Sprite): # 120 width x 120 height
    def __init__(self, color, w, h, direction):
        super().__init__()
        
        self.direction = direction
        
        # Change image to a barrier img if direction is given
        if self.direction == "up":
            self.image = pygame.image.load("floors/floor_up.png").convert()
        elif self.direction == "bottom":
            self.image = pygame.image.load("floors/floor_bottom.png").convert()
        elif self.direction == "left":
            self.image = pygame.image.load("floors/floor_left.png").convert()
        elif self.direction == "right":
            self.image = pygame.image.load("floors/floor_right.png").convert()
        else:
            self.image = pygame.image.load("floors/floor_square.png").convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        
class Barrier(pygame.sprite.Sprite):
    def __init__(self, color, w, h, x, y, direction):
        super().__init__()
        
        self.direction = direction
        # Create an invisible rectangle which will prevent the player from moving
        # Side barriers
        if self.direction == "up":
            self.rect = pygame.Rect((x, y), (120, 60)) # Coords then size 
        elif self.direction == "left":
            self.rect = pygame.Rect((x, y), (60, 120)) # flip dimensions because barrier is on left side 
        elif self.direction == "right":
            self.rect = pygame.Rect((x+60, y), (60, 120)) 
        elif self.direction == "bottom":
            self.rect = pygame.Rect((x, y+60), (120, 60))     
        

class Corner(pygame.sprite.Sprite):
    def __init__(self, color, w, h, x, y, direction):
        super().__init__()
        
        self.direction = direction
        # Corner blocks
        if self.direction == "tl":
            self.image = pygame.image.load("floors/floor_crTL.png").convert()
        elif self.direction == "tr":
            self.image = pygame.image.load("floors/floor_crTR.png").convert()
        elif self.direction == "bl":
            self.image = pygame.image.load("floors/floor_crBL.png").convert()
        elif self.direction == "br":
            self.image = pygame.image.load("floors/floor_crBR.png").convert()            
        self.image.set_colorkey(BLACK)    
        
        # corner hitbox
        #self.rect = pygame.

# Control groups and lists of other objects
class Manager():
    def __init__(self, player, screen):
        
        # Create a reference to the player and screen
        self.player = player
        self.screen = screen
       
        # create a GROUP for all collidable objects (cheese and rats)
        self.all_blocks = pygame.sprite.Group()
        # create a GROUP for all cheeses
        self.cheese_blocks = pygame.sprite.Group()
        # create a GROUP for all rats
        self.rat_blocks = pygame.sprite.Group()
        # create a nested LIST for all floor blocks
        self.floor_blocks = []
        
        # Hold all of the Rects that player cannot move past
        self.barriers = []
        
        # load images and audio here
        self.crunch = pygame.mixer.Sound("crunch.ogg")
        self.magic = pygame.mixer.Sound("magic.ogg")
        self.chew = pygame.mixer.Sound("rat_chew.ogg")
        self.death = pygame.mixer.Sound("rat_die.ogg")
        self.jumpscare = pygame.mixer.Sound("rat_jumpscare.ogg")
        self.squeak = pygame.mixer.Sound("rat_squeak.ogg")
        self.yell = pygame.mixer.Sound("yell_rats.ogg")
        
    # move group of floor blocks 
    def move_floor(self, group, move_x, move_y):
        for row in group:
            for block in row:
                block.rect.x += move_x
                block.rect.y += move_y
                
    # move other objects like rat, cheese
    def move_objects(self, group, move_x, move_y):
        for item in group:
            item.rect.x += move_x
            item.rect.y += move_y
     
    # Generate 3 cheese blocks and add them to the group
    def create_cheese(self, amount):
        for i in range(amount):
            new = Cheese(WHITE, 50, 50)
            new.rect.x = random.randrange(0, 550)
            new.rect.y = random.randrange(0, 450)
            self.all_blocks.add(new)
            self.cheese_blocks.add(new)
     
    def create_rats(self,amount):
        for i in range(amount):
            new = Rat(RED, 80, 40)
            new.rect.x = 620
            new.rect.y = random.randrange(0, 460)
            new.speed_x = new.get_boost(False)
            new.speed_y = new.get_boost(False)
            self.all_blocks.add(new)
            self.rat_blocks.add(new) 
     
    def create_sword(self):
        new = Sword(BLUE, 23, 100)
        new.rect.x = random.randrange(0, 650)
        new.rect.y = random.randrange(0, 400)
        self.all_blocks.add(new) 
     
    def create_floor(self):
        y = -240 # start beyond the screen so player has somewhere to move
        for i in range(9): # also add ~2 blocks worth of space on right+bottom side
            curr_row = []
            x = -240
            for j in range(10):
                # Change image at top,left,right, and bottom sides
                if i == 0 and j == 0:
                    pass
                    #new = Barrier(WHITE, 120, 
                if i == 0 and j != 0: 
                    new = Floor(WHITE, 120, 60, "up")
                elif i == 8: # condtional one before b/c it will never reach 9
                    new = Floor(WHITE, 120, 60, "bottom")
                elif j == 0:
                    new = Floor(WHITE, 120, 60, "left")
                elif j == 9:
                    new = Floor(WHITE, 120, 60, "right")
                else:
                    # keep regular height for regular floors
                    new = Floor(WHITE, 120, 120, "")
                    
                new.rect.x = x 
                new.rect.y = y
                curr_row.append(new)
                x += 120
            self.floor_blocks.append(curr_row)
            y += 120
                
    # display floor blocks on screen
    def draw_floor(self): 
        for row in self.floor_blocks:
            for block in row:
                self.screen.blit(block.image, [block.rect.x, block.rect.y])
                
    def level_up(self):
        self.magic.play()
        pygame.time.wait(100)
        # create new cheeses
        self.create_cheese(3)
        self.player.level += 1
        if self.player.has_sword:
            self.player.rat_num += 1
        
        # increase time which rats move
        for rat in self.rat_blocks:
            rat.duration += 10
         
        if len(self.rat_blocks) == 0:
            self.create_rats(self.player.rat_num)
    
    def create_barriers(self):
        print(self.barriers[-1])
    
    # Create a red rectangle over location of all barriers to see if theyr real
    def show_barriers(self, screen):
        for barrier in self.barriers:
            newrect = pygame.Rect((barrier.x, barrier.y),(120, 60))
            pygame.draw.rect(screen, RED, newrect)
 
# 700 x 500
def game(): # we be making all things into functions
    pygame.init()
    
    size = [700,500]
    screen = pygame.display.set_mode(size)
    # Create player and manager
    kim = Player(DOK_SKIN, 50, 110)
    Mgr = Manager(kim, screen)
    pygame.display.set_caption("Eat the cheese, Kim!")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 25, True, False)


    # Create objects in the world
    Mgr.create_floor()
    Mgr.create_barriers()
    Mgr.create_cheese(3)
    #Mgr.create_rats(kim.rat_num)
        
    
    done = False #-----------------------------------------------------------------------------------------------------------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            # set speed when keys are pressed down
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    kim.is_moving_up = True # if any of these are pressed player is moving
                    kim.y_speed = -3
                if event.key == pygame.K_a:
                    kim.is_moving_l = True
                    kim.x_speed = -3
                if event.key == pygame.K_s:
                    kim.is_moving_d = True
                    kim.y_speed = 3
                if event.key == pygame.K_d:
                    kim.is_moving_r = True
                    kim.x_speed = 3
                #SWING START
                if event.key == pygame.K_e and kim.has_sword:
                    kim.sword.is_swinging = True
                    
            # reset speed when a key is let up
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    kim.y_speed = 0
                    kim.is_moving_up = False
                if event.key == pygame.K_s:
                    kim.y_speed = 0
                    kim.is_moving_d = False
                if event.key == pygame.K_a:
                    kim.is_moving_l = False
                    kim.x_speed = 0
                if event.key == pygame.K_d:
                    kim.x_speed = 0
                    kim.is_moving_r = False
                # SWING RELEASE
                if event.key == pygame.K_e and kim.has_sword:
                    kim.sword.is_swinging = False
                    

        # screen size 700x500
        kim.move(Mgr)
            
        for rat in Mgr.rat_blocks:
            rat.inch(kim)
            rat.jerk()
        
        # check if player has hit a collidable object (cheese or rat)
        kim_hit_blocks = pygame.sprite.spritecollide(kim, Mgr.all_blocks, False)
        for block in kim_hit_blocks:
            if type(block) == Rat:
                Mgr.jumpscare.play()
                death_screen()
                pygame.quit()
            elif type(block) == Cheese:
                kim.eaten += 1
                block.kill()
                Mgr.crunch.play()
            elif type(block) == Sword:
                kim.pick_up_sword(screen, block)
                block.kill()
                Mgr.yell.play()
            elif type(block) == Floor and block.is_barrier == True:
                pass
        
        if kim.has_sword and kim.sword.is_swinging:
            sword_hit_blocks = pygame.sprite.spritecollide(kim.sword, Mgr.all_blocks, False)
            for block in sword_hit_blocks:
                if type(block) == Rat:
                    Mgr.death.play()
                    block.kill()
          
        if len(Mgr.cheese_blocks) == 0:
            Mgr.level_up()
            
        # create ONE sword ONLY!!!!!
        if kim.level >= 3 and not kim.sword_available:
            kim.sword_available = True
            Mgr.create_sword()
        
        #screen.blit(floor,[0,0])
        # draw floor tiles
        Mgr.draw_floor()

        # TEXT
        score = font.render("You have eaten "+str(kim.eaten)+" cheeses", True, RED)
        screen.blit(score,[100,20])
        level_msg = font.render("LEVEL "+str(kim.level), True, DOK_EYES)
        screen.blit(level_msg, [600,20])
        
        # save this one to be displayed while sword is picked up
        help_msg = font.render("Press e to swing your sword!", True, GREEN)
        if kim.has_sword:
            screen.blit(help_msg,[100,50])
        
        kim.draw(screen) # draw player
        Mgr.all_blocks.draw(screen) # draw all collidable objects
        #Mgr.show_barriers(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    
def death_screen():
    pygame.init()
    size = [700,500]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("YOU DIED")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 25, True, False)
    
    message = font.render("You died", True, BLACK)
    message_rect = message.get_rect()
    message_rect.center = (350, 250)
    
    message_2 = font.render("Press 'f' to play again", True, BLACK)
    message_2_rect = message_2.get_rect()
    message_2_rect.center = (350, 300)
    
    done = False
    while not done:
        screen.fill(RED)
        screen.blit(message, message_rect)
        screen.blit(message_2, message_2_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    game()
                    pygame.quit()
                
        pygame.display.update()
    pygame.quit()

# This is the start up screen but we call it main so it runs first      
def main():
    pygame.init()
    size = [700,500]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Welcome to Cheese game!")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 25, True, False)
    
    message = font.render("Press any key to begin!", True, BLACK)
    message_rect = message.get_rect()
    message_rect.center = (350, 250)
    
    done = False
    while not done:
        screen.fill(DOK_EYES)
        screen.blit(message, message_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                game()
                pygame.quit()
                
        pygame.display.update()
    pygame.quit()
    
    
if __name__ == "__main__":
    main()
import tkinter as tk
from random import uniform, choice, random


# Zone de jeu
class Plan():
    
    def __init__(self, window, width, height, color):
        self.canvas = tk.Canvas(window, width = width, height = height, bg = color, cursor = "none")
        self.width = width
        self.height = height
        self.balls = []
        self.players = []
        self.bots = []
        
        
class Ball():
    
    def __init__(self, size : float, coords : tuple, color : str, plan : Plan, vect : tuple, speed):
        self.plan = plan
        self.size = size
        self.id = self.plan.canvas.create_oval(coords[0], coords[1], coords[0]+size, coords[1]+size, fill = color)
        self.vect = vect # Déplacements
        self.count = 0 # Nombre de collisions
        self.speed = speed
        # Valeurs initiales pour reset
        self.val_init = [coords[0], coords[1], coords[0]+size, coords[1]+size], self.speed
        
    
    def move_ball(self):
        x, y, X, Y = self.plan.canvas.coords(self.id)
        vx, vy = self.vect
        self.plan.canvas.coords(self.id, x+vx*self.speed, y+vy*self.speed, X+vx*self.speed, Y+vy*self.speed)
        
    def collisions_plan(self): 
        x, y, X, Y = self.plan.canvas.coords(self.id)
        # Rebonds sur le sol et le plafond
        if Y >= self.plan.height or y <= 0:
            self.vect = (self.vect[0], -self.vect[1])
        # Si sortie à droite alors le joueur 1 gagne un point
        if X >= self.plan.width:
            return 1
        # Si sortie à gauche alors le joueur 2 gagne un point
        elif x <= 0:
            return 2

    def collisions_players(self):
        for player in self.plan.players:
            x1, y1, X1, Y1 = self.plan.canvas.coords(self.id)
            x2, y2, X2, Y2 = player.plan.canvas.coords(player.id)
            if not (X1 < x2 or x1 > X2 or Y1 < y2 or y1 > Y2):
                if self.vect[0] < 0: # Si déplacement vers la gauche
                    self.plan.canvas.coords(self.id, X2, y1, X2+self.size, Y1)
                if self.vect[0] > 0: # Si déplacement vers la droite
                    self.plan.canvas.coords(self.id, x2-self.size, y1, x2, Y1)
                self.vect = (-self.vect[0]*uniform(0.9, 1.1), self.vect[1]*uniform(0.9, 1.1))
                self.count+=1 # +1 collision
                self.change_speed() # Augmente à la fois la vitesse de la balle et celle des joueurs
            
    def change_speed(self):
        if self.count == 1:
            self.speed+=4
            
        if self.count%5==0:
            self.speed+=1
            for player in self.plan.players:
                if player.speed <= 10: # Limite de vitesse pour les joueurs
                    player.speed+=1
    
    def run(self):
        self.move_ball()
        self.collisions_players()
        test = self.collisions_plan() # Teste si la balle est sortie
        return test
    
    def reset(self):
        coords, self.speed = self.val_init
        self.plan.canvas.coords(self.id, *coords)
        self.count = 0
        self.vect = (uniform(0.5, 1)*choice([-1, 1]), uniform(0.5, 1)*choice([-1, 1])) # Coup d'envoi aléatoire
    
    
class Player():
    
    def __init__(self, dimensions : tuple, coords : tuple, color : str, speed : float, plan : Plan, name):
        self.plan = plan
        self.dim = dimensions
        self.color = color
        self.id = plan.canvas.create_rectangle(coords[0], coords[1], coords[0]+dimensions[0], coords[1]+dimensions[1], fill = color)
        self.vect = (0, 0) # Déplacements
        self.speed = speed
        self.val_init = [coords[0], coords[1], coords[0]+dimensions[0], coords[1]+dimensions[1]], speed # Valeurs initiales pour reset
        self.score = Score(self)
        self.name = name
        
    def down(self):
        self.vect = (0, self.speed)
        
    def up(self):
        self.vect = (0, -self.speed)
        
    def move_players(self):
        x, y, X, Y = self.plan.canvas.coords(self.id)
        vx, vy = self.vect
        # Si sortie en haut alors replacement du joueur à la hauteur maximale autorisée
        if Y+vy > self.plan.height:
            self.plan.canvas.coords(self.id, x, self.plan.height, X, self.plan.height-self.dim[1])
        # Si sortie en bas alors replacement du joueur à la hauteur minimale autorisée
        elif y+vy < 0:
            self.plan.canvas.coords(self.id, x, self.dim[1], X, 0)
        else:
            self.plan.canvas.coords(self.id, x, y+vy, X, Y+vy)
        
    def stop(self):
        self.vect = (0, 0)
    
    def reset(self):
        coords, self.speed = self.val_init
        self.plan.canvas.coords(self.id, *coords)


class Score():

    def __init__(self, player):
        self.val = 0
        self.player = player
        x, y, X, Y = player.plan.canvas.coords(player.id)
        self.w, self.h = (x+X)/2, player.plan.height
        # Affichage du score du joueur associé
        self.id = player.plan.canvas.create_text(self.w, self.h*0.02, text = self.val, fill = "#FFFFFF", font = ('Helvetica', 15, 'bold'))
    
    # Ajoute 1 au score du joueur    
    def up(self):
        self.val += 1 
        self.player.plan.canvas.itemconfig(self.id, text=self.val)
        return self.val
        
    def reset(self):
        self.val = 0
        self.player.plan.canvas.itemconfig(self.id, text=self.val)
        

class Bot():
    
    def __init__(self, window, player, ball, plan, side, level):
        self.window = window
        self.ball = ball
        self.player = player
        self.plan = plan
        self.prediction = False
        self.side = side
        self.lvl = level
        
    def process(self):
        x1, y1, X1, Y1 = self.ball.plan.canvas.coords(self.ball.id)
        # prédiction
        if (self.ball.vect[0] > 0 and self.side == 1) or (self.ball.vect[0] < 0 and self.side == -1):
            copy = Ball(self.ball.size, (x1, y1), "#000000", self.plan, self.ball.vect, self.ball.speed)
            test = False
            while not test:
                copy.move_ball()
                test = copy.collisions_plan()
            x1, y1, X1, Y1 = self.player.plan.canvas.coords(copy.id)
            self.player.plan.canvas.delete(copy.id)
            return x1, y1, X1, Y1
        
    def move(self, prediction):
        x1, y1, X1, Y1 = prediction
        x2, y2, X2, Y2 = self.player.plan.canvas.coords(self.player.id)
        center = y2 + self.player.dim[1]/2
        # Mouvements du bot en fonction de la prédiction
        if center-self.player.dim[1]/10 < y1 < center+self.player.dim[1]/10:
            self.player.stop()
        elif y1 < center:
            self.player.up()
        elif y1 > center:
            self.player.down()
    
    # Visionnaire
    def lvl_5(self):
        if not self.prediction:
            self.prediction = self.process()
        else:
            self.move(self.prediction)
            if self.ball.vect[0] < 0 and self.side == 1:
                self.prediction = False
            elif self.ball.vect[0] > 0 and self.side == -1:
                self.prediction = False

    # Brute
    def lvl_4(self):
        x1, y1, X1, Y1 = self.ball.plan.canvas.coords(self.ball.id)
        x2, y2, X2, Y2 = self.player.plan.canvas.coords(self.player.id)
        center = y2 + self.player.dim[1]/2
        if center-self.player.dim[1]/10 < y1 < center+self.player.dim[1]/10:
            self.player.stop()
        elif y1 < center:
            self.player.up()
        elif y1 > center:
            self.player.down()
            
    # Humain       
    def lvl_3(self):
        x1, y1, X1, Y1 = self.ball.plan.canvas.coords(self.ball.id)
        x2, y2, X2, Y2 = self.player.plan.canvas.coords(self.player.id)
        center = y2 + self.player.dim[1]/2
        
        if center-self.player.dim[1]/10 < y1 < center+self.player.dim[1]/10:
            self.player.stop()
        elif (self.ball.vect[0] > 0 and self.side == 1) or (self.ball.vect[0] < 0 and self.side == -1):
            if Y1 < center:
                self.player.up()
            elif y1 > center:
                self.player.down()
                    
    # Paresseux            
    def lvl_2(self):
        x1, y1, X1, Y1 = self.ball.plan.canvas.coords(self.ball.id)
        x2, y2, X2, Y2 = self.player.plan.canvas.coords(self.player.id)
        center = y2 + self.player.dim[1]/2
        if center-self.player.dim[1]/10 < y1 < center+self.player.dim[1]/10:
            self.player.stop()
        elif ((self.ball.vect[0] > 0 and self.side == 1) or (self.ball.vect[0] < 0 and self.side == -1)) and not y2 < y1 < Y2:
            if Y1 < center:
                self.player.up()
            elif y1 > center:
                self.player.down()
                
    # Lent           
    def lvl_1(self):
        p = random()
        if p > 0.5:
            x1, y1, X1, Y1 = self.ball.plan.canvas.coords(self.ball.id)
            x2, y2, X2, Y2 = self.player.plan.canvas.coords(self.player.id)
            center = y2 + self.player.dim[1]/2
            if center-self.player.dim[1]/10 < y1 < center+self.player.dim[1]/10:
                self.player.stop()
            elif ((self.ball.vect[0] > 0 and self.side == 1) or (self.ball.vect[0] < 0 and self.side == -1)) and not y2 < y1 < Y2:
                if Y1 < center:
                    self.player.up()
                elif y1 > center:
                    self.player.down()
        
    def run(self):
        if self.lvl == "1":
            self.lvl_1()
        elif self.lvl == "2":
            self.lvl_2()
        elif self.lvl == "3":
            self.lvl_3()
        elif self.lvl == "4":
            self.lvl_4()
        elif self.lvl == "5":
            self.lvl_5()
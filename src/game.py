import tkinter as tk
from random import uniform, choice
from src.objects import Plan, Ball, Player, Bot


# Bande blanche du terrain
def line(size, plan):
    plan.canvas.create_rectangle(plan.width/2-size/2, 0, plan.width/2+size/2, plan.height, fill = "#FFFFFF", outline = "#FFFFFF")

# Cercle blanc du terrain        
def circle(r, plan):
    plan.canvas.create_oval(plan.width/2-r, plan.height/2-r, plan.width/2+r, plan.height/2+r, fill = "#000000", outline = "#FFFFFF", width=5)
    
            
def set_settings():
    # Choix du mode
    mode = input("Number of players (0|1|2)? ")
    while not mode in ["0", "1", "2"]:
        mode = input("Number of players (0|1|2)? ")  
    # Choix des noms des joueurs
    if mode == "0":
        name1, name2 = "bot 1", "bot 2"
        bot1_lvl =  input("Bot 1 Level (1-5) : ") 
        while not bot1_lvl in ["1", "2", "3", "4", "5"]:
            bot1_lvl =  input("Bot 1 Level (1-5) :  ")
        bot2_lvl =  input("Bot 2 Level (1-5) : ") 
        while not bot2_lvl in ["1", "2", "3", "4", "5"]:
            bot2_lvl =  input("Bot 2 Level (1-5) :  ")  
            
    elif mode == "1":
        name1 = input("Name of the player 1 : ")
        name2 = "bot"
        bot1_lvl =  input("Bot Level (1-5) : ") 
        while not bot1_lvl in ["1", "2", "3", "4", "5"]:
            bot1_lvl =  input("Bot Level (1-5) :  ")
        bot2_lvl = None 
    elif mode == "2":
        name1 = input("Name of the player 1 : ")
        name2 = input("Name of the player 2 : ")
        bot1_lvl = None 
        bot2_lvl = None 
    # Choix de la vitesse initiale de la balle
    scale = input("Choose the game's speed (1-5) : ")
    while not scale in ["1", "2", "3", "4", "5"]:
        scale = input("Choose the game's speed (1-5) : ")
    
    return mode, name1, name2, scale, bot1_lvl, bot2_lvl

# Initialisation des éléments du jeu à partir des paramètres inscrits par l'utilisateur
def initialize(mode, name1, name2, scale, bot1_lvl, bot2_lvl):
    window = tk.Tk(className = "Pingpong")  
    width = window.winfo_screenwidth()*0.9
    height = window.winfo_screenheight()*0.9
    plan = Plan(window, width, height, "#000000")
    plan.canvas.pack()

    circle(250, plan)
    line(6, plan)

    b1 = Ball(20, (width/2-10, height/2-10),"#FFFFFF", plan, (uniform(0.5, 1)*choice([-1, 1]), uniform(0.5, 1)*choice([-1, 1])), 2*scale)
    p1 = Player((20, height/3), (0, height/3), "#FF0000", min(2*scale+4, 10), plan, name1)
    p2 = Player((20, height/3), (width-20, height/3), "#7777FF", min(2*scale+4, 10), plan, name2) # Limite de vitesse initiale des joueurs fixée à 10

    plan.balls = [b1]
    plan.players = [p1, p2]
    if mode in ["0","1"] and bot1_lvl: plan.bots.append(Bot(window, p2, b1, plan, 1, bot1_lvl))
    if mode == "0" and bot2_lvl: plan.bots.append(Bot(window, p1, b1, plan, -1, bot2_lvl))

    if not mode == "0":
        window.bind("q", lambda e: p1.up())
        window.bind("w", lambda e: p1.down())
        window.bind("<KeyRelease-q>", lambda e: p1.stop())
        window.bind("<KeyRelease-w>", lambda e: p1.stop())

    if mode == "2":
        window.bind("p", lambda e: p2.up())
        window.bind("m", lambda e: p2.down())
        window.bind("<KeyRelease-p>", lambda e: p2.stop())
        window.bind("<KeyRelease-m>", lambda e: p2.stop())
    
    return window, plan


class Game():
    
    def __init__(self, window, plan, mode):
        self.window = window
        self.plan = plan
        self.mode = mode   
    
    # Boucle principale d'une partie
    def game_loop(self):
        test = None
        for ball in self.plan.balls:
            test = ball.run() # Déplacements de la balle + détection des collisions
            if test == 1: # Sortie à droite
                score1 = self.plan.players[0].score.up() # Le joueur 1 gagne un point
                if score1 == 3: # Si le joueur 1 a 3 points, alors il a gagné
                    self.win_screen(self.plan.players[0])
                else: # Sinon, on relance une partie
                    self.reset_game()
            if test == 2: # Sortie à gauche
                score2 = self.plan.players[1].score.up() # Le joueur 2 gagne un point
                if score2 == 3: # Si le joueur 2 a 3 points, alors il a gagné
                    self.win_screen(self.plan.players[1])
                else: # Sinon, on relance une partie
                    self.reset_game()
                
            if self.mode in ["0", "1"]: # Activation du/des bot(s) si l'utilisateur a choisi le mode 0 ou 1 joueur
                for bot in self.plan.bots:
                    bot.run()
            for player in self.plan.players:
                player.move_players() # Déplacements des joueurs
        if not test: # Si aucune sortie n'a été détectée, la partie continue
            self.window.after(10, self.game_loop)
        
    # Lancement du jeu (de la toute première partie)
    def set_game(self):
        self.window.update()
        self.window.after(3000, self.game_loop)
        self.window.mainloop()
    
    # Relancement d'une partie   
    def reset_game(self):
        for ball in self.plan.balls:
            ball.reset()
        for player in self.plan.players:
            player.reset()
        self.window.after(3000, self.game_loop)
        
    def win_screen(self, player):
        # Reset des scores de chaque joueur
        for p in self.plan.players:
            p.score.reset()
        w, h = player.plan.width, player.plan.height
        # Création d'un rectangle noir cachant l'écran
        black_screen = player.plan.canvas.create_rectangle(0, 0, w, h, fill = "#000000")
        # Création de l'écran de victoire en fonction du nom et de la couleur du gagnant
        msg = player.plan.canvas.create_text(w/2, h/2, text = f"{player.name} win !", fill = player.color, font = ('Helvetica', 100, 'bold'))
        self.window.update()
        # Lancement d'une nouvelle partie après 3 secondes
        self.window.after(3000, lambda: (player.plan.canvas.delete(black_screen, msg), self.reset_game()))
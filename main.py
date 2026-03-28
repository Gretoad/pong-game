from src.game import set_settings, initialize, Game      
        
        
def main():
    mode, name1, name2, scale, bot1_lvl, bot2_lvl = set_settings()
    # Lancement du jeu en fonction des paramètres spécifiés    
    window, plan = initialize(mode, name1, name2, int(scale), bot1_lvl, bot2_lvl)        
    game = Game(window, plan, mode)
    game.set_game()

main()
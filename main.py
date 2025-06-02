import pygame
from editor import GraphicsEditor

def main():
    pygame.init()
    editor = GraphicsEditor(1600, 900)
    editor.run()

if __name__ == "__main__":
    main()
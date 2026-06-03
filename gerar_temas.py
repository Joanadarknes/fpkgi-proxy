"""
Gerador de Backgrounds Temáticos para PKGi
==========================================
Cria múltiplos backgrounds com diferentes temas
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

def create_gradient_background(width, height, colors, name):
    """Cria um fundo com gradiente personalizado"""
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    
    # Gradiente diagonal
    for y in range(height):
        for x in range(width):
            # Normalizar posição para 0-1
            norm_x = x / width
            norm_y = y / height
            
            # Misturar cores baseado na posição
            blend = (norm_x + norm_y) / 2
            
            r1, g1, b1 = colors[0]
            r2, g2, b2 = colors[1]
            
            r = int(r1 + (r2 - r1) * blend)
            g = int(g1 + (g2 - g1) * blend)
            b = int(b1 + (b2 - b1) * blend)
            
            draw.point((x, y), (r, g, b))
    
    # Adicionar padrão sutil
    add_pattern(draw, width, height)
    
    image.save(f"background_{name}.png", "PNG")
    print(f"✅ Criado: background_{name}.png")

def add_pattern(draw, width, height):
    """Adiciona padrão geométrico sutil"""
    # Grid de pontos
    for x in range(0, width, 60):
        for y in range(0, height, 60):
            # Círculo pequeno semi-transparente
            radius = 1
            color = (255, 255, 255, 10)  # Branco muito transparente
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                        fill=(255, 255, 255))

def create_themed_backgrounds():
    """Cria diferentes temas de background"""
    
    themes = {
        "modern_dark": [(20, 25, 40), (60, 80, 120)],      # Azul escuro moderno
        "purple_space": [(45, 20, 70), (120, 60, 180)],   # Roxo espacial
        "orange_sunset": [(80, 40, 20), (200, 120, 60)],  # Laranja pôr do sol
        "green_matrix": [(10, 40, 20), (40, 120, 60)],    # Verde Matrix
        "red_gaming": [(60, 20, 20), (150, 50, 50)],      # Vermelho gaming
        "cyan_tech": [(20, 60, 80), (60, 150, 200)],      # Ciano tecnológico
    }
    
    # Resolução do PS4: 1920x1080
    width, height = 1920, 1080
    
    for theme_name, colors in themes.items():
        create_gradient_background(width, height, colors, theme_name)

if __name__ == "__main__":
    create_themed_backgrounds()

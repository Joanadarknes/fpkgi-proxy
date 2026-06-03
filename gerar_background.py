"""
Gerador de Background Moderno para FPKGi
========================================
Gera uma imagem de fundo com gradiente moderno
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

def create_modern_background():
    # Dimensões 4K para melhor qualidade
    width, height = 1920, 1080
    
    # Criar imagem base
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Criar gradiente principal
    for y in range(height):
        for x in range(width):
            # Gradiente diagonal complexo
            progress_x = x / width
            progress_y = y / height
            
            # Múltiplos gradientes sobrepostos
            r1 = int(102 + (118 - 102) * progress_x)  # 667eea -> 764ba2
            g1 = int(126 + (75 - 126) * progress_x)
            b1 = int(234 + (162 - 234) * progress_x)
            
            # Segundo gradiente (vertical)
            r2 = int(240 + (245 - 240) * progress_y)  # f093fb -> f5576c
            g2 = int(147 + (87 - 147) * progress_y)
            b2 = int(251 + (108 - 251) * progress_y)
            
            # Terceiro gradiente (radial do centro)
            center_x, center_y = width // 2, height // 2
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            max_distance = math.sqrt(center_x**2 + center_y**2)
            radial_progress = min(distance / max_distance, 1.0)
            
            r3 = int(79 + (254 - 79) * radial_progress)  # 4facfe -> bright
            g3 = int(172 + (254 - 172) * radial_progress)
            b3 = int(254 + (100 - 254) * radial_progress)
            
            # Combinar gradientes com pesos
            r = int((r1 * 0.4 + r2 * 0.3 + r3 * 0.3))
            g = int((g1 * 0.4 + g2 * 0.3 + g3 * 0.3))
            b = int((b1 * 0.4 + b2 * 0.3 + b3 * 0.3))
            
            # Garantir que os valores estão no range correto
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            img.putpixel((x, y), (r, g, b))
    
    # Adicionar efeitos de brilho
    add_glow_effects(img, draw, width, height)
    
    # Adicionar padrão sutil
    add_dot_pattern(img, draw, width, height)
    
    # Salvar
    img.save('background.jpg', 'JPEG', quality=95, optimize=True)
    print("✅ Background moderno criado: background.jpg")
    
    return img

def add_glow_effects(img, draw, width, height):
    """Adiciona efeitos de brilho radial"""
    # Pontos de luz
    glow_points = [
        (width * 0.2, height * 0.8, (120, 119, 198, 80)),  # Roxo
        (width * 0.8, height * 0.2, (255, 107, 157, 80)),  # Rosa
        (width * 0.4, height * 0.4, (0, 245, 255, 60)),    # Ciano
    ]
    
    for x, y, color in glow_points:
        for radius in range(150, 0, -10):
            alpha = int(color[3] * (radius / 150) * 0.3)
            if alpha > 0:
                # Criar máscara circular
                bbox = [x - radius, y - radius, x + radius, y + radius]
                draw.ellipse(bbox, fill=(*color[:3], alpha))

def add_dot_pattern(img, draw, width, height):
    """Adiciona padrão de pontos sutil"""
    dot_size = 1
    spacing = 60
    
    for x in range(0, width, spacing):
        for y in range(0, height, spacing):
            # Variação na opacidade baseada na posição
            opacity = int(8 + 7 * math.sin(x * 0.01) * math.cos(y * 0.01))
            color = (255, 255, 255, opacity)
            
            bbox = [x, y, x + dot_size, y + dot_size]
            draw.ellipse(bbox, fill=color)

if __name__ == "__main__":
    try:
        print("🎨 Criando background moderno para FPKGi...")
        create_modern_background()
    except ImportError:
        print("❌ PIL não encontrado. Instalando...")
        os.system("pip install Pillow")
        create_modern_background()
    except Exception as e:
        print(f"❌ Erro: {e}")

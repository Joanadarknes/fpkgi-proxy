# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

# Criar imagem 512x512
img = Image.new('RGB', (512, 512), color=(26, 26, 46))
draw = ImageDraw.Draw(img)

# Gradiente de fundo
for y in range(512):
    r = int(26 + (15 - 26) * y / 512)
    g = int(26 + (33 - 26) * y / 512)
    b = int(46 + (62 - 46) * y / 512)
    draw.line([(0, y), (512, y)], fill=(r, g, b))

# Círculo central (representa controle)
draw.ellipse([156, 180, 356, 280], fill=(42, 42, 74), outline=(0, 180, 255), width=4)

# Analógicos
draw.ellipse([185, 210, 225, 250], fill=(30, 30, 50))
draw.ellipse([287, 210, 327, 250], fill=(30, 30, 50))

# Botões do controle (PlayStation style)
draw.ellipse([320, 195, 340, 215], fill=(255, 107, 107))  # Vermelho (círculo)
draw.ellipse([345, 220, 365, 240], fill=(78, 205, 196))   # Verde (X)
draw.ellipse([295, 220, 315, 240], fill=(255, 230, 109))  # Amarelo (quadrado)
draw.ellipse([320, 245, 340, 265], fill=(168, 85, 247))   # Roxo (triângulo)

# Texto
try:
    font_large = ImageFont.truetype('arial.ttf', 42)
    font_small = ImageFont.truetype('arial.ttf', 32)
except:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# PS4 GAMES
draw.text((256, 340), 'PS4 GAMES', fill='white', anchor='mm', font=font_large)
# STORE
draw.text((256, 390), 'STORE', fill=(0, 212, 255), anchor='mm', font=font_small)

# Linhas decorativas
draw.line([(100, 440), (220, 440)], fill=(0, 180, 255), width=3)
draw.line([(292, 440), (412, 440)], fill=(0, 180, 255), width=3)

# Ponto central
draw.ellipse([250, 434, 262, 446], fill=(0, 212, 255))

# Salvar
img.save('sce_sys/icon0.png')
print('✅ icon0.png criado com sucesso em sce_sys/')
print('   Tamanho: 512x512 pixels')

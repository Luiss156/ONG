import pygame
import random
import math

# Inicializar Pygame
pygame.init()

# Tamaño de la ventana (ventana principal)
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Juego con espada, animación de golpe y monstruos")

# Tamaño del mundo (mapa grande)
WORLD_WIDTH = 1600
WORLD_HEIGHT = 1200
world = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))

# Configuraciones del minimapa
MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 150
minimap = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))
minimap_rect = minimap.get_rect(topleft=(WINDOW_WIDTH - MINIMAP_WIDTH - 10, 10))

# Jugador
player_size = 50
player_color = (0, 255, 0)
player_pos = [WORLD_WIDTH // 2, WORLD_HEIGHT // 2]
player_speed = 5
player_direction = 'RIGHT'  # Dirección inicial del jugador

# Vida del jugador (10 corazones)
max_hearts = 10
heart_size = 20
hearts = max_hearts  # Comienza con todos los corazones

# Espada
sword_size = (10, 60)  # Ancho y alto de la espada
sword_color = (255, 255, 255)
sword_angle = 0  # Ángulo de la espada
sword_attacking = False
attack_duration = 300  # Duración del ataque en milisegundos
attack_start_time = 0
attack_range = 100  # Rango de ataque en píxeles

# Monstruos
monster_size = 40
monster_color = (255, 0, 0)
monster_speed = 2
num_monsters = 5
monsters = []

for _ in range(num_monsters):
    monster_pos = [random.randint(0, WORLD_WIDTH - monster_size), random.randint(0, WORLD_HEIGHT - monster_size)]
    monsters.append({'pos': monster_pos, 'color': monster_color})

# Dibujar el minimapa
def draw_minimap():
    minimap.fill((100, 100, 100))  # Fondo gris del minimapa
    # Escalar la posición del jugador para el minimapa
    scale_x = MINIMAP_WIDTH / WORLD_WIDTH
    scale_y = MINIMAP_HEIGHT / WORLD_HEIGHT
    scaled_player_pos = (int(player_pos[0] * scale_x), int(player_pos[1] * scale_y))
    
    # Dibujar el jugador en el minimapa
    pygame.draw.rect(minimap, player_color, (*scaled_player_pos, int(player_size * scale_x), int(player_size * scale_y)))

    # Dibujar los monstruos en el minimapa
    for monster in monsters:
        scaled_monster_pos = (int(monster['pos'][0] * scale_x), int(monster['pos'][1] * scale_y))
        pygame.draw.rect(minimap, monster_color, (*scaled_monster_pos, int(monster_size * scale_x), int(monster_size * scale_y)))

# Dibujar la espada
def draw_sword():
    global sword_angle, sword_attacking, attack_start_time
    
    # Determinar la posición de la espada según la dirección del jugador
    sword_pos = player_pos.copy()
    sword_offset = [0, 0]

    if player_direction == 'RIGHT':
        sword_offset = [player_size, player_size // 2]
        sword_angle = 0
    elif player_direction == 'LEFT':
        sword_offset = [-sword_size[0], player_size // 2]
        sword_angle = 180
    elif player_direction == 'UP':
        sword_offset = [player_size // 2, -sword_size[1]]
        sword_angle = 90
    elif player_direction == 'DOWN':
        sword_offset = [player_size // 2, player_size]
        sword_angle = -90

    sword_pos[0] += sword_offset[0]
    sword_pos[1] += sword_offset[1]

    # Crear la superficie de la espada y rotarla
    sword = pygame.Surface(sword_size)
    sword.fill(sword_color)
    sword_rotated = pygame.transform.rotate(sword, sword_angle)
    
    # Ajustar la posición para el blit
    sword_rect = sword_rotated.get_rect(center=(sword_pos[0], sword_pos[1]))
    
    if sword_attacking:
        elapsed_time = pygame.time.get_ticks() - attack_start_time
        if elapsed_time < attack_duration:
            # Hacer que la espada gire 180 grados y vuelva a la posición
            angle = 180 * (elapsed_time / attack_duration)  # Rango de 0 a 180 grados
            sword_rotated = pygame.transform.rotate(sword, sword_angle + angle)
            sword_rect = sword_rotated.get_rect(center=(sword_pos[0], sword_pos[1]))
            # Dibujar el área de ataque
            pygame.draw.circle(world, (255, 255, 255, 100), sword_pos, attack_range, 1)  # Área de ataque translúcida
        else:
            sword_attacking = False  # Finaliza la animación de ataque
            sword_rotated = pygame.transform.rotate(sword, sword_angle)  # Vuelve al ángulo original
            sword_rect = sword_rotated.get_rect(center=(sword_pos[0], sword_pos[1]))
    else:
        sword_rotated = pygame.transform.rotate(sword, sword_angle)
        sword_rect = sword_rotated.get_rect(center=(sword_pos[0], sword_pos[1]))

    world.blit(sword_rotated, sword_rect)

# Dibujar corazones de vida
def draw_hearts():
    for i in range(hearts):  # Dibujar tantos corazones como vidas tenga el jugador
        pygame.draw.rect(window, (255, 0, 0), (10 + i * (heart_size + 5), 10, heart_size, heart_size))  # Corazones rojos

# Controlar el ataque con la espada
def attack():
    global sword_attacking, attack_start_time
    if not sword_attacking:
        sword_attacking = True
        attack_start_time = pygame.time.get_ticks()

# Mover los monstruos
def move_monsters():
    for monster in monsters:
        dx = player_pos[0] - monster['pos'][0]
        dy = player_pos[1] - monster['pos'][1]
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx /= distance
            dy /= distance
        monster['pos'][0] += dx * monster_speed
        monster['pos'][1] += dy * monster_speed

# Detectar colisiones con el área de ataque
def detect_collisions():
    for monster in monsters[:]:
        dist = math.hypot(monster['pos'][0] - player_pos[0], monster['pos'][1] - player_pos[1])
        if sword_attacking and dist <= attack_range:
            monsters.remove(monster)  # Eliminar al monstruo de la lista

# Dibujar los monstruos
def draw_monsters():
    for monster in monsters:
        pygame.draw.rect(world, monster['color'], (*monster['pos'], monster_size, monster_size))

# Ciclo principal del juego
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Controles del jugador
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos[0] -= player_speed
        player_direction = 'LEFT'
    if keys[pygame.K_RIGHT]:
        player_pos[0] += player_speed
        player_direction = 'RIGHT'
    if keys[pygame.K_UP]:
        player_pos[1] -= player_speed
        player_direction = 'UP'
    if keys[pygame.K_DOWN]:
        player_pos[1] += player_speed
        player_direction = 'DOWN'

    # Iniciar ataque con la espada
    if keys[pygame.K_q]:
        attack()

    # Restringir el movimiento del jugador dentro del mundo
    player_pos[0] = max(0, min(player_pos[0], WORLD_WIDTH - player_size))
    player_pos[1] = max(0, min(player_pos[1], WORLD_HEIGHT - player_size))

    # Mover los monstruos
    move_monsters()

    # Detectar colisiones con el área de ataque
    detect_collisions()

    # Determinar la posición de la cámara (centrada en el jugador)
    camera_x = player_pos[0] - WINDOW_WIDTH // 2
    camera_y = player_pos[1] - WINDOW_HEIGHT // 2

    # Restringir la cámara para que no se salga del mundo
    camera_x = max(0, min(camera_x, WORLD_WIDTH - WINDOW_WIDTH))
    camera_y = max(0, min(camera_y, WORLD_HEIGHT - WINDOW_HEIGHT))

    # Dibujar el mundo en la ventana principal
    world.fill((50, 50, 50))  # Fondo del mundo
    pygame.draw.rect(world, player_color, (*player_pos, player_size, player_size))

    # Dibujar los monstruos
    draw_monsters()

    # Dibujar la espada siempre al lado del jugador
    draw_sword()

    # Dibujar el mundo en la ventana principal
    window.blit(world, (0, 0), (camera_x, camera_y, WINDOW_WIDTH, WINDOW_HEIGHT))

    # Dibujar el minimapa
    draw_minimap()
    window.blit(minimap, minimap_rect)

    # Dibujar corazones de vida
    draw_hearts()

    # Actualizar la ventana
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

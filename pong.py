import pygame
import sys
import random
import cv2
import mediapipe as mp
import threading

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_SPEED = 6

BALL_SIZE = 15
BALL_SPEED_X = 3
BALL_SPEED_Y = 3

# Camera dead zone remapping
FINGER_MIN = 0.1
FINGER_MAX = 0.85

# --- Camera & MediaPipe Setup ---
cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

finger_y_normalized = 0.5
hand_detected = False

def camera_loop():
    global finger_y_normalized, hand_detected

    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            hand_detected = True
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                raw_y = hand_landmarks.landmark[8].y

                # Remap raw_y from real usable range to full 0.0 - 1.0
                remapped = (raw_y - FINGER_MIN) / (FINGER_MAX - FINGER_MIN)
                finger_y_normalized = max(0.0, min(1.0, remapped))
        
        else:
            hand_detected = False



camera_thread = threading.Thread(target=camera_loop, daemon=True)
camera_thread.start()

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gesture Pong")
clock = pygame.time.Clock()

font_large = pygame.font.SysFont("monospace", 48)
font_medium = pygame.font.SysFont("monospace", 28)
font_small = pygame.font.SysFont("monospace", 22)

# --- Game Objects ---
player_paddle = pygame.Rect(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ai_paddle = pygame.Rect(SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

ball_dx = BALL_SPEED_X
ball_dy = BALL_SPEED_Y

# --- State ---
game_state = "start"  
rally_count = 0
high_score = 0

def reset_ball():
    global ball_dx, ball_dy
    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    ball_dx = 0
    ball_dy = 0
    pygame.display.flip()
    pygame.time.wait(500)
    angle = random.uniform(30, 60)
    angle_rad = pygame.math.Vector2(1, 0).rotate(angle)
    ball_dx = round(angle_rad.x * BALL_SPEED_X) * random.choice([-1, 1])
    ball_dy = round(angle_rad.y * BALL_SPEED_Y) * random.choice([-1, 1])

def draw_center_line():
    for y in range(0, SCREEN_HEIGHT, 30):
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH // 2 - 2, y, 4, 15))

def draw_playing():
    screen.fill(BLACK)
    draw_center_line()
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, ai_paddle)
    pygame.draw.rect(screen, GREEN, ball)
    score_text = font_large.render(str(rally_count), True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 20, 20))

def draw_start():
    screen.fill(BLACK)
    title = font_large.render("Gesture Pong", True, WHITE)
    sub = font_medium.render("Move your index finger to play", True, GRAY)
    start = font_medium.render("Press SPACE to start", True, WHITE)
    high = font_medium.render(f"High Score: {high_score}", True, GRAY)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
    screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 230))
    screen.blit(start, (SCREEN_WIDTH // 2 - start.get_width() // 2, 310))
    screen.blit(high, (SCREEN_WIDTH // 2 - high.get_width() // 2, 360))

def draw_paused():
    # Draw the game in background dimmed
    draw_playing()
    # Overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    pause_text = font_large.render("PAUSED", True, WHITE)
    sub_text = font_medium.render("Show your hand to resume", True, GRAY)
    screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 230))
    screen.blit(sub_text, (SCREEN_WIDTH // 2 - sub_text.get_width() // 2, 310))

def draw_game_over():
    screen.fill(BLACK)
    over_text = font_large.render("Game Over", True, WHITE)
    score_text = font_medium.render(f"Score: {rally_count}", True, WHITE)
    high_text = font_medium.render(f"High Score: {high_score}", True, GRAY)
    restart_text = font_small.render("Press SPACE to play again", True, WHITE)
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, 150))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 260))
    screen.blit(high_text, (SCREEN_WIDTH // 2 - high_text.get_width() // 2, 310))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))

# --- Main Game Loop ---
while True:

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state in ["start", "game_over"]:
                    rally_count = 0
                    player_paddle.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
                    ai_paddle.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
                    reset_ball()
                    game_state = "playing"

    # --- State Machine ---
    if game_state == "start":
        draw_start()

    elif game_state == "playing":

        # Auto pause if hand not detected
        if not hand_detected:
            game_state = "paused"

        # --- Player Paddle ---
        target_y = int(finger_y_normalized * SCREEN_HEIGHT) - PADDLE_HEIGHT // 2
        target_y = max(0, min(SCREEN_HEIGHT - PADDLE_HEIGHT, target_y))
        if player_paddle.y < target_y:
            player_paddle.y += min(PADDLE_SPEED * 2, target_y - player_paddle.y)
        elif player_paddle.y > target_y:
            player_paddle.y -= min(PADDLE_SPEED * 2, player_paddle.y - target_y)

        # --- AI Paddle ---
        if ai_paddle.centery < ball.centery:
            ai_paddle.y += PADDLE_SPEED - 1
        elif ai_paddle.centery > ball.centery:
            ai_paddle.y -= PADDLE_SPEED - 1
        ai_paddle.y = max(0, min(SCREEN_HEIGHT - PADDLE_HEIGHT, ai_paddle.y))

        # --- Ball ---
        ball.x += ball_dx
        ball.y += ball_dy

        if ball.top <= 0:
            ball.top = 0
            ball_dy *= -1
        if ball.bottom >= SCREEN_HEIGHT:
            ball.bottom = SCREEN_HEIGHT
            ball_dy *= -1

        if ball.colliderect(player_paddle):
            ball.left = player_paddle.right
            ball_dx *= -1
            rally_count += 1

        if ball.colliderect(ai_paddle):
            ball.right = ai_paddle.left
            ball_dx *= -1

        # --- Scoring ---
        if ball.left <= 0:
            high_score = max(high_score, rally_count)
            game_state = "game_over"

        if ball.right >= SCREEN_WIDTH:
            reset_ball()

        draw_playing()

    elif game_state == "paused":
        # Auto resume when hand comes back
        if hand_detected:
            game_state = "playing"
        draw_paused()

    elif game_state == "game_over":
        draw_game_over()

    pygame.display.flip()
    clock.tick(FPS)
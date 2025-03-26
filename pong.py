import pygame
import sys
import random

# 初期化
pygame.init()

# 画面サイズとウィンドウ設定
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Breakout Game - Tribute to Tetris")
clock = pygame.time.Clock()

# 色の定義
WHITE   = (255, 255, 255)
BLACK   = (0, 0, 0)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
BLUE    = (0, 0, 255)
YELLOW  = (255, 255, 0)
CYAN    = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE  = (255, 165, 0)
PURPLE  = (160, 32, 240)

brick_colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, ORANGE, PURPLE]

# サウンドのロード
try:
    bounce_sound = pygame.mixer.Sound("bounce.wav")
    brick_sound = pygame.mixer.Sound("brick.wav")
except Exception as e:
    print("サウンドファイルの読み込みに失敗:", e)
    bounce_sound = None
    brick_sound = None

# ゲーム状態とステージ、スコアの初期設定
game_state = "TITLE"  # "TITLE", "PLAYING", "GAME_OVER", "GAME_CLEAR"
stage = 1
score = 0

# パドルクラス
class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 15
        self.x = (screen_width - self.width) // 2
        self.y = screen_height - self.height - 10
        self.speed = 8
    
    def move(self, direction):
        # direction: -1 で左、1 で右
        self.x += direction * self.speed
        if self.x < 0:
            self.x = 0
        if self.x + self.width > screen_width:
            self.x = screen_width - self.width

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

# ボールクラス
class Ball:
    def __init__(self):
        self.radius = 10
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.speed = 5
        self.dx = self.speed * random.choice([-1, 1])
        self.dy = -self.speed

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

# ブロック(レンガ)クラス
class Brick:
    def __init__(self, x, y, width, height, color, points=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.points = points

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # 枠線

# パーティクルクラス（衝突時の爆発エフェクト用）
class Particle:
    def __init__(self, pos, color):
        self.pos = list(pos)
        self.radius = random.randint(2, 4)
        self.color = color
        self.life = 30
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)
    
    def update(self):
        self.life -= 1
        self.pos[0] += self.dx
        self.pos[1] += self.dy
        self.radius = max(0, self.radius - 0.1)

    def draw(self, screen):
        if self.life > 0 and self.radius > 0:
            pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), int(self.radius))

# パーティクルリスト
particles = []

# レンガの配置設定（グリッド状）
brick_rows = 6
brick_cols = 10
brick_width = screen_width // brick_cols - 5  # 5ピクセルの間隔
brick_height = 20
bricks = []

for row in range(brick_rows):
    for col in range(brick_cols):
        x = col * (brick_width + 5) + 2
        y = row * (brick_height + 5) + 50
        color = random.choice(brick_colors)
        bricks.append(Brick(x, y, brick_width, brick_height, color))

# ゲームオブジェクトの生成
paddle = Paddle()
ball = Ball()
score = 0

# ヘルパー関数: テキスト描画
def draw_text(text, font_size, x, y, color=WHITE, center=True):
    font = pygame.font.SysFont("Arial", font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def init_stage():
    global paddle, ball, bricks, particles
    paddle = Paddle()
    ball = Ball()
    # ステージごとにブロックの行数を増加（例: 基本 3 行＋ステージ数）
    brick_rows = 3 + stage
    brick_cols = 10
    brick_width = screen_width // brick_cols - 5  # 5ピクセルの間隔
    brick_height = 20
    bricks = []
    for row in range(brick_rows):
        for col in range(brick_cols):
            x = col * (brick_width + 5) + 2
            y = row * (brick_height + 5) + 50
            color = random.choice(brick_colors)
            bricks.append(Brick(x, y, brick_width, brick_height, color))
    particles = []

# 初期ステージ設定
init_stage()

# メインループ（状態管理）
running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "TITLE":
                game_state = "PLAYING"
                init_stage()
            elif game_state == "GAME_OVER":
                if event.key == pygame.K_c:
                    game_state = "PLAYING"
                    init_stage()
                elif event.key == pygame.K_q:
                    running = False
            elif game_state == "GAME_CLEAR":
                game_state = "PLAYING"
                stage += 1
                init_stage()
    
    if game_state == "PLAYING":
        # 操作処理
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move(-1)
        if keys[pygame.K_RIGHT]:
            paddle.move(1)
    
        ball.move()
    
        # 壁との衝突判定
        if ball.x - ball.radius <= 0 or ball.x + ball.radius >= screen_width:
            ball.dx *= -1
            if bounce_sound:
                bounce_sound.play()
        if ball.y - ball.radius <= 0:
            ball.dy *= -1
            if bounce_sound:
                bounce_sound.play()
    
        # パドルとの衝突判定
        paddle_rect = pygame.Rect(paddle.x, paddle.y, paddle.width, paddle.height)
        ball_rect = pygame.Rect(int(ball.x - ball.radius), int(ball.y - ball.radius), ball.radius * 2, ball.radius * 2)
        if ball_rect.colliderect(paddle_rect):
            ball.dy *= -1
            ball.y = paddle.y - ball.radius
            if bounce_sound:
                bounce_sound.play()
    
        # ブロックとの衝突判定
        hit_index = None
        for i, brick in enumerate(bricks):
            if ball_rect.colliderect(brick.rect):
                hit_index = i
                ball.dy *= -1
                score += brick.points
                if brick_sound:
                    brick_sound.play()
                for _ in range(20):
                    particles.append(Particle(brick.rect.center, brick.color))
                break
        if hit_index is not None:
            bricks.pop(hit_index)
    
        # ボールが画面下に抜けた場合 → ゲームオーバー
        if ball.y - ball.radius > screen_height:
            game_state = "GAME_OVER"
    
        # パーティクル更新処理
        particles = [p for p in particles if p.life > 0]
        for p in particles:
            p.update()
    
        # 全レンガ破壊でステージクリア
        if not bricks:
            game_state = "GAME_CLEAR"
    
    # 描画処理
    screen.fill(BLACK)
    if game_state == "TITLE":
        draw_text("Breakout Game", 48, screen_width // 2, screen_height // 2 - 50)
        draw_text("Press any key to start", 32, screen_width // 2, screen_height // 2)
    elif game_state == "PLAYING":
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)
        for p in particles:
            p.draw(screen)
        draw_text("Score: " + str(score), 24, 10, 10, center=False)
        draw_text("Stage: " + str(stage), 24, screen_width - 100, 10, center=False)
    elif game_state == "GAME_OVER":
        draw_text("Game Over!", 48, screen_width // 2, screen_height // 2 - 50, RED)
        draw_text("Press C to continue, Q to quit", 32, screen_width // 2, screen_height // 2, WHITE)
        draw_text("Score: " + str(score), 32, screen_width // 2, screen_height // 2 + 50, WHITE)
    elif game_state == "GAME_CLEAR":
        draw_text("Stage Clear!", 48, screen_width // 2, screen_height // 2 - 50, GREEN)
        draw_text("Press any key to proceed to the next stage", 32, screen_width // 2, screen_height // 2, WHITE)
        draw_text("Score: " + str(score), 32, screen_width // 2, screen_height // 2 + 50, WHITE)
    
    pygame.display.flip()

pygame.quit()
sys.exit()

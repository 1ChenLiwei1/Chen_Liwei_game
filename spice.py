import pygame
import random
import os

# 初始化Pygame
pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# 游戏FPS
FPS = 60
clock = pygame.time.Clock()

# 加载怪兽图像
monster_img = pygame.image.load(os.path.join('assets', 'monster.png'))  # 需要准备一张怪兽的图片
monster_img = pygame.transform.scale(monster_img, (50, 50))

# 加载玩家飞机图像（像素飞机）
player_img = pygame.image.load(os.path.join('assets', 'pixel_plane.png'))  # 需要准备一张像素风格的飞机图像
player_img = pygame.transform.scale(player_img, (50, 50))  # 适当缩放飞机大小

# 玩家飞船类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img  # 使用像素飞机图像
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 7

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# 敌人类（小怪兽）
class Enemy(pygame.sprite.Sprite):
    def __init__(self, all_enemies):
        super().__init__()
        self.image = monster_img
        self.rect = self.image.get_rect()
        self.speed = random.randint(1, 3)

        # 随机生成位置，确保敌人不重叠
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)

        # 避免重叠
        while self.check_overlap(all_enemies):
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)

    def check_overlap(self, all_enemies):
        for enemy in all_enemies:
            if self.rect.colliderect(enemy.rect):
                return True
        return False

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)

# 游戏结束页面
def game_over_page(score):
    font = pygame.font.SysFont(None, 48)
    button_font = pygame.font.SysFont(None, 36)

    game_over_text = font.render("Game Over", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)

    restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    exit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    return "restart"
                if exit_button.collidepoint(event.pos):
                    pygame.quit()
                    return "exit"

        screen.fill(BLACK)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))

        pygame.draw.rect(screen, WHITE, restart_button)
        pygame.draw.rect(screen, WHITE, exit_button)

        restart_text = button_font.render("Restart", True, BLACK)
        exit_text = button_font.render("Exit", True, BLACK)

        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 55))
        screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 125))

        pygame.display.flip()

# 游戏主函数
def game():
    # 创建玩家、敌人和子弹的精灵组
    player = Player()
    all_sprites = pygame.sprite.Group(player)
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    # 向敌人组中添加敌人
    for _ in range(6):
        enemy = Enemy(enemies)
        all_sprites.add(enemy)
        enemies.add(enemy)

    score = 0
    game_over = False
    font = pygame.font.SysFont(None, 36)

    # 播放背景音乐
    pygame.mixer.music.load(os.path.join('assets', 'background_music.mp3'))  # 需要准备一首背景音乐
    pygame.mixer.music.play(-1)  # -1表示循环播放

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 发射子弹
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

        # 更新精灵
        all_sprites.update()

        # 检测子弹与敌人碰撞
        for bullet in bullets:
            enemies_hit = pygame.sprite.spritecollide(bullet, enemies, True)
            for enemy in enemies_hit:
                bullet.kill()
                score += 1
                # 添加新的敌人
                new_enemy = Enemy(enemies)
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)

        # 检测敌人是否到达屏幕底部
        if pygame.sprite.spritecollideany(player, enemies):
            game_over = True

        # 填充背景颜色
        screen.fill(BLACK)

        # 绘制所有精灵
        all_sprites.draw(screen)

        # 绘制分数
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # 更新显示
        pygame.display.flip()

        # 设置FPS
        clock.tick(FPS)

    # 停止背景音乐
    pygame.mixer.music.stop()

    # 显示游戏结束页面
    result = game_over_page(score)

    if result == "restart":
        game()  # 如果选择重新开始，则重启游戏
    elif result == "exit":
        pygame.quit()  # 如果选择退出，则关闭游戏

# 运行游戏
if __name__ == "__main__":
    game()
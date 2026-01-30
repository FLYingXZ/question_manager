# Pygame 模块使用教程

Pygame 是一个用于创建 2D 游戏的 Python 库，它基于 SDL（Simple DirectMedia Layer）库，提供了图形、声音、输入设备处理等功能。本教程将带你从基础开始学习 Pygame。

## 目录
1. [安装 Pygame](#安装-pygame)
2. [基础程序结构](#基础程序结构)
3. [绘制图形](#绘制图形)
4. [处理用户输入](#处理用户输入)
5. [精灵和碰撞检测](#精灵和碰撞检测)
6. [声音和图像](#声音和图像)
7. [完整示例](#完整示例)

## 安装 Pygame

```bash
pip install pygame
```

## 基础程序结构

每个 Pygame 程序都遵循相似的结构：

```python
import pygame
import sys

# 初始化 Pygame
pygame.init()

# 设置窗口尺寸
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# 设置窗口标题
pygame.display.set_caption("我的第一个 Pygame 程序")

# 设置颜色 (RGB)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# 游戏主循环
running = True
while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 填充背景色
    screen.fill(WHITE)
    
    # 更新显示
    pygame.display.flip()

# 退出 Pygame
pygame.quit()
sys.exit()
```

## 绘制图形

Pygame 提供了多种绘制基本图形的方法：

```python
import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("绘制图形")

# 颜色定义
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 填充白色背景
    screen.fill((255, 255, 255))
    
    # 绘制矩形 (surface, color, (x, y, width, height))
    pygame.draw.rect(screen, RED, (100, 100, 200, 150))
    
    # 绘制圆形 (surface, color, (x, y), radius)
    pygame.draw.circle(screen, GREEN, (400, 300), 75)
    
    # 绘制线条 (surface, color, start_pos, end_pos, width)
    pygame.draw.line(screen, BLUE, (50, 50), (750, 550), 5)
    
    # 绘制多边形 (surface, color, point_list)
    points = [(600, 100), (700, 200), (650, 300), (550, 300)]
    pygame.draw.polygon(screen, YELLOW, points)
    
    # 绘制椭圆 (surface, color, (x, y, width, height))
    pygame.draw.ellipse(screen, BLACK, (200, 400, 300, 100))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
```

## 处理用户输入

Pygame 可以处理键盘、鼠标等输入设备：

```python
import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("处理用户输入")

# 玩家位置和速度
player_x = 400
player_y = 300
player_speed = 5

# 玩家矩形
player_rect = pygame.Rect(player_x, player_y, 50, 50)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 键盘按下事件
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("空格键被按下")
        
        # 鼠标事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                print("鼠标左键在位置", event.pos, "被点击")
    
    # 持续按键检测
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed
    
    # 更新玩家矩形位置
    player_rect.x = player_x
    player_rect.y = player_y
    
    # 限制玩家在屏幕内
    player_x = max(0, min(player_x, 750))
    player_y = max(0, min(player_y, 550))
    
    # 绘制
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 0, 0), player_rect)
    
    pygame.display.flip()
    
    # 控制帧率
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
```

## 精灵和碰撞检测

精灵(Sprite)是 Pygame 中用于表示游戏对象的重要概念：

```python
import pygame
import sys
import random

# 初始化 Pygame
pygame.init()

# 屏幕设置
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("精灵和碰撞检测")

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 玩家精灵类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height // 2)
        self.speed = 5
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        
        # 限制在屏幕内
        self.rect.x = max(0, min(self.rect.x, screen_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, screen_height - self.rect.height))

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(screen_width - self.rect.width)
        self.rect.y = random.randrange(screen_height - self.rect.height)
        self.speed_x = random.choice([-3, -2, -1, 1, 2, 3])
        self.speed_y = random.choice([-3, -2, -1, 1, 2, 3])
    
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # 碰到边界反弹
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x = -self.speed_x
        if self.rect.top < 0 or self.rect.bottom > screen_height:
            self.speed_y = -self.speed_y

# 创建精灵组
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# 创建玩家
player = Player()
all_sprites.add(player)

# 创建敌人
for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# 游戏主循环
running = True
clock = pygame.time.Clock()
score = 0

while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 更新
    all_sprites.update()
    
    # 碰撞检测
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        score += 1
        print(f"得分: {score}")
    
    # 绘制
    screen.fill(WHITE)
    all_sprites.draw(screen)
    
    # 显示得分
    font = pygame.font.Font(None, 36)
    text = font.render(f"得分: {score}", True, (0, 0, 0))
    screen.blit(text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
```

## 声音和图像

Pygame 可以加载和播放声音文件，以及显示图像：

```python
import pygame
import sys
import os

# 初始化 Pygame
pygame.init()

# 屏幕设置
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("声音和图像")

# 颜色
WHITE = (255, 255, 255)

# 加载图像
try:
    # 替换为你的图像路径
    image_path = "example.png"
    if os.path.exists(image_path):
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (200, 200))
        image_rect = image.get_rect(center=(400, 300))
    else:
        # 如果没有图像文件，创建一个替代的 Surface
        image = pygame.Surface((200, 200))
        image.fill((0, 255, 0))
        image_rect = image.get_rect(center=(400, 300))
        print("未找到图像文件，使用替代图形")
except pygame.error as e:
    print(f"无法加载图像: {e}")
    sys.exit()

# 加载声音
try:
    # 替换为你的声音文件路径
    sound_path = "example.wav"
    if os.path.exists(sound_path):
        sound = pygame.mixer.Sound(sound_path)
    else:
        sound = None
        print("未找到声音文件")
except pygame.error as e:
    print(f"无法加载声音: {e}")
    sound = None

# 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and sound:
                sound.play()
    
    # 绘制
    screen.fill(WHITE)
    screen.blit(image, image_rect)
    
    # 显示说明文字
    font = pygame.font.Font(None, 36)
    text = font.render("按空格键播放声音", True, (0, 0, 0))
    text_rect = text.get_rect(center=(400, 500))
    screen.blit(text, text_rect)
    
    pygame.display.flip()

pygame.quit()
sys.exit()
```

## 完整示例

下面是一个完整的简单游戏示例，结合了前面介绍的所有概念：

```python
import pygame
import sys
import random

# 初始化 Pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("简单射击游戏")

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 8
        self.health = 100
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        
        # 限制在屏幕内
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
    
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 5)
        self.speedx = random.randrange(-2, 2)
    
    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # 如果敌人飞出屏幕底部或侧面，重新生成一个
        if self.rect.top > HEIGHT or self.rect.left < -25 or self.rect.right > WIDTH + 25:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 5)

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
    
    def update(self):
        self.rect.y += self.speedy
        # 如果子弹飞出屏幕顶部，删除它
        if self.rect.bottom < 0:
            self.kill()

# 创建精灵组
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# 创建玩家
player = Player()
all_sprites.add(player)

# 创建敌人
for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# 分数
score = 0

# 字体
font = pygame.font.Font(None, 36)

# 游戏主循环
clock = pygame.time.Clock()
running = True

while running:
    # 保持循环以正确的速度运行
    clock.tick(60)
    
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
    
    # 更新
    all_sprites.update()
    
    # 检测子弹和敌人的碰撞
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
    
    # 检测玩家和敌人的碰撞
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        player.health -= 20
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        if player.health <= 0:
            running = False
    
    # 绘制
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # 显示分数和生命值
    score_text = font.render(f"分数: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    health_text = font.render(f"生命值: {player.health}", True, WHITE)
    screen.blit(health_text, (10, 50))
    
    # 刷新屏幕
    pygame.display.flip()

# 游戏结束
pygame.quit()
sys.exit()
```

## 总结

本教程涵盖了 Pygame 的基础知识，包括：

1. 安装和基本程序结构
2. 绘制基本图形
3. 处理用户输入
4. 使用精灵和碰撞检测
5. 加载和播放声音、图像
6. 创建一个完整的简单游戏

Pygame 还有更多高级功能，如动画、粒子效果、平铺地图等。要深入了解，可以参考 [Pygame 官方文档](https://www.pygame.org/docs/)。

祝你使用 Pygame 开发游戏愉快！
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/6/10 12:26
# @Author  : xiaoaug
# @File    : main.py
# @Software: PyCharm
# @Desc    : 游戏主程序

import pygame  # pip install pygame
import os
import random


pygame.init()   # pygame 初始化


# ------------------------------------------ 素材 ------------------------------------------
IMAGES = {}     # 游戏图像素材包
MUSIC = {}      # 游戏音乐素材包

# 导入图像素材
for i in os.listdir(os.path.join(os.getcwd(), "Resource/Image")):  # 遍历目标文件夹内的所有文件
    name, extension = os.path.splitext(i)           # 将每个文件的文件名、后缀名分开
    if extension == ".png" or ".ico":               # 判断读取的文件是否为 png/ico 格式文件
        path = os.path.join(os.path.join(os.getcwd(), "Resource/Image"), i)    # 将每个图片路径添加到 path 里
        IMAGES[name] = pygame.image.load(path)      # 将读取的文件赋给 images 字典


# 导入音乐素材
for i in os.listdir(os.path.join(os.getcwd(), "Resource/Music")):  # 遍历目标文件夹内的所有文件
    name, extension = os.path.splitext(i)           # 将每个文件的文件名、后缀名分开
    if extension == ".mp3":                         # 判断读取的文件是否为 mp3 格式文件
        path = os.path.join(os.path.join(os.getcwd(), "Resource/Music"), i)    # 将每个音乐路径添加到 path 里
        MUSIC[name] = pygame.mixer.Sound(path)      # 将读取的文件赋给 music 字典


# ------------------------------------------ 常量 ------------------------------------------
WINDOW_WIDTH = 288                      # 窗口的宽度
WINDOW_HEIGHT = 512                     # 窗口的高度
GAME_FPS = 30                           # 游戏帧数
CLOCK = pygame.time.Clock()             # 设置时钟，CLOCK.tick(10)：每秒10帧画面
FLOOR_X = 0                             # 地板图片 X 坐标
FLOOR_Y = WINDOW_HEIGHT - IMAGES["floor"].get_height()        # 地板图片 Y 坐标
FLOOR_GAP = IMAGES["floor"].get_width() - WINDOW_WIDTH        # 计算地板和窗口宽度的差值
BIRD_X = WINDOW_WIDTH * 0.2                                   # 小鸟图像 X 坐标
BIRD_Y = (WINDOW_HEIGHT - IMAGES["red-up"].get_height()) / 2  # 小鸟图像 Y 坐标
PIPES_NUM = 4           # 水管数量
PIPES_DISTANCE = 150    # 水管之间的距离
PIPES_GAP = 100         # 上下水管的间距
GAME_RESULT = {}        # 游戏结果，保存小鸟位置、水管位置、分数的信息
GAME_SCORE = 0          # 游戏分数


# ------------------------------------------- 类 -------------------------------------------
# 小鸟类，继承父类：精灵类
class Bird(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)             # 调用父类精灵类 init 方法
        self.wing_act = [0]*5 + [1]*5 + [2]*5 + [1]*5   # 小鸟翅膀的动作集
        self.wing_num = 0                               # 记录小鸟翅膀当前处在哪个飞行姿态下
        self.images = IMAGES["birds"]                   # 小鸟三种姿态的图像
        self.image = self.images[self.wing_act[self.wing_num]]      # 小鸟当前图像
        self.rect = self.image.get_rect()               # 获取小鸟图像的坐标
        self.rect.x = x                                 # 小鸟图像的X坐标
        self.rect.y = y                                 # 小鸟图像的Y坐标
        self.y_vel = -1                                 # 小鸟在Y轴上下移动的速度
        self.move_y_range = [BIRD_Y-8, BIRD_Y+8]        # 小鸟上下移动的范围
        self.y_gravity = 1                              # Y轴重力（小鸟降落速度）
        self.control_y_vel = -10                        # 拍动翅膀后小鸟上升速度
        self.y_vel_max = 10                             # 小鸟下落的最大速度
        self.rotate = 45                                # 小鸟抬头的角度，默认初始45度
        self.min_rotate = -20                           # 小鸟最小低头角度
        self.rotate_vel = -3                            # 小鸟低头的速度
        self.control_rotate = 45                        # 拍动翅膀后的头部角度
        self.die = False                                # 小鸟是否死亡

    # 小鸟扇翅膀
    def wing(self):
        self.wing_num += 1
        if self.wing_num >= 20:
            self.wing_num = 0
        self.image = self.images[self.wing_act[self.wing_num]]      # 小鸟当前图像

    # 小鸟上下移动
    def move_up_down(self):
        self.rect.y += self.y_vel
        if self.rect.y < self.move_y_range[0] or self.rect.y > self.move_y_range[1]:
            self.y_vel *= -1

    # 操控小鸟飞
    def bird_fly(self, flap=False):
        # 如果按下鼠标（即拍翅膀）
        if flap:
            self.y_vel = self.control_y_vel     # 小鸟立刻以最大速度向上飞

        self.y_vel = min(self.y_vel+self.y_gravity, self.y_vel_max)
        self.rect.y += self.y_vel

    # 小鸟抬头低头
    def bird_rotate(self, flap=False):
        # 如果按下鼠标（即拍翅膀）
        if flap:
            self.rotate = self.control_rotate   # 小鸟立刻抬头（最大角度）

        self.rotate = max(self.rotate+self.rotate_vel, self.min_rotate)
        self.image = pygame.transform.rotate(self.image, self.rotate)  # 旋转图片

    # 小鸟死亡过程
    def bird_dying(self):

        # 如果不是因为撞到地板而死，则不旋转 90 度
        if self.rect.y < FLOOR_Y:
            self.rect.y += self.y_vel_max       # 以最大速度降落
            self.rotate = -90                   # 小鸟低头到最底
            self.image = self.images[self.wing_act[self.wing_num]]
            self.image = pygame.transform.rotate(self.image, self.rotate)
        else:
            self.die = False


# 水管类，继承父类：精灵类
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, up_pipe=True):     # up=True 表示生成向上的水管，反之生成向下的水管
        pygame.sprite.Sprite.__init__(self)     # 调用父类 init 方法

        # 向上的水管
        if up_pipe:
            self.image = IMAGES["pipes"][0]
            self.rect = self.image.get_rect()   # 获取水管图像的坐标
            self.rect.x = x                     # 水管图像的X坐标
            self.rect.top = y                   # 水管图像的顶部坐标
        # 向下的水管
        else:
            self.image = IMAGES["pipes"][1]
            self.rect = self.image.get_rect()   # 获取水管图像的坐标
            self.rect.x = x                     # 水管图像的X坐标
            self.rect.bottom = y                # 水管图像的底部坐标
        self.x_vel = -4         # 水管向左移动的速度

    # 水管移动
    def update(self):
        self.rect.x += self.x_vel


# ------------------------------------------ 设置 ------------------------------------------
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))     # 设置窗口大小
pygame.display.set_caption("Flappy Bird")           # 设置游戏名称
pygame.display.set_icon(IMAGES["flappy"])           # 设置游戏图标


# ---------------------------------------- 菜单界面 ----------------------------------------
def menu_window():
    global GAME_SCORE

    MUSIC["swooshing"].play()       # 播放进入音乐

    GAME_SCORE = 0        # 分数清零

    # 计算图片坐标
    title_x = (WINDOW_WIDTH - IMAGES["title"].get_width()) / 2     # 标题图片X轴坐标
    title_y = (WINDOW_HEIGHT - FLOOR_Y) / 1.5                      # 标题图片Y轴坐标
    ready_x = (WINDOW_WIDTH - IMAGES["ready"].get_width()) / 2     # 准备图片X轴坐标
    ready_y = (WINDOW_HEIGHT - FLOOR_Y) / 0.63                     # 准备图片Y轴坐标
    tap_x = (WINDOW_WIDTH - IMAGES["tap"].get_width()) / 2         # 点击图片X轴坐标
    tap_y = (WINDOW_HEIGHT - FLOOR_Y) / 0.45                       # 点击图片Y轴坐标

    while True:
        # 检测事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:               # 如果检测到程序退出
                quit()      # 退出程序
            if event.type == pygame.MOUSEBUTTONDOWN:    # 如果检测到鼠标按下
                bird_1.y_vel = -10      # 给小鸟向上飞的一个速度（抬头）
                return      # 结束该 while 循环

        dynamic_floor()         # 动态地板
        bird_1.wing()           # 小鸟扇翅膀
        bird_1.move_up_down()   # 小鸟上下移动

        SCREEN.blit(IMAGES["bgpic"], (0, 0))               # 显示背景
        SCREEN.blit(IMAGES["floor"], (FLOOR_X, FLOOR_Y))   # 显示地板
        SCREEN.blit(IMAGES["title"], (title_x, title_y))   # 显示标题
        SCREEN.blit(IMAGES["ready"], (ready_x, ready_y))   # 显示准备
        SCREEN.blit(IMAGES["tap"], (tap_x, tap_y))         # 显示点击
        SCREEN.blit(bird_1.image, bird_1.rect)             # 显示小鸟

        pygame.display.update()     # 更新界面
        CLOCK.tick(GAME_FPS)        # 设置显示帧数


# ---------------------------------------- 游戏界面 ----------------------------------------
def game_window():

    pipe_group = create_pipe()  # 创建水管

    while True:

        flap = False    # 让小鸟控制标志清零

        for event in pygame.event.get():                # 检测事件
            if event.type == pygame.QUIT:               # 如果检测到程序退出
                quit()      # 退出程序
            if event.type == pygame.MOUSEBUTTONDOWN:    # 如果检测到鼠标按下
                MUSIC["wing"].play()    # 扇动翅膀声音
                flap = True

        dynamic_floor()                 # 动态地板
        dynamic_pipes(pipe_group)       # 动态水管
        bird_1.wing()                   # 小鸟扇翅膀
        bird_1.bird_fly(flap)           # 控制小鸟飞
        bird_1.bird_rotate(flap)        # 控制小鸟抬头

        judge_bird_died(pipe_group)     # 判断小鸟是否死亡
        if bird_1.die:
            return

        SCREEN.blit(IMAGES["bgpic"], (0, 0))                 # 显示背景
        # for pipe in pipes:
        #     SCREEN.blit(pipe.image, pipe.rect)
        pipe_group.draw(SCREEN)
        SCREEN.blit(IMAGES["floor"], (FLOOR_X, FLOOR_Y))   # 显示地板

        calc_score(pipe_group)      # 计算游戏分数
        show_game_score()           # 显示游戏分数

        SCREEN.blit(bird_1.image, bird_1.rect)             # 显示小鸟

        pygame.display.update()     # 更新界面
        CLOCK.tick(GAME_FPS)        # 设置显示帧数


# ---------------------------------------- 结束界面 ----------------------------------------
def end_window():

    bird = GAME_RESULT["bird"]       # 获取游戏结束的结果
    pipe_group = GAME_RESULT["pipe"]  # 获取水管数据

    # 计算图片坐标
    game_over_x = (WINDOW_WIDTH - IMAGES["game-over"].get_width()) / 2
    game_over_y = (FLOOR_Y - IMAGES["game-over"].get_height()) / 2
    # score_panel_x = (WINDOW_WIDTH - IMAGES["score_panel"].get_width()) / 2    # 计分板X坐标
    # score_panel_y = (FLOOR_Y - IMAGES["score_panel"].get_height()) / 1.3      # 计分板Y坐标

    while True:

        if bird_1.die:
            bird_1.bird_dying()     # 小鸟死亡画面
        else:
            for event in pygame.event.get():                # 检测事件
                if event.type == pygame.QUIT:               # 如果检测到程序退出
                    quit()      # 退出程序
                if event.type == pygame.MOUSEBUTTONDOWN:    # 如果检测到鼠标按下
                    return      # 结束该 while 循环

        SCREEN.blit(IMAGES["bgpic"], (0, 0))  # 显示背景
        pipe_group.draw(SCREEN)
        SCREEN.blit(IMAGES["floor"], (FLOOR_X, FLOOR_Y))  # 显示地板
        SCREEN.blit(IMAGES["game-over"], (game_over_x, game_over_y))    # 显示游戏结束
        # SCREEN.blit(IMAGES["score_panel"], (score_panel_x, score_panel_y))  # 显示计分板
        SCREEN.blit(bird.image, bird.rect)  # 显示小鸟

        show_game_score()       # 显示游戏分数

        pygame.display.update()     # 更新界面
        CLOCK.tick(GAME_FPS)        # 设置显示帧数


# -------------------------------------- 随机小鸟颜色 ---------------------------------------
def random_color():

    # 随机背景
    IMAGES["bgpic"] = IMAGES[random.choice(["day", "night"])]

    # 随机小鸟颜色
    # 将选定的颜色赋给最终要显示的小鸟图像字典
    # 该字典包括小鸟翅膀上、中、下三个图像
    color = random.choice(["red", "blue", "yellow"])    # 随机选择一个颜色
    IMAGES["birds"] = [IMAGES[color+"-up"], IMAGES[color+"-mid"], IMAGES[color+"-down"]]

    # 水管颜色，根据背景决定，背景是白天则水管为绿色，背景是晚上则水管为红色
    if IMAGES["bgpic"] == IMAGES["day"]:
        pipe = IMAGES["green-pipe"]
        IMAGES["pipes"] = [pipe, pygame.transform.flip(pipe, False, True)]
    else:
        pipe = IMAGES["red-pipe"]
        IMAGES["pipes"] = [pipe, pygame.transform.flip(pipe, False, True)]


# --------------------------------------- 生成小鸟 -----------------------------------------
def create_bird():
    new_bird = Bird(BIRD_X, BIRD_Y)  # 生成一只小鸟
    return new_bird


# --------------------------------------- 生成水管 -----------------------------------------
def create_pipe():
    pipe_group = pygame.sprite.Group()  # 精灵组，用于替代列表 pipes = []，这样就不需要后面 pipes.append() 了
    for pipes_num in range(PIPES_NUM):
        pipe_y = random.randint(int(WINDOW_HEIGHT*0.3), int(WINDOW_HEIGHT*0.6))
        pipe_up = Pipe(WINDOW_WIDTH+pipes_num*PIPES_DISTANCE, pipe_y, True)   # 生成上水管
        pipe_down = Pipe(WINDOW_WIDTH+pipes_num*PIPES_DISTANCE, pipe_y-PIPES_GAP, False)  # 生成下水管

        # 增加水管
        pipe_group.add(pipe_up)
        pipe_group.add(pipe_down)

    return pipe_group


# ------------------------------------ 判断小鸟是否死亡 -------------------------------------
def judge_bird_died(pipe_group):
    global GAME_RESULT

    # 小鸟撞到地板、天花板
    if bird_1.rect.y >= FLOOR_Y or bird_1.rect.y <= 0:
        MUSIC["hit"].play()  # 击中音乐
        MUSIC["die"].play()  # 死亡音乐
        bird_1.die = True    # 小鸟已死
        GAME_RESULT = {"bird": bird_1, "pipe": pipe_group, "score": GAME_SCORE}  # 记录游戏数据

    # 小鸟和水管相撞
    elif pygame.sprite.spritecollideany(bird_1, pipe_group):
        MUSIC["hit"].play()  # 击中音乐
        MUSIC["die"].play()  # 死亡音乐
        bird_1.die = True    # 小鸟已死
        GAME_RESULT = {"bird": bird_1, "pipe": pipe_group, "score": GAME_SCORE}  # 记录游戏数据


# --------------------------------------- 动态地板 -----------------------------------------
def dynamic_floor():
    global FLOOR_X

    FLOOR_X -= 4        # 设定地板移动速度
    if FLOOR_X <= -FLOOR_GAP:
        FLOOR_X = 0


# --------------------------------------- 动态水管 -----------------------------------------
def dynamic_pipes(pipe_group):
    first_pipe_up = pipe_group.sprites()[0]
    first_pipe_down = pipe_group.sprites()[1]
    if first_pipe_up.rect.right < 0:

        # 删除水管
        # pipes.remove(first_pipe_up)
        # pipes.remove(first_pipe_down)
        first_pipe_up.kill()
        first_pipe_down.kill()

        pipe_y = random.randint(int(WINDOW_HEIGHT * 0.3), int(WINDOW_HEIGHT * 0.7))
        new_pipe_up = Pipe(first_pipe_up.rect.x+PIPES_NUM*PIPES_DISTANCE, pipe_y, True)
        new_pipe_down = Pipe(first_pipe_up.rect.x+PIPES_NUM*PIPES_DISTANCE, pipe_y-PIPES_GAP, False)

        # 新增水管
        # pipes.append(new_pipe_up)
        # pipes.append(new_pipe_down)
        pipe_group.add(new_pipe_up)
        pipe_group.add(new_pipe_down)

    # for pipe in pipes:
    #     pipe.update()
    pipe_group.update()


# --------------------------------------- 计算分数 ---------------------------------------
def calc_score(pipe_group):
    global GAME_SCORE

    first_pipe_up = pipe_group.sprites()[0]

    if bird_1.rect.left+first_pipe_up.x_vel < first_pipe_up.rect.centerx < bird_1.rect.left:
        GAME_SCORE += 1
        MUSIC["point"].play()


# --------------------------------------- 显示分数 ---------------------------------------
def show_game_score():
    score_str = str(GAME_SCORE)     # 将分数变成字符串类型
    score_length = len(score_str)   # 计算分数的长度
    score_width = IMAGES["0"].get_width() * 1.1                 # 设置字与字之间的间距
    score_x = (WINDOW_WIDTH - score_length * score_width) / 2   # 分数的 X 坐标
    score_y = WINDOW_HEIGHT * 0.1           # 分数的 Y 坐标

    # 将所有分数显示出来
    for number in score_str:
        SCREEN.blit(IMAGES[number], (score_x, score_y))
        score_x += score_width


# ---------------------------------------- 主程序 -----------------------------------------
if __name__ == '__main__':
    while True:
        random_color()          # 随机选择白天/黑夜背景、小鸟的颜色、管道颜色
        bird_1 = create_bird()  # 创建一只小鸟

        menu_window()       # 菜单界面
        game_window()       # 游戏界面
        end_window()        # 结束界面

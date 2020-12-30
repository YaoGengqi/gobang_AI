from graphics import *
from math import *
import numpy as np
import time


GRID_WIDTH = 35 # 棋盘参数设置
COLUMN = 20
ROW = 20
RATIO = 1  # 进攻的系数   大于1 进攻型，  小于1 防守型
DEPTH = 3  # 搜索深度   只能是单数。  如果是负数， 评估函数评估的的是自己多少步之后的自己得分的最大值，并不意味着是最好的棋， 评估函数的问题

list1 = []  # AI
list2 = []  # human
list3 = []  # all
list_all = []  # 整个棋盘的点
next_point = [0, 0]  # AI下一步最应该下的位置


# 棋型的评估分数,其中数字序列表示一条直线上已经下的棋子
shape_score = [(50, (0, 1, 1, 0, 0)),
               (50, (0, 0, 1, 1, 0)),
               (200, (1, 1, 0, 1, 0)),
               (500, (0, 0, 1, 1, 1)),
               (500, (1, 1, 1, 0, 0)),
               (5000, (0, 1, 1, 1, 0)),
               (5000, (0, 1, 0, 1, 1, 0)),
               (5000, (0, 1, 1, 0, 1, 0)),
               (5000, (1, 1, 1, 0, 1)),
               (5000, (1, 1, 0, 1, 1)),
               (5000, (1, 0, 1, 1, 1)),
               (5000, (1, 1, 1, 1, 0)),
               (5000, (0, 1, 1, 1, 1)),
               (50000, (0, 1, 1, 1, 1, 0)),
               (99999999, (1, 1, 1, 1, 1))]

# 计算下一步的最优选择
def ai():

    global cut_count   # 统计剪枝次数
    cut_count = 0
    global search_count   # 统计搜索次数
    search_count = 0
    negamax(True, DEPTH, -99999999, 99999999)
    print("本次共剪枝次数：" + str(cut_count))
    print("本次共搜索次数：" + str(search_count))
    print("电脑落子坐标为：" + str(next_point))
    return next_point[0], next_point[1]

# 负值极大算法搜索 alpha + beta剪枝
def negamax(is_ai, depth, alpha, beta):     # 初始alpha为-99999999， beta为99999999

    # 游戏是否结束 | | 探索的递归深度是否到边界
    if game_win(list1) or game_win(list2) or depth == 0:
        return evaluation(is_ai)

    # blank_list = list(set(list_all).difference(set(list3)))
    # order(blank_list)   # 搜索顺序排序  提高剪枝效率

    blank_list = order()

    # 遍历每一个候选步
    for next_step in blank_list:

        global search_count
        search_count += 1

        # 如果要评估的位置没有相邻的子， 则不去评估  减少计算
        if not has_neightnor(next_step):
            continue

        if is_ai:
            list1.append(next_step)
        else:
            list2.append(next_step)
        list3.append(next_step)

        value = -negamax(not is_ai, depth - 1, -beta, -alpha)
        if is_ai:
            list1.remove(next_step)
        else:
            list2.remove(next_step)
        list3.remove(next_step)

        if value > alpha:
            # if alpha < -999999:
            #     print(str(value) + "\talpha:\t" + str(alpha) + "\tbeta:\t" + str(beta))
            # else:
            #     print(str(value) + "\talpha:\t" + str(alpha) + "\t\tbeta:\t" + str(beta))

            if depth == DEPTH:
                next_point[0] = next_step[0]
                next_point[1] = next_step[1]
            # alpha + beta剪枝点
            if value >= beta:
                # 剪枝次数加一
                global cut_count
                cut_count += 1
                return beta
            alpha = value

    return alpha

def order():
    pt_list = []
    min_left = 100
    min_bottom = 100
    max_right = -100
    max_up = -100
    for item in list3:
        min_left = min(min_left, item[0])
        min_bottom = min(min_bottom, item[1])
        max_right = max(max_right, item[0])
        max_up = max(max_up, item[1])

    for x in range(min_left-2, max_right+2):
        for y in range(min_bottom-2, max_up+2):
            if x >=0 and x < COLUMN+1 and y >=0 and y < ROW+1 and (x,y) not in list3:
                pt_list.append((x,y))

    last_pt = list3[-1]
    for item in pt_list:
        for i in range(-1, 2): # -1，0，+1
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if (last_pt[0] + i, last_pt[1] + j) in pt_list:
                    # 将上一个落子周围的空位纳入优先考虑
                    pt_list.remove((last_pt[0] + i, last_pt[1] + j))
                    pt_list.insert(0, (last_pt[0] + i, last_pt[1] + j))

    return pt_list

# 用于计算周围是否存在棋子
def has_neightnor(pt):  
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if (pt[0] + i, pt[1]+j) in list3:
                return True
    return False

# 评估函数
def evaluation(is_ai):
    '''
    用于评估分数，其中分数由棋盘上的所有棋子的分布（存在与shape_score中的棋形分布）的分数相加。
    '''
    total_score = 0

    if is_ai:
        my_list = list1
        enemy_list = list2
    else:
        my_list = list2
        enemy_list = list1

    # 算自己的得分
    score_all_arr = []  # 得分形状的位置 用于计算如果有相交 得分翻倍
    my_score = 0
    for pt in my_list:
        m = pt[0]
        n = pt[1]

        #分别计算其在水平、竖直、及两个对角线上的分数
        my_score += cal_score(m, n, 0, 1, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, 1, 0, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, 1, 1, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, -1, 1, enemy_list, my_list, score_all_arr)

    #  算敌人的得分， 并减去
    score_all_arr_enemy = []
    enemy_score = 0
    for pt in enemy_list:
        m = pt[0]
        n = pt[1]
        enemy_score += cal_score(m, n, 0, 1, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, 1, 0, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, 1, 1, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, -1, 1, my_list, enemy_list, score_all_arr_enemy)

    total_score = my_score - enemy_score*RATIO*0.1

    return total_score

def cal_score(m, n, x_decrict, y_derice, enemy_list, my_list, score_all_arr):
    # 每个方向上的分值计算
    
    add_score = 0  # 加分项
    # 在一个方向上， 只取最大的得分项
    max_score_shape = (0, None)

    # 如果此方向上，该点已经有得分形状，不重复计算
    for item in score_all_arr:
        for pt in item[1]:
            if m == pt[0] and n == pt[1] and x_decrict == item[2][0] and y_derice == item[2][1]:
                return 0

    # 在落子点 左右方向上循环查找得分形状
    for offset in range(-5, 1): # -5 -4 -3 -2 -1 0 
        '''
        比如说，在水平线上有11个点，此时的布局为 0 0 0 1 2 1 1 2 0 0 0(0表示无，1表示黑子，2表示白子)，每次遍历六个位置并记录
        '''
        pos = []
        for i in range(0, 6):   # 0 1 2 3 4 5
            if (m + (i + offset) * x_decrict, n + (i + offset) * y_derice) in enemy_list:
                pos.append(2)   # 敌方棋子
            elif (m + (i + offset) * x_decrict, n + (i + offset) * y_derice) in my_list:
                pos.append(1)   # 我方棋子
            else:
                pos.append(0)   # 无
        tmp_shap5 = (pos[0], pos[1], pos[2], pos[3], pos[4])
        tmp_shap6 = (pos[0], pos[1], pos[2], pos[3], pos[4], pos[5])


        # 只记录同一个方向上最大的棋形
        for (score, shape) in shape_score:
            if tmp_shap5 == shape or tmp_shap6 == shape:
                if score > max_score_shape[0]:
                    max_score_shape = (score, ((m + (0+offset) * x_decrict, n + (0+offset) * y_derice),
                                               (m + (1+offset) * x_decrict, n + (1+offset) * y_derice),
                                               (m + (2+offset) * x_decrict, n + (2+offset) * y_derice),
                                               (m + (3+offset) * x_decrict, n + (3+offset) * y_derice),
                                               (m + (4+offset) * x_decrict, n + (4+offset) * y_derice)), (x_decrict, y_derice))

    # 计算两个形状相交
    if max_score_shape[1] is not None:
        for item in score_all_arr:
            for pt1 in item[1]:
                for pt2 in max_score_shape[1]:
                    if pt1 == pt2 and max_score_shape[0] > 10 and item[0] > 10:
                        add_score += item[0] + max_score_shape[0]

        score_all_arr.append(max_score_shape)

    return add_score + max_score_shape[0]

def game_win(list):
    '''
    用于判断是否取胜
    param： list1 or list2
    '''

    for m in range(COLUMN):
        for n in range(ROW):

            if n < ROW - 4 and (m, n) in list and (m, n + 1) in list and (m, n + 2) in list and (
                    m, n + 3) in list and (m, n + 4) in list:
                return True
            elif m < ROW - 4 and (m, n) in list and (m + 1, n) in list and (m + 2, n) in list and (
                        m + 3, n) in list and (m + 4, n) in list:
                return True
            elif m < ROW - 4 and n < ROW - 4 and (m, n) in list and (m + 1, n + 1) in list and (
                        m + 2, n + 2) in list and (m + 3, n + 3) in list and (m + 4, n + 4) in list:
                return True
            elif m < ROW - 4 and n > 3 and (m, n) in list and (m + 1, n - 1) in list and (
                        m + 2, n - 2) in list and (m + 3, n - 3) in list and (m + 4, n - 4) in list:
                return True
    return False

def gobangwin():
    '''
    设置界面， 包括长宽以及行列
    '''
    win = GraphWin("五子棋", GRID_WIDTH * COLUMN, GRID_WIDTH * ROW) # 设置长宽
    win.setBackground("yellow")

    i1 = 0
    while i1 <= GRID_WIDTH * COLUMN:
        l = Line(Point(i1, 0), Point(i1, GRID_WIDTH * COLUMN))
        l.draw(win)
        i1 = i1 + GRID_WIDTH

    i2 = 0
    while i2 <= GRID_WIDTH * ROW:
        l = Line(Point(0, i2), Point(GRID_WIDTH * ROW, i2))
        l.draw(win)
        i2 = i2 + GRID_WIDTH
    return win

def main():
    

    win = gobangwin()   # 界面

    for i in range(COLUMN+1):
        for j in range(ROW+1):
            list_all.append((i, j)) #  将所有棋盘的坐标增加到list_all

    change = 0
    g = 0

    while g == 0:

        if change % 2 == 1: # 玩家执黑，反之电脑执黑
            time1 = time.time()
            
            pos = ai()
            if pos in list3:
                message = Text(Point(200, 200), "不可用的位置" + str(pos[0]) + "," + str(pos[1]))
                message.draw(win)
                g = 1

            list1.append(pos)
            list3.append(pos)

            piece = Circle(Point(GRID_WIDTH * pos[0], GRID_WIDTH * pos[1]), 16)
            piece.setFill('white')
            piece.draw(win)

            if game_win(list1):
                message = Text(Point(100, 100), "white win.")
                message.draw(win)
                g = 1
            change = change + 1

            print("执行时间为：" + str(time.time() - time1))

        else:
            p2 = win.getMouse()
            if not ((round((p2.getX()) / GRID_WIDTH), round((p2.getY()) / GRID_WIDTH)) in list3):

                a2 = round((p2.getX()) / GRID_WIDTH)
                b2 = round((p2.getY()) / GRID_WIDTH)
                list2.append((a2, b2))
                list3.append((a2, b2))

                piece = Circle(Point(GRID_WIDTH * a2, GRID_WIDTH * b2), 16)
                piece.setFill('black')
                piece.draw(win)
                if game_win(list2):
                    message = Text(Point(100, 100), "black win.")
                    message.draw(win)
                    g = 1

                change = change + 1

    message = Text(Point(100, 120), "Click anywhere to quit.")
    message.draw(win)
    win.getMouse()
    win.close()

if __name__ == "__main__":

    main()

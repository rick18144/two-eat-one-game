# 导入数学库（用于无穷大常量）和深拷贝库（用于棋盘状态模拟）
import math
import copy

# ===================== 全局常量配置 =====================
SIZE = 4           # 棋盘大小：4x4
AI = 1            # 黑棋：AI玩家
HUMAN = 2         # 白棋：人类玩家
MAX_DEPTH = 6     # AI搜索深度（推荐5-6，10会卡死，指数级计算量）
INF = math.inf    # 无穷大，用于极小极大算法初始化

# 全局历史记录列表：存储每一步的棋盘状态，用于【悔棋功能】
history = []

# ===================== 游戏核心功能函数 =====================
def init_board():
    """
    初始化棋盘
    规则：黑棋(AI)初始在第0行，白棋(HUMAN)初始在第3行
    返回：初始化后的4x4棋盘二维列表
    """
    # 创建4x4的空棋盘（0表示空位）
    board = [[0]*SIZE for _ in range(SIZE)]
    # 第0行全部放黑棋（AI）
    for j in range(SIZE):
        board[0][j] = AI
    # 第3行全部放白棋（人类）
    for j in range(SIZE):
        board[3][j] = HUMAN
    return board

def print_board(board):
    """
    打印棋盘界面
    格式：●=黑棋，○=白棋，|=空格，带行列坐标
    """
    print("\n  0 1 2 3")
    print(" +-+-+-+-+")
    # 遍历每一行
    for i in range(SIZE):
        line = f"{i}|"
        # 遍历每一列，拼接棋子
        for j in range(SIZE):
            line += "●|" if board[i][j]==1 else "○|" if board[i][j]==2 else " |"
        print(line)
        print(" +-+-+-+-+")
    print()

def count_line_piece(line):
    """统计单行的棋子数量（用于判断满4子不吃子）"""
    return sum(1 for v in line if v != 0)

def count_col_piece(board, y):
    """统计单列的棋子数量（用于判断满4子不吃子）"""
    cnt = 0
    for x in range(SIZE):
        if board[x][y] != 0:
            cnt += 1
    return cnt

def do_eat_only_new(board, px, py, attacker):
    """
    🔥 核心吃子规则函数（严格按你的要求：仅相邻二连吃子）
    board: 当前棋盘
    px, py: 新落子的坐标（只有新落子能吃子）
    attacker: 进攻方（吃子的玩家）
    返回：吃子后的新棋盘 + 是否吃子成功
    """
    defender = 3 - attacker  # 防守方（被吃的一方，1变2，2变1）
    new_board = copy.deepcopy(board)  # 深拷贝棋盘，不修改原棋盘
    eaten = False  # 标记是否吃子成功

    # 规则1：一行/一列满4个子 → 绝对不吃子
    if count_line_piece(new_board[px]) >= 4 or count_col_piece(new_board, py) >= 4:
        return new_board, False

    # ===================== 横向吃子判断（三连检测） =====================
    row = px  # 新落子所在行
    # 遍历所有横向三连（4列只能组成2组三连：0-1-2，1-2-3）
    for y in range(SIZE - 2):
        # 只扫描包含【新落子】的三连（优化效率）
        if py not in (y, y+1, y+2):
            continue
        # 获取三连的三个棋子
        a, b, c = new_board[row][y], new_board[row][y+1], new_board[row][y+2]
        # 规则2：三连中有空位 → 不吃子
        if 0 in (a,b,c):
            continue
        # 规则3：仅【相邻二连】吃子
        # 形态1：攻击方二连 + 防守方（●●○）
        if a == b == attacker and c == defender:
            new_board[row][y+2] = 0  # 吃掉防守方棋子
            eaten = True
        # 形态2：防守方 + 攻击方二连（○●●）
        if b == c == attacker and a == defender:
            new_board[row][y] = 0    # 吃掉防守方棋子
            eaten = True

    # ===================== 纵向吃子判断（三连检测） =====================
    col = py  # 新落子所在列
    # 遍历所有纵向三连
    for x in range(SIZE - 2):
        # 只扫描包含【新落子】的三连
        if px not in (x, x+1, x+2):
            continue
        a, b, c = new_board[x][col], new_board[x+1][col], new_board[x+2][col]
        # 有空位不吃子
        if 0 in (a,b,c):
            continue
        # 仅相邻二连吃子（同上横向逻辑）
        if a == b == attacker and c == defender:
            new_board[x+2][col] = 0
            eaten = True
        if b == c == attacker and a == defender:
            new_board[x][col] = 0
            eaten = True

    return new_board, eaten

def get_moves(board, player):
    """
    生成玩家的【所有合法走法】
    规则：棋子只能上下左右移动一格，且目标位置为空
    返回：所有合法走法的列表 (原x,原y,新x,新y)
    """
    moves = []
    # 遍历整个棋盘
    for x in range(SIZE):
        for y in range(SIZE):
            # 找到当前玩家的棋子
            if board[x][y] == player:
                # 上下左右四个方向
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    # 判断新坐标在棋盘内 + 目标位置为空
                    if 0<=nx<SIZE and 0<=ny<SIZE and board[nx][ny]==0:
                        moves.append((x,y,nx,ny))
    return moves

def is_win(board):
    """
    判断游戏胜负
    胜利条件：
    1. 对方棋子≤1个
    2. 对方无合法走法
    返回：是否结束 + 胜利者
    """
    ai_cnt = sum(row.count(AI) for row in board)    # 黑棋数量
    hu_cnt = sum(row.count(HUMAN) for row in board) # 白棋数量
    
    # AI棋子≤1 → 人类赢
    if ai_cnt <= 1:
        return True, HUMAN
    # 人类棋子≤1 → AI赢
    if hu_cnt <= 1:
        return True, AI
    # AI无棋走 → 人类赢
    if not get_moves(board, AI):
        return True, HUMAN
    # 人类无棋走 → AI赢
    if not get_moves(board, HUMAN):
        return True, AI
    # 游戏继续
    return False, 0

# ===================== AI评分系统（传统博弈：人工手写估值，无机器学习） =====================
def count_adjacent_pairs(board, player):
    """统计玩家的【相邻二连】数量（进攻核心评分项）"""
    count = 0
    # 统计横向二连
    for x in range(SIZE):
        for y in range(SIZE-1):
            if board[x][y] == board[x][y+1] == player:
                count +=1
    # 统计纵向二连
    for y in range(SIZE):
        for x in range(SIZE-1):
            if board[x][y] == board[x+1][y] == player:
                count +=1
    return count

def position_score(x, y):
    """棋盘位置权重评分：中心点位>边缘点位（人工设定的战术优势）"""
    # 棋盘中心4个位置（1,1)(1,2)(2,1)(2,2) 高分
    if (x,y) in [(1,1),(1,2),(2,1),(2,2)]:
        return 10
    # 边缘位置 低分
    return 3

def evaluate(board):
    """
    🔥 AI核心：局面评估函数（传统AI的智商来源）
    作用：给当前棋盘打分，分数越高→对AI越有利
    无机器学习：所有评分规则都是【人工手写固定】的
    评分维度：棋子数量 + 二连优势 + 位置权重
    """
    # 1. 棋子数量评分：自己棋子越多，对方越少，分越高
    ai_pieces = sum(row.count(AI) for row in board)
    hu_pieces = sum(row.count(HUMAN) for row in board)
    piece_score = (ai_pieces - hu_pieces) * 100

    # 2. 相邻二连评分：二连越多，进攻能力越强，分越高
    ai_pairs = count_adjacent_pairs(board, AI)
    hu_pairs = count_adjacent_pairs(board, HUMAN)
    pair_score = (ai_pairs - hu_pairs) * 50

    # 3. 位置评分：占中心位置加分
    pos_score = 0
    for x in range(SIZE):
        for y in range(SIZE):
            if board[x][y] == AI:
                pos_score += position_score(x, y)
            elif board[x][y] == HUMAN:
                pos_score -= position_score(x, y)

    # 总评分：三个维度相加
    return piece_score + pair_score + pos_score

# ===================== AI核心算法：极小极大+αβ剪枝（传统博弈搜索算法） =====================
def minimax(board, depth, alpha, beta, is_max, player):
    """
    🔥 极小极大算法（Minimax）+ αβ剪枝优化
    作用：递归模拟未来N步棋，找到最优解
    核心思想：
    - MAX层：我方（选分数最大的走法）
    - MIN层：对方（选分数最小的走法，坑我方）
    - αβ剪枝：剪掉无用分支，大幅减少计算量
    """
    # 终止条件1：游戏结束，直接返回胜负分
    over, winner = is_win(board)
    if over:
        return 10000 if winner == player else -10000
    # 终止条件2：达到最大搜索深度，返回评估分
    if depth == 0:
        return evaluate(board) if player == AI else -evaluate(board)

    # ===================== MAX层：当前玩家回合，选最大分 =====================
    if is_max:
        best = -INF  # 初始化最优分为负无穷
        # 遍历所有合法走法
        for m in get_moves(board, player):
            x,y,nx,ny = m
            # 深拷贝棋盘，模拟走棋
            nb = copy.deepcopy(board)
            nb[x][y], nb[nx][ny] = 0, player
            # 执行吃子规则
            nb, _ = do_eat_only_new(nb, nx, ny, player)
            # 递归进入下一层（对方回合，MIN层）
            score = minimax(nb, depth-1, alpha, beta, False, player)
            # 更新最优分
            best = max(best, score)
            alpha = max(alpha, best)
            # αβ剪枝：无需计算剩余分支，直接跳出
            if beta <= alpha:
                break
        return best

    # ===================== MIN层：对方回合，选最小分 =====================
    else:
        best = INF   # 初始化最优分为正无穷
        opp = 3 - player  # 对方玩家
        # 遍历对方所有合法走法
        for m in get_moves(board, opp):
            x,y,nx,ny = m
            # 模拟对方走棋
            nb = copy.deepcopy(board)
            nb[x][y], nb[nx][ny] = 0, opp
            nb, _ = do_eat_only_new(nb, nx, ny, opp)
            # 递归进入下一层（我方回合，MAX层）
            score = minimax(nb, depth-1, alpha, beta, True, player)
            # 更新最优分
            best = min(best, score)
            beta = min(beta, best)
            # αβ剪枝
            if beta <= alpha:
                break
        return best

def ai_think(board, player):
    """
    AI决策函数：遍历所有走法，选择【分数最高】的一步
    优先吃子：吃子的走法额外加分
    返回：最优走法 (x1,y1,x2,y2)
    """
    best_s = -INF
    best_m = None
    # 遍历所有合法走法
    for m in get_moves(board, player):
        x,y,nx,ny = m
        # 模拟走棋
        nb = copy.deepcopy(board)
        nb[x][y], nb[nx][ny] = 0, player
        nb, eat_flag = do_eat_only_new(nb, nx, ny, player)
        # 计算该走法的评分
        s = minimax(nb, MAX_DEPTH-1, -INF, INF, False, player)
        # 规则：能吃子 → 额外加分，优先选择
        if eat_flag:
            s += 200
        # 更新最优走法
        if s > best_s:
            best_s = s
            best_m = m
    return best_m

# ===================== 玩家交互功能 =====================
def human_move(board):
    """
    人类玩家走棋输入
    支持：正常走棋 + 输入undo悔棋
    返回：合法走法 或 "undo"
    """
    while True:
        try:
            print("\n走棋 → 例：3,0 2,0   悔棋 → undo")
            user_input = input().strip()
            # 输入undo → 悔棋
            if user_input.lower() == "undo":
                return "undo"
            # 解析走棋坐标
            p1, p2 = user_input.split()
            x1,y1 = map(int, p1.split(","))
            x2,y2 = map(int, p2.split(","))
            # 判断坐标合法性 + 走法规则
            if 0<=x1<4 and 0<=y1<4 and 0<=x2<4 and 0<=y2<4:
                if board[x1][y1]==HUMAN and board[x2][y2]==0 and abs(x1-x2)+abs(y1-y2)==1:
                    return (x1,y1,x2,y2)
            print("走法无效")
        except:
            print("输入错误")

# ===================== 游戏模式 =====================
def ai_vs_ai():
    """模式1：AI自对战（两个AI水平完全一致，公平对弈）"""
    board = init_board()
    print("🤖 模式：AI 互斗")
    print_board(board)
    while True:
        # 黑棋AI走棋
        print("黑棋思考中...")
        m = ai_think(board, AI)
        if not m:
            print("白棋胜利！")
            break
        x1,y1,x2,y2 = m
        board[x1][y1], board[x2][y2] = 0, AI
        board, cap = do_eat_only_new(board, x2, y2, AI)
        if cap: print("⚠️ 黑棋吃子！")
        print_board(board)
        if is_win(board)[0]:
            print("黑棋胜利！")
            break

        # 白棋AI走棋
        print("白棋思考中...")
        m = ai_think(board, HUMAN)
        if not m:
            print("黑棋胜利！")
            break
        x1,y1,x2,y2 = m
        board[x1][y1], board[x2][y2] = 0, HUMAN
        board, cap = do_eat_only_new(board, x2, y2, HUMAN)
        if cap: print("⚠️ 白棋吃子！")
        print_board(board)
        if is_win(board)[0]:
            print("白棋胜利！")
            break

def human_vs_ai():
    """模式2：人机对战 + 悔棋功能"""
    global history
    board = init_board()
    history = [copy.deepcopy(board)]  # 初始化历史记录
    print("👨‍💻 模式：人机对战（undo 悔棋）")
    print_board(board)
    while True:
        # 人类回合
        move = human_move(board)
        # 悔棋逻辑
        if move == "undo":
            if len(history)>=2:
                history.pop()  # 删除最后一步
                board = copy.deepcopy(history[-1])  # 恢复上一步棋盘
                print("↩️ 悔棋成功")
                print_board(board)
                continue
            else:
                print("❌ 无法悔棋")
                continue
        # 执行人类走棋
        x1,y1,x2,y2 = move
        board[x1][y1], board[x2][y2] = 0, HUMAN
        board, cap = do_eat_only_new(board, x2, y2, HUMAN)
        history.append(copy.deepcopy(board))  # 保存历史
        if cap: print("🎉 你吃子！")
        print_board(board)
        # 判断胜负
        if is_win(board)[0]:
            print("🏆 你赢了！")
            break

        # AI回合
        print("AI思考中...")
        m = ai_think(board, AI)
        if not m:
            print("🏆 你赢了！")
            break
        ax1,ay1,ax2,ay2 = m
        board[ax1][ay1], board[ax2][ay2] = 0, AI
        board, cap = do_eat_only_new(board, ax2, ay2, AI)
        history.append(copy.deepcopy(board))  # 保存历史
        if cap: print("⚠️ AI吃子！")
        print_board(board)
        # 判断胜负
        if is_win(board)[0]:
            print("🤖 AI赢了！")
            break

# ===================== 主函数：游戏入口 =====================
def main():
    """游戏主菜单：选择游戏模式"""
    print("===== 四棋游戏 =====")
    print("1 → AI 自对战")
    print("2 → 人机对战")
    while True:
        try:
            mode = int(input("选择模式："))
            if mode == 1:
                ai_vs_ai()
                break
            elif mode == 2:
                human_vs_ai()
                break
        except:
            print("输入 1 或 2")

# 运行游戏
if __name__ == "__main__":
    main()
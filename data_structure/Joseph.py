import random
import turtle
import PySimpleGUI as sg
from Queue import CircleQueue

'''
    /Apr/2023
    
    1: 循环结构模拟 循环队列 循环链表
    优点:简单
    缺点:复杂度高,n,m大时间都很长,严重超时 O(n*m)

    2: 优化索引(有序集合优化)
    注意到在简单模拟中存在m>>n的情况,出现大量空循环,考虑到只要有m>n则空循环存在,选择通过取余的方式去除所有空循环
    index = m % len(list) - 1 { m % len(list) != 0 }
            len(list) - 1 { m % len(list) == 0 }
    或:
    index_new = (index_old + m - 1) % len(list)
    (看作延展开的单链,index_old + m - 1 是在展开单链上的下标,对len(list)取模后就是在真实链表中的下标

    3: 递推公式
    f(n, m) = (f(n - 1, m) + m) % n
    f(n,m)为n个人报数m时离开,最后剩下的人的编号
    注意在公式中n动态变化
    原始的队列与经过删除循环后的队列在下标上存在对应联系,即递推公式所示
    对于未经删除与循环的队列,其与经过了一次删除的队列任一下标的关系均满足公式
    最终剩余的编号也不例外,因此可以从 f(1,m)——>f(n,m)
    时间复杂度到O(n),采取递归函数可以一行解决问题
    递归函数存在反复的问题,也可以用循环从下向上计算,效率更高,或者可以使用记忆化递归进行递归优化

'''


class Node1:
    def __init__(self, data, link=None):
        self.entry = data
        self.next = link


class JosephByLinkedList:
    """
    通过循环链表实现约瑟夫环
    """

    def __init__(self):
        self._head = None

    def build(self, n):
        self._head = p = n_node = Node1(1)
        for i in range(2, n + 1):
            n_node = Node1(i)
            p.next = n_node
            p = p.next
        n_node.next = self._head

    def jsp(self, n, m):
        self.build(n)
        p = self._head
        q = p
        count = n
        while q.next != p:
            q = q.next
        while count != 0:
            num = m % count
            if num == 0:
                num = count
            while num > 1:
                q = q.next
                p = p.next
                num -= 1
            # print(str(p.entry) + 'OUT')
            temp = p.entry
            q.next = p.next
            del p
            count -= 1
            if count == 0:
                return temp
            p = q.next

    def Check(self, times):
        """
        len:验证次数
        正确性验证
        """
        for i in range(times):
            n, m = random.randint(1, 100), random.randint(1, 100)
            ans = joseph(n, m)
            solution = self.jsp(n, m)
            if ans != solution:
                return False
        return True

# TODO 矢量绘图
class GUI:
    """
    输入,控制与绘图
    """

    def __init__(self):
        self.josephCircle = []
        # 绘图中外圈大圆的半径,根据显示器大小相应调整
        # TODO 自动获取显示器像素并确定绘图大小
        self.r = 300

        # 输入数据,初始化约瑟夫环
        sg.change_look_and_feel("LightGrey3")
        self.layout = [
            [sg.Text("Number of Circle:"), sg.InputText(key='n')],
            [sg.Text("Number of Be Killed"), sg.InputText(key='m')],
            [sg.Button("OK"), sg.Button("Cancel")]
        ]
        windowForInit = sg.Window("__Init__", layout=self.layout, element_justification='c')
        while True:
            event, values = windowForInit.read()
            if event in (None, "Cancel"):
                break
            elif event == "OK":
                try:
                    self.m = int(values['m'])
                    self.n = int(values['n'])
                    if self.n <= 0 or self.m <= 0:
                        sg.popup("Value too small")
                        continue
                    self.josephCircle = [i + 1 for i in range(self.n)]
                except ValueError:
                    sg.popup("Illegal Input")
                    continue
                break
        windowForInit.close()

        # 输入窗口正常关闭,控制窗口弹出
        self.layout = [
            [sg.Text("Your JosephCircle of Survivor")],
            [sg.Text(str(self.josephCircle), key='Circle')],
            [sg.Button("Kill")]
        ]
        self.window = sg.Window("JosephCircle", layout=self.layout, element_justification='c')

    def Run(self):
        """
        开始运行
        初始化画布背景
        命令循环
        """

        # 绘制外周大圆
        draw_circle_r_on_pos_without_pos_change(self.r)

        # 绘制n条辐射线
        for i in range(self.n):
            # 画线 记录点坐标
            turtle.down()
            turtle.seth(0 + i * (360 / self.n))
            turtle.forward(self.r * 3 / 2)
            turtle.write(str(i + 1), align='left', font=('黑体', 40, 'normal'))
            turtle.backward(self.r * 1 / 2)
            self.josephCircle[i] = [self.josephCircle[i], turtle.pos()]

            # 画小圆
            turtle.color('white')
            turtle.begin_fill()
            draw_circle_r_on_pos_without_pos_change((self.r // self.n) * 1 / 2,turtle.pos())
            turtle.end_fill()

            # 归位
            turtle.up()
            turtle.goto(0, 0)
            turtle.seth(0)

        # 进入命令循环
        while True:
            event, value = self.window.read()
            if event in (None, "Exit"):
                break
            elif event == "Kill":
                if len(self.josephCircle) == 0:
                    break
                self.Kill()

    def Kill(self):
        """
        Button:Kill 相关操作
        叉去下一应出列成员,绘制下一内圈
        """

        # 判断能否继续Kill 长度为1则不可继续
        if len(self.josephCircle) <= 1:
            turtle.up()
            turtle.goto(self.josephCircle[0][1])
            turtle.pencolor('red')
            turtle.write('Survive', font=('黑体', 20, 'normal'))
            return True

        # 主要判断 队列进行循环并取出出列成员
        if self.m != len(self.josephCircle):
            beKilled = self.josephCircle[self.m % len(self.josephCircle) - 1]
            beKilledPos = beKilled[1]
            if self.m % len(self.josephCircle) == 0:
                self.josephCircle = self.josephCircle[:-1]
            else:
                self.josephCircle = self.josephCircle[self.m % len(self.josephCircle):] + self.josephCircle[0:self.m % len(self.josephCircle) - 1]
        else:
            beKilled = self.josephCircle.pop()
            beKilledPos = beKilled[1]

        # 出列成员打叉
        turtle.up()
        turtle.goto(beKilledPos)
        turtle.down()
        turtle.pencolor('red')
        for i in range(4):
            turtle.speed(10)
            turtle.seth(45 + 90 * i)
            turtle.forward((len(self.josephCircle) / self.n) * ((self.r // self.n) * 5 / 6))
            turtle.goto(beKilledPos)
        turtle.up()
        turtle.speed(5)
        turtle.pencolor('white')

        # 控制窗口内显示更新
        self.window['Circle'].update(str([x[0] for x in self.josephCircle]))
        # 绘制下一内圈圆
        turtle.goto(0, 0)
        draw_circle_r_on_pos_without_pos_change(self.r * (len(self.josephCircle) / self.n),turtle.pos())

        # 绘制内圈圆上小圆
        for i in range(len(self.josephCircle)):
            # 调整方向
            turtle.seth(0 + (360 / self.n) * (self.josephCircle[i][0] - 1))
            turtle.forward(self.r * (len(self.josephCircle) / self.n))
            turtle.seth(-90)
            self.josephCircle[i][1] = turtle.pos()

            # 绘制小圆 填色
            turtle.color('white')
            turtle.begin_fill()
            draw_circle_r_on_pos_without_pos_change((len(self.josephCircle) / self.n) * ((self.r // self.n) * 1 / 2),turtle.pos())
            turtle.end_fill()

            # 归位至原点
            turtle.goto(0, 0)


def JosephByQueue(n, m):
    """
    循环队列求解约瑟夫环
    朴素模拟
    Args:
        n: length of queue
        m: number be killed
    """
    Cir = CircleQueue()
    for i in range(n):
        Cir.append(i + 1)
    cnt = 0
    while len(Cir) > 1:
        cnt += 1
        if cnt % m == 0:
            Cir.serve()
        else:
            Cir.append(Cir.serve())
    return Cir.retrieve()


def joseph(n, m):
    """
    优化的约瑟夫环递归实现
    """
    return n if n == 1 else (joseph(n - 1, m) + m - 1) % n + 1


def draw_circle_r_on_pos_without_pos_change(r, pos=turtle.pos()):
    """
    Args:
        r: radius of circle
        pos: center pos
    """
    turtle.up()
    turtle.goto(pos)
    turtle.seth(-90)
    turtle.forward(r)
    turtle.seth(0)
    turtle.down()
    turtle.circle(r)
    turtle.up()
    turtle.goto(pos)


if __name__ == "__main__":
    # 初始化画布参数
    turtle.hideturtle()
    turtle.screensize(1920, 1080, "black")
    turtle.pencolor("white")
    turtle.speed(5)
    turtle.width(3)

    Main = GUI()
    Main.Run()

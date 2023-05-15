# football_analysis
开源一个自己写的足球结果分析代码，通过大数据匹配相同赔率的比赛，计算比赛结果。


#### 项目运行

* 1.安装python运行环境
* 2.安装依赖包<br>
进行项目目录下执行`pip install --upgrade -r requirement.txt -i https://mirrors.bfsu.edu.cn/pypi/web/simple`
* 3.直接运行分析盘口思路.py文件即可<br>
`python3 分析盘口思路.py`


#### 待优化问题

1. 需要将match_map变量的分组精确，把胜率高的联赛分到一组，胜率低的联赛分到一组，以此来提升胜率。
2. 需要优化赔率计算算法，各位有思路可以提出。或者直接提交pr


#### 部分战绩截图

<img src="./屏幕截图1.png" alt="屏幕截图"/>

#### 运行截图

<img src="./屏幕截图.gif" alt="屏幕截图"/>

#### 问题解决

* 无法克隆仓库，命令改为`git clone ssh://git@ssh.github.com:443/czl0325/football_analysis.git`
import pymysql

march_season = "23中超"

db = pymysql.connect(host="47.99.134.39", port=3306, user="user", password="1111", database="lottery", charset='utf8mb4')
cursor = db.cursor()
query_str = f"select home_team from football_500 where match_group regexp '{march_season}' group by home_team;"
cursor.execute(query_str)
result = cursor.fetchall()
teams = []
for item in result:
    teams.append(item[0])
team_map = {}
for team in teams:
    query_str = f"select count(*) from football_500 where match_group regexp '{march_season}' and (home_team = '{team}' or visit_team = '{team}')"
    cursor.execute(query_str)
    result = cursor.fetchone()
    all_count = result[0]
    query_str = f"select count(*) from football_500 where match_group regexp '{march_season}' and ((home_team = '{team}' and match_pan = '赢') or (visit_team = '{team}' and match_pan = '输'));"
    cursor.execute(query_str)
    result = cursor.fetchone()
    win_count = result[0]
    win_rate = win_count / all_count
    team_map[team] = {
        "all": all_count,
        "win": win_count,
        "rate": round(win_rate, 2)
    }
team_map = sorted(team_map.items(), key=lambda kv: (kv[1]["rate"]), reverse=True)
print(f"{march_season}各只球队的赢盘率从大到小排列如下：")
for item in team_map:
    print(f"{item[0]}: 总场次{item[1]['all']}，赢盘{item[1]['win']}，赢盘率{item[1]['rate']}")
db.close()
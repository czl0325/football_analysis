# -*- coding: utf-8 -*-
import math
import requests
from lxml import etree
import pymysql
import re
import time
import datetime
import scipy.stats as stats
from decimal import Decimal
import hashlib


###########################################################################
# match的字段
# match_group: 具体赛事名称，如22/23赛季英超第3轮
# match_type: 赛事类型，如22/23赛季英超
# match_category: 赛事名称，如英超
# match_round: 赛事轮次，如第3轮
# match_time: 比赛时间
# home_team: 主队
# home_team_rank: 主队排名
# home_score: 主队积分
# visit_team: 客队
# visit_team_rank: 客队排名
# visit_score: 客队积分
# origin_pan_most: 初始盘口
# instant_pan_most: 即时盘口
###########################################################################

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
db = pymysql.connect(host="47.99.134.39", port=3306, user="user", password="1111", database="lottery", charset='utf8mb4')
cursor = db.cursor()
europe_map = {
    "威廉希尔": "wl",
    "澳门": "macao",
    "立博": "lb",
    "Bet365": "365",
    "Interwetten": "interwetten",
    "SNAI": "SNAI",
    "皇冠": "crown",
    "易胜博": "ysb",
    "伟德": "wd",
    "Oddset": "oddset",
    "Pinnacle平博": "pinnacle",
    "10BET": "10",
    "Coral": "coral",
    "利记": "lj",
    "金宝博": "jbb",
    "必发": "bf",
    "12BET": "12BET",
    "明升": "mansion"
}
asia_map = {
    "澳门": "macao",
    "Bet365": "365",
    "易胜博": "ysb",
    "金宝博": "jbb",
    "Pinnacle平博": "pinnacle",
    "Interwetten": "interwetten",
    "威廉希尔": "wl",
    "10BET": "10",
    "立博": "lb",
    "12BET": "12BET",
    "皇冠": "crown",
    "伟德": "wd",
    "利记": "lj",
    "明升": "mansion",
    "Coral": "coral",
    "18BET": "18BET",
    "盈禾": "yh"
}
match_map = {
    # "group1": [],
    "group2": ["英超", "英甲", "西甲", "意甲", "法甲", "德甲", "德丙联", "葡超", "荷甲", "英冠", "英足总杯", "欧冠", "欧罗巴", "德国杯", "意超杯", "意杯", "意乙", "意丙1A", "意丙1B", "意丙1C", "意青联", "法国杯", "西班牙杯", "非洲杯", "欧洲杯", "解放者杯", "西乙", "西丙1", "西丙2", "西丙3", "西丙4", "西协甲", "法乙", "德乙", "荷乙", "比杯", "瑞典超", "丹超", "瑞士超", "克罗甲", "塞甲联", "波甲", "波乙", "苏冠", "苏甲", "土超", "土甲", "苏超", "瑞士甲", "丹甲", "罗甲", "英乙", "比乙", "保超", "挪超", "挪甲", "德东北", "爱超", "爱甲", "黑山甲", "阿巴超", "埃及甲", "摩洛超", "阿尔及甲", "捷甲", "捷克乙", "黑山甲", "阿甲", "巴甲", "巴圣锦", "巴乙", "阿乙", "乌拉超", "智利甲", "厄瓜多尔甲", "秘鲁甲", "巴拉圭联", "墨西联", "墨西乙", "哥斯甲", "哥甲", "美职联", "澳超", "日职", "韩足杯", "日职乙", "日联杯", "K1联赛", "K2联赛", "印度超", "印度甲", "印尼超", "澳南超", "澳维超", "越南联", "伊朗超", "伊朗甲", "阿联超", "马来超", "泰超", "巴西杯", "欧会杯", "乌兹超", "冰岛联", "沙特联", "波黑超", "澳昆超", "中超", "中甲", "中协杯", "智甲", "智乙", "斯洛文甲", "南非超", "冰岛超", "卡塔联", "亚冠杯", "希腊超A", "厄甲", "奥甲", "奥乙", "巴拉联", "芬超", "南俱杯"],
    "group_inaccuracy": ["乌超", "葡甲", "比甲", "法丙"]
}
error_odds = Decimal('0.02')


# 分析基本面
def parse_fundamentals(match, url):
    response = requests.get(url, headers=headers)
    response.encoding = "gb2312"
    html2 = etree.HTML(response.text)
    match_group = html2.xpath("//div[@class='odds_header']//table//tr/td[3]//a[@class='hd_name']/text()")
    if len(match_group) > 0:
        match["match_group"] = match_group[0].strip()
        match_type = re.findall(r"(.*?)(第|分组|小组|资格|半|决|十六|八|季军|外围|排名|附加|升|降|春|秋)", match["match_group"])
        match_category = re.findall(r"\d+/?\d+(.*?)(第|分组|小组|资格|半|决|十六|八|季军|外围|秋季|排名|附加|升|降|春|秋)", match["match_group"])
        match_round = re.findall(r"第(\d+)轮", match["match_group"])
        if len(match_type):
            match["match_type"] = match_type[0][0]
        if len(match_category):
            match["match_category"] = match_category[0][0]
        if len(match_round):
            match["match_round"] = int(match_round[0])
    home_team = html2.xpath("//div[@class='odds_header']//table//tr/td[1]/ul/li/a/text()")
    if len(home_team) > 0:
        match["home_team"] = home_team[0]
    visit_team = html2.xpath("//div[@class='odds_header']//table//tr/td[5]/ul/li/a/text()")
    if len(visit_team) > 0:
        match["visit_team"] = visit_team[0]
    home_team_rank = html2.xpath(
        "//div[@class='odds_header']/div[@class='odds_hd_cont']/table/tbody/tr/td[1]/ul/li[2]/span[@class='red']/text()")
    if len(home_team_rank) > 0:
        match["home_team_rank"] = int(home_team_rank[0])
    else:
        match["home_team_rank"] = 0
    visit_team_rank = html2.xpath(
        "//div[@class='odds_header']/div[@class='odds_hd_cont']/table/tbody/tr/td[5]/ul/li[2]/span[@class='red']/text()")
    if len(visit_team_rank) > 0:
        match["visit_team_rank"] = int(visit_team_rank[0])
    else:
        match["visit_team_rank"] = 0
    score_table = html2.xpath("//div[@id='nav_jifen']//tr[position()<last()]")
    if len(score_table) > 0 and match["home_team_rank"] and match["visit_team_rank"]:
        all_teams = len(score_table)
        match["team_count"] = int(all_teams)
        for score_tr in score_table:
            tr_class = score_tr.xpath("./@class")
            if len(tr_class) > 0 and "jfb_this" in tr_class[0]:
                rank_td = score_tr.xpath("./td[1]/text()")
                if rank_td:
                    rank_td = rank_td[0]
                    if int(rank_td) == int(match["home_team_rank"]):
                        match["home_score"] = int(score_tr.xpath("./td[3]/text()")[0])
                    elif int(rank_td) == int(match["visit_team_rank"]):
                        match["visit_score"] = int(score_tr.xpath("./td[3]/text()")[0])
                    if "home_score" in match and "visit_score" in match:
                        break
    match_time1 = html2.xpath("//div[@class='odds_header']/div[@class='odds_hd_cont']/table/tbody/tr/td[3]/div/p[1]/text()")
    if len(match_time1) > 0:
        match["match_time"] = match_time1[0]
    match_filter = None
    for key, value in match_map.items():
        if "match_category" in match and match["match_category"] in value:
            match_filter = "|".join(value)
            break
    match["match_filter"] = match_filter
    return match


# 分析欧赔
def parse_europe(match, url):
    response = requests.get(url, headers=headers)
    response.encoding = "gb2312"
    html2 = etree.HTML(response.text)
    europe_trs = html2.xpath("//table[@id='datatb']/tr[@ttl='zy']")
    europe_odds = []
    for europe_tr in europe_trs:
        company = europe_tr.xpath("./td[2]/@title")
        if len(company):
            company = company[0]
        if "12BET" in company:
            company = "12BET"
        elif "明升" in company:
            company = "明升"
        origin_win_odds = europe_tr.xpath("./td[3]/table/tbody/tr[1]/td[1]/text()")
        if len(origin_win_odds):
            origin_win_odds = Decimal(origin_win_odds[0].strip())
        origin_even_odds = europe_tr.xpath("./td[3]/table/tbody/tr[1]/td[2]/text()")
        if len(origin_even_odds):
            origin_even_odds = Decimal(origin_even_odds[0].strip())
        origin_lose_odds = europe_tr.xpath("./td[3]/table/tbody/tr[1]/td[3]/text()")
        if len(origin_lose_odds):
            origin_lose_odds = Decimal(origin_lose_odds[0].strip())
        origin_win_kelly = europe_tr.xpath("./td[6]/table/tbody/tr[1]/td[1]/text()")
        if len(origin_win_kelly):
            origin_win_kelly = Decimal(origin_win_kelly[0].strip())
        origin_even_kelly = europe_tr.xpath("./td[6]/table/tbody/tr[1]/td[2]/text()")
        if len(origin_even_kelly):
            origin_even_kelly = Decimal(origin_even_kelly[0].strip())
        origin_lose_kelly = europe_tr.xpath("./td[6]/table/tbody/tr[1]/td[3]/text()")
        if len(origin_lose_kelly):
            origin_lose_kelly = Decimal(origin_lose_kelly[0].strip())
        origin_return_rate = europe_tr.xpath("./td[5]/table/tbody/tr[1]/td/text()")
        if len(origin_return_rate):
            origin_return_rate = Decimal(origin_return_rate[0].strip().replace("%", ""))
        instant_win_odds = europe_tr.xpath("./td[3]/table/tbody/tr[2]/td[1]/text()")
        if len(instant_win_odds):
            instant_win_odds = Decimal(instant_win_odds[0].strip())
        instant_even_odds = europe_tr.xpath("./td[3]/table/tbody/tr[2]/td[2]/text()")
        if len(instant_even_odds):
            instant_even_odds = Decimal(instant_even_odds[0].strip())
        instant_lose_odds = europe_tr.xpath("./td[3]/table/tbody/tr[2]/td[3]/text()")
        if len(instant_lose_odds):
            instant_lose_odds = Decimal(instant_lose_odds[0].strip())
        instant_win_kelly = europe_tr.xpath("./td[6]/table/tbody/tr[2]/td[1]/text()")
        if len(instant_win_kelly):
            instant_win_kelly = Decimal(instant_win_kelly[0].strip())
        instant_even_kelly = europe_tr.xpath("./td[6]/table/tbody/tr[2]/td[2]/text()")
        if len(instant_even_kelly):
            instant_even_kelly = Decimal(instant_even_kelly[0].strip())
        instant_lose_kelly = europe_tr.xpath("./td[6]/table/tbody/tr[2]/td[3]/text()")
        if len(instant_lose_kelly):
            instant_lose_kelly = Decimal(instant_lose_kelly[0].strip())
        instant_return_rate = europe_tr.xpath("./td[5]/table/tbody/tr[2]/td/text()")
        if len(instant_return_rate):
            instant_return_rate = Decimal(instant_return_rate[0].strip().replace("%", ""))
        europe_odd = {
            "company": company,
            "origin_win_odds": origin_win_odds,
            "origin_even_odds": origin_even_odds,
            "origin_lose_odds": origin_lose_odds,
            "origin_win_kelly": origin_win_kelly,
            "origin_even_kelly": origin_even_kelly,
            "origin_lose_kelly": origin_lose_kelly,
            "origin_return_rate": origin_return_rate,
            "instant_win_odds": instant_win_odds,
            "instant_even_odds": instant_even_odds,
            "instant_lose_odds": instant_lose_odds,
            "instant_win_kelly": instant_win_kelly,
            "instant_even_kelly": instant_even_kelly,
            "instant_lose_kelly": instant_lose_kelly,
            "instant_return_rate": instant_return_rate
        }
        europe_odds.append(europe_odd)
    match["europe_odds"] = europe_odds
    whole_pan = []
    league_pan = []
    all_win_count = 0
    all_even_count = 0
    all_lose_count = 0
    league_win_count = 0
    league_even_count = 0
    league_lose_count = 0
    for odds in europe_odds:
        if odds["company"] in asia_map and "match_filter" in match and match["match_filter"] is not None:
            company_value = asia_map[odds["company"]]
            origin_win_up = odds["origin_win_odds"] if odds["instant_win_odds"] > odds["origin_win_odds"] else (odds["origin_win_odds"] + error_odds)
            origin_win_down = (odds["origin_win_odds"] - error_odds) if odds["instant_win_odds"] > odds["origin_win_odds"] else odds["origin_win_odds"]
            origin_even_up = odds["origin_even_odds"] if odds["instant_even_odds"] > odds["origin_even_odds"] else (odds["origin_even_odds"] + error_odds)
            origin_even_down = (odds["origin_even_odds"] - error_odds) if odds["instant_even_odds"] > odds["origin_even_odds"] else odds["origin_even_odds"]
            origin_lose_up = odds["origin_lose_odds"] if odds["instant_lose_odds"] > odds["origin_lose_odds"] else (odds["origin_lose_odds"] + error_odds)
            origin_lose_down = (odds["origin_lose_odds"] - error_odds) if odds["instant_lose_odds"] > odds["origin_lose_odds"] else odds["origin_lose_odds"]
            instant_win_up = (odds["instant_win_odds"] + error_odds) if odds["instant_win_odds"] > odds["origin_win_odds"] else odds["instant_win_odds"]
            instant_win_down = odds["instant_win_odds"] if odds["instant_win_odds"] > odds[
                "origin_win_odds"] else (odds["instant_win_odds"] - error_odds)
            instant_even_up = (odds["instant_even_odds"] + error_odds) if odds["instant_even_odds"] > odds["origin_even_odds"] else odds["instant_even_odds"]
            instant_even_down = odds["instant_even_odds"] if odds["instant_even_odds"] > odds[
                "origin_even_odds"] else (odds["instant_even_odds"] - error_odds)
            instant_lose_up = (odds["instant_lose_odds"] + error_odds) if odds["instant_lose_odds"] > odds["origin_lose_odds"] else odds["instant_lose_odds"]
            instant_lose_down = odds["instant_lose_odds"] if odds["instant_lose_odds"] > odds[
                "origin_lose_odds"] else (odds["instant_lose_odds"] - error_odds)
            query_sql = f"select match_group, home_team_full, visit_team_full, field_score, instant_pan_{company_value} from football_500 where origin_win_odds_{company_value} between {origin_win_down} and {origin_win_up} and origin_even_odds_{company_value} between {origin_even_down} and {origin_even_up} and origin_lose_odds_{company_value} between {origin_lose_down} and {origin_lose_up} and instant_win_odds_{company_value} between {instant_win_down} and {instant_win_up} and instant_even_odds_{company_value} between {instant_even_down} and {instant_even_up} and instant_lose_odds_{company_value} between {instant_lose_down} and {instant_lose_up} and match_group regexp '{match['match_filter']}' "
            if "team_count" in match and match["team_count"] > 0 and match["match_round"] > match["team_count"] / 2:
                if match["home_team_rank"] and match["visit_team_rank"]:
                    query_sql += f" and home_team_rank {'<' if match['home_team_rank'] < match['visit_team_rank'] else '>'} visit_team_rank"
                if "home_score" in match and match["home_score"] is not None and "visit_score" in match and match["visit_score"] is not None:
                    if match["home_score"] > match["visit_score"]:
                        distance = match["home_score"] - match["visit_score"]
                        query_sql += f" and home_score - visit_score >= {distance - 2}"
                    else:
                        distance = match["visit_score"] - match["home_score"]
                        query_sql += f" and visit_score - home_score >= {distance - 2}"
            cursor.execute(query_sql)
            result = cursor.fetchall()
            if len(result) <= 0:
                continue
            pan_result = {
                "胜": 0,
                "平": 0,
                "负": 0,
            }
            league_pan_result = {
                "胜": 0,
                "平": 0,
                "负": 0,
            }
            for r in result:
                score_lst = r[3].split(":")
                if len(score_lst) != 2:
                    continue
                home_score = int(score_lst[0])
                visit_score = int(score_lst[1])
                if home_score > visit_score:
                    pan_result["胜"] += 1
                elif home_score == visit_score:
                    pan_result["平"] += 1
                else:
                    pan_result["负"] += 1
                if match["match_category"] in r[0]:
                    if home_score > visit_score:
                        league_pan_result["胜"] += 1
                    elif home_score == visit_score:
                        league_pan_result["平"] += 1
                    else:
                        league_pan_result["负"] += 1
            print(f"欧赔全网匹配结果：{odds['company']}, 胜:{pan_result['胜']}, 平:{pan_result['平']}, 负:{pan_result['负']}")
            all_win_count += pan_result["胜"]
            all_even_count += pan_result["平"]
            all_lose_count += pan_result["负"]
            if pan_result["胜"] > pan_result["平"] and pan_result["胜"] > pan_result["负"]:
                whole_pan.append("胜")
            elif pan_result["平"] > pan_result["胜"] and pan_result["平"] > pan_result["负"]:
                whole_pan.append("平")
            elif pan_result["负"] > pan_result["胜"] and pan_result["负"] > pan_result["平"]:
                whole_pan.append("负")
            else:
                whole_pan.append("均势")
            league_win_count += league_pan_result["胜"]
            league_even_count += league_pan_result["平"]
            league_lose_count += league_pan_result["负"]
            if league_pan_result["胜"] > 0 or league_pan_result["平"] > 0 or league_pan_result["负"] > 0:
                print(f"\033[4;34m欧赔本联赛匹配结果：{odds['company']}, 胜:{league_pan_result['胜']}, 平:{league_pan_result['平']}, 负:{league_pan_result['负']}\033[0m")
                if league_pan_result["胜"] > league_pan_result["平"] and league_pan_result["胜"] > league_pan_result["负"]:
                    league_pan.append("胜")
                elif league_pan_result["平"] > league_pan_result["胜"] and league_pan_result["平"] > league_pan_result["负"]:
                    league_pan.append("平")
                elif league_pan_result["负"] > league_pan_result["胜"] and league_pan_result["负"] > league_pan_result["平"]:
                    league_pan.append("负")
                else:
                    league_pan.append("均势")
    if len(set(whole_pan)) == 1 and len(whole_pan) > 1:
        print(f"\033[1;32;45m欧赔全网完美匹配！{set(whole_pan)}\033[0m")
    if len(set(league_pan)) == 1 and len(league_pan) > 1:
        print(f"\033[1;33;46m欧赔本联赛完美匹配！{set(league_pan)}\033[0m")
    return match


# 分析亚盘
def parse_asia(match, url):
    response = requests.get(url, headers=headers)
    response.encoding = "gb2312"
    html2 = etree.HTML(response.text)
    size_trs = html2.xpath("//div[@id='table_cont']/table/tr")
    odds_items = []
    origin_pan_map = {}
    instant_pan_map = {}
    for i in range(0, len(size_trs)):
        asia_tr = size_trs[i]
        company = asia_tr.xpath("./td[2]/p/a/@title")
        if len(company) <= 0:
            continue
        company = company[0].strip()
        if company is None:
            continue
        origin_odds = Decimal(asia_tr.xpath("./td[position()=5]/table/tbody/tr/td[2]/@ref")[0])
        origin_odds_home = asia_tr.xpath("./td[position()=5]/table/tbody/tr/td[1]/text()")[0].strip()
        if len(origin_odds_home) <= 0:
            continue
        origin_odds_home = Decimal(re.sub(r"[^(\d+|\.)]", "", origin_odds_home))
        origin_odds_visit = asia_tr.xpath("./td[position()=5]/table/tbody/tr/td[3]/text()")[0].strip()
        if len(origin_odds_visit) <= 0:
            continue
        origin_odds_visit = Decimal(re.sub(r"[^(\d+|\.)]", "", origin_odds_visit))
        instant_odds = Decimal(asia_tr.xpath("./td[position()=3]/table/tbody/tr/td[2]/@ref")[0])
        instant_odds_home = asia_tr.xpath("./td[position()=3]/table/tbody/tr/td[1]/text()")[0].strip()
        if len(instant_odds_home) <= 0:
            continue
        instant_odds_home = Decimal(re.sub(r"[^(\d+|\.)]", "", instant_odds_home))
        instant_odds_visit = asia_tr.xpath("./td[position()=3]/table/tbody/tr/td[3]/text()")[0]
        if len(instant_odds_visit) <= 0:
            continue
        instant_odds_visit = Decimal(re.sub(r"[^(\d+|\.)]", "", instant_odds_visit))
        if origin_odds in origin_pan_map:
            origin_pan_map[origin_odds] += 1
        else:
            origin_pan_map[origin_odds] = 1
        if instant_odds in instant_pan_map:
            instant_pan_map[instant_odds] += 1
        else:
            instant_pan_map[instant_odds] = 1
        if "盈禾" in company:
            company = "盈禾"
        elif "12BET" in company:
            company = "12BET"
        elif "明升" in company:
            company = "明升"
        elif "18BET" in company.upper():
            company = "18BET"
        odds_item = {
            "company": company,
            "origin_odds": origin_odds,
            "origin_odds_home": origin_odds_home,
            "origin_odds_visit": origin_odds_visit,
            "instant_odds": instant_odds,
            "instant_odds_home": instant_odds_home,
            "instant_odds_visit": instant_odds_visit
        }
        odds_items.append(odds_item)
    match["odds_items"] = odds_items
    origin_pan_tuple = sorted(origin_pan_map.items(), key=lambda x: x[1], reverse=True)
    if len(origin_pan_tuple):
        match["origin_pan_most"] = origin_pan_tuple[0][0]
    instant_pan_tuple = sorted(instant_pan_map.items(), key=lambda x: x[1], reverse=True)
    if len(instant_pan_tuple):
        match["instant_pan_most"] = instant_pan_tuple[0][0]
    if "instant_pan_most" in match and "origin_pan_most" in match and abs(match["instant_pan_most"] - match["origin_pan_most"]) >= 0.75:
        print(f"\033[1;34;43m注意：盘口变化{int(abs(match['instant_pan_most'] - match['origin_pan_most'])/Decimal('0.25'))}个，初盘{match['origin_pan_most']}, 即时盘{match['instant_pan_most']}\033[0m")
        query_str = f"""SELECT match_pan, COUNT(*) FROM football_500 WHERE origin_pan_most = {match['origin_pan_most']} and instant_pan_most = {match['instant_pan_most']} GROUP BY match_pan;"""
        cursor.execute(query_str)
        result = cursor.fetchall()
        if len(result) > 0:
            print(f"\033[1;34;43m查询历史数据，该盘口下胜率为：{result}\033[0m")
    if {"home_team_rank", "visit_team_rank", "home_score", "visit_score", "team_count", "match_round", "instant_pan_most"}.issubset(match.keys()):
        if match["match_round"] >= match["team_count"] / 2 + 1:
            if abs(match["home_team_rank"] - match["visit_team_rank"]) <= (3 if match["team_count"] > 10 else 2) and abs(match["instant_pan_most"]) >= 1.25:
                print(f"\033[1;30;45m注意：主队排名{match['home_team_rank']}，客队排名{match['visit_team_rank']}，让球{match['instant_pan_most']}偏深，预计{'主队' if match['instant_pan_most'] < 0 else '客队'}会有一场大胜，至少赢{math.ceil(abs(match['instant_pan_most']))}球。\033[0m")
            if match["home_team_rank"] <= match["visit_team_rank"] - (match["team_count"] / 2) and match["home_score"] >= match["visit_score"] + 15:
                if match["instant_pan_most"] >= -0.25:
                    print(f"\033[1;30;45m注意：主队排名{match['home_team_rank']}，客队排名{match['visit_team_rank']}，两者分差{match['home_score']-match['visit_score']}，让球{match['instant_pan_most']}，主队盘口非常便宜！\033[0m")
                    result_dic = {
                        "赢": 0,
                        "输": 0,
                        "走": 0
                    }
                    query_sql = f"select match_group, home_team_full, visit_team_full, field_score, match_url from football_500 where home_team_rank <= {match['home_team_rank']} and visit_team_rank >= {match['visit_team_rank']} and home_score >= {match['home_score']} and visit_score <= {match['visit_score']} and origin_pan_most = {match['origin_pan_most']} and instant_pan_most = {match['instant_pan_most']}"
                    cursor.execute(query_sql)
                    result = cursor.fetchall()
                    if len(result) > 0:
                        for res in result:
                            field_score = res[3].split(":")
                            if len(field_score) == 2:
                                if int(field_score[0]) + match["origin_pan_most"] > int(field_score[1]):
                                    result_dic["赢"] += 1
                                elif int(field_score[0]) + match["origin_pan_most"] < int(field_score[1]):
                                    result_dic["输"] += 1
                                else:
                                    result_dic["走"] += 1
                        print(f"\033[1;30;45m该盘口下主队赢盘概率为{round(result_dic['赢']/(result_dic['赢']+result_dic['输'])*100, 2)}%，{result_dic}\033[0m")
            if match["home_team_rank"] >= match["visit_team_rank"] + 10 and match["visit_score"] >= match["home_score"] + 15:
                if match["instant_pan_most"] <= 0:
                    print(f"\033[1;30;45m警惕：主队排名{match['home_team_rank']}，客队排名{match['visit_team_rank']}，两者分差{match['visit_score'] - match['home_score']}，让球{match['instant_pan_most']}，客队盘口非常便宜！\033[0m")
                    result_dic = {
                        "赢": 0,
                        "输": 0,
                        "走": 0
                    }
                    query_sql = f"select match_group, home_team_full, visit_team_full, field_score, instant_pan_most, match_url from football_500 where home_team_rank >= {match['home_team_rank']} and visit_team_rank <= {match['visit_team_rank']} and home_score <= {match['home_score']} and visit_score >= {match['visit_score']} and origin_pan_most = {match['origin_pan_most']} and instant_pan_most = {match['instant_pan_most']}"
                    cursor.execute(query_sql)
                    result = cursor.fetchall()
                    if len(result) > 0:
                        for res in result:
                            field_score = res[3].split(":")
                            if len(field_score) == 2:
                                if int(field_score[0]) + match["origin_pan_most"] > int(field_score[1]):
                                    result_dic["赢"] += 1
                                elif int(field_score[0]) + match["origin_pan_most"] < int(field_score[1]):
                                    result_dic["输"] += 1
                                else:
                                    result_dic["走"] += 1
                        print(f"该盘口下主队盘路情况为：{result_dic}")
                    query_sql = f"select match_group, home_team_full, visit_team_full, field_score, instant_pan_most, match_url from football_500 where ((home_team_full = '{match['home_team']}' and visit_team_full = '{match['visit_team']}') or (home_team_full = '{match['visit_team']}' and visit_team_full = '{match['home_team']}')) and DATE_FORMAT(match_time, '%Y-%m-%d') > DATE_SUB(CURDATE(),interval 3 year) order by match_time desc;"
                    cursor.execute(query_sql)
                    result = cursor.fetchall()
                    if len(result) > 0:
                        pan_dic = {
                            "赢": 0,
                            "输": 0,
                            "走": 0
                        }
                        win_dic = {
                            "胜": 0,
                            "平": 0,
                            "负": 0
                        }
                        for res in result:
                            field_score = res[3].split(":")
                            if len(field_score) == 2 and res[4] is not None:
                                if res[1] == match['home_team']:
                                    if int(field_score[0]) > int(field_score[1]):
                                        win_dic["胜"] += 1
                                    elif int(field_score[0]) == int(field_score[1]):
                                        win_dic["平"] += 1
                                    else:
                                        win_dic["负"] += 1
                                    if int(field_score[0]) + res[4] > int(field_score[1]):
                                        pan_dic["赢"] += 1
                                    elif int(field_score[0]) + res[4] < int(field_score[1]):
                                        pan_dic["输"] += 1
                                    else:
                                        pan_dic["走"] += 1
                                elif res[2] == match['home_team']:
                                    if int(field_score[1]) > int(field_score[0]):
                                        win_dic["胜"] += 1
                                    elif int(field_score[1]) == int(field_score[0]):
                                        win_dic["平"] += 1
                                    else:
                                        win_dic["负"] += 1
                                    if int(field_score[1]) - res[4] > int(field_score[0]):
                                        pan_dic["赢"] += 1
                                    elif int(field_score[1]) - res[4] < int(field_score[0]):
                                        pan_dic["输"] += 1
                                    else:
                                        pan_dic["走"] += 1
                        pan_dic = sorted(pan_dic.items(), key=lambda x: x[1], reverse=True)
                        win_dic = sorted(win_dic.items(), key=lambda x: x[1], reverse=True)
                        print(f"历史交战主队欧赔情况{win_dic}")
                        print(f"历史交战主队亚盘情况{pan_dic}")
    whole_pan = []
    league_pan = []
    all_win_count = 0
    all_lose_count = 0
    all_run_count = 0
    league_win_count = 0
    league_lose_count = 0
    league_run_count = 0
    score_map = {}
    for odds in odds_items:
        if odds["company"] in asia_map and "match_filter" in match and match["match_filter"] is not None:
            company_value = asia_map[odds["company"]]
            query_sql = f"select match_group, home_team_full, visit_team_full, field_score, instant_pan_{company_value} from football_500 where origin_pan_{company_value} = {odds['origin_odds']} and origin_pan_odds_home_{company_value} between {odds['origin_odds_home'] - error_odds} and {odds['origin_odds_home'] + error_odds} and origin_pan_odds_visit_{company_value} between {odds['origin_odds_visit'] - error_odds} and {odds['origin_odds_visit'] + error_odds} and instant_pan_{company_value} = {odds['instant_odds']} and match_group regexp '{match['match_filter']}' "
            if odds['origin_odds_home'] < odds['instant_odds_home']:
                query_sql += f" and instant_pan_odds_home_{company_value} between {odds['instant_odds_home']} and {odds['instant_odds_home'] + error_odds}  and instant_pan_odds_visit_{company_value} between {round(odds['instant_odds_visit'] - error_odds, 2)} and {odds['instant_odds_visit']}"
            else:
                query_sql += f" and instant_pan_odds_home_{company_value} between {odds['instant_odds_home'] - error_odds} and {odds['instant_odds_home']}  and instant_size_odds_visit_{company_value} between {odds['instant_odds_visit']} and {round(odds['instant_odds_visit'] + error_odds, 2)}"
            if "team_count" in match and match["team_count"] > 0 and match["match_round"] > match["team_count"] / 4:
                if match["home_team_rank"] and match["visit_team_rank"]:
                    query_sql += f" and home_team_rank {'<' if match['home_team_rank'] < match['visit_team_rank'] else '>'} visit_team_rank"
                if "home_score" in match and match["home_score"] is not None and "visit_score" in match and match["visit_score"] is not None:
                    if match["home_score"] > match["visit_score"]:
                        distance = match["home_score"] - match["visit_score"]
                        query_sql += f" and home_score - visit_score >= {distance - 2}"
                    else:
                        distance = match["visit_score"] - match["home_score"]
                        query_sql += f" and visit_score - home_score >= {distance - 2}"
            cursor.execute(query_sql)
            # print(query_sql)
            result = cursor.fetchall()
            if len(result) <= 0:
                continue
            pan_result = {
                "赢": 0,
                "输": 0,
                "走": 0,
            }
            league_pan_result = {
                "赢": 0,
                "输": 0,
                "走": 0,
            }
            for r in result:
                score_lst = r[3].split(":")
                if len(score_lst) != 2:
                    continue
                home_score = int(score_lst[0])
                visit_score = int(score_lst[1])
                key_hash = f"{r[3]}_{hashlib.md5((r[0]+r[1]+r[2]).encode()).hexdigest()}"
                if key_hash in score_map:
                    score_map[key_hash] += 1
                else:
                    score_map[key_hash] = 1
                if home_score + r[4] > visit_score:
                    pan_result["赢"] += 1
                elif home_score + r[4] < visit_score:
                    pan_result["输"] += 1
                else:
                    pan_result["走"] += 1
                if match["match_category"] in r[0]:
                    if home_score + r[4] > visit_score:
                        league_pan_result["赢"] += 1
                    elif home_score + r[4] < visit_score:
                        league_pan_result["输"] += 1
                    else:
                        league_pan_result["走"] += 1
            print(f"亚盘全网匹配结果：{odds['company']}, 让球：{r[4]}, 赢:{pan_result['赢']}, 输:{pan_result['输']}, 走:{pan_result['走']}")
            all_win_count += pan_result["赢"]
            all_run_count += pan_result["走"]
            all_lose_count += pan_result["输"]
            if pan_result["赢"] > pan_result["输"] and pan_result["赢"] > pan_result["走"]:
                whole_pan.append("赢")
            elif pan_result["走"] > pan_result["输"] and pan_result["走"] > pan_result["赢"]:
                whole_pan.append("走")
            elif pan_result["输"] > pan_result["走"] and pan_result["输"] > pan_result["赢"]:
                whole_pan.append("输")
            else:
                whole_pan.append("均势")
            league_win_count += league_pan_result["赢"]
            league_run_count += league_pan_result["走"]
            league_lose_count += league_pan_result["输"]
            if league_pan_result["赢"] > 0 or league_pan_result["输"] > 0 or league_pan_result["走"] > 0:
                print(f"\033[4;34m亚盘本联赛匹配结果：{odds['company']}, 让球：{r[4]}, 赢:{league_pan_result['赢']}, 输:{league_pan_result['输']}, 走:{league_pan_result['走']}\033[0m")
                if league_pan_result["赢"] > league_pan_result["输"] and league_pan_result["赢"] > league_pan_result["走"]:
                    league_pan.append("赢")
                elif league_pan_result["走"] > league_pan_result["输"] and league_pan_result["走"] > league_pan_result["赢"]:
                    league_pan.append("走")
                elif league_pan_result["输"] > league_pan_result["走"] and league_pan_result["输"] > league_pan_result["赢"]:
                    league_pan.append("输")
                else:
                    league_pan.append("均势")
    if len(set(whole_pan)) == 1 and len(whole_pan) > 1:
        print(f"\033[1;32;45m亚盘全网盘口完美匹配！{set(whole_pan)}\033[0m")
    if all_win_count + all_run_count + all_lose_count > 0:
        result_str = f"亚盘全网盘口:赢={all_win_count},输={all_lose_count},走={all_run_count},"
        if all_win_count > all_lose_count and all_win_count > all_run_count:
            result_str += "赢盘概率最大,为{:.2f}%".format(all_win_count / (all_win_count + all_lose_count + all_run_count) * 100)
            print(f"\033[1;35m{result_str}\033[0m")
        elif all_run_count > all_lose_count and all_run_count > all_win_count:
            result_str += "走盘概率最大,为{:.2f}%".format(all_run_count / (all_win_count + all_lose_count + all_run_count) * 100)
            print(f"\033[1;32m{result_str}\033[0m")
        elif all_lose_count > all_run_count and all_lose_count > all_win_count:
            result_str += "输盘概率最大,为{:.2f}%".format(all_lose_count / (all_win_count + all_lose_count + all_run_count) * 100)
            print(f"\033[1;34m{result_str}\033[0m")
    if len(set(league_pan)) == 1 and len(league_pan) > 1:
        print(f"\033[1;33;46m亚盘本联赛盘口完美匹配！{set(league_pan)}\033[0m")
    if league_win_count + league_run_count + league_lose_count > 0:
        result_str = f"亚盘本联赛盘口:赢={league_win_count},输={league_lose_count},走={league_run_count},"
        if league_win_count > league_lose_count and league_win_count > league_run_count:
            result_str += "赢盘概率最大,为{:.2f}%".format(league_win_count / (league_win_count + league_lose_count + league_run_count) * 100)
            print(f"\033[1;35m{result_str}\033[0m")
        elif league_run_count > league_lose_count and league_run_count > league_win_count:
            result_str += "走盘概率最大,为{:.2f}%".format(league_run_count / (league_win_count + league_lose_count + league_run_count) * 100)
            print(f"\033[1;32m{result_str}\033[0m")
        elif league_lose_count > league_run_count and league_lose_count > league_win_count:
            result_str += "输盘概率最大,为{:.2f}%".format(league_lose_count / (league_win_count + league_lose_count + league_run_count) * 100)
            print(f"\033[1;34m{result_str}\033[0m")
    if len(score_map):
        new_score_map = {}
        for key in score_map:
            key_lst = key.split("_")
            new_key = key_lst[0]
            if new_key in new_score_map:
                new_score_map[new_key] += score_map[key]
            else:
                new_score_map[new_key] = score_map[key]
        new_score_map = dict(sorted(new_score_map.items(), key=lambda item: item[1], reverse=True))
        score_str = "比分概率前三分别是："
        index = 0
        for key in new_score_map:
            score_str += f"[{key}]({new_score_map[key]}次)     "
            index += 1
            if index >= 3:
                break
        print(score_str)
    return match


# 分析大小球
def parse_size(match, url):
    response = requests.get(url, headers=headers, timeout=30)
    response.encoding = "gb2312"
    html = etree.HTML(response.text)
    size_trs = html.xpath("//table[@id='datatb']/tr")
    if "match_type" in match:
        query_sql = f"""SELECT home_team_full, visit_team_full, field_score from football_500 where match_group regexp '^{match["match_type"]}'"""
        cursor.execute(query_sql)
        result = cursor.fetchall()
        home_goals = 0
        home_miss = 0
        home_count = 0
        league_home_goals = 0
        league_visit_goals = 0
        visit_goals = 0
        visit_miss = 0
        visit_count = 0
        team_map = {}
        if len(result) > 0:
            for res in result:
                score_lst = res[2].split(':')
                if len(score_lst) == 2:
                    if res[0] == match["home_team"]:
                        home_goals += int(score_lst[0])
                        home_miss += int(score_lst[1])
                        home_count += 1
                    if res[1] == match["visit_team"]:
                        visit_goals += int(score_lst[1])
                        visit_miss += int(score_lst[0])
                        visit_count += 1
                    league_home_goals += int(score_lst[0])
                    league_visit_goals += int(score_lst[1])
                    if res[0] not in team_map:
                        team_map[res[0]] = {
                            "home_goal": 0,
                            "home_miss": 0,
                            "home_count": 0,
                            "visit_goal": 0,
                            "visit_miss": 0,
                            "visit_count": 0,
                        }
                    if res[1] not in team_map:
                        team_map[res[1]] = {
                            "home_goal": 0,
                            "home_miss": 0,
                            "home_count": 0,
                            "visit_goal": 0,
                            "visit_miss": 0,
                            "visit_count": 0,
                        }
                    team_map[res[0]]["home_goal"] += int(score_lst[0])
                    team_map[res[0]]["home_miss"] += int(score_lst[1])
                    team_map[res[0]]["home_count"] += 1
                    team_map[res[1]]["visit_goal"] += int(score_lst[1])
                    team_map[res[1]]["visit_miss"] += int(score_lst[0])
                    team_map[res[1]]["visit_count"] += 1
            size_lst = None
            if home_count > 0 and visit_count > 0:
                home_exception = (home_goals / home_count) / (league_home_goals / len(result)) * (visit_miss / visit_count)
                visit_exception = (visit_goals / visit_count) / (league_visit_goals / len(result)) * (home_miss / home_count)
                home_avg = round(home_goals / home_count, 1)
                visit_avg = round(visit_goals / visit_count, 1)
                home_goal_exception = [round(stats.poisson.pmf(i, home_exception), 4) for i in range(7)]
                visit_goal_exception = [round(stats.poisson.pmf(i, visit_exception), 4) for i in range(7)]
                home_goal_most_likely = -1
                visit_goal_most_likely = -1
                goal = 0
                for i in range(len(home_goal_exception)):
                    if home_goal_exception[i] > goal:
                        goal = home_goal_exception[i]
                        home_goal_most_likely = i
                goal = 0
                for i in range(len(visit_goal_exception)):
                    if visit_goal_exception[i] > goal:
                        goal = visit_goal_exception[i]
                        visit_goal_most_likely = i
                size_lst = [home_goal_exception[0] * visit_goal_exception[0],
                            home_goal_exception[1] * visit_goal_exception[0] + home_goal_exception[0] * visit_goal_exception[1],
                            home_goal_exception[2] * visit_goal_exception[0] + home_goal_exception[0] * visit_goal_exception[2] + home_goal_exception[1] * visit_goal_exception[1],
                            home_goal_exception[3] * visit_goal_exception[0] + home_goal_exception[0] * visit_goal_exception[3] + home_goal_exception[2] * visit_goal_exception[1] + home_goal_exception[1] * visit_goal_exception[2],
                            home_goal_exception[0] * visit_goal_exception[4] + home_goal_exception[4] * visit_goal_exception[0] + home_goal_exception[3] * visit_goal_exception[1] + home_goal_exception[1] * visit_goal_exception[3] + home_goal_exception[2] * visit_goal_exception[2],
                            home_goal_exception[0] * visit_goal_exception[5] + home_goal_exception[5] * visit_goal_exception[0] + home_goal_exception[4] * visit_goal_exception[1] + home_goal_exception[1] * visit_goal_exception[4] + home_goal_exception[3] * visit_goal_exception[2] + home_goal_exception[2] * visit_goal_exception[3]]
                print(f"""{match["home_team"]}主场平均进球{home_avg}，泊松计算最大概率进球数{home_goal_most_likely}，{match["visit_team"]}客场平均进球{visit_avg}，泊松计算最大概率进球数{visit_goal_most_likely}""")
            compare_size = []
            all_compare = True
            for size_tr in size_trs:
                company = size_tr.xpath("./td[2]/p/a/@title")
                if len(company) <= 0:
                    continue
                company = company[0]
                if company is None:
                    continue
                if company in asia_map:
                    try:
                        company_value = asia_map[company]
                        origin_size = abs(Decimal(size_tr.xpath(
                            "./td[position()=5]/table/tbody/tr/td[2]/@ref")[0]))
                        origin_size_odds_home = Decimal(re.sub(r"[^(\d+|\.)]", "", size_tr.xpath(
                            "./td[position()=5]/table/tbody/tr/td[1]/text()")[0]))
                        origin_size_odds_visit = Decimal(re.sub(r"[^(\d+|\.)]", "", size_tr.xpath(
                            "./td[position()=5]/table/tbody/tr/td[3]/text()")[0]))
                        instant_size = abs(Decimal(size_tr.xpath(
                            "./td[position()=3]/table/tbody/tr/td[2]/@ref")[0]))
                        instant_size_odds_home = Decimal(re.sub(r"[^(\d+|\.)]", "", size_tr.xpath(
                            "./td[position()=3]/table/tbody/tr/td[1]/text()")[0]))
                        instant_size_odds_visit = Decimal(re.sub(r"[^(\d+|\.)]", "", size_tr.xpath(
                            "./td[position()=3]/table/tbody/tr/td[3]/text()")[0]))
                        query_sql = f"select match_group, home_team_full, visit_team_full, field_score, instant_size_{company_value} from football_500 where origin_size_{company_value} = {origin_size} and origin_size_odds_home_{company_value} between {origin_size_odds_home - error_odds} and {origin_size_odds_home + error_odds} and origin_size_odds_visit_{company_value} between {origin_size_odds_visit - error_odds} and {origin_size_odds_visit + error_odds} and instant_size_{company_value} = {instant_size}"
                        if origin_size == instant_size:
                            if origin_size_odds_home < instant_size_odds_home:
                                query_sql += f" and instant_size_odds_home_{company_value} between {instant_size_odds_home} and {instant_size_odds_home + error_odds}  and instant_size_odds_visit_{company_value} between {instant_size_odds_visit - error_odds} and {instant_size_odds_visit}"
                            else:
                                query_sql += f" and instant_size_odds_home_{company_value} between {instant_size_odds_home - error_odds} and {instant_size_odds_home}  and instant_size_odds_visit_{company_value} between {instant_size_odds_visit} and {instant_size_odds_visit + error_odds}"
                        else:
                            query_sql += f" and instant_size_odds_home_{company_value} between {instant_size_odds_home - error_odds} and {instant_size_odds_home + error_odds} and instant_size_odds_visit_{company_value} between {instant_size_odds_visit - error_odds} and {instant_size_odds_visit + error_odds}"
                        if match["match_filter"] is not None:
                            query_sql += f" and match_group regexp '{match['match_filter']}'"
                        cursor.execute(query_sql)
                        result = cursor.fetchall()
                        if len(result) > 0:
                            size_map = {"大": 0, "小": 0, "走": 0}
                            small_probability = 0
                            drop_probability = 0
                            big_probability = 0
                            current_size = None
                            for res in result:
                                score_lst = res[3].split(":")
                                current_size = res[4]
                                if int(score_lst[0]) + int(score_lst[1]) > current_size:
                                    size_map["大"] += 1
                                elif int(score_lst[0]) + int(score_lst[1]) < current_size:
                                    size_map["小"] += 1
                                else:
                                    size_map["走"] += 1
                            if size_lst and current_size:
                                for i in range(int(current_size) + 1):
                                    small_probability += size_lst[i]
                                if isinstance(current_size, int):
                                    drop_probability = size_lst[current_size]
                                big_probability = 1 - small_probability - drop_probability
                            if size_map["大"] > size_map["小"] and size_map["大"] > size_map["走"]:
                                if big_probability > small_probability and big_probability > drop_probability:
                                    print(f"{company}盘口，开盘{current_size}球，大球概率最大，泊松={round(big_probability*100, 2)}%，同赔=大：{size_map['大']}，小：{size_map['小']}，走：{size_map['走']}")
                                    compare_size.append("大")
                                else:
                                    print(f"{company}盘口，开盘{current_size}球，泊松小球概率={round(small_probability * 100, 2)}%，同赔=大：{size_map['大']}，小：{size_map['小']}，走：{size_map['走']}，泊松和同赔不匹配")
                                    all_compare = False
                            elif size_map["小"] > size_map["大"] and size_map["小"] > size_map["走"]:
                                if small_probability > big_probability and small_probability > drop_probability:
                                    print(f"{company}盘口，开盘{current_size}球，小球概率最大，泊松={round(small_probability * 100, 2)}%，同赔=大：{size_map['大']}，小：{size_map['小']}，走：{size_map['走']}")
                                    compare_size.append("小")
                                else:
                                    print(f"{company}盘口，开盘{current_size}球，泊松大球概率={round(big_probability * 100, 2)}%，同赔=大：{size_map['大']}，小：{size_map['小']}，走：{size_map['走']}，泊松和同赔不匹配")
                                    all_compare = False
                            elif size_map["走"] > size_map["大"] and size_map["走"] > size_map["小"]:
                                if drop_probability > big_probability and drop_probability > small_probability:
                                    print(f"{company}盘口，开盘{current_size}球，走盘概率最大，泊松={round(drop_probability*100, 2)}%，同赔=大：{size_map['大']}，小：{size_map['小']}，走：{size_map['走']}")
                                    compare_size.append("走")
                                else:
                                    print(f"{company}盘口，开盘{current_size}球，泊松大球概率={round(big_probability * 100, 2)}%，同赔=大：{size_map['大']}，小：{size_map['小']}，走：{size_map['走']}，泊松和同赔不匹配")
                                    all_compare = False
                    except Exception as e:
                        print(f"遇到错误={str(e)}, 网址{match['url']}")
                        continue
            if all_compare:
                print(f"\033[1;32m全部盘口一致，{set(compare_size)}\033[0m")
            home_closed = []
            visit_closed = []
            try:
                for team in team_map:
                    if team != match["home_team"] and team != match["visit_team"]:
                        if team_map[team]["home_count"] <= 0 or team_map[team]["visit_count"] <= 0 or team_map[team]["home_count"] <= 0 or team_map[team]["visit_count"] <= 0 or team_map[match["visit_team"]]["visit_count"] <= 0 or team_map[match["home_team"]]["home_count"] <= 0:
                            continue
                        if abs(team_map[team]["home_goal"]/team_map[team]["home_count"]-team_map[match["home_team"]]["home_goal"]/team_map[match["home_team"]]["home_count"]) <= 0.1 and abs(team_map[team]["home_miss"]/team_map[team]["home_count"]-team_map[match["home_team"]]["home_miss"]/team_map[match["home_team"]]["home_count"]) <= 0.1:
                            home_closed.append(team)
                        if abs(team_map[team]["visit_goal"]/team_map[team]["visit_count"]-team_map[match["visit_team"]]["visit_goal"]/team_map[match["visit_team"]]["visit_count"]) <= 0.1 and abs(team_map[team]["visit_miss"]/team_map[team]["visit_count"]-team_map[match["visit_team"]]["visit_miss"]/team_map[match["visit_team"]]["visit_count"]) <= 0.1:
                            visit_closed.append(team)
                if len(visit_closed) > 0:
                    print(f"与客队相近球队:{visit_closed}")
                    print("对比主队与相似队伍战绩:")
                    for team in visit_closed:
                        cursor.execute(f"""select field_score from football_500 where home_team_full = '{match["home_team"]}' and visit_team_full = '{team}' and match_group regexp '{match["match_type"]}'""")
                        result1 = cursor.fetchall()
                        if len(result1) > 0:
                            for res in result1:
                                score_lst = res[0].split(":")
                                print(f"{match['home_team']}vs{team}：比分{score_lst[0]}:{score_lst[1]}")
                if len(home_closed) > 0:
                    print(f"与主队相近球队:{home_closed}")
                    print("对比客队与相似队伍战绩:")
                    for team in home_closed:
                        cursor.execute(f"""select field_score from football_500 where home_team_full = '{team}' and visit_team_full = '{match["visit_team"]}' and match_group regexp '{match["match_type"]}'""")
                        result1 = cursor.fetchall()
                        if len(result1) > 0:
                            for res in result1:
                                score_lst = res[0].split(":")
                                print(f"{team}vs{match['visit_team']}: 比分{score_lst[0]}:{score_lst[1]}")
            except Exception as e:
                print(f"遇到错误={str(e)}, 网址{match['url']}")
    return match


def analyse_match():
    response1 = requests.get("https://live.500.com/2h1.php", headers=headers) # 全部
    # response1 = requests.get("https://live.500.com", headers=headers)  # 竞彩
    response1.encoding = "gb2312"
    html1 = etree.HTML(response1.text)
    tr_list = html1.xpath("//table[@id='table_match']/tbody/tr")
    for tr in tr_list:
        match_item = {}
        match_time = tr.xpath("./td[4]/text()")
        if len(match_time) <= 0:
            continue
        is_start = tr.xpath("./td[5]/text()")
        if len(is_start) <= 0:
            continue
        is_start = is_start[0]
        is_finish = tr.xpath("./td[5]/span/text()")
        if len(is_finish) > 0:
            is_finish = is_finish[0]
            if is_finish == "完":
                match_item["field_score"] = tr.xpath("./td[7]/div/a[1]/text()")[0] + ":" + tr.xpath("./td[7]/div/a[3]/text()")[0]
        # if is_start != "未" and is_finish != "完":
        #     continue
        today = datetime.datetime.today()
        year = today.year
        match_time = f"{year}-" + match_time[0]
        match_time = time.strptime(match_time, "%Y-%m-%d %H:%M")
        current_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        time_diff = time.mktime(match_time) - time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M"))
        if time_diff < -3600 * 1:
            continue
        if time_diff > 3600 * 2 and is_start == "未":
            break
        is_friend = tr.xpath("./td[2]/a/text()")
        if len(is_friend) <= 0:
            continue
        is_friend = is_friend[0]
        if "友谊" in is_friend:
            continue
        # if is_friend != "英超" or is_friend != "意甲":
        #     continue
        pan = tr.xpath("./td[7]/div/a[2]/text()")
        if len(pan) <= 0:
            continue
        pan = pan[0]
        # if pan == "-" or len(pan) <= 0:
        #     continue
        detail_url = tr.xpath(".//td[last()-1]/a[1]/@href")
        if len(detail_url) <= 0:
            continue
        detail_url = "https:" + detail_url[0]
        match_item["url"] = detail_url
        match_item = parse_fundamentals(match_item, detail_url)
        if "field_score" in match_item:
            print(f"\033[1;32m{match_item['match_group']}, 主队:{match_item['home_team']}, 客队:{match_item['visit_team']}, {match_item['match_time']}。已结束比分: {match_item['field_score']}\033[0m")
        else:
            print(f"\033[1;31m{match_item['match_group']}, 主队:{match_item['home_team']}, 客队:{match_item['visit_team']}, {match_item['match_time']}。\033[0m")
        if match_item["match_category"] in match_map["group_inaccuracy"]:
            print("不准确的联赛，暂不预测")
            continue
        match_item = parse_europe(match_item, detail_url.replace("shuju", "ouzhi"))
        time.sleep(3)
        match_item = parse_asia(match_item, detail_url.replace("shuju", "yazhi"))
        time.sleep(3)
        match_item = parse_size(match_item, detail_url.replace("shuju", "daxiao"))
        time.sleep(3)
    db.close()


def analyse_detail(detail_url):
    match_item = {"url": detail_url}
    match_item = parse_fundamentals(match_item, detail_url)
    if "field_score" in match_item:
        print(
            f"\033[1;32m{match_item['match_group']}, 主队:{match_item['home_team']}, 客队:{match_item['visit_team']}, {match_item['match_time']}。已结束比分: {match_item['field_score']}\033[0m")
    else:
        print(
            f"\033[1;31m{match_item['match_group']}, 主队:{match_item['home_team']}, 客队:{match_item['visit_team']}, {match_item['match_time']}。\033[0m")
    match_item = parse_europe(match_item, detail_url.replace("shuju", "ouzhi"))
    match_item = parse_asia(match_item, detail_url.replace("shuju", "yazhi"))
    match_item = parse_size(match_item, detail_url.replace("shuju", "daxiao"))
    db.close()


if __name__ == '__main__':
    analyse_match()
    # analyse_detail("https://odds.500.com/fenxi/shuju-1090804.shtml")

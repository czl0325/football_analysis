# -*- coding: utf-8 -*-
import requests
from lxml import etree
import pymysql
import re
import time
import datetime
import scipy.stats as stats
from decimal import Decimal

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
# field_score: 完场比分
# match_filter：赛事筛选条件
# odds_items：每家公司赔率数组 {'company': 开盘公司, 'origin_odds': 初赔, 'origin_odds_home': 主队初赔水位, 'origin_odds_visit': 客队初赔水位, 'instant_odds': 即赔, 'instant_odds_home': 主队即赔水位, 'instant_odds_visit': 客队即赔水位}
###########################################################################

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
db = pymysql.connect(host="47.99.134.39", port=3306, user="user", password="1111", database="lottery", charset='utf8mb4')
# db = pymysql.connect(host="localhost", port=3306, user="root", password="1111", database="lottery", charset='utf8mb4')
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
    "group": [
        # 欧洲
        "英超", "英冠", "英甲", "英乙", "英足总杯", "西甲", "西乙", "西丙1", "西丙2", "西丙3", "西丙4", "西协甲", "西班牙杯", "意甲", "意乙", "意丙1A", "意丙1B", "意丙1C", "意青联", "意超杯", "意杯", "法甲", "法乙", "法国杯", "德甲", "德乙", "德丙联", "德东北", "德国杯", "荷甲", "荷乙", "荷杯", "葡超", "葡联杯", "比乙", "比杯", "瑞典超", "瑞典甲", "瑞典杯", "丹超", "丹甲", "丹麦杯", "瑞士超", "瑞士甲", "瑞士杯", "克罗甲", "克罗杯", "塞甲联", "波甲", "波乙", "波兰杯", "苏超", "苏冠", "苏甲", "土甲", "罗甲", "罗杯", "保超", "挪超", "挪甲", "挪威杯", "爱超", "爱甲", "黑山甲", "阿巴超", "捷甲", "捷克乙", "捷克杯", "波黑超", "斯洛文甲", "冰岛超", "希腊超A", "奥甲", "奥乙", "芬超", "俄超", "塞浦甲", "以超", "北爱超"
        # 欧洲赛事  
        "欧冠", "欧罗巴", "欧会杯",
        # 南美洲
        "巴甲", "巴圣锦", "巴乙", "巴西杯", "阿甲", "阿乙", "乌拉超", "秘鲁甲", "巴拉圭联", "解放者杯", "巴拉联", "南俱杯", "智甲", "智乙",
        # 北美洲
        "美职联", "公开赛", "美冠", "哥甲", "哥伦杯", "墨西联", "墨西乙", "墨西杯", "厄甲", "玻甲", "哥斯甲",
        # 大洋洲
        "澳超", "澳南超", "澳维超", "澳昆超", "澳西超",
        # 亚洲赛事
        "日职", "日职乙", "日天皇杯", "日联杯", "K1联赛", "K2联赛", "韩足杯", "印度超", "印度甲", "印尼超", "越南联", "伊朗超", "伊朗甲", "阿联超", "马来超", "泰超", "乌兹超", "沙特联", "沙特甲", "中超", "中甲", "中协杯", "卡塔联", "亚冠杯",
        # 非洲
        "埃及甲", "摩洛超", "阿尔及甲", "突尼斯甲", "南非超", "尼日超",
        # 世界赛事
        "非洲杯", "欧洲杯", "世青赛", "世界杯"
        "乌超", "葡甲", "比甲", "土超", "法丙"],
    # 不准确的联赛放下面来 ！！！！
    "group_inaccuracy": []
    # "group_inaccuracy": ["乌超", "葡甲", "比甲", "土超", "法丙"]
}
error_odds = Decimal('0.03')


# 分析基本面
def parse_fundamentals(match, url):
    response = requests.get(url, headers=headers)
    response.encoding = "gb2312"
    html2 = etree.HTML(response.text)
    match_group = html2.xpath("//div[@class='odds_header']//table//tr/td[3]//a[@class='hd_name']/text()")
    if len(match_group) > 0:
        match["match_group"] = match_group[0].strip()
        match_type = re.findall(r"(.*?)(第|分组|小组|资格赛|半|决赛|十六|八|季军|外围|排名|升|降|春|秋|16|附加赛|欧会杯资格附加.*?赛)", match["match_group"])
        match_category = re.findall(r"\d+/?\d+(.*?)(第|分组|小组|资格赛|半|决赛|十六|八|季军|外围|排名|升|降|春|秋|16|附加赛|欧会杯资格附加.*?赛)", match["match_group"])
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
    home_team_rank = html2.xpath("//div[@class='odds_header']/div[@class='odds_hd_cont']/table/tbody/tr/td[1]/ul/li[2]/span[@class='red']/text()")
    if len(home_team_rank) > 0:
        match["home_team_rank"] = int(home_team_rank[0])
    else:
        match["home_team_rank"] = 0
    visit_team_rank = html2.xpath("//div[@class='odds_header']/div[@class='odds_hd_cont']/table/tbody/tr/td[5]/ul/li[2]/span[@class='red']/text()")
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
    match_time1 = html2.xpath(
        "//div[@class='odds_header']/div[@class='odds_hd_cont']/table/tbody/tr/td[3]/div/p[1]/text()")
    if len(match_time1) > 0:
        match["match_time"] = match_time1[0].replace("比赛时间", "").strip()
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
            origin_win_down = (odds["origin_win_odds"] - error_odds) if odds["instant_win_odds"] > odds[
                "origin_win_odds"] else odds["origin_win_odds"]
            origin_even_up = odds["origin_even_odds"] if odds["instant_even_odds"] > odds["origin_even_odds"] else (
                    odds["origin_even_odds"] + error_odds)
            origin_even_down = (odds["origin_even_odds"] - error_odds) if odds["instant_even_odds"] > odds[
                "origin_even_odds"] else odds["origin_even_odds"]
            origin_lose_up = odds["origin_lose_odds"] if odds["instant_lose_odds"] > odds["origin_lose_odds"] else (
                    odds["origin_lose_odds"] + error_odds)
            origin_lose_down = (odds["origin_lose_odds"] - error_odds) if odds["instant_lose_odds"] > odds[
                "origin_lose_odds"] else odds["origin_lose_odds"]
            instant_win_up = (odds["instant_win_odds"] + error_odds) if odds["instant_win_odds"] > odds[
                "origin_win_odds"] else odds["instant_win_odds"]
            instant_win_down = odds["instant_win_odds"] if odds["instant_win_odds"] > odds[
                "origin_win_odds"] else (odds["instant_win_odds"] - error_odds)
            instant_even_up = (odds["instant_even_odds"] + error_odds) if odds["instant_even_odds"] > odds[
                "origin_even_odds"] else odds["instant_even_odds"]
            instant_even_down = odds["instant_even_odds"] if odds["instant_even_odds"] > odds[
                "origin_even_odds"] else (odds["instant_even_odds"] - error_odds)
            instant_lose_up = (odds["instant_lose_odds"] + error_odds) if odds["instant_lose_odds"] > odds[
                "origin_lose_odds"] else odds["instant_lose_odds"]
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
                print(
                    f"\033[4;34m欧赔本联赛匹配结果：{odds['company']}, 胜:{league_pan_result['胜']}, 平:{league_pan_result['平']}, 负:{league_pan_result['负']}\033[0m")
                if league_pan_result["胜"] > league_pan_result["平"] and league_pan_result["胜"] > league_pan_result[
                    "负"]:
                    league_pan.append("胜")
                elif league_pan_result["平"] > league_pan_result["胜"] and league_pan_result["平"] > league_pan_result[
                    "负"]:
                    league_pan.append("平")
                elif league_pan_result["负"] > league_pan_result["胜"] and league_pan_result["负"] > league_pan_result[
                    "平"]:
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
        instant_odds_home_state = ""
        if "↑" in instant_odds_home:
            instant_odds_home_state = "up"
        elif "↓" in instant_odds_home:
            instant_odds_home_state = "down"
        instant_odds_home = Decimal(re.sub(r"[^(\d+|\.)]", "", instant_odds_home))
        instant_odds_visit = asia_tr.xpath("./td[position()=3]/table/tbody/tr/td[3]/text()")[0]
        if len(instant_odds_visit) <= 0:
            continue
        instant_odds_visit_state = ""
        if "↑" in instant_odds_visit:
            instant_odds_visit_state = "up"
        elif "↓" in instant_odds_visit:
            instant_odds_visit_state = "down"
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
            "instant_odds_home_state": instant_odds_home_state,
            "instant_odds_visit": instant_odds_visit,
            "instant_odds_visit_state": instant_odds_visit_state
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
        print(f"\033[1;34;43m注意：盘口变化{int(abs(match['instant_pan_most'] - match['origin_pan_most']) / Decimal('0.25'))}个，初盘{match['origin_pan_most']}, 即时盘{match['instant_pan_most']}\033[0m")
        query_str = f"""SELECT match_pan, COUNT(*) FROM football_500 WHERE origin_pan_most = {match['origin_pan_most']} and instant_pan_most = {match['instant_pan_most']} GROUP BY match_pan;"""
        cursor.execute(query_str)
        result = cursor.fetchall()
        if len(result) > 0:
            print(f"\033[1;34;43m查询历史数据，该盘口下胜率为：{result}\033[0m")
    if {"home_team_rank", "visit_team_rank", "home_score", "visit_score", "team_count", "match_round", "instant_pan_most"}.issubset(match.keys()):
        if match["match_round"] >= match["team_count"] / 2 + 1:
            if abs(match["home_team_rank"] - match["visit_team_rank"]) <= (3 if match["team_count"] > 10 else 2) and abs(match["instant_pan_most"]) >= 1.25:
                print(f"\033[1;30;45m注意：主队排名{match['home_team_rank']}，客队排名{match['visit_team_rank']}，让球{match['instant_pan_most']}偏深，预计{'主队' if match['instant_pan_most'] < 0 else '客队'}会有一场大胜，可以上独赢。\033[0m")
            if match["home_team_rank"] <= match["visit_team_rank"] - (match["team_count"] / 2) and match["home_score"] >= match["visit_score"] + 15:
                if match["instant_pan_most"] >= -0.25:
                    print(f"\033[1;30;45m注意：主队排名{match['home_team_rank']}，客队排名{match['visit_team_rank']}，两者分差{match['home_score'] - match['visit_score']}，让球{match['instant_pan_most']}，主队盘口非常便宜！\033[0m")
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
                        print(f"\033[1;30;45m该盘口下主队赢盘概率为{round(result_dic['赢'] / (result_dic['赢'] + result_dic['输']) * 100, 2)}%，{result_dic}\033[0m")
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
    if {"instant_pan_most"}.issubset(match.keys()):
        # 对比历史让球数
        concede = "visit"
        if match["instant_pan_most"] <= 0:
            concede = "home"
        query_sql = f"select match_group, home_team_full, visit_team_full, field_score, instant_pan_most, match_pan from football_500 where ((home_team_full = '{match['home_team']}' and visit_team_full = '{match['visit_team']}') or (home_team_full = '{match['visit_team']}' and visit_team_full = '{match['home_team']}')) and DATE_FORMAT(match_time, '%Y-%m-%d') > DATE_SUB('{match['match_time']}', interval 3 year) and match_time < '{match['match_time']}' order by match_time desc;"
        cursor.execute(query_sql)
        result = cursor.fetchall()
        if len(result) > 0:
            home_concede = []
            visit_concede = []
            for r in result:
                if r[4] is not None:
                    if concede == "home":
                        if r[1] == match['home_team']:
                            home_concede.append(r[4])
                        else:
                            visit_concede.append(r[4])
                    else:
                        if r[1] == match['visit_team']:
                            home_concede.append(r[4])
                        else:
                            visit_concede.append(r[4])
            all_concede = sorted([abs(x) for x in home_concede] + [abs(x) for x in visit_concede], reverse=True)
            if len(all_concede) >= 3:
                if abs(match["instant_pan_most"]) >= all_concede[0] + Decimal('0.5'):
                        print(f"\033[1;30;45m{'主队' if concede == 'home' else '客队'}让球高于历史让球数，预计{'主队' if concede == 'home' else '客队'}会打出盘口。\033[0m")
        # 对比状态，判断是否有反弹情况
        home_pan_status = []
        home_res_status = []
        visit_pan_status = []
        visit_res_status = []
        history_count = 6
        query_sql = f"select match_group, home_team_full, visit_team_full, field_score, instant_pan_most, match_pan, match_result from football_500 where (home_team_full = '{match['home_team']}' or visit_team_full = '{match['home_team']}') and match_time < '{match['match_time']}' order by match_time desc limit {history_count};"
        cursor.execute(query_sql)
        result = cursor.fetchall()
        if len(result) >= history_count:
            for r in result:
                if r[1] == match['home_team']:
                    home_pan_status.append(r[5])
                    home_res_status.append(r[6])
                elif r[2] == match['home_team']:
                    if r[5] == "赢":
                        home_pan_status.append("输")
                    elif r[5] == "输":
                        home_pan_status.append("赢")
                    else:
                        home_pan_status.append("走")
                    if r[6] == "胜":
                        home_res_status.append("负")
                    elif r[6] == "负":
                        home_res_status.append("胜")
                    else:
                        home_res_status.append("平")
        query_sql = f"select match_group, home_team_full, visit_team_full, field_score, instant_pan_most, match_pan, match_result from football_500 where (home_team_full = '{match['visit_team']}' or visit_team_full = '{match['visit_team']}') and match_time < '{match['match_time']}' order by match_time desc limit {history_count};"
        cursor.execute(query_sql)
        result = cursor.fetchall()
        if len(result) >= history_count:
            for r in result:
                if r[1] == match['visit_team']:
                    visit_pan_status.append(r[5])
                    visit_res_status.append(r[6])
                elif r[2] == match['visit_team']:
                    if r[5] == "赢":
                        visit_pan_status.append("输")
                    elif r[5] == "输":
                        visit_pan_status.append("赢")
                    else:
                        visit_pan_status.append("走")
                    if r[6] == "胜":
                        visit_res_status.append("负")
                    elif r[6] == "负":
                        visit_res_status.append("胜")
                    else:
                        visit_res_status.append("平")
        if home_pan_status.count("输") >= history_count - 2 and home_pan_status[:3].count("赢") <= 0 and (visit_pan_status.count("赢") >= history_count - 2 or visit_pan_status[:2].count("赢") == 2) and match["instant_pan_most"] <= -0.75:
            print(f"\033[1;30;45m主队近期状态不佳，却让出{abs(match['instant_pan_most'])}球。预计主队反弹概率极大。\033[0m")
        elif visit_pan_status.count("输") >= history_count - 2 and visit_pan_status[:3].count("赢") <= 0 and (home_pan_status.count("赢") >= history_count - 2 or home_pan_status[:2].count("赢") == 2) and match["instant_pan_most"] >= 0.75:
            print(f"\033[1;30;45m客队近期状态不佳，却让出{abs(match['instant_pan_most'])}球。预计客队反弹概率极大。\033[0m")
        if home_res_status.count("胜") <= 0 and visit_res_status.count("胜") >= history_count - 3 and match["instant_pan_most"] <= -0.5:
            print(f"\033[1;30;45m主队近5场未尝一胜，却让出{abs(match['instant_pan_most'])}球。预计主队反弹概率极大。\033[0m")
        elif visit_res_status.count("胜") <= 0 and home_res_status.count("胜") >= history_count - 3 and match["instant_pan_most"] >= 0.5:
            print(f"\033[1;30;45m客队近5场未尝一胜，却让出{abs(match['instant_pan_most'])}球。预计客队反弹概率极大。\033[0m")
    all_win_count = 0
    all_lose_count = 0
    all_run_count = 0
    league_win_count = 0
    league_lose_count = 0
    league_run_count = 0
    score_map = {}
    team_map = {}
    if {"origin_pan_most", "instant_pan_most"}.issubset(match):
        print(f"亚盘初盘让球{match['origin_pan_most']}，即时盘让球{match['instant_pan_most']}")
    for odds in odds_items:
        if odds["company"] in asia_map and "match_filter" in match and match["match_filter"] is not None:
            company_value = asia_map[odds["company"]]
            query_sql = f"select match_group, home_team_full, visit_team_full, field_score, instant_pan_{company_value} from football_500 where origin_pan_{company_value} = {odds['origin_odds']} and origin_pan_odds_home_{company_value} between {round(odds['origin_odds_home'] - error_odds / 2, 3)} and {round(odds['origin_odds_home'] + error_odds / 2, 3)} and origin_pan_odds_visit_{company_value} between {round(odds['origin_odds_visit'] - error_odds / 2, 3)} and {round(odds['origin_odds_visit'] + error_odds / 2, 3)} and instant_pan_{company_value} = {odds['instant_odds']} "
            if odds["instant_odds_home_state"] == "up":
                query_sql += f" and instant_pan_odds_home_{company_value} between {odds['instant_odds_home']} and {round(odds['instant_odds_home'] + error_odds, 3)}"
            elif odds["instant_odds_home_state"] == "down":
                query_sql += f" and instant_pan_odds_home_{company_value} between {round(odds['instant_odds_home'] - error_odds, 3)} and {odds['instant_odds_home']}"
            else:
                query_sql += f" and instant_pan_odds_home_{company_value} between {round(odds['instant_odds_home'] - error_odds / 2, 3)} and {round(odds['instant_odds_home'] + error_odds / 2, 3)}"
            if odds["instant_odds_visit_state"] == "up":
                query_sql += f" and instant_pan_odds_visit_{company_value} between {odds['instant_odds_visit']} and {round(odds['instant_odds_visit'] + error_odds, 3)}"
            elif odds["instant_odds_visit_state"] == "down":
                query_sql += f" and instant_pan_odds_visit_{company_value} between {round(odds['instant_odds_visit'] - error_odds, 3)} and {odds['instant_odds_visit']}"
            else:
                query_sql += f" and instant_pan_odds_visit_{company_value} between {round(odds['instant_odds_visit'] - error_odds / 2, 3)} and {round(odds['instant_odds_visit'] + error_odds / 2, 3)}"
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
            query_sql += f" and match_group regexp '{match['match_filter']}';"
            # print(query_sql)
            cursor.execute(query_sql)
            old_result = cursor.fetchall()
            result = [r for r in old_result if (r[0] != match["match_group"] and r[1] != match["home_team"] and r[2] != match["visit_team"])]
            if len(result) <= 0:
                continue
            for r in result:
                score_lst = r[3].split(":")
                if len(score_lst) != 2:
                    continue
                home_score = int(score_lst[0])
                visit_score = int(score_lst[1])
                match_hash = r[0] + "_" + r[1] + "_" + r[2] # hashlib.md5((r[0] + r[1] + r[2]).encode()).hexdigest()
                score_hash = f"{r[3]}_{match_hash}"
                temp_result = "走"
                if home_score + r[4] > visit_score:
                    temp_result = "赢"
                elif home_score + r[4] < visit_score:
                    temp_result = "输"
                if match_hash in team_map:
                    if team_map[match_hash] != temp_result:
                        print("有冲突的结果", team_map)
                else:
                    team_map[match_hash] = temp_result
                if score_hash in score_map:
                    score_map[score_hash] += 1
                else:
                    score_map[score_hash] = 1
    for key in team_map:
        if team_map[key] == "赢":
            all_win_count += 1
        elif team_map[key] == "输":
            all_lose_count += 1
        else:
            all_run_count += 1
        if match["match_category"] in key:
            if team_map[key] == "赢":
                league_win_count += 1
            elif team_map[key] == "输":
                league_lose_count += 1
            else:
                league_run_count += 1
    if all_win_count + all_run_count + all_lose_count > 0:
        result_str = f"亚盘全网盘口:赢={all_win_count},输={all_lose_count},走={all_run_count},"
        if all_win_count > all_lose_count and all_win_count > all_run_count:
            result_str += "赢盘概率最大,为{:.2f}%".format(
                all_win_count / (all_win_count + all_lose_count + all_run_count) * 100)
            print(f"\033[1;35m{result_str}\033[0m")
        elif all_run_count > all_lose_count and all_run_count > all_win_count:
            result_str += "走盘概率最大,为{:.2f}%".format(
                all_run_count / (all_win_count + all_lose_count + all_run_count) * 100)
            print(f"\033[1;32m{result_str}\033[0m")
        elif all_lose_count > all_run_count and all_lose_count > all_win_count:
            result_str += "输盘概率最大,为{:.2f}%".format(
                all_lose_count / (all_win_count + all_lose_count + all_run_count) * 100)
            print(f"\033[1;34m{result_str}\033[0m")
        else:
            print(result_str)
    else:
        if match["match_filter"]:
            print("未匹配到相同赔率相同水位的比赛")
    if league_win_count + league_run_count + league_lose_count > 0:
        result_str = f"亚盘本联赛盘口:赢={league_win_count},输={league_lose_count},走={league_run_count},"
        if league_win_count > league_lose_count and league_win_count > league_run_count:
            result_str += "赢盘概率最大,为{:.2f}%".format(
                league_win_count / (league_win_count + league_lose_count + league_run_count) * 100)
            print(f"\033[1;35m{result_str}\033[0m")
        elif league_run_count > league_lose_count and league_run_count > league_win_count:
            result_str += "走盘概率最大,为{:.2f}%".format(
                league_run_count / (league_win_count + league_lose_count + league_run_count) * 100)
            print(f"\033[1;32m{result_str}\033[0m")
        elif league_lose_count > league_run_count and league_lose_count > league_win_count:
            result_str += "输盘概率最大,为{:.2f}%".format(
                league_lose_count / (league_win_count + league_lose_count + league_run_count) * 100)
            print(f"\033[1;34m{result_str}\033[0m")
        else:
            print(result_str)
    if len(score_map):
        new_score_map = {}
        for key in score_map:
            key_lst = key.split("_")
            new_key = key_lst[0]
            if new_key in new_score_map:
                new_score_map[new_key] += 1
            else:
                new_score_map[new_key] = 1
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
            if home_count > 3 and visit_count > 3:
                home_exception = (home_goals / home_count) / (league_home_goals / len(result)) * (visit_miss / visit_count)
                visit_exception = (visit_goals / visit_count) / (league_visit_goals / len(result)) * (home_miss / home_count)
                home_avg = round(home_goals / home_count, 1)
                visit_avg = round(visit_goals / visit_count, 1)
                home_goal_exception = [round(stats.poisson.pmf(i, home_exception), 4) for i in range(7)]
                visit_goal_exception = [round(stats.poisson.pmf(i, visit_exception), 4) for i in range(7)]
                print(f"""{match["home_team"]}主场平均进球{home_avg}，泊松分布计算{home_goal_exception}，{match["visit_team"]}客场平均进球{visit_avg}，泊松分布计算{visit_goal_exception}""")
                size_dict = {
                    0: home_goal_exception[0] * visit_goal_exception[0],
                    1: home_goal_exception[1] * visit_goal_exception[0] + home_goal_exception[0] * visit_goal_exception[1],
                    2: home_goal_exception[2] * visit_goal_exception[0] + home_goal_exception[0] * visit_goal_exception[2] + home_goal_exception[1] * visit_goal_exception[1],
                    3: home_goal_exception[3] * visit_goal_exception[0] + home_goal_exception[0] * visit_goal_exception[3] + home_goal_exception[2] * visit_goal_exception[1] + home_goal_exception[1] * visit_goal_exception[2],
                    4: home_goal_exception[0] * visit_goal_exception[4] + home_goal_exception[4] * visit_goal_exception[0] + home_goal_exception[3] * visit_goal_exception[1] + home_goal_exception[1] * visit_goal_exception[3] + home_goal_exception[2] * visit_goal_exception[2],
                    5: home_goal_exception[0] * visit_goal_exception[5] + home_goal_exception[5] * visit_goal_exception[0] + home_goal_exception[4] * visit_goal_exception[1] + home_goal_exception[1] * visit_goal_exception[4] + home_goal_exception[3] * visit_goal_exception[2] + home_goal_exception[2] * visit_goal_exception[3]
                }
                small_probability = size_dict[0]+size_dict[1]+size_dict[2]
                print(f"泊松分布2.5球小概率={round(small_probability * 100, 2)}%，2.5球大概率={round((1 - small_probability) * 100, 2)}%")
                size_str = "泊松分布计算进球数，按概率从大到小排列：\n"
                size_dict = dict(sorted(size_dict.items(), key=lambda x: x[1], reverse=True))
                for key, value in size_dict.items():
                    size_str += f"({key}球：概率{round(value*100, 2)}%)  "
                print(size_str)
            else:
                print(f"{match['home_team']}主场或{match['visit_team']}客场比赛场次不足4场，不计算泊松分布")
            all_matches = {}
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
                instant_size_odds_home = size_tr.xpath("./td[position()=3]/table/tbody/tr/td[1]/text()")
                if len(instant_size_odds_home) <= 0:
                    continue
                instant_size_odds_home = instant_size_odds_home[0]
                instant_size_odds_home_state = ""
                if "↑" in instant_size_odds_home:
                    instant_size_odds_home_state = "up"
                elif "↓" in instant_size_odds_home:
                    instant_size_odds_home_state = "down"
                instant_size_odds_home = Decimal(re.sub(r"[^(\d+|\.)]", "", instant_size_odds_home))
                instant_size_odds_visit = size_tr.xpath(
                    "./td[position()=3]/table/tbody/tr/td[3]/text()")
                if len(instant_size_odds_visit) <= 0:
                    continue
                instant_size_odds_visit = instant_size_odds_visit[0]
                instant_size_odds_visit_state = ""
                if "↑" in instant_size_odds_visit:
                    instant_size_odds_visit_state = "up"
                elif "↓" in instant_size_odds_visit:
                    instant_size_odds_visit_state = "down"
                instant_size_odds_visit = Decimal(re.sub(r"[^(\d+|\.)]", "", instant_size_odds_visit))
                query_sql = f"select match_group, home_team_full, visit_team_full, field_score, instant_size_{company_value} from football_500 where origin_size_{company_value} = {origin_size} and origin_size_odds_home_{company_value} between {origin_size_odds_home - error_odds / 2} and {origin_size_odds_home + error_odds / 2} and origin_size_odds_visit_{company_value} between {origin_size_odds_visit - error_odds / 2} and {origin_size_odds_visit + error_odds / 2} and instant_size_{company_value} = {instant_size}"
                if instant_size_odds_home_state == "up":
                    query_sql += f" and instant_pan_odds_home_{company_value} between {instant_size_odds_home} and {round(instant_size_odds_home + error_odds, 3)}"
                elif instant_size_odds_home_state == "down":
                    query_sql += f" and instant_pan_odds_home_{company_value} between {round(instant_size_odds_home - error_odds, 3)} and {instant_size_odds_home}"
                else:
                    query_sql += f" and instant_pan_odds_home_{company_value} between {round(instant_size_odds_home - error_odds / 2, 3)} and {round(instant_size_odds_home + error_odds / 2, 3)}"
                if instant_size_odds_visit_state == "up":
                    query_sql += f" and instant_pan_odds_visit_{company_value} between {instant_size_odds_visit} and {round(instant_size_odds_visit + error_odds, 3)}"
                elif instant_size_odds_visit_state == "down":
                    query_sql += f" and instant_pan_odds_visit_{company_value} between {round(instant_size_odds_visit - error_odds, 3)} and {instant_size_odds_visit}"
                else:
                    query_sql += f" and instant_pan_odds_visit_{company_value} between {round(instant_size_odds_visit - error_odds / 2, 3)} and {round(instant_size_odds_visit + error_odds / 2, 3)}"
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
                # print(query_sql)
                cursor.execute(query_sql)
                result = cursor.fetchall()
                if len(result) > 0:
                    for res in result:
                        score_lst = res[3].split(":")
                        key_str = f"{res[0]}_{res[1]}_{res[2]}"
                        if key_str not in all_matches:
                            all_matches[key_str] = int(score_lst[0]) + int(score_lst[1])
            except Exception as e:
                print(f"遇到错误={str(e)}, 网址{match['url']}")
                continue
    all_matches = dict(sorted(all_matches.items(), key=lambda item: item[1]))
    size_dict = {}
    for key, value in all_matches.items():
        if value in size_dict:
            size_dict[value] += 1
        else:
            size_dict[value] = 1
    size_dict = dict(sorted(size_dict.items(), key=lambda item: item[1], reverse=True))
    if len(size_dict) > 0:
        size_str = "大小同赔计算，按概率从大到小排列：\n"
        for key, value in size_dict.items():
            size_str += f"({key}球：{value}场)  "
        print(size_str)
    if "match_type" in match:
        home_closed = []
        visit_closed = []
        try:
            for team in team_map:
                if team != match["home_team"] and team != match["visit_team"]:
                    if team_map[team]["home_count"] <= 0 or team_map[team]["visit_count"] <= 0 or team_map[team][
                        "home_count"] <= 0 or team_map[team]["visit_count"] <= 0 or team_map[match["visit_team"]][
                        "visit_count"] <= 0 or team_map[match["home_team"]]["home_count"] <= 0:
                        continue
                    if abs(team_map[team]["home_goal"] / team_map[team]["home_count"] -
                           team_map[match["home_team"]]["home_goal"] / team_map[match["home_team"]][
                               "home_count"]) <= 0.1 and abs(
                        team_map[team]["home_miss"] / team_map[team]["home_count"] -
                        team_map[match["home_team"]]["home_miss"] / team_map[match["home_team"]][
                            "home_count"]) <= 0.1:
                        home_closed.append(team)
                    if abs(team_map[team]["visit_goal"] / team_map[team]["visit_count"] -
                           team_map[match["visit_team"]]["visit_goal"] / team_map[match["visit_team"]][
                               "visit_count"]) <= 0.1 and abs(
                        team_map[team]["visit_miss"] / team_map[team]["visit_count"] -
                        team_map[match["visit_team"]]["visit_miss"] / team_map[match["visit_team"]][
                            "visit_count"]) <= 0.1:
                        visit_closed.append(team)
            if len(visit_closed) > 0:
                print(f"与客队相近球队:{visit_closed}")
                print("对比主队与相似队伍战绩:")
                for team in visit_closed:
                    cursor.execute(
                        f"""select field_score from football_500 where home_team_full = '{match["home_team"]}' and visit_team_full = '{team}' and match_group regexp '{match["match_type"]}'""")
                    result1 = cursor.fetchall()
                    if len(result1) > 0:
                        for res in result1:
                            score_lst = res[0].split(":")
                            print(f"{match['home_team']}vs{team}：比分{score_lst[0]}:{score_lst[1]}")
            if len(home_closed) > 0:
                print(f"与主队相近球队:{home_closed}")
                print("对比客队与相似队伍战绩:")
                for team in home_closed:
                    cursor.execute(
                        f"""select field_score from football_500 where home_team_full = '{team}' and visit_team_full = '{match["visit_team"]}' and match_group regexp '{match["match_type"]}'""")
                    result1 = cursor.fetchall()
                    if len(result1) > 0:
                        for res in result1:
                            score_lst = res[0].split(":")
                            print(f"{team}vs{match['visit_team']}: 比分{score_lst[0]}:{score_lst[1]}")
        except Exception as e:
            print(f"遇到错误={str(e)}, 网址{match['url']}")
    return match


def analyse_match():
    response1 = requests.get("https://live.500.com/2h1.php", headers=headers)  # 全部
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
                match_item["field_score"] = tr.xpath("./td[7]/div/a[1]/text()")[0] + ":" +  tr.xpath("./td[7]/div/a[3]/text()")[0]
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
            print(f"\033[1;32m{match_item['match_group']}, 主队:{match_item['home_team']}, 客队:{match_item['visit_team']}, 比赛时间:{match_item['match_time']}。已结束比分: {match_item['field_score']}\033[0m")
        else:
            print(f"\033[1;31m{match_item['match_group']}, 主队:{match_item['home_team']}, 客队:{match_item['visit_team']}, 比赛时间:{match_item['match_time']}。\033[0m")
        if "match_category" in match_item and match_item["match_category"] in match_map["group_inaccuracy"]:
            print("************************************不准确的联赛************************************")
            # continue
        # match_item = parse_europe(match_item, detail_url.replace("shuju", "ouzhi"))
        # time.sleep(3)
        match_item = parse_asia(match_item, detail_url.replace("shuju", "yazhi"))
        time.sleep(3)
        match_item = parse_size(match_item, detail_url.replace("shuju", "daxiao"))
        time.sleep(3)
    db.close()


def analyse_detail(detail_url):
    match_item = {"url": detail_url}
    match_item = parse_fundamentals(match_item, detail_url)
    if "field_score" in match_item:
        print(f"\033[1;32m{match_item['match_group']}, 主队:{match_item['home_team']}, 客队:{match_item['visit_team']}, 比赛时间:{match_item['match_time']}。已结束比分: {match_item['field_score']}\033[0m")
    else:
        print(f"\033[1;31m{match_item['match_group']}, 主队:{match_item['home_team']}, 客队:{match_item['visit_team']}, 比赛时间:{match_item['match_time']}。\033[0m")
    # match_item = parse_europe(match_item, detail_url.replace("shuju", "ouzhi"))
    match_item = parse_asia(match_item, detail_url.replace("shuju", "yazhi"))
    match_item = parse_size(match_item, detail_url.replace("shuju", "daxiao"))
    db.close()


if __name__ == '__main__':
    analyse_match()
    # analyse_detail("https://odds.500.com/fenxi/shuju-1059560.shtml")


# 热那亚 https://odds.500.com/fenxi/shuju-1055325.shtml
# 墨尔本骑士 https://odds.500.com/fenxi/shuju-1075552.shtml
# 切尔西多特 https://odds.500.com/fenxi/shuju-1070059.shtml
# 哥德堡盖斯 https://odds.500.com/fenxi/shuju-1084114.shtml

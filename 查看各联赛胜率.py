import pandas as pd
import re

df = pd.read_excel('结果分析.xlsx', sheet_name='让球匹配')
winRate = {}
num_rows = df.shape[0]
win_hand = 0
correct_match = 0
wrong_match = 0
for index, row in df.iterrows():
    data = row.to_dict()
    match_category = re.findall(r"\d+/?\d+(.*?)(第|分组|小组|资格|半|决|十六|八|季军|外围|秋季|排名|附加)", data["比赛类别"])
    if len(match_category) <= 0:
        continue
    match_category = match_category[0][0]
    predict = data["预测结果"]
    result = data["赛果"]
    if pd.isna(predict) or pd.isna(result):
        continue
    if match_category not in winRate:
        winRate[match_category] = {
            "正确": 0,
            "错误": 0,
        }
    if ("赢" in predict and "赢" in result) or ("输" in predict and "输" in result) or ("走" in predict and "走" in result):
        winRate[match_category]["正确"] += 1
        correct_match += 1
        win_hand += 0.5 if "半" in result else 1
    else:
        if "走" not in result:
            wrong_match += 1
            winRate[match_category]["错误"] += 1
            win_hand -= 0.5 if "半" in result else 1
sorted_dict = sorted(winRate.items(), key=lambda kv: (kv[1]["正确"] - kv[1]["错误"]), reverse=True)
# for item in sorted_dict:
#     print(item)
print(f"总测试{correct_match + wrong_match}场比赛，正确{correct_match}场，错误{wrong_match}场，预测准确率{correct_match / (correct_match + wrong_match) * 100:.2f}%，总胜{win_hand:.1f}手")
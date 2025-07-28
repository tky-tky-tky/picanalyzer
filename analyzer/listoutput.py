import re
from pathlib import Path

# 手動でカテゴリを選択
c_list = ["Animal (category)", "Sports (category)", "Machine (category)", "Landscape (category)", "Human (category)"]
Cotegory = c_list[4]  # ← ここを手動変更

# ユーザーが貼り付けるラベル（ペーストでOK）
INPUT_TEXT = """
1. vestment (0.12)
2. academic_gown (0.08)
3. bathing_cap (0.07)
4. cloak (0.07)
5. book_jacket (0.07)
6. neck_brace (0.05)
7. pickelhaube (0.05)
8. wig (0.04)
9. wool (0.02)
10. mortarboard (0.02)
11. flute (0.02)
12. mask (0.01)
13. microphone (0.01)
14. stole (0.01)
15. fur_coat (0.01)
16. shower_cap (0.01)
17. panpipe (0.01)
18. bonnet (0.01)
19. abaya (0.01)
20. bow_tie (0.01)
21. accordion (0.01)
22. trombone (0.01)
23. bath_towel (0.01)
24. bearskin (0.01)
25. velvet (0.01)
"""

# --- ラベル抽出 ---
lines = INPUT_TEXT.strip().split("\n")
labels = [line.split(". ", 1)[1].split(" (")[0].lower() for line in lines]  # 小文字化

# --- category_map.py 読み込み ---
map_path = Path(__file__).parent / "category_map.py"
with open(map_path, "r", encoding="utf-8") as f:
    content = f.read()

# --- 対象カテゴリのリスト抽出＆更新 ---
# （スペース有無を無視・柔軟にマッチ）
# --- 対象カテゴリのリスト抽出＆更新（正規表現を使わない版） ---
start_token = f'"{Cotegory}": [s.lower() for s in ['
start_index = content.find(start_token)
if start_index != -1:
    start_index += len(start_token)
    end_index = content.find("]]", start_index)
    if end_index != -1:
        matched_text = content[start_index:end_index]
        current_items = [s.strip().strip('"') for s in matched_text.split(",") if s.strip()]
        merged_items = sorted(set(current_items + labels))

        # 改行数設定（8単語ごと）
        LINE_WRAP = 8
        INDENT = " " * 8

        formatted_items = ""
        for i, item in enumerate(merged_items, 1):
            if (i - 1) % LINE_WRAP == 0:  # 改行時だけインデント
                formatted_items += INDENT
            formatted_items += f'"{item}", '
            if i % LINE_WRAP == 0:
                formatted_items += "\n"
        formatted_items = formatted_items.rstrip(", \n")

        # 内容置換（最後の ]] 行は通常のインデントに戻す）
        new_block = f'{start_token}\n{formatted_items}\n    ]]'
        content = content[:content.find(start_token)] + new_block + content[end_index+2:]

        with open(map_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ '{Cotegory}' カテゴリを更新しました。（文字列版・インデント最適化）")
    else:
        print("⚠ 終端 ]] が見つかりませんでした。")
else:
    print("⚠ 対象カテゴリが見つかりませんでした。（文字列版）")

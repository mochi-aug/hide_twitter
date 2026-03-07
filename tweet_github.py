import os
import json
import random
from datetime import datetime, date
from zoneinfo import ZoneInfo

import requests
import tweepy

import songs_add
import songs_add_birthday

BEARER_TOKEN = os.environ["BEARER_TOKEN"]
API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

DATA_FILE = "data.json"
START_DATE = date(2024, 6, 17)
JST = ZoneInfo("Asia/Tokyo")


def client_info():
    return tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )


def create_tweet(message: str):
    return client_info().create_tweet(text=message)


def discord_notify(message: str):
    if not WEBHOOK_URL:
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message}, timeout=20)
    except Exception as e:
        print(f"Discord通知失敗: {e}")


def init_data(song_count: int):
    return {
        "weight_list": [10] * song_count,
        "flag_list": [0] * song_count,
        "sad_list": [0] * song_count,
    }


def load_data(song_count: int):
    if not os.path.exists(DATA_FILE):
        return init_data(song_count)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    weight_list = data.get("weight_list", [])
    flag_list = data.get("flag_list", [])
    sad_list = data.get("sad_list", [])

    # 曲数変更時の保険
    if not (len(weight_list) == len(flag_list) == len(sad_list) == song_count):
        return init_data(song_count)

    return {
        "weight_list": weight_list,
        "flag_list": flag_list,
        "sad_list": sad_list,
    }


def save_data(weight_list, flag_list, sad_list):
    data = {
        "weight_list": weight_list,
        "flag_list": flag_list,
        "sad_list": sad_list,
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def compute_count(today_jst: date) -> int:
    return (today_jst - START_DATE).days + 1


def advance_lists(song_list, weight_list, flag_list, sad_list, chosen_song, count):
    if count % 5 == 0:
        for j in range(len(song_list)):
            if sad_list[j] >= 5 and flag_list[j] == 0:
                weight_list[j] += 2

    # flag進行
    for j in range(len(song_list)):
        if 1 <= flag_list[j] <= 9:
            flag_list[j] += 1
        elif flag_list[j] == 10:
            flag_list[j] = 0
            weight_list[j] = 10

    idx = song_list.index(chosen_song)

    # 特定曲が直近で出て weight=0 の場合の救済
    if weight_list[idx] == 0:
        weight_list[idx] = 10
        flag_list[idx] = 0

    if weight_list[idx] >= 1:
        weight_list[idx] = 0
        if flag_list[idx] == 0:
            flag_list[idx] += 1

    for j in range(len(song_list)):
        if flag_list[j] == 0:
            sad_list[j] += 1
        elif flag_list[j] == 1:
            sad_list[j] = 0
        else:
            sad_list[j] += 1

    return weight_list, flag_list, sad_list


def choose_song(today):
    month = today.month
    day = today.day

    if month == 6 and day == 4:
        song_list = songs_add_birthday.hide_list
        data = load_data(len(song_list))
        hide = random.choices(song_list, weights=data["weight_list"])[0]
        return song_list, data, hide

    song_list = songs_add.hide_list
    data = load_data(len(song_list))

    if month == 10 and day == 25:
        hide = "#一日一秀和\n「自分REST@RT」\nhttps://music.apple.com/jp/album/%E8%87%AA%E5%88%86rest-rt-m-ster-version/558745005?&i=558745631"
    elif month == 2 and day == 14:
        hide = "#一日一秀和\n「新・チョコレート事件」\nhttps://music.apple.com/jp/album/%E6%96%B0-%E3%83%81%E3%83%A7%E3%82%B3%E3%83%AC%E3%83%BC%E3%83%88%E4%BA%8B%E4%BB%B6/1401797472?&i=1401797872"
    else:
        hide = random.choices(song_list, weights=data["weight_list"])[0]

    return song_list, data, hide


def should_run(mode: str, now_jst: datetime) -> bool:
    # daily-noon workflow 用
    if mode == "daily":
        # 6/4 は hourly workflow 側に任せる
        return not (now_jst.month == 6 and now_jst.day == 4)

    # birthday hourly workflow 用
    if mode == "birthday":
        return now_jst.month == 6 and now_jst.day == 4

    return True


def main():
    now_jst = datetime.now(JST)
    today_jst = now_jst.date()
    mode = os.environ.get("RUN_MODE", "daily")

    if not should_run(mode, now_jst):
        print(f"skip: mode={mode}, jst={now_jst.isoformat()}")
        return

    count = compute_count(today_jst)

    song_list, data, hide = choose_song(today_jst)
    weight_list = data["weight_list"]
    flag_list = data["flag_list"]
    sad_list = data["sad_list"]

    weight_list, flag_list, sad_list = advance_lists(
        song_list, weight_list, flag_list, sad_list, hide, count
    )

    print(f"JST now: {now_jst}")
    print(f"count: {count}")
    print(f"tweet: {hide}")

    create_tweet(hide)
    discord_notify(f"今日の一日一秀和は\n{hide}\nでした")

    save_data(weight_list, flag_list, sad_list)


if __name__ == "__main__":
    main()

import tweepy
from pprint import pprint
import schedule
from time import sleep
import random
import datetime
import subprocess
import traceback
import requests
import csv
from bs4 import BeautifulSoup
import songs_add
import songs_add_birthday
from datetime import datetime
import json

import os

BEARER_TOKEN        = os.environ["BEARER_TOKEN"]
API_KEY             = os.environ["API_KEY"]
API_SECRET          = os.environ["API_SECRET"]
ACCESS_TOKEN        = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]
WEBHOOK_URL         = os.environ["WEBHOOK_URL"]

# クライアント関数を作成
def ClientInfo():
    client = tweepy.Client(bearer_token    = BEARER_TOKEN,
                           consumer_key    = API_KEY,
                           consumer_secret = API_SECRET,
                           access_token    = ACCESS_TOKEN,
                           access_token_secret = ACCESS_TOKEN_SECRET,
                          )
    
    return client

acc_token = 'pVCmokwOnfCAcOgx3iDmoAkaGan80exKzkwgMUIyCzg'

def save_data():
    data = {
        "weight_list": weight_list,
        "flag_list": flag_list,
        "sad_list": sad_list,
        "count": count
    }
    with open("data.json", "w") as file:
        json.dump(data, file)

def load_data():
    global weight_list, flag_list, sad_list, count
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
            weight_list = data["weight_list"]
            flag_list = data["flag_list"]
            sad_list = data["sad_list"]
            count = data["count"]
    except FileNotFoundError:
        print("No saved data found, using initial values.")

# def send_line(msg): 
#     url = 'https://notify-api.line.me/api/notify'
#     headers = {'Authorization': 'Bearer ' + acc_token}
#     payload = {'message': msg}
#     requests.post(url, headers=headers, params=payload)

# def line_notify(msg='Test', token='pVCmokwOnfCAcOgx3iDmoAkaGan80exKzkwgMUIyCzg'):
#     subprocess.run(['curl', '-H', f'Authorization: Bearer {token}', '-F', f'message={msg}', 'https://notify-api.line.me/api/notify'])

# def disco_notify():
#     message = f"start"

#     # Webhook で送信
#     data = {"content": message}
#     response = requests.post(WEBHOOK_URL, json=data)

# try:
# 	print('in try:')
# # except Exception as e:
# # 	line_notify(traceback.format_exc())
# # else:
# # 	line_notify('start')
# except Exception as e:
# 	disco_notify(traceback.format_exc())
# else:
# 	disco_notify('start')
def CreateTweet(message):
    ClientInfo().create_tweet(text=message)
    
weight_list = []
flag_list = []
sad_list =[]

#01 定期実行する関数を準備
def tweet():
    load_data()
    global count
    d_today = datetime.now()
    #10/25の処理
    if d_today.month == 10 and d_today.day == 25 :
        #5日ごとにflagが0かつ5日以上選ばれてないと重み+2
        if count%5==0:
            for j in range(len(songs_add.hide_list)):
                if sad_list[j]>=5 and flag_list[j]==0:
                    weight_list[j]+=2
        hide = "#一日一秀和\n「自分REST@RT」\nhttps://music.apple.com/jp/album/%E8%87%AA%E5%88%86rest-rt-m-ster-version/558745005?&i=558745631"
        #もしジブリが直近で選ばれていたら重み0,flagが1以上だとまずいので重みは10,flagは0だったことにしてあげる
        if weight_list[songs_add.hide_list.index(hide)] == 0 :
            weight_list[songs_add.hide_list.index(hide)] == 10
            flag_list[songs_add.hide_list.index(hide)] == 0

        #flag_listは選ばれてからの日数をカウントするので10日まではカウント,10日経ったら重みとflagをリセットしてあげる
        for j in range(len(songs_add.hide_list)):
            if 9>= flag_list[j] >= 1:
                flag_list[j] += 1
            elif flag_list[j] == 10:
                flag_list[j] = 0
                weight_list[j] = 10

        #選ばれた曲の重みを0にし、flag_listに+1してあげる            
        if weight_list[songs_add.hide_list.index(hide)] >= 1 :
            weight_list[songs_add.hide_list.index(hide)] = 0
            if flag_list[songs_add.hide_list.index(hide)] == 0:
                flag_list[songs_add.hide_list.index(hide)] +=1

                # print(flag_list[songs_add.hide_list.index(hide)])
        #選ばれていない曲(flag=0)はsad+1,選ばれた曲(flag=1)はsad==0,flagが2以上ならsad+1(基本的にsad+1、選ばれた日だけリセットが入る)
        for j in range(len(songs_add.hide_list)):
            if  flag_list[j] == 0:
                sad_list[j]+=1
            elif flag_list[j] == 1:
                sad_list[j]=0
            elif flag_list[j]>1:
                sad_list[j]+=1
        pprint((CreateTweet(hide)))
        print(weight_list)
        print(flag_list)
        print(hide)
        message = f"今日の一日一秀和は\n{hide}\nでした"

        # Webhook で送信
        data = {"content": message}
        response = requests.post(WEBHOOK_URL, json=data)

        # # 結果を表示
        # if response.status_code == 204:
        #     print("Discord に送信しました！")
        # else:
        #     print(f"エラー: {response.status_code}")
        # send_line(hide)
        # send_line(weight_list)
        # send_line(flag_list)
        # send_line(sad_list)
        # send_line(count)
        save_data()
    #誕生日の処理
    elif d_today.month == 6 and d_today.day == 4 : 
        if count%5==0:
            for j in range(len(songs_add_birthday.hide_list)):
                if sad_list[j]>=5 and flag_list[j]==0:
                    weight_list[j]+=2
        hide = random.choices(songs_add_birthday.hide_list,weights=weight_list)[0]
        print(f"重みは{weight_list[songs_add_birthday.hide_list.index(hide)]}でした")
        for j in range(len(songs_add_birthday.hide_list)):
            if 9>= flag_list[j] >= 1:
                flag_list[j]+=1
            elif flag_list[j] == 10:
                flag_list[j]=0
                weight_list[j] = 10
        if weight_list[songs_add_birthday.hide_list.index(hide)] >= 1 :
            weight_list[songs_add_birthday.hide_list.index(hide)] = 0
            if flag_list[songs_add_birthday.hide_list.index(hide)] == 0:
                flag_list[songs_add_birthday.hide_list.index(hide)] +=1
                # print(flag_list[songs_add_birthday.hide_list.index(hide)])

        for j in range(len(songs_add_birthday.hide_list)):
            if  flag_list[j] == 0:
                sad_list[j]+=1
            elif flag_list[j] == 1:
                sad_list[j]=0
            elif flag_list[j]>1:
                sad_list[j]+=1
        pprint((CreateTweet(hide)))
        print(weight_list)
        print(flag_list)
        print(sad_list)
        print(hide)
        print(f'{count}日目です')
        
        message = f"今日の一日一秀和は\n{hide}\nでした"

        # Webhook で送信
        data = {"content": message}
        response = requests.post(WEBHOOK_URL, json=data)

        # 結果を表示
        if response.status_code == 204:
            print("Discord に送信しました！")
        else:
            print(f"エラー: {response.status_code}")

        # send_line(hide)
        # send_line(weight_list)
        # send_line(flag_list)
        # send_line(sad_list)
        # send_line(count)
        save_data()
    elif d_today.month == 2 and d_today.day == 14 :
        #5日ごとにflagが0かつ5日以上選ばれてないとsad_list(選ばれていない日数をカウント)+1
        if count%5==0:
            for j in range(len(songs_add.hide_list)):
                if sad_list[j]>=5 and flag_list[j]==0:
                    weight_list[j]+=2
        hide = "#一日一秀和\n「新・チョコレート事件」\nhttps://music.apple.com/jp/album/%E6%96%B0-%E3%83%81%E3%83%A7%E3%82%B3%E3%83%AC%E3%83%BC%E3%83%88%E4%BA%8B%E4%BB%B6/1401797472?&i=1401797872"
        #もし新チョコが直近で選ばれていたら重み0,flagが1以上だとまずいので重みは10,flagは0だったことにしてあげる
        if weight_list[songs_add.hide_list.index(hide)] == 0 :
            weight_list[songs_add.hide_list.index(hide)] == 10
            flag_list[songs_add.hide_list.index(hide)] == 0

        #flag_listは選ばれてからの日数をカウントするので10日まではカウント,10日経ったら重みとflagをリセットしてあげる
        for j in range(len(songs_add.hide_list)):
            if 9>= flag_list[j] >= 1:
                flag_list[j] += 1
            elif flag_list[j] == 10:
                flag_list[j] = 0
                weight_list[j] = 10

        #選ばれた曲の重みを0にし、flag_listに+1してあげる            
        if weight_list[songs_add.hide_list.index(hide)] >= 1 :
            weight_list[songs_add.hide_list.index(hide)] = 0
            if flag_list[songs_add.hide_list.index(hide)] == 0:
                flag_list[songs_add.hide_list.index(hide)] +=1

                # print(flag_list[songs_add.hide_list.index(hide)])
        #選ばれていない曲(flag=0)はsad+1,選ばれた曲(flag=1)はsad==0,flagが2以上ならsad+1(基本的にsad+1、選ばれた日だけリセットが入る)
        for j in range(len(songs_add.hide_list)):
            if  flag_list[j] == 0:
                sad_list[j]+=1
            elif flag_list[j] == 1:
                sad_list[j]=0
            elif flag_list[j]>1:
                sad_list[j]+=1
        pprint((CreateTweet(hide)))
        print(weight_list)
        print(flag_list)
        print(hide)
        message = f"今日の一日一秀和は\n{hide}\nでした"

        # Webhook で送信
        data = {"content": message}
        response = requests.post(WEBHOOK_URL, json=data)

        # # 結果を表示
        # if response.status_code == 204:
        #     print("Discord に送信しました！")
        # else:
        #     print(f"エラー: {response.status_code}")
        # send_line(hide)
        # send_line(weight_list)
        # send_line(flag_list)
        # send_line(sad_list)
        # send_line(count)
        save_data()
    #通常日の処理
    else :
        if count%5==0:
            for j in range(len(songs_add.hide_list)):
                if sad_list[j]>=5 and flag_list[j]==0:
                    weight_list[j]+=2
        hide = random.choices(songs_add.hide_list,weights=weight_list)[0]
        print(f"重みは{weight_list[songs_add.hide_list.index(hide)]}でした")
        for j in range(len(songs_add.hide_list)):
            if 9>= flag_list[j] >= 1:
                flag_list[j]+=1
            elif flag_list[j] == 10:
                flag_list[j]=0
                weight_list[j] = 10
        if weight_list[songs_add.hide_list.index(hide)] >= 1 :
            weight_list[songs_add.hide_list.index(hide)] = 0
            if flag_list[songs_add.hide_list.index(hide)] == 0:
                flag_list[songs_add.hide_list.index(hide)] +=1
                # print(flag_list[songs_add.hide_list.index(hide)])

        for j in range(len(songs_add.hide_list)):
            if  flag_list[j] == 0:
                sad_list[j]+=1
            elif flag_list[j] == 1:
                sad_list[j]=0
            elif flag_list[j]>1:
                sad_list[j]+=1
        
        print(weight_list)
        print(flag_list)
        print(sad_list)
        print(hide)
        print(f'{count}日目です')
        message = f"今日の一日一秀和は\n{hide}\nでした"

        # Webhook で送信
        data = {"content": message}
        response = requests.post(WEBHOOK_URL, json=data)

        # 結果を表示
        if response.status_code == 204:
            print("Discord に送信しました！")
        else:
            print(f"エラー: {response.status_code}")
        # send_line(hide)
        # send_line(weight_list)
        # send_line(flag_list)
        # send_line(sad_list)
        # send_line(count)
        save_data()
        pprint((CreateTweet(hide)))
def task_check():
    now = datetime.now()
    today = now.strftime('%Y年%m月%d日')
    print(now)
    # mess = "実行中です"
    # send_line(mess)    
    message = f"実行中です"

    # Webhook で送信
    data = {"content": message}
    response = requests.post(WEBHOOK_URL, json=data)

    # 結果を表示
    if response.status_code == 204:
        print("Discord に送信しました！")
    else:
        print(f"エラー: {response.status_code}")
def count_up():
    load_data()
    global count
    count+=1
    save_data()


#初日は2024/6/17 


# 初日の日付を設定
start_date = datetime(2024, 6, 17)

# 現在(再稼働日)の日付を設定
current_date = datetime(2024, 10, 2)

# 日数を計算
count = (current_date - start_date).days + 1




#リストをリセット
# for _ in range (len(songs_add.hide_list)):
#     weight_list.append(10)
#     flag_list.append(0)
#     sad_list.append(0)
# weight_list = [30, 12, 30, 30, 17, 12, 26, 23, 30, 10, 30, 14, 13, 30, 30, 20, 25, 28, 20, 30, 30, 18, 30, 0, 30, 17, 26, 30, 30, 30, 30, 29, 0, 16, 25, 30, 30, 17, 12, 0, 0, 30, 11, 0, 4, 15, 27, 10, 14, 30, 30, 11, 30, 30, 21, 0, 15, 30, 13, 30, 25, 30, 15, 17, 30, 23, 30, 11, 13, 29, 11, 30, 30, 15, 30, 30, 30, 30, 30, 19, 22, 16, 18, 30, 18, 30, 17, 30, 25, 10, 30, 20, 13, 16, 27, 29, 30, 19, 20, 18, 4, 30, 0, 30, 23, 0, 24, 30, 21, 30, 30, 30, 26, 12, 30, 12, 30, 22, 14, 25, 30, 15, 23, 30, 19, 30, 21, 18, 30, 30, 30, 21, 21, 30, 30, 30, 27, 0, 13, 22, 11, 30, 0, 16, 30]

# flag_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 10, 6, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 4, 0, 0]

# sad_list = [107, 18, 107, 107, 45, 19, 88, 74, 107, 10, 107, 32, 23, 107, 107, 58, 85, 99, 61, 107, 107, 49, 107, 4, 107, 46, 89, 107, 107, 107, 107, 105, 8, 38, 84, 107, 107, 47, 22, 9, 5, 107, 16, 6, 28, 34, 95, 12, 30, 107, 107, 14, 107, 107, 65, 1, 35, 107, 25, 107, 87, 107, 37, 44, 107, 73, 107, 17, 27, 103, 15, 107, 107, 33, 107, 107, 107, 107, 107, 55, 71, 39, 51, 107, 50, 107, 43, 107, 83, 11, 107, 60, 24, 41, 94, 106, 107, 56, 59, 48, 29, 107, 7, 107, 77, 0, 80, 107, 63, 107, 107, 107, 92, 21, 107, 20, 107, 72, 31, 86, 107, 36, 76, 107, 54, 107, 67, 52, 107, 107, 107, 64, 66, 107, 107, 107, 93, 2, 26, 68, 13, 107, 3, 40, 107]

# schedule.every(10).seconds.do(tweet)
# schedule.every(9).seconds.do(count_up)
#  関数実行・結果出力
#  指定時刻で処理実行

d_today = datetime.now()
if d_today.month == 6 and d_today.day == 4:
    schedule.every().day.at('00:00').do(tweet)
    schedule.every().day.at('01:00').do(tweet)
    schedule.every().day.at('02:00').do(tweet)
    schedule.every().day.at('03:00').do(tweet)
    schedule.every().day.at('04:00').do(tweet)
    schedule.every().day.at('05:00').do(tweet)
    schedule.every().day.at('06:00').do(tweet)
    schedule.every().day.at('07:00').do(tweet)
    schedule.every().day.at('08:00').do(tweet)
    schedule.every().day.at('09:00').do(tweet)
    schedule.every().day.at('10:00').do(tweet)
    schedule.every().day.at('11:00').do(tweet)
    schedule.every().day.at('12:00').do(tweet)
    schedule.every().day.at('13:00').do(tweet)
    schedule.every().day.at('14:00').do(tweet)
    schedule.every().day.at('15:00').do(tweet)
    schedule.every().day.at('16:00').do(tweet)
    schedule.every().day.at('17:00').do(tweet)
    schedule.every().day.at('18:00').do(tweet)
    schedule.every().day.at('19:00').do(tweet)
    schedule.every().day.at('20:00').do(tweet)
    schedule.every().day.at('21:00').do(tweet)
    schedule.every().day.at('22:00').do(tweet)
    schedule.every().day.at('23:00').do(tweet)
    # schedule.every(10).seconds.do(tweet)
    schedule.every().day.at("11:50").do(count_up)
    schedule.every().day.at("11:30").do(task_check)
    schedule.every(6).hours.do(task_check)
else:
    schedule.every().day.at("12:00").do(tweet)
    schedule.every().day.at("00:00").do(count_up)
    schedule.every().day.at("11:30").do(task_check)
    schedule.every(6).hours.do(task_check)
# line_notify
# while True:
#     schedule.run_pending() 
# # 指定時間が来てたら実行、まだなら何もしない
#     sleep(10)                    # 待ちs
if __name__ == "__main__":
    load_data()
    tweet()
    count_up()
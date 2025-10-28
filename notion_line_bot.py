import os
import requests
from datetime import datetime, timedelta
import pytz
from config import (
    NOTION_PROPERTY_TITLE,
    NOTION_PROPERTY_DATE,
    MESSAGE_TEMPLATE,
    TIME_FORMAT,
    DATE_FORMAT,
    EVENT_FORMAT,
    TIMEZONE,
    DAYS_AHEAD,
    SEND_EMPTY_MESSAGE,
    EMPTY_MESSAGE
)

# 環境変数から取得
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_GROUP_ID = os.environ.get('LINE_GROUP_ID')

# タイムゾーン設定
JST = pytz.timezone(TIMEZONE)


def get_future_events():
    """Notionから指定日数後の予定を取得"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 指定日数後の日付範囲を計算
    now = datetime.now(JST)
    target_start = (now + timedelta(days=DAYS_AHEAD)).replace(hour=0, minute=0, second=0, microsecond=0)
    target_end = target_start + timedelta(days=1)
    
    # Notion APIでデータベースをクエリ
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    
    payload = {
        "filter": {
            "and": [
                {
                    "property": NOTION_PROPERTY_DATE,
                    "date": {
                        "on_or_after": target_start.isoformat()
                    }
                },
                {
                    "property": NOTION_PROPERTY_DATE,
                    "date": {
                        "before": target_end.isoformat()
                    }
                }
            ]
        },
        "sorts": [
            {
                "property": NOTION_PROPERTY_DATE,
                "direction": "ascending"
            }
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    response.raise_for_status()
    
    results = response.json().get('results', [])
    
    events = []
    for page in results:
        # タイトルを取得
        name_property = page['properties'].get(NOTION_PROPERTY_TITLE, {})
        if name_property.get('title'):
            name = name_property['title'][0]['plain_text']
        else:
            name = "（タイトルなし）"
        
        # 日付を取得
        date_property = page['properties'].get(NOTION_PROPERTY_DATE, {})
        if date_property.get('date'):
            date_str = date_property['date']['start']
            
            # 時刻が含まれているかチェック
            has_time = 'T' in date_str or len(date_str) > 10
            
            # ISO形式の日付をパース
            event_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            # 指定タイムゾーンに変換
            event_date_local = event_date.astimezone(JST)
            
            events.append({
                'name': name,
                'datetime': event_date_local,
                'has_time': has_time
            })
    
    return events


def format_message(events):
    """通知メッセージを整形"""
    if not events:
        if SEND_EMPTY_MESSAGE:
            return EMPTY_MESSAGE
        return None
    
    target_date = (datetime.now(JST) + timedelta(days=DAYS_AHEAD)).strftime(DATE_FORMAT)
    
    message = MESSAGE_TEMPLATE.format(date=target_date)
    
    for event in events:
        if event['has_time']:
            # 時刻が設定されている場合
            time_str = event['datetime'].strftime(TIME_FORMAT)
            message += EVENT_FORMAT.format(time=time_str, name=event['name'])
        else:
            # 時刻が設定されていない場合（終日イベント）
            message += f"📌 {event['name']}\n"
    
    return message


def send_line_message(message):
    """LINEグループにメッセージを送信"""
    if not message:
        print("送信する予定がありません")
        return
    
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    
    payload = {
        "to": LINE_GROUP_ID,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    print("メッセージ送信成功！")


def main():
    """メイン処理"""
    try:
        days_text = "明日" if DAYS_AHEAD == 1 else f"{DAYS_AHEAD}日後"
        print(f"{days_text}の予定を取得中...")
        events = get_future_events()
        
        print(f"{len(events)}件の予定が見つかりました")
        
        message = format_message(events)
        
        if message:
            print("LINEに送信中...")
            send_line_message(message)
        else:
            print(f"{days_text}の予定はありません")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    main()

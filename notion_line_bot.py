import os
import requests
from datetime import datetime, timedelta
import pytz

# 環境変数から取得
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_GROUP_ID = os.environ.get('LINE_GROUP_ID')

# 日本時間のタイムゾーン
JST = pytz.timezone('Asia/Tokyo')


def get_tomorrow_events():
    """Notionから翌日の予定を取得"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 翌日の日付範囲を計算（日本時間）
    now = datetime.now(JST)
    tomorrow_start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_end = tomorrow_start + timedelta(days=1)
    
    # Notion APIでデータベースをクエリ
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    
    payload = {
        "filter": {
            "and": [
                {
                    "property": "日付",
                    "date": {
                        "on_or_after": tomorrow_start.isoformat()
                    }
                },
                {
                    "property": "日付",
                    "date": {
                        "before": tomorrow_end.isoformat()
                    }
                }
            ]
        },
        "sorts": [
            {
                "property": "日付",
                "direction": "ascending"
            }
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    results = response.json().get('results', [])
    
    events = []
    for page in results:
        # 名前を取得
        name_property = page['properties'].get('名前', {})
        if name_property.get('title'):
            name = name_property['title'][0]['plain_text']
        else:
            name = "（タイトルなし）"
        
        # 日付を取得
        date_property = page['properties'].get('日付', {})
        if date_property.get('date'):
            date_str = date_property['date']['start']
            # ISO形式の日付をパース
            event_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            # 日本時間に変換
            event_date_jst = event_date.astimezone(JST)
            
            events.append({
                'name': name,
                'datetime': event_date_jst
            })
    
    return events


def format_message(events):
    """通知メッセージを整形"""
    if not events:
        return None
    
    tomorrow = (datetime.now(JST) + timedelta(days=1)).strftime('%m月%d日')
    
    message = f"📅 明日（{tomorrow}）の予定\n\n"
    
    for event in events:
        time_str = event['datetime'].strftime('%H:%M')
        message += f"🕐 {time_str} - {event['name']}\n"
    
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
        print("翌日の予定を取得中...")
        events = get_tomorrow_events()
        
        print(f"{len(events)}件の予定が見つかりました")
        
        message = format_message(events)
        
        if message:
            print("LINEに送信中...")
            send_line_message(message)
        else:
            print("翌日の予定はありません")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    main()

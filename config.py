"""
設定ファイル - カスタマイズ可能な変数
"""

# Notionデータベースのプロパティ名
NOTION_PROPERTY_TITLE = "名前"  # タイトルを取得するプロパティ名
NOTION_PROPERTY_DATE = "日付"   # 日付を取得するプロパティ名

# 通知メッセージのカスタマイズ
MESSAGE_TEMPLATE = "📅 2日後（{date}）の予定\n\n"  # メッセージのヘッダー
TIME_FORMAT = "%H:%M"  # 時刻のフォーマット（例: 14:30）
DATE_FORMAT = "%m月%d日"  # 日付のフォーマット（例: 10月28日）
EVENT_FORMAT = "🕐 {time} - {name}\n"  # 各予定のフォーマット

# タイムゾーン
TIMEZONE = "Asia/Tokyo"  # タイムゾーン（日本時間）

# 通知する日数（何日後の予定を通知するか）
DAYS_AHEAD = 2  # 1 = 明日、2 = 明後日

# 予定がない場合の動作
SEND_EMPTY_MESSAGE = False  # True にすると予定がなくても通知する
EMPTY_MESSAGE = "2日後の予定はありません。"  # 予定がない場合のメッセージ

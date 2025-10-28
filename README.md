# Notion to LINE Bot

NotionデータベースからスケジュールをLINEグループに自動通知するボットです。GitHub Actionsを使って毎日定時に実行されます。

## 機能

- Notionデータベースから翌日（または指定日数後）の予定を取得
- 毎日決まった時刻にLINEグループへ通知
- カスタマイズ可能な設定ファイル

## セットアップ

### 1. Notion統合の作成

1. [Notion Integrations](https://www.notion.so/my-integrations) にアクセス
2. 「New integration」をクリック
3. 名前を入力して「Submit」
4. **Internal Integration Token** をコピー（後で使用）

### 2. Notionデータベースの設定

1. Notionでスケジュール管理用のデータベースを作成
2. 以下のプロパティを確認：
   - **名前** (Title) - イベントのタイトル
   - **日付** (Date) - イベントの日時
3. データベースページの右上「...」→「接続」→作成した統合を選択
4. データベースIDを取得：
   - URLの `https://notion.so/xxxx?v=yyyy` の `xxxx` 部分

### 3. LINE Messaging APIの設定

1. [LINE Developers Console](https://developers.line.biz/console/) にアクセス
2. 新しいプロバイダーとMessaging APIチャネルを作成
3. **Channel access token** を発行
4. ボットをLINEグループに追加
5. グループIDを取得（[こちらの方法](https://developers.line.biz/ja/docs/messaging-api/getting-started/)を参照）

### 4. GitHub Secretsの設定

このリポジトリの Settings → Secrets and variables → Actions → New repository secret から以下を追加：

| Secret名 | 説明 |
|---------|------|
| `NOTION_TOKEN` | NotionのIntegration Token |
| `NOTION_DATABASE_ID` | NotionデータベースのID |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINEのChannel Access Token |
| `LINE_GROUP_ID` | 通知先のLINEグループID |

### 5. 通知時刻の設定

`.github/workflows/daily_notification.yml` の `cron` を編集：
```yaml
schedule:
  # 毎日20:30 JST (11:30 UTC) に実行
  - cron: '30 11 * * *'
```

**重要**: GitHub Actionsのcronは **UTC時刻** で指定します。
- JST 21:00 = UTC 12:00 → `'0 12 * * *'`
- JST 20:30 = UTC 11:30 → `'30 11 * * *'`

※ 実際の実行には数分〜数十分の遅延が発生する可能性があります

## カスタマイズ

`config.py` で以下の設定を変更できます：

### Notionプロパティ名
```python
NOTION_PROPERTY_TITLE = "名前"  # タイトルのプロパティ名
NOTION_PROPERTY_DATE = "日付"   # 日付のプロパティ名
```

Notionのデータベースプロパティ名が異なる場合は変更してください。

### メッセージフォーマット
```python
MESSAGE_TEMPLATE = "📅 明日（{date}）の予定\n\n"
TIME_FORMAT = "%H:%M"  # 14:30
DATE_FORMAT = "%m月%d日"  # 10月28日
EVENT_FORMAT = "🕐 {time} - {name}\n"
```

### 通知する日数
```python
DAYS_AHEAD = 1  # 1 = 明日、2 = 明後日
```

### 予定がない場合の動作
```python
SEND_EMPTY_MESSAGE = False  # True にすると予定がなくても通知
EMPTY_MESSAGE = "明日の予定はありません。"
```

## 手動実行

GitHub Actions の画面から手動で実行できます：

1. [Actions タブ](../../actions) を開く
2. 「Daily Notion to LINE Notification」を選択
3. 「Run workflow」をクリック

## トラブルシューティング

### 通知が来ない

1. [Actions](../../actions) で実行履歴とログを確認
2. GitHub Secretsが正しく設定されているか確認
3. Notionデータベースに統合が接続されているか確認
4. LINE botがグループに招待されているか確認

### プロパティが見つからないエラー

`config.py` の `NOTION_PROPERTY_TITLE` と `NOTION_PROPERTY_DATE` をNotionデータベースのプロパティ名と一致させてください。

### 時刻がずれる

GitHub Actionsのスケジュール実行は正確ではありません。余裕を持って30分程度早めに設定することをおすすめします。

## ライセンス

MIT License

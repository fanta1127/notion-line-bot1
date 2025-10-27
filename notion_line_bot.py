"""
LINEグループIDを取得するための簡易スクリプト（Webhook不要版）

BOTが参加しているグループの一覧を取得します。

使い方:
1. 環境変数を設定:
   export LINE_CHANNEL_ACCESS_TOKEN='your_token'
2. python get_group_id_simple.py を実行
"""

import os
import requests

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

if not LINE_CHANNEL_ACCESS_TOKEN:
    print("エラー: LINE_CHANNEL_ACCESS_TOKENが設定されていません")
    print("\n以下のコマンドを実行してください:")
    print("export LINE_CHANNEL_ACCESS_TOKEN='your_token_here'")
    exit(1)

def get_bot_info():
    """BOTの情報を取得"""
    url = "https://api.line.me/v2/bot/info"
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        info = response.json()
        print(f"\nBOT名: {info.get('displayName', 'N/A')}")
        print(f"BOT ID: {info.get('userId', 'N/A')}")
        return True
    else:
        print(f"エラー: BOT情報の取得に失敗しました (Status: {response.status_code})")
        print(f"レスポンス: {response.text}")
        return False

def main():
    print("="*60)
    print("LINE グループID取得ツール")
    print("="*60)
    
    # BOT情報の確認
    if not get_bot_info():
        return
    
    print("\n" + "="*60)
    print("【重要】グループIDの取得方法")
    print("="*60)
    print("""
残念ながら、LINE Messaging APIでは直接グループ一覧を
取得する方法がありません。

以下のいずれかの方法でグループIDを取得してください:

【方法1】Webhookを使用する（推奨）
---------------------------------------
1. LINE Developersコンソールを開く
2. Webhook設定を有効化（一時的でOK）
3. ngrokなどでローカルサーバーを公開:
   - ngrok http 5000
   - 表示されたURLをWebhook URLに設定
4. get_group_id.py を実行
5. グループでBOTに何かメッセージを送信
6. コンソールにグループIDが表示される

【方法2】LINE Official Account Managerから確認
---------------------------------------
1. https://manager.line.biz/ にアクセス
2. 該当のアカウントを選択
3. 「メッセージ」→「応答メッセージ」などから
   グループでテストメッセージを送信
4. Webhookログでgroup_idを確認

【方法3】テストメッセージを送信してエラーから取得
---------------------------------------
適当なIDで送信を試みて、エラーメッセージから
正しいIDのフォーマットを確認する方法です。
（あまり推奨しません）
"""
    
    print("\n" + "="*60)
    print("次のステップ:")
    print("="*60)
    print("1. BOTをグループに追加")
    print("2. 上記の方法でグループIDを取得")
    print("3. GitHubのSecretsにLINE_GROUP_IDとして設定")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

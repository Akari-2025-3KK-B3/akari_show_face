# akari_show_face
Akariのカメラに顔を写し続けるゲームです

## 概要
- Akariのディスプレイ直下の3ボタンを用いて難易度を設定する。
- 自分の顔をAkariのカメラに写し続ける
- 顔が映らなくなるまで繰り返す

## セットアップ手順
1.ローカルにクローン
```bash
cd~
```

```bash
git clone https://github.com/Akari-2025-3KK-3B/akari_show_face
```

```bash
cd akari_show_face
```

2.仮想環境の作成(初回だけ)
```bash
python3 -m venv venv
```

```bash
. venv/bin/activate
```

```bash
pip install -r requirements.txt
```

## 起動方法
1.仮想環境の有効化
```bash
. venv/bin/activate
```

2.開始する
```bash
python3 main.py
```

3.終了する

画像がなくなるまで任意のキーを押す

## 使い方
1. アプリ起動後、難易度設定要求画面が出現するため、Akariでスプレイ直下のボタンを用いて難易度を選択する．

2. カウントダウンが終了したら、Akariの首がランダムに動くので、顔をAkariに映し続ける．

3. 顔が映らなくなったら終了．

4. ディスプレイに素敵な笑顔が表示されるので、みんなで眺めて楽しもう．


## その他

このアプリケーションは愛知工業大学 情報科学部 知的制御研究室により作成されたものです.
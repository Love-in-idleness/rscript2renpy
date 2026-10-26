# 環境構築と初回ビルド

[中文](SETUP.zh.md) | [English](SETUP.en.md) | [Русский](SETUP.ru.md) | [日本語](SETUP.ja.md)

[プロジェクトの説明](../README.ja.md)

対応済み作品のビルド手順です。未対応作品は[新ゲーム移植ガイド](NEW_GAME_PORTING.ja.md)へ。`/path/to/...` は自身のパスに置き換えます。

## 1. 依存関係

| 依存 | 用途 |
| --- | --- |
| Python 3（3.11+ 推奨） | 生成スクリプト |
| Pillow | 画像寸法、アプリアイコン |
| Ren'Py 8 SDK | 実行、lint、パッケージ |
| [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool) | 展開、スクリプト・画像・音声変換 |
| Git | ソース取得 |

完全な Ren'Py SDK を展開します。Linux は `renpy.sh`、Windows は `renpy.exe`。対応済み作品の通常ビルドに Wine、RsComp.dll、Windows VM は不要です。

## 2. ソースを取得する

Linux / macOS:

```bash
git clone https://github.com/Love-in-idleness/rscript2renpy.git
cd rscript2renpy
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Pillow
```

Windows はルートの PowerShell で:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install Pillow
```

Windows の例では `python3` を `.\.venv\Scripts\python.exe` に置き換えられます。Linux は有効化した環境の `python` / `python3` を使います。

## 3. 作業コピーを準備する

原本、変換コピー、出力工程を別々に保存します。

```text
work/
├── originals/Game/       原ゲーム
├── prepared/Game/        変換コピー
├── prepared/Game.zh/     中国語パッチの変換コピー
└── projects/Game/        Ren'Py 出力
```

原本を変換せず、出力と入力を包含・重複させません。各 README の版条件も確認してください。霞外籠逗留記は「ハチポチ特典」が必要です。

日本語リソースは通常 CP932:

```bash
/path/to/liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/prepared/Game
```

GBK の中国語パッチは別のコピーで:

```bash
/path/to/liarsofttool -R --unpack-only --gsc-to-tsc -e gbk /path/to/prepared/Game.zh
```

変換後は `scr/*.tsc`、利用可能な画像・音声を用意します。`.meta.xml` を保持し、普通の PCM WAV と元 MPG はそのまま使えます。スクリプト再出力も LiarsoftTool で行い、変更済み TSC は先にバックアップします。

## 4. 工程を生成する

ルートから Forest を生成する例:

```bash
python3 forest/build_forest_rscript.py /path/to/prepared/Forest /path/to/projects/Forest \
    --language jp --language zh=/path/to/prepared/Forest.zh
```

パッチがなければ `--language zh=...` は省略します。`jp` は基準言語名、`zh=ディレクトリ` は切替可能な言語パッケージです。タグは文字コードを変換しません。作品別の規則は[ゲーム別ガイド](../README.ja.md#ゲーム別ガイド)を参照してください。

初回は新規出力先を使います。再生成前に工程内の手動変更を保存し、必要に応じて `--force` を指定します。

## 5. 実行と確認

```bash
/path/to/renpy-sdk/renpy.sh /path/to/projects/Forest lint
/path/to/renpy-sdk/renpy.sh /path/to/projects/Forest
```

Windows は Ren'Py ランチャーで工程を選択して検査・実行できます。Android は SDK の Android 機能を使い、RAPT の設定も必要です。

問題時は全出力、ゲーム版、コマンド、場面を保存してください。lint 後も画面、音、選択肢、セーブ・ロードを確認します。

## 補足

ゲーム本体やビルド済みゲームは配布しません。配布前に[第三者資産](../THIRD_PARTY_NOTICES.ja.md)を確認し、セーブや署名鍵を含めないでください。

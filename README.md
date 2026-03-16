# Score Processing Tool

Google DriveからMIDIファイルとQRコードPNGをダウンロードし、楽譜PDFの生成・QRコード埋め込み・印刷管理を自動化するツールです。

## Features

1. **Google Drive連携**: Google Drive APIを使用してMIDIファイルとQRコードPNGを自動ダウンロード
2. **MIDI→PDF変換**: `music21`ライブラリを使用してMIDIファイルを楽譜PDFに変換
3. **メタデータ編集**: XMLパーサーによるMusicXMLの曲名・作曲者名・テンポ位置の編集
4. **QRコード埋め込み**: 楽譜画像にQRコードを自動合成
5. **印刷管理**: 処理済みファイルのディレクトリ管理と印刷準備

## Prerequisites

### Software
- **Python 3.8+**
- **MuseScore v3.6.2**: MusicXML/PDF変換に必要。[ダウンロード](https://github.com/musescore/MuseScore/releases/tag/v3.6.2)

### Libraries

```bash
pip install -r requirements.txt
```

主要な依存ライブラリ:
- `music21` - 音楽記譜処理
- `Pillow` - 画像処理
- `pdf2image` - PDF→画像変換
- `google-api-python-client` / `google-auth` - Google Drive API

## Setup

1. **Google API認証情報の配置**:
   ```bash
   mkdir credentials
   # サービスアカウントのcredentials.jsonを配置
   cp /path/to/credentials.json credentials/
   ```

2. **設定ファイルの編集** (`config.json`):
   ```json
   {
       "data_dir": "./data",
       "output_dir": "./output",
       "credentials_path": "credentials/credentials.json",
       "song_name_pattern": "(.+?)_output_",
       "composer_name": "東京都市大学 大谷研究室",
       "polling_interval_sec": 10,
       "drive_page_size": 10
   }
   ```

   | 項目 | 説明 |
   |------|------|
   | `data_dir` | ダウンロードファイルの保存先 |
   | `output_dir` | 処理済みファイルの出力先 |
   | `credentials_path` | Google API認証ファイルのパス |
   | `song_name_pattern` | ファイル名から曲名を抽出する正規表現 |
   | `composer_name` | 楽譜に表示する作曲者名 |
   | `polling_interval_sec` | Google Driveのポーリング間隔（秒） |
   | `drive_page_size` | Google Drive APIのページサイズ |

## Usage

```bash
python main.py
```

起動後、`config.json`で指定した間隔でGoogle Driveを監視し、新しいファイルを自動処理します。`Ctrl+C`で安全に停止できます。

### Processing Pipeline

```
Google Drive → download() → [.mid + .png]
                                  ↓
                            make_score() → [.musicxml + .pdf]
                                  ↓
                            pdf_to_jpg() → [.jpg]
                                  ↓
                            embed_qr()   → [.jpg with QR]
                                  ↓
                            print_score() → ./output/printed/
```

## Directory Structure

```
.
├── main.py              # メインスクリプト
├── config.json          # 設定ファイル
├── requirements.txt     # 依存パッケージ
├── tests/               # テストコード
│   ├── conftest.py      # テスト用モック設定
│   ├── test_download.py
│   ├── test_make_score.py
│   ├── test_pdf_to_jpg.py
│   ├── test_embed_qr.py
│   ├── test_print_score.py
│   ├── test_get_extensions.py
│   └── test_main.py
├── credentials/         # Google API認証情報 (git管理外)
├── data/                # ダウンロードデータ (git管理外)
└── output/              # 出力ファイル (git管理外)
    ├── unprint/         # 印刷待ち
    └── printed/         # 印刷済み
```

## Functions

| 関数 | 説明 |
|------|------|
| `download()` | Google Driveからmid/pngファイルをダウンロード |
| `make_score(path)` | MIDIファイルをパースし、MusicXMLメタデータを編集してPDFを生成 |
| `pdf_to_jpg(path)` | PDFをJPG画像に変換 |
| `embed_qr(path)` | 楽譜画像にQRコードPNGを埋め込み |
| `print_score(path)` | 印刷処理とファイル移動 |
| `get_extensions(path)` | ディレクトリ内のファイル拡張子セットを取得 |
| `main()` | パイプライン全体を実行 |

## Testing

```bash
python -m unittest discover -s tests -v
```

外部依存パッケージ（music21, Pillow等）がインストールされていない環境でも、モックにより全テストが実行可能です。

## Note

Google Drive APIの利用にはサービスアカウントの認証情報が必要です。認証情報は`credentials/`ディレクトリに配置し、Gitリポジトリにはコミットしないでください。

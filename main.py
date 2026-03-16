# -*- coding: utf-8 -*-
import io
import os
import re
import glob
import time
import shutil
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

import music21 as m2
from PIL import Image
from pathlib import Path
from pdf2image import convert_from_path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

data_dir = './data' # Directory to save files
output_dir = './output' # Directory to save output files
pattern = r"(.+?)_output_" # Pattern to get song name

def download():
    '''
    Download files from Google Drive
    '''

    # Check credentials
    if not os.path.exists('credentials'):
        print('Please put credentials.json in credentials directory.')
        exit(1)

    # Check data directory
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Set Google Drive API
    SCOPES = ['https://www.googleapis.com/auth/drive']
    try:
        credentials = service_account.Credentials.from_service_account_file(
            'credentials/credentials.json', scopes=SCOPES
        )
        drive_service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print('Failed to authenticate with Google Drive: {0}'.format(e))
        return

    # Get file list
    try:
        results = (
            drive_service.files()
            .list(pageSize=10, fields='nextPageToken, files(id, name)')
            .execute()
        )
        items = results.get('files', [])
    except Exception as e:
        print('Failed to get file list from Google Drive: {0}'.format(e))
        return

    # Download files
    for item in items:
        # Create directory
        file_base, ext = os.path.splitext(item['name'])

        # Create data directory
        fdir = os.path.join(data_dir, file_base)
        if ext != '':
            os.makedirs(fdir, exist_ok=True)

        # Download files
        fname = os.path.join(fdir, item['name'])
        if not os.path.exists(fname):
            if '.mid' in item['name'] or '.png' in item['name']:
                try:
                    request = drive_service.files().get_media(fileId=item['id'])
                    with io.FileIO(fname, 'wb') as fh:
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print('Download {0} {1}%'.format(item['name'], int(status.progress() * 100)))
                except Exception as e:
                    print('Failed to download {0}: {1}'.format(item['name'], e))
                    if os.path.exists(fname):
                        os.remove(fname)

def make_score(path):
    mid_files = glob.glob(os.path.join(path, '*.mid'))
    if not mid_files:
        print('No MIDI file found in {0}'.format(path))
        return
    mid_path = mid_files[0]

    try:
        mid = m2.converter.parse(mid_path)
    except Exception as e:
        print('Failed to parse MIDI file {0}: {1}'.format(mid_path, e))
        return

    # Create musicxml
    fn = mid.write("musicxml.pdf", mid_path.replace(".mid", ".pdf"))

    # Get song name
    matches = re.findall(pattern, mid_path.split('/')[-1])
    if not matches:
        print('Failed to extract song name from {0}'.format(mid_path))
        return
    song_name = matches[0]

    # Edit musicxml
    musicxml_path = mid_path.replace(".mid", ".musicxml")
    with open(musicxml_path, encoding="utf-8") as f:
        data_lines = f.read()

    # Change song name
    data_lines = data_lines.replace("Music21 Fragment", str(song_name))
    # Change composer name
    data_lines = data_lines.replace("Music21", "東京都市大学 大谷研究室")
    # Change tempo position
    data_lines = data_lines.replace("<direction>", '<direction placement="above">')

    # Save musicxml
    with open(musicxml_path, mode="w", encoding="utf-8") as f:
        f.write(data_lines)

    # Save score from musicxml
    try:
        s = m2.converter.parse(musicxml_path)
        fn = s.write("musicxml.pdf", mid_path.replace(".mid", ".pdf"))
    except Exception as e:
        print('Failed to create score PDF from {0}: {1}'.format(musicxml_path, e))

def pdf_to_jpg(path):
    '''
    Convert pdf to jpg
    '''
    pdf_files = glob.glob(os.path.join(path, '*.pdf'))
    if not pdf_files:
        print('No PDF file found in {0}'.format(path))
        return
    pdf_path = pdf_files[0]
    jpg_path = pdf_path.replace('.pdf', '.jpg')
    try:
        image = convert_from_path(str(pdf_path))[0]
        image.save(jpg_path, 'JPEG')
    except Exception as e:
        print('Failed to convert PDF to JPG {0}: {1}'.format(pdf_path, e))

def embed_qr(path):
    '''
    Embed QR code to jpg
    '''
    # Get image path
    score_files = glob.glob(os.path.join(path, '*.jpg'))
    qr_files = glob.glob(os.path.join(path, '*.png'))
    if not score_files:
        print('No JPG file found in {0}'.format(path))
        return
    if not qr_files:
        print('No QR code PNG file found in {0}'.format(path))
        return
    score_path = score_files[0]
    qr_path = qr_files[0]

    try:
        # Embed QR code to score
        score = Image.open(score_path)
        qr = Image.open(qr_path)

        # Embed QR code
        score.paste(qr, (score.width - qr.width, score.height - qr.height))

        # Get embed path
        unprint_dir = os.path.join(output_dir, 'unprint')
        embed_path = os.path.join(unprint_dir, os.path.basename(score_path))

        # Create directory
        os.makedirs(unprint_dir, exist_ok=True)

        # Save image
        score.save(embed_path)
    except Exception as e:
        print('Failed to embed QR code in {0}: {1}'.format(path, e))

def print_score(path):
    '''
    Print score
    '''
    if not os.path.exists(path):
        print('File not found: {0}'.format(path))
        return

    # os.system('lp ' + path)
    print(path)

    # Move file to printed directory
    try:
        printed_path = os.path.join(output_dir, 'printed')
        os.makedirs(printed_path, exist_ok=True)
        shutil.move(path, printed_path)
    except Exception as e:
        print('Failed to move file {0}: {1}'.format(path, e))

def main():
    # Download files
    download()

    # Get file list
    path_list = glob.glob(os.path.join(data_dir, '*'))
    for path in path_list:
        file_len = len(glob.glob(os.path.join(path, '*')))
        if file_len == 2:
            make_score(path)

    # Convert pdf to jpg snd embed QR code
    for path in path_list:
        file_len = len(glob.glob(os.path.join(path, '*')))
        if file_len == 4:
            pdf_to_jpg(path)
            embed_qr(path)

    # Print files
    unprint_path_list = glob.glob(os.path.join(output_dir, 'unprint', '*'))
    for path in unprint_path_list:
        print_score(path)

if __name__ == '__main__':
    # Run main function per 10 seconds
    while True:
        main()
        time.sleep(10)


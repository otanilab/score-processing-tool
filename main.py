# -*- coding: utf-8 -*-
import io
import os
import re
import glob
import json
import time
import signal
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

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
with open(config_path, encoding='utf-8') as f:
    config = json.load(f)

data_dir = config['data_dir']
output_dir = config['output_dir']
credentials_path = config['credentials_path']
pattern = config['song_name_pattern']
composer_name = config['composer_name']
polling_interval_sec = config['polling_interval_sec']
drive_page_size = config['drive_page_size']

def download():
    '''
    Download files from Google Drive
    '''

    # Check credentials
    if not os.path.exists(credentials_path):
        logger.error('Credentials file not found: %s', credentials_path)
        exit(1)

    # Check data directory
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Set Google Drive API
    SCOPES = ['https://www.googleapis.com/auth/drive']
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        drive_service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        logger.error('Failed to authenticate with Google Drive: %s', e)
        return

    # Get file list
    try:
        results = (
            drive_service.files()
            .list(pageSize=drive_page_size, fields='nextPageToken, files(id, name)')
            .execute()
        )
        items = results.get('files', [])
    except Exception as e:
        logger.error('Failed to get file list from Google Drive: %s', e)
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
                            logger.info('Download %s %d%%', item['name'], int(status.progress() * 100))
                except Exception as e:
                    logger.error('Failed to download %s: %s', item['name'], e)
                    if os.path.exists(fname):
                        os.remove(fname)

def make_score(path):
    mid_files = glob.glob(os.path.join(path, '*.mid'))
    if not mid_files:
        logger.warning('No MIDI file found in %s', path)
        return
    mid_path = mid_files[0]

    try:
        mid = m2.converter.parse(mid_path)
    except Exception as e:
        logger.error('Failed to parse MIDI file %s: %s', mid_path, e)
        return

    # Create musicxml
    fn = mid.write("musicxml.pdf", mid_path.replace(".mid", ".pdf"))

    # Get song name
    matches = re.findall(pattern, mid_path.split('/')[-1])
    if not matches:
        logger.warning('Failed to extract song name from %s', mid_path)
        return
    song_name = matches[0]

    # Edit musicxml
    musicxml_path = mid_path.replace(".mid", ".musicxml")
    with open(musicxml_path, encoding="utf-8") as f:
        data_lines = f.read()

    # Change song name
    data_lines = data_lines.replace("Music21 Fragment", str(song_name))
    # Change composer name
    data_lines = data_lines.replace("Music21", composer_name)
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
        logger.error('Failed to create score PDF from %s: %s', musicxml_path, e)

def pdf_to_jpg(path):
    '''
    Convert pdf to jpg
    '''
    pdf_files = glob.glob(os.path.join(path, '*.pdf'))
    if not pdf_files:
        logger.warning('No PDF file found in %s', path)
        return
    pdf_path = pdf_files[0]
    jpg_path = pdf_path.replace('.pdf', '.jpg')
    try:
        image = convert_from_path(str(pdf_path))[0]
        image.save(jpg_path, 'JPEG')
    except Exception as e:
        logger.error('Failed to convert PDF to JPG %s: %s', pdf_path, e)

def embed_qr(path):
    '''
    Embed QR code to jpg
    '''
    # Get image path
    score_files = glob.glob(os.path.join(path, '*.jpg'))
    qr_files = glob.glob(os.path.join(path, '*.png'))
    if not score_files:
        logger.warning('No JPG file found in %s', path)
        return
    if not qr_files:
        logger.warning('No QR code PNG file found in %s', path)
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
        logger.error('Failed to embed QR code in %s: %s', path, e)

def print_score(path):
    '''
    Print score
    '''
    if not os.path.exists(path):
        logger.warning('File not found: %s', path)
        return

    # os.system('lp ' + path)
    logger.info('Printing: %s', path)

    # Move file to printed directory
    try:
        printed_path = os.path.join(output_dir, 'printed')
        os.makedirs(printed_path, exist_ok=True)
        shutil.move(path, printed_path)
    except Exception as e:
        logger.error('Failed to move file %s: %s', path, e)

def get_extensions(path):
    '''Get set of file extensions in a directory'''
    files = glob.glob(os.path.join(path, '*'))
    return {os.path.splitext(f)[1].lower() for f in files}

def main():
    # Download files
    download()

    # Get file list
    path_list = glob.glob(os.path.join(data_dir, '*'))
    for path in path_list:
        if not os.path.isdir(path):
            continue
        exts = get_extensions(path)

        # Stage 1: MIDI + PNG downloaded, but no PDF yet → create score
        has_midi = '.mid' in exts
        has_png = '.png' in exts
        has_pdf = '.pdf' in exts
        has_jpg = '.jpg' in exts

        if has_midi and has_png and not has_pdf:
            make_score(path)

        # Stage 2: PDF exists but no JPG yet → convert and embed QR
        exts = get_extensions(path)
        has_pdf = '.pdf' in exts
        has_jpg = '.jpg' in exts
        if has_pdf and has_png and not has_jpg:
            pdf_to_jpg(path)
            embed_qr(path)

    # Print files
    unprint_path_list = glob.glob(os.path.join(output_dir, 'unprint', '*'))
    for path in unprint_path_list:
        print_score(path)

if __name__ == '__main__':
    running = True

    def shutdown_handler(signum, frame):
        global running
        logger.info('Shutdown signal received (signal=%s). Finishing current cycle...', signum)
        running = False

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info('Score processing tool started. Press Ctrl+C to stop.')
    while running:
        try:
            main()
        except Exception as e:
            logger.error('Unexpected error in main loop: %s', e)
        if running:
            time.sleep(polling_interval_sec)
    logger.info('Score processing tool stopped.')


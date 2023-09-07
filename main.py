# -*- coding: utf-8 -*-
import io
import os
import re
import glob
import time
import shutil

import music21 as m2
from PIL import Image
from pathlib import Path
from httplib2 import Http
from apiclient.discovery import build
from pdf2image import convert_from_path
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials

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
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials/credentials.json', SCOPES)
    http_auth = credentials.authorize(Http())
    drive_service = build('drive', 'v3', http=http_auth)

    # Get file list
    results = (
        drive_service.files()
        .list(pageSize=10, fields='nextPageToken, files(id, name)')
        .execute()
    )
    items = results.get('files', [])

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
                request = drive_service.files().get_media(fileId=item['id'])
                fh = io.FileIO(fname, 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print('Download {0} {1}%'.format(item['name'], int(status.progress() * 100)))

def make_score(path):
    mid_path = glob.glob(os.path.join(path, '*.mid'))[0]

    mid = m2.converter.parse(mid_path)

    # Create musicxml
    fn = mid.write("musicxml.pdf", mid_path.replace(".mid", ".pdf"))

    # Get song name
    song_name = re.findall(pattern, mid_path.split('/')[-1])[0]

    # Edit musicxml
    with open(mid_path.replace(".mid", ".musicxml"), encoding="utf-8") as f:
        data_lines = f.read()

    # Change song name
    data_lines = data_lines.replace("Music21 Fragment", str(song_name))
    # Change composer name
    data_lines = data_lines.replace("Music21", "東京都市大学 大谷研究室")
    # Change tempo position
    data_lines = data_lines.replace("<direction>", '<direction placement="above">')

    # Save musicxml
    with open(
        mid_path.replace(".mid", ".musicxml"),
        mode="w",
        encoding="utf-8",
    ) as f:
        f.write(data_lines)

    # Save score from musicxml
    s = m2.converter.parse(mid_path.replace(".mid", ".musicxml"))
    fn = s.write("musicxml.pdf", mid_path.replace(".mid", ".pdf"))

def pdf_to_jpg(path):
    '''
    Convert pdf to jpg
    '''
    pdf_path = glob.glob(os.path.join(path, '*.pdf'))[0]
    jpg_path = pdf_path.replace('.pdf', '.jpg')
    image = convert_from_path(str(pdf_path))[0]
    image.save(jpg_path, 'JPEG')

def embed_qr(path):
    '''
    Embed QR code to jpg
    '''
    # Get image path
    score_path = glob.glob(os.path.join(path, '*.jpg'))[0]
    qr_path = glob.glob(os.path.join(path, '*.png'))[0]

    # Embed QR code to score
    score = Image.open(score_path)
    qr = Image.open(qr_path)

    # Embed QR code
    score.paste(qr, (score.width - qr.width, score.height - qr.height))

    # Get embed path
    embed_path = output_dir + '/unprint/' + score_path.split('/')[-1]

    # Create directory
    if not os.path.exists(output_dir + '/unprint/'):
        os.makedirs(output_dir + '/unprint/')

    # Save image
    score.save(embed_path)

def print_score(path):
    '''
    Print score
    '''
    # os.system('lp ' + path)
    print(path)

    # Move file to printed directory
    printed_path = os.path.join(output_dir, 'printed')
    if not os.path.exists(printed_path):
        os.makedirs(printed_path)
    shutil.move(path, printed_path)

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


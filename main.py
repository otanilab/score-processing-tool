# -*- coding: utf-8 -*-
import glob
import io
import os
import re

import music21 as m2
from httplib2 import Http
from apiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials

data_dir = './data' # Directory to save files

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

def main():
    download()
    path_list = glob.glob(os.path.join(data_dir, '*'))
    for path in path_list:
        file_len = len(glob.glob(os.path.join(path, '*')))
        if file_len == 2:
            make_score(path)


if __name__ == '__main__':
    main()

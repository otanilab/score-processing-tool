# Score Processing Tool

This Python script provides a complete pipeline to manage, modify, and print musical scores fetched from Google Drive. It downloads MIDI files and corresponding QR code PNGs from Google Drive, converts the MIDI files to PDFs, embeds the QR codes onto the PDFs, and prepares the scores for printing.

## Features

1. **Google Drive Downloading**: Downloads files from a Google Drive account using Google Drive API with the support of OAuth2 authentication.
2. **MIDI to PDF Conversion**: Uses `music21` library to convert MIDI files to PDF scores.
3. **PDF Embedding**: Embeds QR codes from PNG images onto the PDF scores.
4. **Printing Preparation**: Prepares the modified scores for printing and organizes them into directories based on their print status.

## Prerequisites

### Software Requirements
- **MuseScore v3.6.2**: It's essential to have MuseScore v3.6.2 installed on your PC. You can download it from [here](https://github.com/musescore/MuseScore/releases/tag/v3.6.2).

### Libraries
To run the script, you must have the following libraries installed:
- music21 (`m2`)
- PIL (`Image`)
- httplib2 (`Http`)
- googleapiclient (`build`, `MediaIoBaseDownload`)
- oauth2client (`ServiceAccountCredentials`)
- pdf2image (`convert_from_path`)

## Directory Structure

- `./data`: Directory where the downloaded files from Google Drive are stored.
- `./output`: Directory where the processed files are stored.

## Usage

1. **Setup Google API Credentials**:
   - Ensure you have your `credentials.json` file and place it in a `credentials` directory.

2. **Run the Script**:
   ```bash
   python main.py
   ```

3. The script will run in a loop, processing new files from Google Drive every 10 seconds.

## Functions Overview

- `download()`: Downloads files from Google Drive.
- `make_score(path)`: Converts a MIDI file to a PDF score.
- `pdf_to_jpg(path)`: Converts a PDF to a JPG image.
- `embed_qr(path)`: Embeds a QR code PNG onto the JPG score.
- `print_score(path)`: Prepares the score for printing (currently just displays the path).
- `main()`: The main function that calls the above functions in sequence.

**Note**: Ensure you have the appropriate permissions and setup when interacting with Google Drive and ensure you follow Google's API usage guidelines.


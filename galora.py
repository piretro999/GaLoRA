
"""
Created on Mon Jun 17 16:01:34 2024

@author: piret
"""

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from azure.storage.blob import BlobServiceClient
import json
import os
import logging
import argparse
from datetime import datetime
import fitz  # PyMuPDF
from pptx import Presentation
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import AudioSegment
import pandas as pd
import csv
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from pydub.silence import split_on_silence
from pytube import YouTube
from docx import Document
import zipfile
import re
from difflib import SequenceMatcher
import requests
import shutil
import vlc
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import subprocess

# Configure logging
log_dir = "log"
temp_dir = "temp"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

def configure_logger(module_name):
    timestamp = datetime.now().strftime("%Y%m%d")
    log_dir = "log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, f'{module_name}_{timestamp}.log')
    try:
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("Logger has been configured successfully.")
        print(f"Logger configured: {log_file}")  # Stampa di debug
    except Exception as e:
        print(f"Failed to configure logger: {e}")
    return log_file

def log_message(key, level="info", *args):
    try:
        message = key.format(*args)
    except KeyError:
        message = f"Logging key error: {key} with args {args}"

    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "debug":
        logging.debug(message)
    print(f"Log message: {message}")  # Stampa di debug

# Load configuration
def load_config(module_name, config_path='config.json'):
    try:
        with open(config_path, 'r') as config_file:
            configs = json.load(config_file)
            for config in configs:
                if config["module"] == module_name:
                    log_message('Config loaded for module: {}', 'info', module_name)
                    return config
        log_message('Config module not found: {}', 'warning', module_name)
    except json.JSONDecodeError as e:
        log_message('JSON decode error: {}', 'error', str(e))
    except Exception as e:
        log_message('Config load failed: {}', 'error', str(e))
    return None

# Language translations
def load_translations(language_code):
    try:
        with open(f'language/cli_{language_code}.json', 'r', encoding='utf-8') as lang_file:
            return json.load(lang_file)
    except FileNotFoundError:
        log_message('Language file not found: {}', 'error', language_code)
        return {}
    except json.JSONDecodeError as e:
        log_message('JSON decode error in language file: {}', 'error', str(e))
        return {}
    except Exception as e:
        log_message('Error loading language file: {}', 'error', str(e))
        return {}

# Remove headers and footers from text
def remove_headers_footers(text):
    lines = text.split('\n')
    if len(lines) > 3:
        return '\n'.join(lines[1:-1])
    return text

# Handle text files
def handle_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            text = file.read()
        log_message('Text file processed: {}', 'info', file_path)
        return remove_headers_footers(text), file_path
    except Exception as e:
        log_message('Error processing text file: {} - {}', 'error', file_path, str(e))
        return f"Failed to read or process text file: {str(e)}", None

# Handle PDF files
def handle_pdf_file(file_path):
    try:
        doc = fitz.open(file_path)
        text = [page.get_text("text") for page in doc]
        doc.close()
        log_message('PDF file processed: {}', 'info', file_path)
        return remove_headers_footers('\n'.join(text)), file_path
    except Exception as e:
        log_message('Error processing PDF file: {} - {}', 'error', file_path, str(e))
        return f"Failed to process PDF file: {file_path} - {str(e)}", None

# Handle Word files
def handle_word_file(file_path):
    try:
        doc = Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
        log_message('Word file processed: {}', 'info', file_path)
        return remove_headers_footers(text), file_path
    except Exception as e:
        log_message('Error processing Word file: {} - {}', 'error', file_path, str(e))
        return f"Failed to process Word file: {file_path} - {str(e)}", None

# Handle PPT files
def handle_ppt_file(file_path):
    try:
        ppt = Presentation(file_path)
        text = [shape.text for slide in ppt.slides for shape in slide.shapes if hasattr(shape, "text")]
        log_message('PPT file processed: {}', 'info', file_path)
        return remove_headers_footers('\n'.join(text)), file_path
    except Exception as e:
        log_message('Error processing PPT file: {} - {}', 'error', file_path, str(e))
        return f"Failed to process PowerPoint file: {file_path} - {str(e)}", None

# Handle Excel files
def handle_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)
        log_message('Excel file processed: {}', 'info', file_path)
        return df.to_csv(index=False), file_path
    except Exception as e:
        log_message('Error processing Excel file: {} - {}', 'error', file_path, str(e))
        return f"Failed to process Excel file: {file_path} - {str(e)}", None

# Handle CSV files
def handle_csv_file(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
        log_message('CSV file processed: {}', 'info', file_path)
        return '\n'.join([','.join(row) for row in data]), file_path
    except Exception as e:
        log_message('Error processing CSV file: {} - {}', 'error', file_path, str(e))
        return f"Failed to process CSV file: {file_path} - {str(e)}", None

# Handle EPUB files
def handle_epub_file(file_path):
    try:
        book = epub.read_epub(file_path)
        text = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text.append(soup.get_text())
        log_message('EPUB file processed: {}', 'info', file_path)
        return remove_headers_footers('\n'.join(text)), file_path
    except Exception as e:
        log_message('Error processing EPUB file: {} - {}', 'error', file_path, str(e))
        return f"Failed to process EPUB file: {file_path} - {str(e)}", None

def handle_xml_gan_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        texts = [elem.text for elem in root.iter() if elem.text is not None]
        return '\n'.join(texts), file_path
    except Exception as e:
        logging.error(f"Failed to process XML/GAN file: {file_path} - {str(e)}")
        return f"Failed to process XML/GAN file: {file_path} - {str(e)}", None        

# Handle audio files
def handle_audio_file(file_path):
    if file_path.lower().endswith('.m4a'):
        sound = AudioSegment.from_file(file_path, format='m4a')
        wav_path = file_path.replace('.m4a', '.wav')
        sound.export(wav_path, format='wav')
        file_path = wav_path

    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='it-IT')
            log_message('Audio file processed: {}', 'info', file_path)
            return text, file_path
        except sr.UnknownValueError:
            log_message('Speech not understood: {}', 'error', file_path)
            return "Speech not understood", file_path
        except sr.RequestError as e:
            log_message('Speech recognition request failed: {} - {}', 'error', file_path, str(e))
            return f"Speech recognition request failed; {e}", file_path

# Handle video files
def handle_video_file(file_path):
    try:
        audio_path = extract_audio_from_video(file_path)
        text = transcribe_audio(audio_path)
        os.remove(audio_path)
        log_message('Video file processed: {}', 'info', file_path)
        return text, file_path
    except Exception as e:
        log_message('Error processing video file: {} - {}', 'error', file_path, str(e))
        return f"Failed to process video file: {file_path} - {str(e)}", None

# Extract audio from video
def extract_audio_from_video(video_path):
    video = VideoFileClip(video_path)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    audio_path = os.path.join(temp_dir, f"temp_audio_{timestamp}.wav")
    video.audio.write_audiofile(audio_path)
    return audio_path

# Transcribe audio
def transcribe_audio(audio_path, language='it-IT'):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data, language=language)
        except sr.UnknownValueError:
            return "Speech not understood"
        except sr.RequestError as e:
            return f"Could not request results; {e}"

# Write to output
def write_to_output(content, output_dir, file_index, original_path):
    output_file_path = os.path.join(output_dir, f'model_{file_index}.txt')
    with open(output_file_path, 'a', encoding='utf-8') as file:
        file.write(f"\nOriginal file path: {original_path}\nFile content:\n{content}\n")
    log_message('Output written: {}', 'info', output_file_path)
    return file_index + 1

# Handle files in zip
def handle_zip_file(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(temp_dir)
            extracted_files = z.namelist()
            for file_name in extracted_files:
                internal_path = os.path.join(temp_dir, file_name)
                if os.path.isfile(internal_path):
                    content, _ = handle_file(internal_path)
                    if content and not content.startswith("Unsupported"):
                        log_message('ZIP file processed: {}', 'info', zip_path)
                        return f"{content} (from {file_name} in {zip_path})", zip_path
                    os.remove(internal_path)
        log_message('No supported files found in ZIP: {}', 'warning', zip_path)
        return "No supported files found or failed to process", None
    except Exception as e:
        log_message('Error processing ZIP file: {} - {}', 'error', zip_path, str(e))
        return f"Failed to process ZIP file: {str(e)}", None

# Handle generic files
def handle_file(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    handler = {
        '.txt': handle_text_file,
        '.htm': handle_text_file,
        '.html': handle_text_file,
        '.pdf': handle_pdf_file,
        '.docx': handle_word_file,
        '.doc': handle_word_file,
        '.pptx': handle_ppt_file,
        '.ppt': handle_ppt_file,
        '.xls': handle_excel_file,
        '.xlsx': handle_excel_file,
        '.xml': handle_text_file,
        '.gan': handle_text_file,
        '.xsd': handle_text_file,
        '.wav': handle_audio_file,
        '.mp3': handle_audio_file,
        '.m4a': handle_audio_file,
        '.mp4': handle_video_file,
        '.avi': handle_video_file,
        '.mov': handle_video_file,
        '.mkv': handle_video_file,
        '.mpeg': handle_video_file,
        '.mpg': handle_video_file,
        '.3gp': handle_video_file,
        '.csv': handle_csv_file,
        '.epub': handle_epub_file,
        '.zip': handle_zip_file
    }.get(extension)
    if handler:
        return handler(file_path)
    return f"Unsupported file format for {file_path}", None

# Handle directory
def handle_directory(directory_path, output_dir):
    file_index = 1
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            content, original_path = handle_file(file_path)
            if content and not content.startswith("Unsupported"):
                file_index = write_to_output(content, output_dir, file_index, original_path)

# Limit file search based on specific criteria
def limit_files_search(files, limit_search):
    if limit_search == 'noLimit':
        return files
    if limit_search == 'lastProducedPerType':
        file_types = {}
        for file in files:
            file_type = os.path.splitext(file)[1]
            if (file_type not in file_types) or (os.path.getmtime(file) > os.path.getmtime(file_types[file_type])):
                file_types[file_type] = file
        return list(file_types.values())
    elif limit_search == 'lastProducedInFolder':
        if files:
            return [max(files, key=os.path.getmtime)]
    elif limit_search == 'lastProducedSimilarTitle':
        similar_titles = {}
        for file in files:
            base_name = os.path.splitext(file)[0]
            if base_name not in similar_titles or os.path.getmtime(file) > os.path.getmtime(similar_titles[base_name]):
                similarity = SequenceMatcher(None, base_name, os.path.splitext(similar_titles.get(base_name, ""))[0]).ratio()
                if similarity > 0.9:
                    similar_titles[base_name] = file
        return list(similar_titles.values())
    return files

# Process text with keywords and create JSON data
def process_text_with_keywords(text, keywords):
    json_data = []
    keyword_positions = []

    # Find all keyword positions in text
    for keyword in keywords:
        pattern = re.compile(keyword, re.IGNORECASE)
        matches = list(pattern.finditer(text))
        for match in matches:
            keyword_positions.append((match.start(), match.end(), match.group()))

    # Sort keyword positions by their position in text
    keyword_positions.sort()

    # Add contents between keywords to JSON
    for i in range(len(keyword_positions)):
        start, end, matched_keyword = keyword_positions[i]
        next_start = keyword_positions[i + 1][0] if i + 1 < len(keyword_positions) else len(text)

        content = text[end:next_start].strip()
        json_data.append({"title": matched_keyword, "content": content})

    log_message('JSON data created', 'info')
    return json_data

# Write JSON data to file
def write_json(data, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        log_message('JSON file written: {}', 'info', output_file)
    except PermissionError:
        log_message('Permission denied: {}', 'error', output_file)
    except Exception as e:
        log_message('Error writing JSON file: {} - {}', 'error', output_file, str(e))

# Download video from YouTube
def download_youtube_video(url, download_audio_only=False):
    if not url.strip():
        log_message('Download URL empty', 'error')
        return None
    try:
        yt = YouTube(url)
        title = ''.join([c for c in yt.title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        if download_audio_only:
            stream = yt.streams.filter(only_audio=True).first()
            file_path = stream.download(output_path=temp_dir, filename=f"{title}.mp3")
        else:
            stream = yt.streams.get_highest_resolution()
            file_path = stream.download(output_path=temp_dir, filename=f"{title}.mp4")
        log_message('Successfully downloaded YouTube video: {}', 'info', file_path)
        return file_path
    except Exception as e:
        log_message('Error downloading YouTube video: {}', 'error', str(e))
        return None

# Download video from Vimeo
def download_vimeo_video(url):
    if not url.strip():
        log_message('Download URL empty', 'error')
        return None
    try:
        response = requests.get(url, stream=True)
        title = url.split("/")[-1]
        title = ''.join([c for c in title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        file_path = os.path.join(temp_dir, f"{title}.mp4")
        with open(file_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        log_message('Successfully downloaded Vimeo video: {}', 'info', file_path)
        return file_path
    except Exception as e:
        log_message('Error downloading Vimeo video: {}', 'error', str(e))
        return None

# Generate SRT file from audio
def generate_srt(audio_file, output_file, language='it-IT'):
    recognizer = sr.Recognizer()
    sound = AudioSegment.from_wav(audio_file)
    chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=sound.dBFS-14, keep_silence=500)

    with open(output_file, 'w') as file:
        start = 0
        for i, chunk in enumerate(chunks):
            chunk_filename = os.path.join(temp_dir, f"chunk_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}.wav")
            chunk.export(chunk_filename, format="wav")
            with sr.AudioFile(chunk_filename) as source:
                audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio, language=language)
                duration = len(chunk) / 1000
                start_time = start
                end_time = start + duration
                file.write(f"{i+1}\n")
                file.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
                file.write(f"{text.strip()}\n\n")
                start += duration
                log_message('SRT segment generated: {}', 'info', i+1)
            except sr.UnknownValueError:
                file.write(f"{i+1}\n")
                file.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
                file.write("Audio not understandable\n\n")
                start += duration
                log_message('Audio not understood in segment: {}', 'warning', i+1)
            except sr.RequestError as e:
                file.write(f"{i+1}\n")
                file.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
                file.write(f"Service error: {e}\n\n")
                start += duration
                log_message('Service error in segment: {} - {}', 'error', i+1, str(e))
    
    # Clean up chunk files
    for chunk_filename in os.listdir(temp_dir):
        if chunk_filename.startswith("chunk") and chunk_filename.endswith(".wav"):
            os.remove(os.path.join(temp_dir, chunk_filename))
            log_message('Removed chunk file: {}', 'info', chunk_filename)

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},000"

# Google Drive Functions
def upload_to_gdrive(credentials, file_path, folder_id):
    try:
        service = build('drive', 'v3', credentials=credentials)
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        log_message('Successfully uploaded {} to Google Drive', 'info', file_path)
    except Exception as e:
        log_message('Error uploading to Google Drive: {}', 'error', str(e))

def create_folder_on_gdrive(credentials, folder_name, parent_folder_id='root'):
    try:
        service = build('drive', 'v3', credentials=credentials)
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        log_message('Successfully created folder {} on Google Drive', 'info', folder_name)
        return folder.get('id')
    except Exception as e:
        log_message('Error creating folder on Google Drive: {}', 'error', str(e))
        return None

def upload_json_to_gdrive(credentials, json_dir, gdrive_folder_id):
    try:
        service = build('drive', 'v3', credentials=credentials)
        for file_name in os.listdir(json_dir):
            file_path = os.path.join(json_dir, file_name)
            if os.path.isfile(file_path):
                upload_to_gdrive(credentials, file_path, gdrive_folder_id)
    except Exception as e:
        log_message('Error uploading JSON files to Google Drive: {}', 'error', str(e))

def download_files_from_folder(service, folder_id, parent_path):
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])

    for item in items:
        file_id = item['id']
        file_name = item['name']
        file_path = os.path.join(parent_path, file_name)
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            download_files_from_folder(service, file_id, file_path)
        else:
            request = service.files().get_media(fileId=file_id)
            with open(file_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download {file_name}: {int(status.progress() * 100)}%")

def download_from_gdrive(credentials, file_id, download_path):
    try:
        service = build('drive', 'v3', credentials=credentials)

        # Check if the provided file_id is a folder or a file
        file_metadata = service.files().get(fileId=file_id, fields="id, name, mimeType").execute()
        if file_metadata['mimeType'] == 'application/vnd.google-apps.folder':
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            download_files_from_folder(service, file_id, download_path)
        else:
            request = service.files().get_media(fileId=file_id)
            with open(download_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download {file_metadata['name']}: {int(status.progress() * 100)}%")
            log_message('Successfully downloaded {} to {}', 'info', file_id, download_path)
    except Exception as e:
        log_message('Error downloading from Google Drive: {}', 'error', str(e))

def download_all_files_from_gdrive(credentials, download_dir):
    service = build('drive', 'v3', credentials=credentials)

    # Get the root folder ID
    root_folder_id = 'root'

    download_files_from_folder(service, root_folder_id, download_dir)

# AWS S3 Functions
def upload_to_s3(file_path, bucket_name):
    try:
        s3_client = boto3.client('s3',
                                 aws_access_key_id=config['aws_access_key_id'],
                                 aws_secret_access_key=config['aws_secret_access_key'])
        s3_client.upload_file(file_path, bucket_name, os.path.basename(file_path))
        log_message('Successfully uploaded {} to S3 bucket {}', 'info', file_path, bucket_name)
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error uploading to S3: {} - {}', 'error', file_path, bucket_name, str(e))

def download_from_s3(file_key, bucket_name, download_path):
    try:
        s3_client = boto3.client('s3',
                                 aws_access_key_id=config['aws_access_key_id'],
                                 aws_secret_access_key=config['aws_secret_access_key'])
        s3_client.download_file(bucket_name, file_key, download_path)
        log_message('Successfully downloaded {} from S3 bucket {} to {}', 'info', file_key, bucket_name, download_path)
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error downloading from S3: {} - {}', 'error', file_key, bucket_name, str(e))

def create_folder_on_s3(bucket_name, folder_name):
    try:
        s3_client = boto3.client('s3',
                                 aws_access_key_id=config['aws_access_key_id'],
                                 aws_secret_access_key=config['aws_secret_access_key'])
        s3_client.put_object(Bucket=bucket_name, Key=(folder_name + '/'))
        log_message('Successfully created folder {} in S3 bucket {}', 'info', folder_name, bucket_name)
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error creating folder in S3: {} - {}', 'error', folder_name, bucket_name, str(e))

def upload_json_to_s3(json_dir, bucket_name, folder_name):
    try:
        s3_client = boto3.client('s3',
                                 aws_access_key_id=config['aws_access_key_id'],
                                 aws_secret_access_key=config['aws_secret_access_key'])
        for file_name in os.listdir(json_dir):
            file_path = os.path.join(json_dir, file_name)
            if os.path.isfile(file_path):
                s3_client.upload_file(file_path, bucket_name, f"{folder_name}/{file_name}")
        log_message('Successfully uploaded JSON files to S3 folder {} in bucket {}', 'info', folder_name, bucket_name)
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error uploading JSON files to S3: {} - {}', 'error', folder_name, bucket_name, str(e))
        
def download_directory_from_s3(bucket_name, s3_directory, local_directory):
    try:
        s3_client = boto3.client('s3',
                                 aws_access_key_id=config['aws_access_key_id'],
                                 aws_secret_access_key=config['aws_secret_access_key'])
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name, Prefix=s3_directory):
            for obj in page.get('Contents', []):
                s3_key = obj['Key']
                local_file_path = os.path.join(local_directory, os.path.relpath(s3_key, s3_directory))
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                s3_client.download_file(bucket_name, s3_key, local_file_path)
                log_message('Successfully downloaded {} to {}', 'info', s3_key, local_file_path)
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error downloading from S3: {}', 'error', str(e))

# Azure Blob Storage Functions
def upload_to_azure(file_path, container_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(config['azure_connection_str'])
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=os.path.basename(file_path))
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)
        log_message('Successfully uploaded {} to Azure container {}', 'info', file_path, container_name)
    except Exception as e:
        log_message('Error uploading to Azure: {} - {}', 'error', file_path, container_name, str(e))

def download_from_azure(blob_name, container_name, download_path):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(config['azure_connection_str'])
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        log_message('Successfully downloaded {} from Azure container {} to {}', 'info', blob_name, container_name, download_path)
    except Exception as e:
        log_message('Error downloading from Azure: {} - {}', 'error', blob_name, container_name, str(e))

def create_folder_on_azure(container_name, folder_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(config['azure_connection_str'])
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=(folder_name + '/'))
        blob_client.upload_blob('', overwrite=True)
        log_message('Successfully created folder {} in Azure container {}', 'info', folder_name, container_name)
    except Exception as e:
        log_message('Error creating folder in Azure: {} - {}', 'error', folder_name, container_name, str(e))

def upload_json_to_azure(json_dir, container_name, folder_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(config['azure_connection_str'])
        for file_name in os.listdir(json_dir):
            file_path = os.path.join(json_dir, file_name)
            if os.path.isfile(file_path):
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{folder_name}/{file_name}")
                with open(file_path, "rb") as data:
                    blob_client.upload_blob(data)
        log_message('Successfully uploaded JSON files to Azure folder {} in container {}', 'info', folder_name, container_name)
    except Exception as e:
        log_message('Error uploading JSON files to Azure: {} - {}', 'error', folder_name, container_name, str(e))

# Aruba Cloud Object Storage Functions
def upload_to_aruba(file_path, bucket_name):
    try:
        s3_client = boto3.client('s3',
                                 endpoint_url=config['aruba_endpoint'],
                                 aws_access_key_id=config['aruba_access_key_id'],
                                 aws_secret_access_key=config['aruba_secret_access_key'])
        s3_client.upload_file(file_path, bucket_name, os.path.basename(file_path))
        log_message('Successfully uploaded {} to Aruba bucket {}', 'info', file_path, bucket_name)
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error uploading to Aruba: {} - {}', 'error', file_path, bucket_name, str(e))

def download_from_aruba(file_key, bucket_name, download_path):
    try:
        s3_client = boto3.client('s3',
                                 endpoint_url=config['aruba_endpoint'],
                                 aws_access_key_id=config['aruba_access_key_id'],
                                 aws_secret_access_key=config['aruba_secret_access_key'])
        s3_client.download_file(bucket_name, file_key, download_path)
        log_message('Successfully downloaded {} from Aruba bucket {} to {}', 'info', file_key, bucket_name, download_path)
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error downloading from Aruba: {} - {}', 'error', file_key, bucket_name, str(e))

def create_folder_on_aruba(bucket_name, folder_name):
    try:
        s3_client = boto3.client('s3',
                                 endpoint_url=config['aruba_endpoint'],
                                 aws_access_key_id=config['aruba_access_key_id'],
                                 aws_secret_access_key=config['aruba_secret_access_key'])
        s3_client.put_object(Bucket=bucket_name, Key=(folder_name + '/'))
        log_message('Successfully created folder {} in Aruba bucket {}', 'info', folder_name, bucket_name)
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error creating folder in Aruba: {} - {}', 'error', folder_name, bucket_name, str(e))

def upload_json_to_aruba(json_dir, bucket_name, folder_name):
    try:
        s3_client = boto3.client('s3',
                                 endpoint_url=config['aruba_endpoint'],
                                 aws_access_key_id=config['aruba_access_key_id'],
                                 aws_secret_access_key=config['aruba_secret_access_key'])
        for file_name in os.listdir(json_dir):
            file_path = os.path.join(json_dir, file_name)
            if os.path.isfile(file_path):
                s3_client.upload_file(file_path, bucket_name, f"{folder_name}/{file_name}")
        log_message('Successfully uploaded JSON files to Aruba folder {} in bucket {}', 'info', folder_name, bucket_name)
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error uploading JSON files to Aruba: {} - {}', 'error', folder_name, bucket_name, str(e))

def play_video_with_srt(video_path, srt_path):
    instance = vlc.Instance()
    player = instance.media_player_new()

    media = instance.media_new(video_path)
    media.add_option(f'sub-file={srt_path}')
    
    player.set_media(media)
    player.play()

    # Wait until the video is finished
    while True:
        state = player.get_state()
        if state in [vlc.State.Ended, vlc.State.Error]:
            break

def play_video_from_command_line(video_path, srt_path):
    if os.path.isfile(video_path) and os.path.isfile(srt_path):
        play_video_with_srt(video_path, srt_path)
    else:
        log_message('Invalid file paths: {} or {}', 'error', video_path, srt_path)
        
def download_directory_from_azure(container_name, azure_directory, local_directory):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(config['azure_connection_str'])
        container_client = blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs(name_starts_with=azure_directory)

        for blob in blob_list:
            blob_client = container_client.get_blob_client(blob.name)
            local_file_path = os.path.join(local_directory, os.path.relpath(blob.name, azure_directory))
            
            # Se il blob rappresenta una directory, crea la directory
            if blob.name.endswith('/'):
                os.makedirs(local_file_path, exist_ok=True)
            else:
                # Creazione della directory, se non esiste
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                
                # Gestire il caso in cui un file con lo stesso nome della directory esiste già
                if os.path.exists(local_file_path):
                    if os.path.isfile(local_file_path):
                        local_file_path = local_file_path + "_conflict"
                    else:
                        continue

                with open(local_file_path, "wb") as download_file:
                    download_file.write(blob_client.download_blob().readall())
                log_message('Successfully downloaded {} to {}', 'info', blob.name, local_file_path)
    except Exception as e:
        log_message('Error downloading from Azure: {}', 'error', str(e))


def download_directory_from_aruba(bucket_name, aruba_directory, local_directory):
    try:
        s3_client = boto3.client('s3',
                                 endpoint_url=config['aruba_endpoint'],
                                 aws_access_key_id=config['aruba_access_key_id'],
                                 aws_secret_access_key=config['aruba_secret_access_key'])
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name, Prefix=aruba_directory):
            for obj in page.get('Contents', []):
                s3_key = obj['Key']
                local_file_path = os.path.join(local_directory, os.path.relpath(s3_key, aruba_directory))
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                s3_client.download_file(bucket_name, s3_key, local_file_path)
                log_message('Successfully downloaded {} to {}', 'info', s3_key, local_file_path)
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error downloading from Aruba: {}', 'error', str(e))

def read_file_from_gdrive(credentials, folder_id, file_name):
    try:
        service = build('drive', 'v3', credentials=credentials)
        query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            log_message('No file found with name {} in Google Drive folder {}', 'error', file_name, folder_id)
            return None

        file_id = items[0]['id']
        request = service.files().get_media(fileId=file_id)
        file_content = request.execute()
        log_message('Successfully read file {} from Google Drive folder {}', 'info', file_name, folder_id)
        return file_content
    except Exception as e:
        log_message('Error reading file from Google Drive: {}', 'error', str(e))
        return None

def read_file_from_s3(bucket_name, s3_directory, file_name):
    try:
        s3_client = boto3.client('s3',
                                 aws_access_key_id=config['aws_access_key_id'],
                                 aws_secret_access_key=config['aws_secret_access_key'])
        s3_key = os.path.join(s3_directory, file_name)
        obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        file_content = obj['Body'].read()
        log_message('Successfully read file {} from S3 directory {}', 'info', file_name, s3_directory)
        return file_content
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error reading file from S3: {}', 'error', str(e))
        return None

def read_file_from_azure(container_name, azure_directory, file_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(config['azure_connection_str'])
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=os.path.join(azure_directory, file_name))
        file_content = blob_client.download_blob().readall()
        log_message('Successfully read file {} from Azure directory {}', 'info', file_name, azure_directory)
        return file_content
    except Exception as e:
        log_message('Error reading file from Azure: {}', 'error', str(e))
        return None

def read_file_from_aruba(bucket_name, aruba_directory, file_name):
    try:
        s3_client = boto3.client('s3',
                                 endpoint_url=config['aruba_endpoint'],
                                 aws_access_key_id=config['aruba_access_key_id'],
                                 aws_secret_access_key=config['aruba_secret_access_key'])
        s3_key = os.path.join(aruba_directory, file_name)
        obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        file_content = obj['Body'].read()
        log_message('Successfully read file {} from Aruba directory {}', 'info', file_name, aruba_directory)
        return file_content
    except (NoCredentialsError, PartialCredentialsError) as e:
        log_message('Error reading file from Aruba: {}', 'error', str(e))
        return None


def create_container_if_not_exists(container_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(config['azure_connection_str'])
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
            log_message('Container {} created successfully.', 'info', container_name)
        else:
            log_message('Container {} already exists.', 'info', container_name)
    except Exception as e:
        log_message('Error creating container: {} - {}', 'error', container_name, str(e))

def upload_directory_to_azure(directory_path, container_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(config['azure_connection_str'])
        create_container_if_not_exists(container_name)
        for root, _, files in os.walk(directory_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                blob_name = os.path.relpath(file_path, directory_path).replace("\\", "/")
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                with open(file_path, "rb") as data:
                    blob_client.upload_blob(data)
                log_message('Successfully uploaded {} to Azure container {} as blob {}', 'info', file_path, container_name, blob_name)
    except Exception as e:
        log_message('Error uploading directory to Azure: {} - {}', 'error', directory_path, str(e))

def launch_gui():
    """Function to launch the GUI by running gui.py"""
    try:
        subprocess.run(['python', 'gui.py'], check=True)
        log_message('GUI launched successfully.', 'info')
    except subprocess.CalledProcessError as e:
        log_message('Error launching GUI: {}', 'error', str(e))

def main():
    print("Starting main function...")  # Stampa di debug
    parser = argparse.ArgumentParser(description="CLI Tool")
    parser.add_argument("--language", type=str, default="eng", help="Language code for localization")
    parser.add_argument("--operation", type=str, help="Operation to perform")
    parser.add_argument("--file_path", type=str, help="Path to the file")
    parser.add_argument("--directory_path", type=str, help="Path to the directory")
    parser.add_argument("--bucket_name", type=str, help="Bucket name for cloud storage")
    parser.add_argument("--folder_id", type=str, help="Folder ID for Google Drive")
    parser.add_argument("--file_id", type=str, help="File ID for Google Drive")
    parser.add_argument("--blob_name", type=str, help="Blob name for Azure Blob storage")
    parser.add_argument("--file_key", type=str, help="File key for S3/Aruba")
    parser.add_argument("--download_path", type=str, help="Path to download the file")
    parser.add_argument("--output_dir", type=str, help="Output directory")
    parser.add_argument("--keywords", nargs='*', help="Keywords for processing text files")
    parser.add_argument("--limit_search", type=str, default="noLimit", help="Limit file search criteria")
    parser.add_argument("--download_audio_only", action='store_true', help="Download audio only from video")
    parser.add_argument("--gui", action='store_true', help="Launch GUI interface")
    parser.add_argument("--play_video", action='store_true', help="Play video with SRT")
    parser.add_argument("--video_path", type=str, help="Path to the video file")
    parser.add_argument("--srt_path", type=str, help="Path to the SRT file")
    parser.add_argument("--file_name", type=str, help="Name of the file to read")
    parser.add_argument("--upload_directory_to_azure", action="store_true", help="Upload directory to Azure Blob Storage")
    parser.add_argument("--download_directory_from_azure", action="store_true", help="Download directory from Azure Blob Storage")
    parser.add_argument("--container_name", type=str, help="Container name for Azure Blob storage")
    parser.add_argument("--azure_directory", type=str, help="Directory path in Azure Blob storage")

    args = parser.parse_args()

    global translations
    translations = load_translations(args.language)
    print("Translations loaded.")  # Stampa di debug

    global config
    config = load_config("cli_tool")
    print("Config loaded.")  # Stampa di debug

    # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
    if config and 'google_application_credentials' in config:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['google_application_credentials']
        log_message('Google application credentials set: {}', 'info', config['google_application_credentials'])
        print("Google application credentials set.")  # Stampa di debug

    credentials = service_account.Credentials.from_service_account_file(
        config['google_application_credentials'],
        scopes=config['gdrive_scopes']
    )
    print("Credentials loaded.")  # Stampa di debug

    configure_logger("cli_tool")
    print("Logger configured in main.")  # Stampa di debug
    # Launch GUI if --gui argument is passed
    if args.gui:
        launch_gui()
        return

    # Handle the play video operation
    if args.play_video:
        if args.video_path and args.srt_path:
            play_video_from_command_line(args.video_path, args.srt_path)
        else:
            log_message('Video or SRT path missing', 'error')
        return

    # Check that --operation is provided if --play_video is not specified
    if not args.operation and not args.upload_directory_to_azure and not args.download_directory_from_azure:
        parser.error('--operation is required unless --play_video is specified or --upload_directory_to_azure or --download_directory_from_azure is used')

    print(f"Operation: {args.operation}")  # Stampa di debug
    print(f"Upload to Azure: {args.upload_directory_to_azure}")  # Stampa di debug
    print(f"Download from Azure: {args.download_directory_from_azure}")  # Stampa di debug

    if args.upload_directory_to_azure:
        if config.get('use_azure', False):
            print(f"Uploading directory {args.directory_path} to Azure container {args.container_name}")  # Stampa di debug
            upload_directory_to_azure(args.directory_path, args.container_name)
        else:
            log_message('Azure integration is disabled', 'error')
    elif args.download_directory_from_azure:
        if config.get('use_azure', False):
            print(f"Downloading directory {args.azure_directory} from Azure container {args.container_name} to {args.download_path}")  # Stampa di debug
            download_directory_from_azure(args.container_name, args.azure_directory, args.download_path)
        else:
            log_message('Azure integration is disabled', 'error')
    elif args.operation == "upload_gdrive":
        if config.get('use_gdrive', False):
            upload_to_gdrive(credentials, args.file_path, args.folder_id)
        else:
            log_message('Google Drive integration is disabled', 'error')
    elif args.operation == "download_gdrive":
        if config.get('use_gdrive', False):
            download_from_gdrive(credentials, args.file_id, args.download_path)
        else:
            log_message('Google Drive integration is disabled', 'error')
    elif args.operation == "download_all_gdrive":
        if config.get('use_gdrive', False):
            download_all_files_from_gdrive(credentials, args.output_dir)
        else:
            log_message('Google Drive integration is disabled', 'error')
    elif args.operation == "create_gdrive_folder":
        if config.get('use_gdrive', False):
            folder_id = create_folder_on_gdrive(credentials, args.folder_id)
            if folder_id:
                print(f"{folder_id}")
            else:
                log_message('Failed to create folder on Google Drive', 'error')
        else:
            log_message('Google Drive integration is disabled', 'error')
    elif args.operation == "upload_json_to_gdrive":
        if config.get('use_gdrive', False):
            upload_json_to_gdrive(credentials, args.directory_path, args.folder_id)
        else:
            log_message('Google Drive integration is disabled', 'error')
    elif args.operation == "upload_s3":
        if config.get('use_s3', False):
            upload_to_s3(args.file_path, args.bucket_name)
        else:
            log_message('S3 integration is disabled', 'error')
    elif args.operation == "download_s3":
        if config.get('use_s3', False):
            download_from_s3(args.file_key, args.bucket_name, args.download_path)
        else:
            log_message('S3 integration is disabled', 'error')
    elif args.operation == "create_s3_folder":
        if config.get('use_s3', False):
            create_folder_on_s3(args.bucket_name, args.folder_id)
        else:
            log_message('S3 integration is disabled', 'error')
    elif args.operation == "upload_json_to_s3":
        if config.get('use_s3', False):
            upload_json_to_s3(args.directory_path, args.bucket_name, args.folder_id)
        else:
            log_message('S3 integration is disabled', 'error')
    elif args.operation == "upload_azure":
        if config.get('use_azure', False):
            upload_to_azure(args.file_path, args.container_name)
        else:
            log_message('Azure integration is disabled', 'error')
    elif args.operation == "download_azure":
        if config.get('use_azure', False):
            download_from_azure(args.blob_name, args.container_name, args.download_path)
        else:
            log_message('Azure integration is disabled', 'error')
    elif args.operation == "create_azure_folder":
        if config.get('use_azure', False):
            create_folder_on_azure(args.container_name, args.folder_id)
        else:
            log_message('Azure integration is disabled', 'error')
    elif args.operation == "upload_json_to_azure":
        if config.get('use_azure', False):
            upload_json_to_azure(args.directory_path, args.container_name, args.folder_id)
        else:
            log_message('Azure integration is disabled', 'error')
    elif args.operation == "upload_aruba":
        if config.get('use_aruba', False):
            upload_to_aruba(args.file_path, args.bucket_name)
        else:
            log_message('Aruba integration is disabled', 'error')
    elif args.operation == "download_aruba":
        if config.get('use_aruba', False):
            download_from_aruba(args.file_key, args.bucket_name, args.download_path)
        else:
            log_message('Aruba integration is disabled', 'error')
    elif args.operation == "create_aruba_folder":
        if config.get('use_aruba', False):
            create_folder_on_aruba(args.bucket_name, args.folder_id)
        else:
            log_message('Aruba integration is disabled', 'error')
    elif args.operation == "upload_json_to_aruba":
        if config.get('use_aruba', False):
            upload_json_to_aruba(args.directory_path, args.bucket_name, args.folder_id)
        else:
            log_message('Aruba integration is disabled', 'error')
    elif args.operation == "download_youtube":
        download_youtube_video(args.file_path, args.download_audio_only)
    elif args.operation == "download_vimeo":
        download_vimeo_video(args.file_path)
    elif args.operation == "generate_srt":
        generate_srt(args.file_path, args.output_dir)
    elif args.operation == "handle_directory":
        handle_directory(args.directory_path, args.output_dir)
    elif args.operation == "download_s3_directory":
        if config.get('use_s3', False):
            download_directory_from_s3(args.bucket_name, args.directory_path, args.download_path)
        else:
            log_message('S3 integration is disabled', 'error')
    elif args.operation == "download_azure_directory":
        if config.get('use_azure', False):
            download_directory_from_azure(args.container_name, args.directory_path, args.download_path)
        else:
            log_message('Azure integration is disabled', 'error')
    elif args.operation == "download_aruba_directory":
        if config.get('use_aruba', False):
            download_directory_from_aruba(args.bucket_name, args.directory_path, args.download_path)
        else:
            log_message('Aruba integration is disabled', 'error')
    elif args.operation == "read_gdrive_file":
        if config.get('use_gdrive', False):
            file_content = read_file_from_gdrive(credentials, args.folder_id, args.file_name)
            if file_content:
                with open(args.download_path, 'wb') as f:
                    f.write(file_content)
        else:
            log_message('Google Drive integration is disabled', 'error')
    elif args.operation == "read_s3_file":
        if config.get('use_s3', False):
            file_content = read_file_from_s3(args.bucket_name, args.directory_path, args.file_name)
            if file_content:
                with open(args.download_path, 'wb') as f:
                    f.write(file_content)
        else:
            log_message('S3 integration is disabled', 'error')
    elif args.operation == "read_azure_file":
        if config.get('use_azure', False):
            file_content = read_file_from_azure(args.container_name, args.directory_path, args.file_name)
            if file_content:
                with open(args.download_path, 'wb') as f:
                    f.write(file_content)
        else:
            log_message('Azure integration is disabled', 'error')
    elif args.operation == "read_aruba_file":
        if config.get('use_aruba', False):
            file_content = read_file_from_aruba(args.bucket_name, args.directory_path, args.file_name)
            if file_content:
                with open(args.download_path, 'wb') as f:
                    f.write(file_content)
        else:
            log_message('Aruba integration is disabled', 'error')
    elif args.upload_directory_to_azure:
        if config.get('use_azure', False):
            print(f"Uploading directory {args.directory_path} to Azure container {args.container_name}")  # Stampa di debug
            upload_directory_to_azure(args.directory_path, args.container_name)
        else:
            log_message('Azure integration is disabled', 'error')
    elif args.download_directory_from_azure:
        if config.get('use_azure', False):
            print(f"Downloading directory {args.azure_directory} from Azure container {args.container_name} to {args.download_path}")  # Stampa di debug
            download_directory_from_azure(args.container_name, args.azure_directory, args.download_path)
        else:
            log_message('Azure integration is disabled', 'error')
    elif args.operation == "process_keywords":
        if args.directory_path and args.output_dir and args.keywords:
            for root, _, files in os.walk(args.directory_path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    content, _ = handle_file(file_path)
                    if content and not content.startswith("Unsupported"):
                        json_data = process_text_with_keywords(content, args.keywords)
                        output_file = os.path.join(args.output_dir, f'{os.path.splitext(file_name)[0]}.json')
                        write_json(json_data, output_file)
        else:
            parser.error('--directory_path, --output_dir, and --keywords are required for process_keywords operation')
    else:
        log_message('Unknown operation: {}', 'error', args.operation)

    logging.shutdown()  # Assicurarsi che i log vengano scritti nel file
    print("Logging shutdown.")  # Stampa di debug

if __name__ == "__main__":
    main()

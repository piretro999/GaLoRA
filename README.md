# Galora

Galora is the definitive evolution of the previous solutions Lora Help and MagicALora. This solution represents the future development under the name Galora, providing enhanced features and capabilities for managing and processing content for AI systems using Local Resource Access (LoRa) technology.

## Features

- **Upload and Download**: Effortlessly upload and download files to and from Google Drive, AWS S3, and Azure Blob Storage.
- **Transliteration**: Convert text files into a standardized format, useful for pre-processing text data for NLP models.
- **JSON Creation**: Automatically generate JSON files from text files by identifying and extracting content based on specified keywords.
- **Directory Management**: Download entire directories from cloud storage to a local path for batch processing.
- **Media Transcoding**: Convert media files between different formats to ensure compatibility with various AI models.

## Components

### 1. Command Line Interface (CLI) - `galora.py`

The CLI component of Galora offers a powerful and flexible way to interact with the system through terminal commands.

#### Advantages of CLI:
- **Efficiency**: Quickly perform batch operations and automate workflows.
- **Scriptable**: Easily integrate with other tools and scripts for seamless automation.
- **Resource-Friendly**: Lightweight and requires minimal system resources.

### 2. Graphical User Interface (GUI) - `gui.py`

The GUI component provides a user-friendly interface that simplifies interaction with Galora, especially for users who prefer visual interfaces over command-line operations.

#### Advantages of GUI:
- **Ease of Use**: Intuitive interface that is easy to navigate, reducing the learning curve.
- **Visualization**: Better visualization of processes and data, making it easier to manage complex tasks.
- **Accessibility**: Accessible to users who are not comfortable with command-line operations.

## What is a Local Resource Access (LoRa) Manager?

A Local Resource Access (LoRa) manager like Galora is designed to facilitate the seamless management and processing of large datasets, ensuring efficient feeding of AI systems. Galora leverages LoRa technology to handle the flow of data between local and cloud storage, making sure that AI models have access to up-to-date and relevant data without manual intervention.

## Use Cases

### 1. Building Knowledge Bases

Organizations can use Galora to upload and manage internal documentation, research papers, and reports to cloud storage. The AI models can then process this data to create a comprehensive knowledge base that employees can query to find relevant information quickly.

### 2. Training Chatbots

Companies can use Galora to collect and manage customer service interactions, emails, and support tickets. This data is uploaded to cloud storage and used to train AI chatbots, enabling them to understand and respond to customer inquiries more effectively.

### 3. Document Management

Businesses can use Galora to automate the process of uploading, categorizing, and managing documents such as contracts, invoices, and HR files. AI models can then analyze these documents to extract key information, detect anomalies, and ensure compliance.

### 4. Research and Development

Research institutions can use Galora to gather and manage scientific data, experimental results, and publications. This data can be processed by AI models to identify trends, generate insights, and accelerate the R&D process.

### 5. Content Management

Media companies can use Galora to manage large volumes of video, audio, and text content. The AI models can transcode media files, generate subtitles, and create metadata to improve content discovery and user experience.

## Prerequisites

To run Galora, you need to have the following dependencies installed:

- Python 3.x
- boto3
- azure-storage-blob
- google-auth
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client
- PyMuPDF
- python-pptx
- moviepy
- speechrecognition
- pydub
- pandas
- ebooklib
- BeautifulSoup4
- docx
- vlc
- requests

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/galora.git
    cd galora
    ```

2. Install the required packages:
    ```sh
    pip install -r prerequisites.txt
    ```

## Usage

### Uploading Files

- To upload a file to Google Drive:
    ```sh
    ./upload_to_gdrive.bat
    ```

- To upload a file to AWS S3:
    ```sh
    ./upload_to_aws.bat
    ```

- To upload a file to Azure Blob Storage:
    ```sh
    ./upload_to_azure.bat
    ```

### Downloading Files

- To download a file from Google Drive:
    ```sh
    ./download_from_gdrive.bat
    ```

- To download a file from AWS S3:
    ```sh
    ./download_from_aws.bat
    ```

- To download a file from Azure Blob Storage:
    ```sh
    ./download_from_azure.bat
    ```

### Transliterating Text Files

- To transliterate a text file:
    ```sh
    ./transliterate_text.bat
    ```

### Creating JSON Files

- To create JSON from a single text file:
    ```sh
    ./create_json_single.bat
    ```

- To create JSON from multiple text files:
    ```sh
    ./create_json_multiple.bat
    ```

### Downloading Entire Directory

- To download an entire directory from cloud storage:
    ```sh
    ./download_directory.bat
    ```

### Transcoding Media Files

- To transcode media files:
    ```sh
    ./transcode_media.bat
    ```

## License

This project is licensed under the GPL 3.0 License - see the LICENSE file for details.

# Simple RAG Flask App

A lightweight Retrieval-Augmented Generation (RAG) application built with Flask, ChromaDB, and Google Gemini. It lets you store custom knowledge in a local vector database and ask questions that are answered using the retrieved context.

## Overview

This project provides a simple web interface for:

- adding custom text documents to a local ChromaDB collection
- retrieving the most relevant stored context
- generating grounded answers with Google Gemini using that retrieved context

It is designed as a small demo or starter project for experimenting with local RAG workflows without needing a complex backend.

## Features

- Local vector storage with ChromaDB
- Persistent database storage under the chroma_db folder
- Web UI for adding documents and asking questions
- Gemini-based answer generation grounded in retrieved context
- Simple REST-style endpoints for integration

## Project Structure

- app.py: Main Flask application, routes, ChromaDB initialization, and Gemini integration
- templates/index.html: Frontend UI for adding documents and submitting queries
- requirements.txt: Python dependencies
- chroma_db/: Local persistent ChromaDB storage
- .env: Environment variables such as your Gemini API key (not committed to source control if present)

## Requirements

- Python 3.10+
- A valid Google Gemini API key
- Internet access for the initial model and dependency download

## Installation

1. Open the project folder
2. Create and activate a virtual environment

   On Windows PowerShell:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   On Bash:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a .env file in the project root with your Gemini API key:

   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## Running the Application

Start the app with:

```bash
python app.py
```

Then open your browser at:

```text
http://127.0.0.1:5000/
```

## How It Works

### 1. Add knowledge

From the web interface, enter:

- a document ID
- the text content to store

The app sends this data to the /add_document endpoint, which stores the content in ChromaDB.

### 2. Ask a question

Enter a question in the query box. The backend:

1. searches the ChromaDB collection for the two most relevant stored documents
2. builds a prompt with that retrieved context
3. sends the prompt to Gemini for a grounded answer

## API Endpoints

### GET /

Returns the main web interface.

### POST /add_document

Adds a document to the local vector database.

Request body:

```json
{
  "id": "doc_1",
  "text": "Your knowledge text here"
}
```

### POST /query

Queries the vector database and generates an answer.

Request body:

```json
{
  "query": "What information do you have about this topic?"
}
```

## Notes

- The vector database is stored locally in the chroma_db folder, so data persists between runs.
- The first run may take longer because ChromaDB and the embedding-related components are being initialized.
- This is a simple starter project and does not include user authentication, production deployment configuration, or advanced document chunking.

## Example Usage

1. Launch the app
2. Add a document such as company policies or project notes
3. Ask a question related to that content
4. Review the response and the retrieved context shown in the UI

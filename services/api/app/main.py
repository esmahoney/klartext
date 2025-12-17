from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
import base64

# =============================================================================
# API Documentation
# =============================================================================

API_DESCRIPTION = """
## KlarText API

**Turn complex German/English text into easy-to-understand language.**

KlarText is an accessibility-first tool designed for people who get overwhelmed by long sentences, 
legal/bureaucratic phrasing, or technical language. This includes people with:
- Reading or cognitive difficulties
- Dyslexia
- Non-native speakers
- Anyone who needs simpler text

### How It Works

1. **Send text** via paste, PDF upload, or URL
2. **Choose a difficulty level** (very_easy, easy, medium)
3. **Get simplified text** back — optionally with audio (TTS)

### Important Notes

⚠️ KlarText produces "easy language" simplifications. It is **not** certified "Leichte Sprache" 
and does not guarantee legal/medical/financial accuracy. Always consult professionals for 
important decisions.

### Quick Start

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/simplify",
    json={
        "text": "Your complex text here...",
        "target_lang": "de",
        "level": "easy"
    }
)
print(response.json()["simplified_text"])
```
"""

TAGS_METADATA = [
    {
        "name": "Health",
        "description": "Health check endpoint for monitoring and orchestration. "
                       "Use this to verify the API is running and responsive.",
    },
    {
        "name": "Simplification",
        "description": "**Core feature** — Transform complex text into easy-to-understand language. "
                       "Supports German and English with three difficulty levels.",
    },
    {
        "name": "Ingestion",
        "description": "Extract text from various sources (PDF files, web URLs) so it can be simplified. "
                       "Use these endpoints to get text, then send it to `/v1/simplify`.",
    },
    {
        "name": "TTS",
        "description": "**Text-to-Speech** — Convert simplified text to audio. "
                       "Essential for accessibility: helps users with dyslexia, visual impairments, "
                       "or anyone who prefers listening.",
    },
]

app = FastAPI(
    title="KlarText API",
    description=API_DESCRIPTION,
    version="0.1.0",
    openapi_tags=TAGS_METADATA,
    license_info={
        "name": "Non-Commercial Use",
        "url": "https://github.com/klartext/klartext#license",
    },
    contact={
        "name": "KlarText Team",
    },
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request/Response Models
# =============================================================================

class SimplifyRequest(BaseModel):
    """Request body for text simplification."""
    
    text: str = Field(
        min_length=1,
        max_length=40000,
        description="The complex text to simplify. Can be German or English.",
        json_schema_extra={"example": "Der Antragsteller muss die erforderlichen Unterlagen innerhalb der gesetzlich vorgeschriebenen Frist einreichen."}
    )
    source_lang: Optional[str] = Field(
        default=None,
        pattern="^(de|en)$",
        description="Source language of the input text. If not provided, will be auto-detected. Options: `de` (German), `en` (English)."
    )
    target_lang: str = Field(
        default="de",
        pattern="^(de|en)$",
        description="Target language for the simplified output. Options: `de` (German), `en` (English).",
        json_schema_extra={"example": "de"}
    )
    level: str = Field(
        default="easy",
        pattern="^(very_easy|easy|medium)$",
        description="""Simplification level:
        
- **very_easy**: Very short sentences (8-10 words max), defines all uncommon words in parentheses, extra whitespace between paragraphs, uses bullet points
- **easy**: Short sentences (12-15 words), clear structure with headings, minimal jargon, active voice
- **medium**: Plain language with normal sentence length, avoids complex structures, technical terms only when necessary""",
        json_schema_extra={"example": "easy"}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Der Antragsteller muss die erforderlichen Unterlagen innerhalb der gesetzlich vorgeschriebenen Frist einreichen.",
                    "target_lang": "de",
                    "level": "very_easy"
                }
            ]
        }
    }


class SimplifyResponse(BaseModel):
    """Response containing the simplified text."""
    
    simplified_text: str = Field(
        description="The simplified version of the input text, written in easy-to-understand language."
    )
    key_points: Optional[list[str]] = Field(
        default=None,
        description="Optional list of 2-3 key points summarizing the main ideas. Useful for quick understanding."
    )
    warnings: list[str] = Field(
        default=[],
        description="Any warnings about the simplification (e.g., 'contains_legal_content', 'very_long_input_chunked')."
    )


class PDFIngestResponse(BaseModel):
    """Response from PDF text extraction."""
    
    extracted_text: str = Field(
        description="The full text content extracted from the PDF document."
    )
    pages: int = Field(
        description="Number of pages in the PDF."
    )
    warnings: list[str] = Field(
        default=[],
        description="Warnings about the extraction (e.g., 'page_3_appears_to_be_image_only', 'password_protected')."
    )


class URLIngestRequest(BaseModel):
    """Request body for URL content extraction."""
    
    url: HttpUrl = Field(
        description="The webpage URL to extract article content from. The API will fetch the page and extract the main content, removing navigation, ads, and other boilerplate.",
        json_schema_extra={"example": "https://example.com/news/article"}
    )


class URLIngestResponse(BaseModel):
    """Response from URL content extraction."""
    
    extracted_text: str = Field(
        description="The main article/content text extracted from the webpage, with boilerplate removed."
    )
    title: Optional[str] = Field(
        default=None,
        description="The page or article title, if detected."
    )
    warnings: list[str] = Field(
        default=[],
        description="Warnings about the extraction (e.g., 'paywall_detected', 'content_may_be_incomplete')."
    )


class TTSRequest(BaseModel):
    """Request body for text-to-speech conversion."""
    
    text: str = Field(
        min_length=1,
        max_length=5000,
        description="The text to convert to speech. Should be the simplified text for best results.",
        json_schema_extra={"example": "Sie müssen diese Dokumente mitbringen. Das ist wichtig."}
    )
    lang: str = Field(
        default="de",
        pattern="^(de|en)$",
        description="Language for speech synthesis. Affects voice selection and pronunciation. Options: `de` (German), `en` (English).",
        json_schema_extra={"example": "de"}
    )


class TTSResponse(BaseModel):
    """Response containing the generated audio."""
    
    audio_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded audio data. Decode and save as the specified format to play."
    )
    audio_url: Optional[str] = Field(
        default=None,
        description="URL to the audio file (if stored externally). Use this for streaming playback."
    )
    format: str = Field(
        default="mp3",
        description="Audio format of the response. Currently always 'mp3'."
    )


# =============================================================================
# Health Check
# =============================================================================

@app.get(
    "/healthz",
    tags=["Health"],
    summary="Health check",
    response_description="Returns ok:true if the API is healthy",
)
def healthz():
    """
    **Health check endpoint** for monitoring and container orchestration.
    
    Use this endpoint to:
    - Verify the API is running
    - Configure Docker/Kubernetes health checks
    - Set up load balancer health probes
    
    Returns `{"ok": true}` when healthy.
    """
    return {"ok": True}


# =============================================================================
# Simplify Endpoint
# =============================================================================

@app.post(
    "/v1/simplify",
    response_model=SimplifyResponse,
    tags=["Simplification"],
    summary="Simplify text into easy language",
    response_description="The simplified text with optional key points",
)
def simplify(req: SimplifyRequest):
    """
    **Core feature** — Transform complex text into easy-to-understand language.
    
    This is the main endpoint of KlarText. Send any complex German or English text 
    and receive a simplified version appropriate for people with reading difficulties.
    
    ## How it works
    
    1. Text is analyzed for language (or uses provided `source_lang`)
    2. Long texts are automatically chunked to stay within LLM limits
    3. Each chunk is simplified according to the selected `level`
    4. Results are recombined into coherent output
    
    ## Simplification Levels
    
    | Level | Sentence Length | Style |
    |-------|-----------------|-------|
    | **very_easy** | 8-10 words max | Defines all uncommon words, bullet points, extra spacing |
    | **easy** | 12-15 words | Clear structure, headings, minimal jargon |
    | **medium** | Normal length | Plain language, avoids complex structures |
    
    ## Guidelines followed
    
    - ✅ Short sentences, common words
    - ✅ Explains technical terms when unavoidable
    - ✅ Preserves meaning — no invented facts
    - ✅ Adds "not professional advice" note for legal/medical/financial content
    - ❌ Does NOT add new information
    - ❌ Does NOT guarantee certified "Leichte Sprache"
    
    ## Example
    
    **Input (German legal text):**
    > "Der Antragsteller muss die erforderlichen Unterlagen innerhalb der gesetzlich vorgeschriebenen Frist einreichen."
    
    **Output (level: very_easy):**
    > "Sie müssen Papiere abgeben. Das müssen Sie bis zu einem bestimmten Tag tun. Der Tag steht im Gesetz."
    """
    # TODO: Implement chunking + LLM adapter
    # Placeholder implementation
    return SimplifyResponse(
        simplified_text=f"[{req.target_lang}/{req.level}] {req.text}",
        key_points=["This is a placeholder response"],
        warnings=["placeholder_response"],
    )


# =============================================================================
# PDF Ingestion Endpoint
# =============================================================================

@app.post(
    "/v1/ingest/pdf",
    response_model=PDFIngestResponse,
    tags=["Ingestion"],
    summary="Extract text from PDF",
    response_description="Extracted text content and metadata",
)
async def ingest_pdf(
    file: UploadFile = File(
        ...,
        description="PDF file to extract text from (max 10MB recommended)"
    )
):
    """
    **Extract text from an uploaded PDF file** so it can be simplified.
    
    Many official documents (government forms, legal notices, medical reports) come as PDFs. 
    This endpoint extracts the text content so you can then simplify it with `/v1/simplify`.
    
    ## Supported PDFs
    
    - ✅ Text-based PDFs (most common)
    - ✅ Multi-page documents
    - ⚠️ Scanned/image PDFs (limited — may return warning)
    - ❌ Password-protected PDFs (will return error)
    
    ## Workflow
    
    ```
    1. Upload PDF → /v1/ingest/pdf
    2. Get extracted_text from response
    3. Send extracted_text → /v1/simplify
    4. (Optional) Send simplified_text → /v1/tts
    ```
    
    ## Warnings
    
    The response may include warnings such as:
    - `page_X_appears_to_be_image_only` — Some pages may need OCR
    - `document_is_very_long` — Consider simplifying in sections
    - `extraction_may_be_incomplete` — Complex layouts may lose some text
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # TODO: Implement PDF extraction with PyMuPDF
    # Placeholder implementation
    content = await file.read()
    
    return PDFIngestResponse(
        extracted_text=f"[Placeholder] Extracted text from {file.filename} ({len(content)} bytes)",
        pages=1,
        warnings=["placeholder_response", "pdf_extraction_not_implemented"],
    )


# =============================================================================
# URL Ingestion Endpoint (Stretch Goal)
# =============================================================================

@app.post(
    "/v1/ingest/url",
    response_model=URLIngestResponse,
    tags=["Ingestion"],
    summary="Extract article text from URL",
    response_description="Extracted article content and metadata",
)
def ingest_url(req: URLIngestRequest):
    """
    **Extract main article text from a webpage** (stretch goal).
    
    Users often want to simplify news articles, government pages, or medical information 
    without manually copying text. This endpoint fetches the URL and intelligently extracts 
    just the main content.
    
    ## What gets extracted
    
    - ✅ Main article body text
    - ✅ Article title
    - ❌ Navigation menus (removed)
    - ❌ Advertisements (removed)
    - ❌ Sidebars, footers (removed)
    - ❌ Comments sections (removed)
    
    ## How it works
    
    Uses [trafilatura](https://github.com/adbar/trafilatura) for intelligent content extraction. 
    This library is specifically designed for extracting article content from news sites, 
    blogs, and documentation pages.
    
    ## Limitations
    
    - ⚠️ Paywalled content cannot be accessed
    - ⚠️ JavaScript-heavy sites may not extract fully
    - ⚠️ Some complex layouts may lose content
    
    ## Workflow
    
    ```
    1. Send URL → /v1/ingest/url
    2. Get extracted_text from response
    3. Send extracted_text → /v1/simplify
    ```
    """
    # TODO: Implement URL extraction with trafilatura
    # Placeholder implementation
    return URLIngestResponse(
        extracted_text=f"[Placeholder] Extracted text from {req.url}",
        title="Placeholder Title",
        warnings=["placeholder_response", "url_extraction_not_implemented"],
    )


# =============================================================================
# Text-to-Speech Endpoint
# =============================================================================

@app.post(
    "/v1/tts",
    response_model=TTSResponse,
    tags=["TTS"],
    summary="Convert text to speech",
    response_description="Audio data as base64 or URL",
)
def text_to_speech(req: TTSRequest):
    """
    **Convert text to speech audio** — essential for accessibility.
    
    This endpoint generates audio from text, allowing users to listen instead of 
    (or while) reading. This is critical for:
    
    - 👁️ Users with visual impairments
    - 📖 Users with dyslexia (often comprehend better when hearing)
    - 🚗 Multitasking users who want to listen
    - 🌍 Non-native speakers practicing pronunciation
    
    ## Best practice
    
    Send the **simplified text** (output from `/v1/simplify`) rather than the original 
    complex text. The simplified version will be clearer when spoken.
    
    ## Response format
    
    The response includes either:
    - `audio_base64`: Base64-encoded audio data (decode and play directly)
    - `audio_url`: URL to stream/download the audio file
    
    Currently returns MP3 format.
    
    ## Language support
    
    | Language | Code | Voice |
    |----------|------|-------|
    | German | `de` | Native German voice |
    | English | `en` | Native English voice |
    
    ## Example usage (JavaScript)
    
    ```javascript
    const response = await fetch('/v1/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: 'Hallo Welt', lang: 'de' })
    });
    const { audio_base64 } = await response.json();
    const audio = new Audio(`data:audio/mp3;base64,${audio_base64}`);
    audio.play();
    ```
    """
    # TODO: Implement TTS with configurable provider
    # Placeholder: return empty audio with warning
    return TTSResponse(
        audio_base64=None,
        audio_url=None,
        format="mp3",
    )

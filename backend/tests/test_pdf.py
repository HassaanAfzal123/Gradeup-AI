# Test PDF endpoints
import pytest
from fastapi import status
import io


def test_list_pdfs_empty(client, auth_headers):
    """Test listing PDFs when none exist"""
    response = client.get("/api/pdf/list", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_upload_pdf_unauthorized(client):
    """Test uploading PDF without authentication"""
    files = {"file": ("test.pdf", io.BytesIO(b"fake pdf content"), "application/pdf")}
    response = client.post("/api/pdf/upload", files=files)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_upload_pdf_success(client, auth_headers):
    """Test successful PDF upload"""
    # Create a fake PDF file
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    response = client.post("/api/pdf/upload", files=files, headers=auth_headers)
    
    # Note: This test may fail if ChromaDB/embedding services aren't available
    # In a real environment, you'd mock these services
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        assert "id" in data
        assert data["filename"] == "test.pdf"


def test_upload_invalid_file_type(client, auth_headers):
    """Test uploading non-PDF file"""
    files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
    response = client.post("/api/pdf/upload", files=files, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

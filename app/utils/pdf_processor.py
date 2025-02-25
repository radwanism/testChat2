import os
import uuid
import shutil
from typing import List, Dict
from fastapi import UploadFile

class PDFProcessor:
    def __init__(self, upload_dir: str = "uploads"):
        """Initialize the PDF processor with an upload directory."""
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
        
    async def save_uploaded_pdfs(self, files: List[UploadFile]) -> List[str]:
        """
        Save uploaded PDF files to the upload directory and return their paths.
        
        Args:
            files: List of uploaded PDF files
            
        Returns:
            List of file paths where the PDFs are saved
        """
        saved_paths = []
        
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                continue
                
            # Create a unique filename to avoid collisions
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            saved_paths.append(file_path)
            
        return saved_paths
    
    def get_saved_pdfs(self) -> List[Dict[str, str]]:
        """
        Get a list of all saved PDFs in the upload directory.
        
        Returns:
            List of dictionaries with PDF file information
        """
        pdf_files = []
        
        for filename in os.listdir(self.upload_dir):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(self.upload_dir, filename)
                # Get the original filename by removing the UUID prefix
                original_name = "_".join(filename.split("_")[1:])
                
                pdf_files.append({
                    "filename": original_name,
                    "path": file_path
                })
                
        return pdf_files
    
    def delete_pdf(self, filename: str) -> bool:
        """
        Delete a PDF file from the upload directory.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            file_path = os.path.join(self.upload_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
            
        return False
    
    def delete_all_pdfs(self) -> bool:
        """
        Delete all PDF files from the upload directory.
        
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            for filename in os.listdir(self.upload_dir):
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.isfile(file_path) and filename.lower().endswith('.pdf'):
                    os.remove(file_path)
            return True
        except Exception:
            return False
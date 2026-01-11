import { useState } from 'react'
import { uploadDocument } from '../services/api'
import './DocumentUpload.css'

function DocumentUpload() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
      if (validTypes.includes(selectedFile.type) || selectedFile.name.endsWith('.pdf') || selectedFile.name.endsWith('.docx') || selectedFile.name.endsWith('.txt')) {
        setFile(selectedFile)
        setMessage({ type: '', text: '' })
      } else {
        setMessage({ type: 'error', text: 'Please upload a PDF, DOCX, or TXT file' })
        setFile(null)
      }
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setMessage({ type: 'error', text: 'Please select a file first' })
      return
    }

    setUploading(true)
    setMessage({ type: '', text: '' })

    try {
      const result = await uploadDocument(file)
      setMessage({ 
        type: 'success', 
        text: `✅ ${result.filename} uploaded successfully! ${result.chunks_created} chunks created.` 
      })
      setFile(null)
      // Reset file input
      document.getElementById('file-input').value = ''
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to upload file. Please try again.' 
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="document-upload">
      <div className="upload-card">
        <h2>📁 Document Upload</h2>
        <p className="upload-description">
          Upload your syllabus, notes, or textbooks (PDF, DOCX, TXT)
        </p>
        
        <div className="upload-area">
          <input
            id="file-input"
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            disabled={uploading}
            className="file-input"
          />
          {file && (
            <div className="file-info">
              <span>📄 {file.name}</span>
              <span className="file-size">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            </div>
          )}
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="upload-button"
        >
          {uploading ? 'Uploading...' : 'Upload Document'}
        </button>

        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentUpload


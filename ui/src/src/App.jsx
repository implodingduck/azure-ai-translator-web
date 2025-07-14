import { useState, useEffect } from 'react'
import { BackendApi } from './BackendApi.js'
import { config } from './config.js'
import './App.css'

function App() {
  const [directories, setDirectories] = useState([])
  const [selectedDirectory, setSelectedDirectory] = useState('')
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [newDirectoryName, setNewDirectoryName] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState('')

  // Authentication object - using config for flexibility
  const auth = {
    user: {
      access_token: config.auth.mockToken
    }
  }

  // Initialize API client with configuration
  const api = new BackendApi(config.apiBaseUrl, auth)

  useEffect(() => {
    loadDirectories()
  }, [])

  const loadDirectories = async () => {
    setLoading(true)
    setError('')
    try {
      const result = await api.listDirectories()
      setDirectories(result || [])
    } catch (err) {
      setError('Failed to load directories: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadFiles = async (directory) => {
    setLoading(true)
    setError('')
    try {
      const result = await api.listFiles(directory)
      setFiles(result || [])
      setSelectedDirectory(directory)
    } catch (err) {
      setError('Failed to load files: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const createDirectory = async () => {
    if (!newDirectoryName.trim()) {
      setError('Please enter a directory name')
      return
    }
    
    setLoading(true)
    setError('')
    try {
      await api.createDirectory(newDirectoryName.trim())
      setNewDirectoryName('')
      await loadDirectories()
      setError('')
    } catch (err) {
      setError('Failed to create directory: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    
    if (!file) {
      setSelectedFile(null)
      return
    }

    // Validate file size
    if (file.size > config.upload.maxFileSize) {
      setError(`File size exceeds ${Math.round(config.upload.maxFileSize / (1024 * 1024))}MB limit`)
      event.target.value = ''
      return
    }

    // Validate file type (optional - you may want to allow all file types)
    // if (!config.upload.allowedTypes.includes(file.type)) {
    //   setError('File type not supported')
    //   event.target.value = ''
    //   return
    // }

    setSelectedFile(file)
    setUploadStatus('')
    setUploadProgress(0)
    setError('')
  }

  const uploadFile = async () => {
    if (!selectedFile) {
      setError('Please select a file')
      return
    }
    if (!selectedDirectory) {
      setError('Please select a directory')
      return
    }

    setLoading(true)
    setError('')
    setUploadStatus('Uploading file...')
    
    try {
      // Upload file directly through the API
      const uploadResponse = await api.uploadFile(selectedDirectory, selectedFile)
      
      setUploadStatus('Upload successful!')
      setSelectedFile(null)
      document.getElementById('file-input').value = ''
      // Reload files in the current directory
      if (selectedDirectory) {
        await loadFiles(selectedDirectory)
      }
    } catch (err) {
      setError('Failed to upload file: ' + err.message)
      setUploadStatus('Upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="app-container">
        <header className="app-header">
          <h1>Azure AI Translator - File Management</h1>
        </header>

        {error && <div className="error-message">{error}</div>}

        <div className="main-content">
          {/* Directory Management Section */}
          <div className="section">
            <h2>Directories</h2>
            <div className="directory-controls">
              <input
                type="text"
                placeholder="New directory name"
                value={newDirectoryName}
                onChange={(e) => setNewDirectoryName(e.target.value)}
                className="input"
              />
              <button 
                onClick={createDirectory} 
                disabled={loading}
                className="btn btn-primary"
              >
                Create Directory
              </button>
              <button 
                onClick={loadDirectories} 
                disabled={loading}
                className="btn btn-secondary"
              >
                Refresh
              </button>
            </div>
            
            <div className="directory-list">
              {loading && directories.length === 0 ? (
                <div className="loading">Loading directories...</div>
              ) : (
                directories.map((dir, index) => (
                  <div 
                    key={index}
                    className={`directory-item ${selectedDirectory === dir ? 'selected' : ''}`}
                    onClick={() => loadFiles(dir)}
                  >
                    📁 {dir}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* File Upload Section */}
          <div className="section">
            <h2>File Upload</h2>
            <div className="upload-controls">
              <input
                id="file-input"
                type="file"
                onChange={handleFileSelect}
                className="file-input"
              />
              <button 
                onClick={uploadFile} 
                disabled={loading || !selectedFile || !selectedDirectory}
                className="btn btn-primary"
              >
                Upload File
              </button>
            </div>
            {selectedFile && (
              <div className="file-info">
                Selected: {selectedFile.name} ({Math.round(selectedFile.size / 1024)}KB)
              </div>
            )}
            {uploadStatus && (
              <div className="upload-status">{uploadStatus}</div>
            )}
            {!selectedDirectory && (
              <div className="warning">Please select a directory first</div>
            )}
          </div>

          {/* Files in Directory Section */}
          {selectedDirectory && (
            <div className="section">
              <h2>Files in "{selectedDirectory}"</h2>
              <div className="files-list">
                {loading && files.length === 0 ? (
                  <div className="loading">Loading files...</div>
                ) : files.length === 0 ? (
                  <div className="no-files">No files in this directory</div>
                ) : (
                  files.map((file, index) => (
                    <div key={index} className="file-item">
                      📄 {file}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default App

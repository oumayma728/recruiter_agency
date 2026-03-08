import { useState } from 'react';
import { Upload, FileText, X } from 'lucide-react';

function FileUpload({ onFileSelect, onAnalyze, loading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError(null);
      onFileSelect(file);
    } else {
      setError('Please select a PDF file');
      setSelectedFile(null);
      onFileSelect(null);
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setError(null);
    onFileSelect(null);
  };

  return (
    <div className="mb-8 max-w-md mx-auto">
      <div className="bg-white shadow-lg rounded-xl p-6 transition-transform hover:scale-[1.01]">
        
        {!selectedFile ? (
          <label
            htmlFor="file-input"
            className="flex flex-col items-center justify-center gap-4 p-12 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-primary hover:bg-blue-50 transition-all text-center"
          >
            <Upload className="text-primary" size={48} />
            <h3 className="text-xl font-semibold text-gray-800">Upload Resume</h3>
            <p className="text-gray-600">Drag & drop or select a PDF file</p>
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
            />
            <span className="mt-2 inline-block bg-primary text-black px-6 py-2 rounded-lg font-medium hover:bg-primary/90 transition-all">
              Choose File
            </span>
          </label>
        ) : (
          <>
            <div className="flex items-center gap-4 p-4 bg-blue-50 rounded-xl mb-4 shadow-sm">
              <FileText className="text-primary flex-shrink-0" size={40} />
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-800 truncate">{selectedFile.name}</p>
                <p className="text-sm text-gray-600">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
              <button
                onClick={handleRemove}
                className="flex items-center justify-center p-2 bg-red-500 text-black rounded-lg hover:bg-red-600 transition-colors flex-shrink-0"
              >
                <X size={20} />
              </button>
            </div>

            <button
              onClick={onAnalyze}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-primary text-black font-semibold py-3 rounded-lg hover:bg-primary/90 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? 'Analyzing...' : 'Analyze Resume'}
            </button>
          </>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-center text-sm">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default FileUpload;
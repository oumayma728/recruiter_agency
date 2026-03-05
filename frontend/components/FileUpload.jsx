import { useState } from 'react';
import { Upload, FileText, X } from 'lucide-react';

function FileUpload({ onFileSelect, selectedFile, onRemove }) {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf') {
        onFileSelect(file);
      } else {
        alert('Please upload a PDF file');
      }
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div className="w-full max-w-lg mx-auto">
      {!selectedFile ? (
        <div
          className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-8 text-center transition 
          ${dragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 bg-white"}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload size={48} className="text-gray-500 mb-4" />
          <h3 className="text-lg font-semibold text-gray-800">Upload Resume</h3>
          <p className="text-gray-500 text-sm mb-4">
            Drag and drop your PDF resume here, or click to browse
          </p>

          <input
            type="file"
            accept=".pdf"
            onChange={handleChange}
            className="hidden"
            id="file-input"
          />

          <label
            htmlFor="file-input"
            className="cursor-pointer bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Choose File
          </label>
        </div>
      ) : (
        <div className="flex items-center justify-between bg-gray-100 p-4 rounded-lg shadow-sm">
          <div className="flex items-center gap-3">
            <FileText size={32} className="text-blue-600" />
            <div>
              <p className="font-medium text-gray-800">{selectedFile.name}</p>
              <p className="text-sm text-gray-500">
                {(selectedFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
          </div>

          <button
            onClick={onRemove}
            className="p-2 rounded-full hover:bg-red-100 text-red-600 transition"
          >
            <X size={20} />
          </button>
        </div>
      )}
    </div>
  );
}

export default FileUpload;
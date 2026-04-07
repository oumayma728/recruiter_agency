import { useState } from 'react';
import { FileText, X, CheckCircle, MapPin, Briefcase, Sparkles, ArrowRight, Shield, Zap, Award } from 'lucide-react';

function FileUpload({
  onFileSelect, // Callback when file is selected
  onAnalyze, //Callback when analyze button is clicked
  loading,
  selectedCountry,
  onCountryChange,
  selectedScraperSource,
  onScraperSourceChange,
}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);
  const [notCvError, setNotCvError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const countries = [
    { code: 'usa', label: 'United States', flag: '🇺🇸', region: 'North America' },
    { code: 'tunisia', label: 'Tunisia', flag: '🇹🇳', region: 'Africa' },
    { code: 'france', label: 'France', flag: '🇫🇷', region: 'Europe' },
    { code: 'germany', label: 'Germany', flag: '🇩🇪', region: 'Europe' },
    { code: 'uk', label: 'United Kingdom', flag: '🇬🇧', region: 'Europe' },
    { code: 'canada', label: 'Canada', flag: '🇨🇦', region: 'North America' },
    { code: 'india', label: 'India', flag: '🇮🇳', region: 'Asia' },
    { code: 'remote', label: 'Remote / Worldwide', flag: '🌍', region: 'Global' }
  ];

  const handleFileChange = async (e) => {
    const file = e.target.files[0]; //get the first file from the input
    if (file && file.type === 'application/pdf') { //checks if the file is a PDF
      // Simulate upload progress
      for (let i = 0; i <= 100; i += 20) {
        setTimeout(() => setUploadProgress(i), i * 10);
      }
      setTimeout(() => {
        validateAndSetFile(file);
        setUploadProgress(100);
      }, 500);
    } else if (file) {
      setError('Please select a PDF file');
      setSelectedFile(null);
      onFileSelect(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    validateAndSetFile(file);
  };

  const validateAndSetFile = (file) => {
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError(null);
      onFileSelect(file);
    } else if (file) {
      setError('Please select a PDF file');
      setSelectedFile(null);
      onFileSelect(null);
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setError(null);
    onFileSelect(null);
    setUploadProgress(0);
  };

  const groupedCountries = countries.reduce((acc, country) => {
    if (!acc[country.region]) acc[country.region] = [];
    acc[country.region].push(country);
    return acc;
  }, {});

  return (
    <div className="w-full max-w-4xl mx-auto px-2 sm:px-4">
      {/* Animated Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 -z-10" />
      
      <div className="relative">
        {/* Floating Decorative Elements */}
        <div className="absolute -top-10 -right-10 w-40 h-40 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse" />
        <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse delay-1000" />
        
        {/* Main Card */}
        <div className="relative bg-white/95 backdrop-blur rounded-3xl shadow-2xl overflow-hidden transform transition-all duration-500 hover:shadow-2xl border border-white/70">
          
          {/* Premium Header with Pattern */}
          <div className="relative bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 px-8 py-6 overflow-hidden">
            <div className="absolute inset-0 opacity-10">
              <div className="absolute inset-0" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                backgroundRepeat: 'repeat'
              }} />
            </div>
            
            <div className="relative flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                <div className="bg-white/10 backdrop-blur-sm p-3 rounded-2xl">
                  <Briefcase className="text-black" size={28} />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-black tracking-tight">AI Resume Analyzer</h1>
                  <p className="text-black/70 text-sm mt-1">Intelligent job matching powered by AI</p>
                </div>
              </div>
            
            </div>
          </div>

          {/* Content */}
          <div className="p-4 sm:p-6 lg:p-8">
            
            {/* Country Selector - Premium Design */}
            <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
                <MapPin size={12} className="inline mr-2 mb-0.5" />
                Job Location
              </label>
              <div className="relative group">
                <select
                  value={selectedCountry || 'usa'}
                  onChange={(e) => onCountryChange(e.target.value)}
                  className="w-full px-5 py-3.5 bg-gray-50 border-2 border-gray-100 rounded-2xl text-gray-700 text-sm 
                          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                          appearance-none cursor-pointer hover:bg-gray-100 transition-all duration-200
                          group-hover:border-gray-200 font-medium"
                >
                  {Object.entries(groupedCountries).map(([region, regionCountries]) => (
                    <optgroup key={region} label={`— ${region} —`} className="font-bold text-gray-600">
                      {regionCountries.map((country) => (
                        <option key={country.code} value={country.code} className="font-normal">
                          {country.flag} {country.label}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>

              </div>

              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 ">
                Job Source
              </label>
              <div className="relative group">
                <select
                  value={selectedScraperSource || 'platforms'}
                  onChange={(e) => onScraperSourceChange(e.target.value)}
                  className="w-full px-5 py-3.5 bg-gray-50 border-2 border-gray-100 rounded-2xl text-gray-700 text-sm 
                          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                          appearance-none cursor-pointer hover:bg-gray-100 transition-all duration-200
                          group-hover:border-gray-200 font-medium"
                >
                  <option value="platforms">Other platforms (Linkedin , Google jobs , indeed)</option>
                  <option value="keejob">Keejob (Tunisia) </option>
                </select>
              </div>
            </div>
            </div>
</div>
            {/* File Upload Area */}
            {!selectedFile ? (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`
                  relative group cursor-pointer
                  border-2 rounded-2xl p-12 text-center transition-all duration-300
                  ${isDragging 
                    ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-indigo-50 scale-[0.99]' 
                    : 'border-gray-200 bg-gradient-to-br from-gray-50 to-white hover:border-blue-400 hover:shadow-xl'
                  }
                `}
              >
                <input
                  id="file-input"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />
                
                <label
                  htmlFor="file-input"
                  className="cursor-pointer block"
                >
                  <div className="flex flex-col items-center gap-4">
                    {/* Animated Icon */}
                    <div className={`
                      relative p-5 rounded-full transition-all duration-300
                      ${isDragging 
                        ? 'bg-blue-100 scale-110' 
                        : 'bg-gray-100 group-hover:bg-blue-100 group-hover:scale-110'
                      }
                    `}>
                      <FileText className="text-slate-700" size={28} />
                    </div>
                  </div>
                </label>
              </div>
            ) : (
              /* Selected File Preview - Premium */
              <div className="space-y-6 p-4 animate-in slide-in-from-bottom duration-300">
                {/* File Info Card */}
                <div className="relative overflow-hidden bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl border border-green-200 p-5">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-green-200 rounded-full filter blur-3xl opacity-20" />
                  
                  <div className="relative flex items-center gap-4">
                    <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl shadow-lg">
                      <FileText className="text-black" size={24} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-bold text-gray-800 truncate text-base">{selectedFile.name}</p>
                      <div className="flex items-center gap-3 mt-1">
                        <p className="text-xs text-gray-500">
                          {(selectedFile.size / 1024).toFixed(0)} KB
                        </p>
                        <div className="flex items-center gap-1">
                          <CheckCircle size={12} className="text-green-600" />
                          <span className="text-xs text-green-600 font-medium">Ready for analysis</span>
                        </div>
                      </div>
                      {/* Progress Bar */}
                      {uploadProgress < 100 && (
                        <div className="mt-3 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full transition-all duration-300"
                            style={{ width: `${uploadProgress}%` }}
                          />
                        </div>
                      )}
                    </div>
                    <button
                      onClick={handleRemove}
                      className="p-2 hover:bg-white/50 rounded-xl transition-all group"
                      title="Remove file"
                    >
                      <X size={18} className="text-gray-400 group-hover:text-red-500 transition-colors" />
                    </button>
                  </div>
                </div>

              </div>
            )}

            {/* Analyze Button - Always visible */}
            <button
              onClick={onAnalyze}
              disabled={loading || !selectedFile}
              className="
                mt-5 w-full relative group overflow-hidden
                bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900
                text-black font-semibold py-4 rounded-2xl
                transition-all duration-300
                hover:shadow-2xl hover:scale-[1.02]
                active:scale-[0.98]
                disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100
              "
            >
              {/* Animated Shine Effect */}
              <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent" />

              <span className="relative flex items-center justify-center gap-3">
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Analyzing your resume...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={20} className="text-yellow-400" />
                    <span>{selectedFile ? 'Analyze Resume' : 'Upload a PDF to Analyze'}</span>
                    <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </span>
            </button>

            {/* Error Message - Premium */}
            {error && (
              <div className="mt-5 p-4 bg-gradient-to-r from-red-50 to-rose-50 border border-red-200 rounded-2xl animate-in slide-in-from-top duration-200">
                <div className="flex items-center gap-3">
                  <div className="p-1.5 bg-red-100 rounded-lg">
                    <X size={16} className="text-red-600" />
                  </div>
                  <p className="text-red-700 text-sm font-medium flex-1">{error}</p>
                </div>
              </div>
            )}
            {notCvError && (
            <div className="mt-5 p-4 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-300 rounded-2xl animate-in slide-in-from-top duration-200">
              <div className="flex items-start gap-3">
                <div className="p-1.5 bg-amber-100 rounded-lg">
                  <FileText size={16} className="text-amber-700" />
                </div>
                <div className="flex-1">
                  <p className="text-amber-800 font-semibold text-sm">Invalid Document</p>
                  <p className="text-amber-700 text-sm mt-0.5">{notCvError}</p>
                  <p className="text-amber-600 text-xs mt-2">
                    Please upload a standard resume/CV with sections like: Experience, Education, Skills
                  </p>
                </div>
                <button onClick={() => setNotCvError(null)} className="p-1 hover:bg-amber-100 rounded-lg transition-colors">
                  <X size={14} className="text-amber-600" />
                </button>
              </div>
            </div>
)}
          </div>

        
        </div>
      </div>
  );
}

export default FileUpload;
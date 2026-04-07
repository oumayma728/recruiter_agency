import { useState } from "react";
import { analyzeResume } from "../services/api";
import FileUpload from "../components/FileUpload";
import LoadingSpinner from "../components/LoadingSpinner";
import SkillsAnalysis from "../components/SkillsAnalysis";
import JobMatches from "../components/JobMatches";
import Recommendations from "../components/Recommendations";

import {
  AlertCircle,
  CheckCircle,
  Brain,
  Briefcase,
  Lightbulb
} from "lucide-react";

function App() {
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedCountry, setSelectedCountry] = useState('usa');
  const [selectedScraperSource, setSelectedScraperSource] = useState('platforms');
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("skills");

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setResults(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      const response = await analyzeResume(selectedFile, selectedCountry, selectedScraperSource);

      if (response.success) {
        setResults(response.data);
      } else {
        throw new Error("Analysis failed");
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Failed to analyze resume"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen px-4 py-8 sm:px-6 lg:px-10 relative overflow-hidden">
      <div className="pointer-events-none absolute -top-24 -left-20 h-72 w-72 rounded-full bg-cyan-200/40 blur-3xl" />
      <div className="pointer-events-none absolute top-16 -right-24 h-80 w-80 rounded-full bg-emerald-200/35 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-sky-200/30 blur-3xl" />

      {/* HEADER */}
      <header className="relative text-center text-slate-900 mb-10 sm:mb-12">
        <p className="inline-flex items-center rounded-full border border-cyan-300/70 bg-white/70 px-4 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-cyan-700">
          Intelligent Hiring Workspace
        </p>
        <h1 className="mt-4 text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight">
          AI Recruiter Studio
        </h1>
        <p className="mt-3 text-sm sm:text-base text-slate-600 max-w-2xl mx-auto">
          Analyse CV, matching intelligent et recommandations actionnables dans une interface claire et moderne.
        </p>
      </header>

      <main className="relative max-w-6xl mx-auto space-y-7 sm:space-y-8">

        {/* Upload Card */}
        <div className="card p-4 sm:p-6 lg:p-8">
          <FileUpload
            onFileSelect={handleFileSelect}
            onAnalyze={handleAnalyze}
            loading={loading}
            selectedCountry={selectedCountry}
            onCountryChange={setSelectedCountry}
            selectedScraperSource={selectedScraperSource}
            onScraperSourceChange={setSelectedScraperSource}
          />
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50/90 border border-red-300 rounded-2xl p-5 sm:p-6 flex items-start gap-4 shadow-sm">
            <AlertCircle className="text-red-500" size={28} />
            <p className="text-red-700 font-medium">{error}</p>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="card p-10">
            <LoadingSpinner />
          </div>
        )}

        {/* Results */}
        {results && !loading && (
          <div className="space-y-6">

            {/* Success */}
            <div className="bg-emerald-50/90 border border-emerald-300 rounded-2xl p-5 sm:p-6 flex items-center gap-3 shadow-sm">
              <CheckCircle className="text-green-600" size={28} />
              <span className="text-lg font-semibold text-green-700">
                Analysis Completed Successfully
              </span>
            </div>

            {/* Tabs */}
            <div className="card p-2 sm:p-3">

              <div className="flex flex-col sm:flex-row gap-2">

              <button
                onClick={() => setActiveTab("skills")}
                className={`flex items-center justify-center gap-2 flex-1 py-3 rounded-xl transition-all duration-200 ${
                  activeTab === "skills"
                    ? "bg-gradient-to-r from-cyan-600 to-sky-600 text-white shadow-lg"
                    : "text-gray-600 hover:bg-slate-100"
                }`}
              >
                <Brain size={18} />
                Skills
              </button>

              <button
                onClick={() => setActiveTab("matches")}
                className={`flex items-center justify-center gap-2 flex-1 py-3 rounded-xl transition-all duration-200 ${
                  activeTab === "matches"
                    ? "bg-gradient-to-r from-cyan-600 to-sky-600 text-white shadow-lg"
                    : "text-gray-600 hover:bg-slate-100"
                }`}
              >
                <Briefcase size={18} />
                Job Matches
              </button>

              <button
                onClick={() => setActiveTab("recommendations")}
                className={`flex items-center justify-center gap-2 flex-1 py-3 rounded-xl transition-all duration-200 ${
                  activeTab === "recommendations"
                    ? "bg-gradient-to-r from-cyan-600 to-sky-600 text-white shadow-lg"
                    : "text-gray-600 hover:bg-slate-100"
                }`}
              >
                <Lightbulb size={18} />
                Recommendations
              </button>
              </div>

            </div>

            {/* Content */}
            <div className="card p-4 sm:p-6 lg:p-8">

              {activeTab === "skills" && (
                <SkillsAnalysis data={results} />
              )}

              {activeTab === "matches" && (
                <JobMatches data={results} />
              )}

              {activeTab === "recommendations" && (
                <Recommendations data={results} />
              )}

            </div>

          </div>
        )}

      </main>
    </div>
  );
}

export default App;
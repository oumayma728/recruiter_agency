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
      const response = await analyzeResume(selectedFile);

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
    <div className="min-h-screen p-6">

      {/* HEADER */}
      <header className="text-center text-black mb-12">
        <h1 className="text-2xl font-bold mb-4">
          🤖 AI Recruiter
        </h1>
        <p className="text-lg opacity-90">
          Multi-Agent AI Resume Intelligence Platform
        </p>
      </header>

      <main className="max-w-4xl mx-auto space-y-8">

        {/* Upload Card */}
        <div className=" p-8">
          <FileUpload
            onFileSelect={handleFileSelect}
            onAnalyze={handleAnalyze}
            loading={loading}
          />
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-400 rounded-xl p-6 flex items-center gap-4">
            <AlertCircle className="text-red-500" size={28} />
            <p className="text-red-700 font-medium">{error}</p>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="bg-white rounded-2xl shadow-lg p-10">
            <LoadingSpinner />
          </div>
        )}

        {/* Results */}
        {results && !loading && (
          <div className="space-y-6">

            {/* Success */}
            <div className="bg-green-50 border border-green-400 rounded-xl p-6 flex items-center gap-3">
              <CheckCircle className="text-green-600" size={28} />
              <span className="text-lg font-semibold text-green-700">
                Analysis Completed Successfully
              </span>
            </div>

            {/* Tabs */}
            <div className="bg-white rounded-2xl shadow-lg p-2 flex">

              <button
                onClick={() => setActiveTab("skills")}
                className={`flex items-center justify-center gap-2 flex-1 py-3 rounded-xl transition ${
                  activeTab === "skills"
                    ? "bg-indigo-600 text-white shadow"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <Brain size={18} />
                Skills
              </button>

              <button
                onClick={() => setActiveTab("matches")}
                className={`flex items-center justify-center gap-2 flex-1 py-3 rounded-xl transition ${
                  activeTab === "matches"
                    ? "bg-indigo-600 text-white shadow"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <Briefcase size={18} />
                Job Matches
              </button>

              <button
                onClick={() => setActiveTab("recommendations")}
                className={`flex items-center justify-center gap-2 flex-1 py-3 rounded-xl transition ${
                  activeTab === "recommendations"
                    ? "bg-indigo-600 text-white shadow"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <Lightbulb size={18} />
                Recommendations
              </button>

            </div>

            {/* Content */}
            <div className="bg-white rounded-2xl shadow-xl p-8">

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
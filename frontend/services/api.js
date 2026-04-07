import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Get all jobs
export const getJobs = async () => {
  const response = await api.get("/api/jobs");
  return response.data;
};

// Get job by id
export const getJob = async (id) => {
  const response = await api.get(`/api/jobs/${id}`);
  return response.data;
};

// Analyze resume
export const analyzeResume = async (file, country = 'usa') => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("country", country);

  const response = await api.post("/api/analyze_resume", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

// Health check
export const healthCheck = async () => {
  const response = await api.get("/api/health");
  return response.data;
};

export default api;
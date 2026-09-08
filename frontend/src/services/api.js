import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const getAnalysisHistory = () =>
  api.get("/api/v1/analysis");

export const analyzeProject = (path) =>
  api.post("/api/v1/analyze", { path });

export const uploadProject = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/api/v1/analyze/upload", form);
};

export const getSource = (file, line) =>
  api.get("/api/v1/source", {
    params: { file, line },
  });

export const explainIssue = (issue, source) =>
  api.post("/api/v1/ai/explain", {
    issue,
    source,
  });
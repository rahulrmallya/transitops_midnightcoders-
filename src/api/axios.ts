import axios from "axios";

// Base HTTP client for future REST integration. No live calls are made yet.
export const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;

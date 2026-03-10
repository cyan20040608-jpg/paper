import http from "./http";

export function analyzeSentiment(payload) {
  return http.post("/sentiment/analyze", payload);
}

export function fetchHealth() {
  return http.get("/health");
}

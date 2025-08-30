// helpers/getDomain.js
import { isProduction } from "./isProduction";

/**
 * Environment-specific domain helper:
 * - Dev: Uses localhost URLs (React: 3000, Backend: 8000 – matches FastAPI's default port)
 * - Production: Uses your deployed frontend (e.g., Vercel) and Railway backend URLs
 */
export const getDomain = () => {
  // --------------------------
  // PRODUCTION URLs (UPDATE THESE!)
  // --------------------------
  if (isProduction()) {
    return {
      // Your deployed React frontend (e.g., Vercel, Netlify)
      frontendDomain: "https://your-fashion-agent-frontend.vercel.app", 
      // Your Railway backend URL (from Railway → Deployments → "View Deployment")
      backendDomain: "https://your-fashion-rag-backend.up.railway.app", 
    };
  }

  // --------------------------
  // DEVELOPMENT URLs (LOCALHOST)
  // --------------------------
  // Matches:
  // - React dev server: npm start → http://localhost:3000
  // - FastAPI dev server: uvicorn app.main:app --port 8000 → http://localhost:8000
  return {
    frontendDomain: "http://localhost:3000", 
    backendDomain: "http://localhost:8000", 
  };
};
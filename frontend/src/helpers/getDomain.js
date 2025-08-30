// helpers/getDomain.js
import { isProduction } from "./isProduction";

/**
 * Environment-specific domain helper:
 * - Dev: Uses localhost URLs (React: 3000, Backend: 8000)
 * - Production: Uses environment variables set in Vercel
 */
export const getDomain = () => {
  // --------------------------
  // PRODUCTION URLs (FROM ENVIRONMENT VARIABLES)
  // --------------------------
  if (isProduction()) {
    // Use REACT_APP_API_URL from Vercel environment variables
    const backendUrl = process.env.REACT_APP_API_URL || "https://llm-rag-fashion-agent-production.up.railway.app";
    const frontendUrl = process.env.REACT_APP_FRONTEND_URL || window.location.origin;
    
    return {
      frontendDomain: frontendUrl,
      backendDomain: backendUrl,
    };
  }

  // --------------------------
  // DEVELOPMENT URLs (LOCALHOST)
  // --------------------------
  return {
    frontendDomain: "http://localhost:3000", 
    backendDomain: "http://localhost:8000", 
  };
};
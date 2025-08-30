/**
 * Helper to detect if the app is running in production environment.
 * React auto-sets NODE_ENV to "production" when built with `npm run build`.
 * In development (npm start), NODE_ENV is "development".
 * 
 * @returns {boolean} True if production, false if development
 */
export const isProduction = () => {
  // Fallback to "development" if NODE_ENV is undefined (edge cases)
  return process.env.NODE_ENV === "production";
};
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#8B5CF6', // Purple - fashionable and modern
        secondary: '#EC4899', // Pink - complementary to purple
        neutral: {
          100: '#F3F4F6',
          800: '#1F2937',
          900: '#111827'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
    
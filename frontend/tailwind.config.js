/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef6ff',
          100: '#d9e8ff',
          200: '#b5d2ff',
          300: '#86b5ff',
          400: '#4f8cff',
          500: '#2b6bff',
          600: '#1f51d6',
          700: '#1d45ad',
          800: '#1d3b86',
          900: '#1b3168',
        },
        surface: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5f0',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1f2937',
          900: '#111827',
        },
      },
      boxShadow: {
        card: '0 10px 30px -20px rgba(15, 23, 42, 0.35)',
      },
    },
  },
  plugins: [],
}

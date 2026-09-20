/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bloop: {
          50: '#f0f4ff',
          100: '#e0eaff',
          200: '#c7d7fe',
          300: '#a4bcfe',
          400: '#8098f9',
          500: '#6172f3',
          600: '#444ce7',
          700: '#3538cd',
          800: '#2d31a6',
          900: '#282a82',
          950: '#19194e',
        },
        quantum: {
          50: '#fbf5ff',
          100: '#f4e8ff',
          200: '#ebd5ff',
          300: '#ddb5ff',
          400: '#c784ff',
          500: '#ad4efa',
          600: '#932aee',
          700: '#7a19ce',
          800: '#6517a6',
          900: '#531685',
          950: '#380660',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}

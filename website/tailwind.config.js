/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        ninho: {
          50: '#fef7ed',
          100: '#fcecd4',
          200: '#f8d5a8',
          300: '#f3b871',
          400: '#ed9038',
          500: '#e87316',
          600: '#d9590c',
          700: '#b4420d',
          800: '#903512',
          900: '#742e12',
          950: '#3f1407',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
      },
    },
  },
  plugins: [],
}

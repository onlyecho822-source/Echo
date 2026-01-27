/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
    "./pages/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#ffffff',
          100: '#fafafa',
          200: '#f5f5f5',
          300: '#e5e5e5',
          400: '#d4d4d4',
          500: '#a3a3a3',
          600: '#737373',
          700: '#525252',
          800: '#404040',
          900: '#262626',
          950: '#171717',
        },
        accent: {
          navy: '#00205b',
          gold: '#ffd700',
          green: '#4d8055',
          red: '#b22234',
          silver: '#c0c0c0',
        },
        success: {
          light: '#d1fae5',
          DEFAULT: '#10b981',
          dark: '#065f46',
        },
        warning: {
          light: '#fef3c7',
          DEFAULT: '#f59e0b',
          dark: '#92400e',
        },
        danger: {
          light: '#fee2e2',
          DEFAULT: '#ef4444',
          dark: '#991b1b',
        },
        info: {
          light: '#dbeafe',
          DEFAULT: '#3b82f6',
          dark: '#1e40af',
        },
        hazard: {
          burnPit: '#ff6b35',
          agentOrange: '#ff8c00',
          lejeune: '#4169e1',
          radiation: '#9d00ff',
        },
        progress: {
          empty: '#e5e5e5',
          low: '#ef4444',
          medium: '#f59e0b',
          good: '#eab308',
          complete: '#10b981',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        military: ['Oswald', 'Impact', 'sans-serif'],
      },
      boxShadow: {
        'military': '0 4px 6px -1px rgba(0, 32, 91, 0.2)',
      },
    },
  },
  plugins: [],
}

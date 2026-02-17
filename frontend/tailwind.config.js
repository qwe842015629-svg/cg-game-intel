/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Legacy cyber classes remapped to theme tokens
        cyber: {
          black: 'hsl(var(--theme-light-foreground) / <alpha-value>)',
          dark: 'hsl(var(--card) / <alpha-value>)',
          blue: 'hsl(var(--muted) / <alpha-value>)',
          neon: {
            green: 'hsl(var(--primary) / <alpha-value>)',
            pink: 'hsl(var(--secondary) / <alpha-value>)',
            blue: 'hsl(var(--accent) / <alpha-value>)',
            purple: 'hsl(var(--secondary) / <alpha-value>)',
          },
        },
        // Keep existing colors for compatibility
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      boxShadow: {
        'neon-green': 'var(--surface-shadow)',
        'neon-pink': 'var(--surface-shadow)',
        'neon-blue': 'var(--surface-shadow)',
      },
      dropShadow: {
        'glow-green': '0 8px 22px color-mix(in srgb, var(--primary-color) 26%, transparent)',
        'glow-pink': '0 8px 22px color-mix(in srgb, var(--secondary-color) 26%, transparent)',
        'glow-blue': '0 8px 22px color-mix(in srgb, var(--primary-color) 20%, transparent)',
      },
      animation: {
        'glitch': 'glitch 1s infinite',
        'scan': 'scan 2s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'flicker': 'flicker 0.15s infinite',
      },
      keyframes: {
        glitch: {
          '0%, 100%': { transform: 'translate(0)' },
          '33%': { transform: 'translate(-2px, 2px)', filter: 'hue-rotate(90deg)' },
          '66%': { transform: 'translate(2px, -2px)', filter: 'hue-rotate(-90deg)' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '50%': { opacity: '0.5' },
          '100%': { transform: 'translateY(100%)', opacity: '0' },
        },
        flicker: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
      },
    },
  },
  plugins: [
    function ({ addUtilities }) {
      addUtilities({
        '.clip-path-hexagon-inset': {
          'clip-path': 'polygon(15% 0%, 85% 0%, 100% 50%, 85% 100%, 15% 100%, 0% 50%)',
        },
        '.clip-path-hexagon': {
          'clip-path': 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
        },
      });
    },
  ],
}

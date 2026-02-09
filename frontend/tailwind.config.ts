import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#030712", // Rich Black
        surface: "#111827",    // Slate 900
        primary: "#3b82f6",    // Blue 500
        secondary: "#8b5cf6",  // Violet 500
        accent: "#10b981",     // Emerald 500
        danger: "#ef4444",     // Red 500
      },
    },
  },
  plugins: [],
};
export default config;
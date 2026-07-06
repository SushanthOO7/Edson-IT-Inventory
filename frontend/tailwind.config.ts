import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}", "./types/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#d6b28f",
        panel: "#181817",
        panelSoft: "#24231f",
        line: "rgba(255, 255, 255, 0.10)",
        accent: {
          DEFAULT: "#d9ff3f",
          strong: "#efff7a",
        },
        alert: {
          DEFAULT: "#caa57f",
          strong: "#f0d0ad",
        },
      },
      boxShadow: {
        glow: "0 24px 80px rgba(0, 0, 0, 0.35)",
      },
      backgroundImage: {
        "aurora-grid": "linear-gradient(135deg, rgba(202, 165, 127, 0.92), rgba(112, 94, 73, 0.98))",
      },
    },
  },
  plugins: [],
};

export default config;

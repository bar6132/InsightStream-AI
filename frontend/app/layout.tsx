import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "@/components/Navbar"; // הוספנו את ה-Navbar

export const metadata: Metadata = {
  title: "InsightStream AI",
  description: "AI Powered News Aggregator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {/* ה-Navbar נמצא בתוך ה-Provider כדי שיהיה לו גישה למשתמש */}
          <Navbar /> 
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
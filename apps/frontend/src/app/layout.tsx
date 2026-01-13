import type { Metadata } from "next";
import "./globals.css";
import Menu from "../components/templates/Menu";
import ChatbotWidget from "../components/templates/ChatbotWidget";

export const metadata: Metadata = {
  title: "Draco Cheng - Senior Software Engineer",
  description: "I craft resilient, accessible web apps with a focus on delightful developer experience and measurable outcomes.",
};

// Minimal layout for the frontend app with a top menu
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Menu />
        {children}
        <ChatbotWidget />
      </body>
    </html>
  );
}

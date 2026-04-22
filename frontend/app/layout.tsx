import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "sweOS Companion",
  description: "AI-native software engineering companion for profile direction, skills, and goals.",
};

type RootLayoutProps = Readonly<{
  children: React.ReactNode;
}>;

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

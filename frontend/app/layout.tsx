import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "sweOS Epic 1",
  description: "Profile, skills, and goals workspace for software engineers.",
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

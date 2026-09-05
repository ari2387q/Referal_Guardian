import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/AuthContext";
import { HeaderNav } from "@/components/HeaderNav";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Referral Guardian MVP",
  description: "AI-assisted referral continuity & coordination system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-50 text-slate-900 min-h-screen flex flex-col`}>
        <AuthProvider>
          {/* Dynamic Navigation Header with Supabase Auth */}
          <HeaderNav />

          {/* Main Content */}
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>

          {/* Footer */}
          <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
            Referral Guardian &copy; 2026 — AI Referral Continuity & Coordination System (Operational Only)
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}

import type {
  Metadata,
} from "next";
import type {
  ReactNode,
} from "react";

import "./globals.css";

import AppShell from "@/components/layout/AppShell";
import {
  ToastProvider,
} from "@/components/ui/ToastProvider";

export const metadata: Metadata = {
  title: "AURA",
  description:
    "Autonomous AI runtime and orchestration workspace.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <ToastProvider>
          <AppShell>
            {children}
          </AppShell>
        </ToastProvider>
      </body>
    </html>
  );
}
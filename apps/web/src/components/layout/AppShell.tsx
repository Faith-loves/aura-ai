"use client";

import {
  useState,
} from "react";

import Sidebar from "./Sidebar";
import Topbar from "./Topbar";


export default function AppShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const [
    mobileSidebarOpen,
    setMobileSidebarOpen,
  ] = useState(false);

  return (
    <div
      className="
        min-h-screen
        overflow-x-hidden
        bg-[#070B14]
        text-white
      "
    >
      <Sidebar
        mobileOpen={
          mobileSidebarOpen
        }
        onMobileClose={() =>
          setMobileSidebarOpen(
            false
          )
        }
      />

      <Topbar
        onOpenSidebar={() =>
          setMobileSidebarOpen(
            true
          )
        }
      />

      <main
        className="
          min-h-screen
          pt-[72px]
          transition-[margin]
          duration-200
          lg:ml-[260px]
        "
      >
        <div
          className="
            aura-grid-background
            min-h-[calc(100vh-72px)]
            px-4
            py-5
            sm:px-5
            sm:py-6
            lg:p-7
          "
        >
          {children}
        </div>
      </main>

      {mobileSidebarOpen && (
        <button
          type="button"
          aria-label="Close navigation"
          className="
            fixed
            inset-0
            z-30
            bg-black/60
            backdrop-blur-[2px]
            lg:hidden
          "
          onClick={() =>
            setMobileSidebarOpen(
              false
            )
          }
        />
      )}
    </div>
  );
}
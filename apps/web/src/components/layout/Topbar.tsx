"use client";

import {
  Bell,
  Menu,
  Search,
  Sparkles,
} from "lucide-react";

import BackendStatus from "@/components/system/BackendStatus";


type TopbarProps = {
  onOpenSidebar: () => void;
};


export default function Topbar({
  onOpenSidebar,
}: TopbarProps) {
  return (
    <header
      className="
        fixed
        left-0
        right-0
        top-0
        z-30
        flex
        h-[72px]
        items-center
        justify-between
        border-b
        border-[#162036]
        bg-[#070B14]/85
        px-4
        backdrop-blur-xl
        sm:px-6
        lg:left-[260px]
        lg:px-7
      "
    >
      <div
        className="
          flex
          min-w-0
          items-center
          gap-3
        "
      >
        <button
          type="button"
          aria-label="Open navigation"
          onClick={onOpenSidebar}
          className="
            flex
            h-10
            w-10
            shrink-0
            items-center
            justify-center
            rounded-xl
            border
            border-[#1D2942]
            bg-[#0D1321]
            text-[#94A3B8]
            transition
            hover:border-[#334155]
            hover:text-white
            focus-visible:outline-none
            focus-visible:ring-2
            focus-visible:ring-[#7C5CFC]
            lg:hidden
          "
        >
          <Menu size={19} />
        </button>

        <div className="min-w-0">
          <p
            className="
              m-0
              text-[10px]
              font-medium
              uppercase
              tracking-[0.14em]
              text-[#64748B]
              sm:text-[11px]
              sm:tracking-[0.16em]
            "
          >
            AURA RUNTIME
          </p>

          <h2
            className="
              m-0
              mt-0.5
              max-w-[160px]
              truncate
              text-xs
              font-medium
              text-[#CBD5E1]
              sm:max-w-[280px]
              sm:text-sm
              md:max-w-none
            "
          >
            Autonomous Intelligence Workspace
          </h2>
        </div>
      </div>

      <div
        className="
          flex
          shrink-0
          items-center
          gap-2
          sm:gap-3
        "
      >
        <button
          type="button"
          aria-label="Search AURA"
          className="
            hidden
            h-9
            w-[240px]
            items-center
            gap-2
            rounded-xl
            border
            border-[#1D2942]
            bg-[#0D1321]
            px-3
            text-left
            text-xs
            text-[#64748B]
            transition
            hover:border-[#334155]
            focus-visible:outline-none
            focus-visible:ring-2
            focus-visible:ring-[#7C5CFC]
            xl:flex
          "
        >
          <Search size={15} />

          <span className="flex-1">
            Search AURA
          </span>

          <span
            className="
              rounded-md
              border
              border-[#26334D]
              bg-[#111A2E]
              px-1.5
              py-1
              text-[10px]
              text-[#64748B]
            "
          >
            ⌘ K
          </span>
        </button>

        <div className="hidden sm:block">
          <BackendStatus />
        </div>

        <button
          type="button"
          aria-label="Notifications"
          className="
            relative
            hidden
            h-10
            w-10
            items-center
            justify-center
            rounded-xl
            border
            border-[#1D2942]
            bg-[#0D1321]
            text-[#94A3B8]
            transition
            hover:border-[#334155]
            hover:text-white
            focus-visible:outline-none
            focus-visible:ring-2
            focus-visible:ring-[#7C5CFC]
            sm:flex
          "
        >
          <Bell size={18} />

          <span
            aria-hidden="true"
            className="
              absolute
              right-2
              top-2
              h-1.5
              w-1.5
              rounded-full
              bg-[#7C5CFC]
            "
          />
        </button>

        <div
          aria-label="AURA"
          className="
            flex
            h-9
            w-9
            shrink-0
            items-center
            justify-center
            rounded-xl
            bg-gradient-to-br
            from-[#7C5CFC]
            to-[#6045D8]
            text-white
            shadow-lg
            shadow-[#7C5CFC]/20
            sm:h-10
            sm:w-10
          "
        >
          <Sparkles
            size={17}
          />
        </div>
      </div>
    </header>
  );
}
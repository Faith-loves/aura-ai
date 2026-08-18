"use client";

import type {
  ElementType,
} from "react";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BrainCircuit,
  CheckCircle2,
  ClipboardList,
  Gauge,
  History,
  MemoryStick,
  MessageSquareText,
  PlayCircle,
  Settings,
  ShieldCheck,
  Sparkles,
  Wrench,
  X,
} from "lucide-react";


const workspaceNavigation = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: Gauge,
  },
  {
    label: "Chat",
    href: "/chat",
    icon: MessageSquareText,
  },
  {
    label: "Tasks",
    href: "/tasks",
    icon: ClipboardList,
  },
  {
    label: "Plans",
    href: "/plans",
    icon: BrainCircuit,
  },
  {
    label: "Executions",
    href: "/executions",
    icon: PlayCircle,
  },
];


const systemNavigation = [
  {
    label: "Memory",
    href: "/memory",
    icon: MemoryStick,
  },
  {
    label: "Tools",
    href: "/tools",
    icon: Wrench,
  },
  {
    label: "Approvals",
    href: "/approvals",
    icon: CheckCircle2,
  },
  {
    label: "Audit",
    href: "/audit",
    icon: History,
  },
  {
    label: "System",
    href: "/system",
    icon: Activity,
  },
];


type NavigationItem = {
  label: string;
  href: string;
  icon: ElementType;
};


type SidebarProps = {
  mobileOpen: boolean;
  onMobileClose: () => void;
};


export default function Sidebar({
  mobileOpen,
  onMobileClose,
}: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      aria-label="AURA navigation"
      className={`
        fixed
        inset-y-0
        left-0
        z-50
        flex
        w-[260px]
        flex-col
        border-r
        border-[#162036]
        bg-[#090E19]/98
        backdrop-blur-xl
        transition-transform
        duration-200
        ease-out
        lg:z-40
        lg:translate-x-0
        ${
          mobileOpen
            ? "translate-x-0"
            : "-translate-x-full"
        }
      `}
    >
      <div
        className="
          flex
          h-[72px]
          shrink-0
          items-center
          gap-3
          border-b
          border-[#162036]
          px-4
          sm:px-5
          lg:px-6
        "
      >
        <div
          className="
            flex
            h-10
            w-10
            shrink-0
            items-center
            justify-center
            rounded-xl
            bg-[#7C5CFC]
            text-white
            shadow-lg
            shadow-[#7C5CFC]/20
          "
        >
          <Sparkles
            size={20}
            strokeWidth={2}
          />
        </div>

        <div className="min-w-0 flex-1">
          <div
            className="
              text-lg
              font-semibold
              tracking-tight
              text-white
            "
          >
            AURA
          </div>

          <div
            className="
              truncate
              text-[11px]
              font-medium
              uppercase
              tracking-[0.18em]
              text-[#64748B]
            "
          >
            AUTONOMOUS AI
          </div>
        </div>

        <button
          type="button"
          aria-label="Close navigation"
          onClick={onMobileClose}
          className="
            flex
            h-9
            w-9
            shrink-0
            items-center
            justify-center
            rounded-xl
            text-[#64748B]
            transition
            hover:bg-white/[0.05]
            hover:text-white
            focus-visible:outline-none
            focus-visible:ring-2
            focus-visible:ring-[#7C5CFC]
            lg:hidden
          "
        >
          <X size={19} />
        </button>
      </div>

      <div
        className="
          flex-1
          overflow-y-auto
          overscroll-contain
          px-3
          py-5
        "
      >
        <SidebarSection
          label="WORKSPACE"
          items={workspaceNavigation}
          pathname={pathname}
          onNavigate={onMobileClose}
        />

        <div className="my-5">
          <div className="aura-divider" />
        </div>

        <SidebarSection
          label="SYSTEM"
          items={systemNavigation}
          pathname={pathname}
          onNavigate={onMobileClose}
        />
      </div>

      <div
        className="
          shrink-0
          border-t
          border-[#162036]
          p-3
        "
      >
        <NavLink
          href="/settings"
          icon={Settings}
          label="Settings"
          pathname={pathname}
          onNavigate={onMobileClose}
        />

        <div
          className="
            mt-3
            rounded-xl
            border
            border-[#162036]
            bg-[#0D1321]
            p-3
          "
        >
          <div
            className="
              flex
              items-center
              gap-3
            "
          >
            <div
              className="
                flex
                h-9
                w-9
                shrink-0
                items-center
                justify-center
                rounded-lg
                bg-[#22C55E]/10
                text-[#22C55E]
              "
            >
              <ShieldCheck size={18} />
            </div>

            <div className="min-w-0">
              <p
                className="
                  m-0
                  text-xs
                  font-medium
                  text-white
                "
              >
                Protected
              </p>

              <p
                className="
                  mt-0.5
                  truncate
                  text-[11px]
                  text-[#64748B]
                "
              >
                Safety layer active
              </p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}


function SidebarSection({
  label,
  items,
  pathname,
  onNavigate,
}: {
  label: string;
  items: NavigationItem[];
  pathname: string;
  onNavigate: () => void;
}) {
  return (
    <div>
      <p
        className="
          mb-2
          px-3
          text-[10px]
          font-semibold
          uppercase
          tracking-[0.18em]
          text-[#475569]
        "
      >
        {label}
      </p>

      <div className="space-y-1">
        {items.map((item) => (
          <NavLink
            key={item.href}
            {...item}
            pathname={pathname}
            onNavigate={onNavigate}
          />
        ))}
      </div>
    </div>
  );
}


function NavLink({
  href,
  icon: Icon,
  label,
  pathname,
  onNavigate,
}: NavigationItem & {
  pathname: string;
  onNavigate: () => void;
}) {
  const active =
    pathname === href
    || pathname.startsWith(
      `${href}/`
    );

  return (
    <Link
      href={href}
      aria-current={
        active
          ? "page"
          : undefined
      }
      onClick={onNavigate}
      className={`
        group
        flex
        items-center
        gap-3
        rounded-xl
        px-3
        py-2.5
        text-sm
        font-medium
        transition-all
        duration-150
        focus-visible:outline-none
        focus-visible:ring-2
        focus-visible:ring-[#7C5CFC]
        ${
          active
            ? "bg-[#7C5CFC]/15 text-white"
            : "text-[#94A3B8] hover:bg-white/[0.04] hover:text-white"
        }
      `}
    >
      <div
        className={`
          flex
          h-8
          w-8
          shrink-0
          items-center
          justify-center
          rounded-lg
          transition
          ${
            active
              ? "bg-[#7C5CFC]/15 text-[#9B87FF]"
              : "text-[#64748B] group-hover:text-[#94A3B8]"
          }
        `}
      >
        <Icon size={17} />
      </div>

      <span
        className="
          min-w-0
          flex-1
          truncate
        "
      >
        {label}
      </span>

      {active && (
        <span
          aria-hidden="true"
          className="
            h-1.5
            w-1.5
            shrink-0
            rounded-full
            bg-[#7C5CFC]
          "
        />
      )}
    </Link>
  );
}
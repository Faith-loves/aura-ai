import Link from "next/link";

import {
  FileQuestion,
  Home,
} from "lucide-react";

import Button from "@/components/ui/Button";


export default function NotFound() {
  return (
    <div
      className="
        mx-auto
        flex
        min-h-[calc(100vh-130px)]
        w-full
        max-w-[900px]
        items-center
        justify-center
      "
    >
      <div
        className="
          flex
          w-full
          flex-col
          items-center
          justify-center
          rounded-2xl
          border
          border-[#1D2942]
          bg-[#0D1321]/75
          px-6
          py-14
          text-center
          shadow-2xl
          shadow-black/20
          backdrop-blur-xl
        "
      >
        <div
          className="
            flex
            h-16
            w-16
            items-center
            justify-center
            rounded-2xl
            border
            border-[#7C5CFC]/20
            bg-[#7C5CFC]/10
            text-[#9B87FF]
          "
        >
          <FileQuestion
            size={28}
            strokeWidth={1.7}
          />
        </div>

        <p
          className="
            mb-0
            mt-6
            text-xs
            font-semibold
            uppercase
            tracking-[0.18em]
            text-[#7C5CFC]
          "
        >
          404
        </p>

        <h1
          className="
            mb-0
            mt-2
            text-2xl
            font-semibold
            tracking-[-0.03em]
            text-white
            sm:text-3xl
          "
        >
          Workspace not found
        </h1>

        <p
          className="
            mb-0
            mt-3
            max-w-md
            text-sm
            leading-6
            text-[#94A3B8]
          "
        >
          The AURA page you requested does not
          exist or may have been moved.
        </p>

        <Link
          href="/dashboard"
          className="mt-7"
        >
          <Button>
            <Home size={16} />

            Return to Dashboard
          </Button>
        </Link>
      </div>
    </div>
  );
}
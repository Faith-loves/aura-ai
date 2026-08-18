import type {
  ReactNode,
} from "react";


export default function SettingsSection({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <section
      className="
        rounded-[20px]
        border
        border-[#1D2942]
        bg-[#0D1321]/78
        p-5
        shadow-2xl
        shadow-black/20
        sm:p-6
      "
    >
      <div
        className="
          mb-6
          border-b
          border-[#162036]
          pb-5
        "
      >
        <h2
          className="
            m-0
            text-xl
            font-semibold
            tracking-[-0.02em]
            text-white
          "
        >
          {title}
        </h2>

        <p
          className="
            mb-0
            mt-1.5
            max-w-2xl
            text-sm
            leading-6
            text-[#94A3B8]
          "
        >
          {description}
        </p>
      </div>

      <div
        className="
          divide-y
          divide-[#162036]
        "
      >
        {children}
      </div>
    </section>
  );
}
import type {
  ReactNode,
} from "react";


type PageHeaderProps = {
  eyebrow?: string;

  title: string;

  description?: string;

  actions?: ReactNode;

  badges?: ReactNode;
};


export default function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  badges,
}: PageHeaderProps) {
  return (
    <header
      className="
        flex
        flex-col
        gap-5
        lg:flex-row
        lg:items-end
        lg:justify-between
      "
    >
      <div className="min-w-0">
        {eyebrow && (
          <p
            className="
              mb-2
              text-[11px]
              font-semibold
              uppercase
              tracking-[0.16em]
              text-[#64748B]
            "
          >
            {eyebrow}
          </p>
        )}

        {badges && (
          <div
            className="
              mb-3
              flex
              flex-wrap
              items-center
              gap-2
            "
          >
            {badges}
          </div>
        )}

        <h1
          className="
            m-0
            text-2xl
            font-semibold
            tracking-[-0.035em]
            text-white
            sm:text-3xl
          "
        >
          {title}
        </h1>

        {description && (
          <p
            className="
              mb-0
              mt-2
              max-w-2xl
              text-sm
              leading-6
              text-[#94A3B8]
            "
          >
            {description}
          </p>
        )}
      </div>

      {actions && (
        <div
          className="
            flex
            shrink-0
            flex-wrap
            items-center
            gap-2
          "
        >
          {actions}
        </div>
      )}
    </header>
  );
}
import Card from "@/components/ui/Card";

function SkeletonBlock({
  className = "",
}: {
  className?: string;
}) {
  return <div className={`animate-pulse rounded-lg bg-[#1D2942]/60 ${className}`} />;
}

export default function DashboardSkeleton() {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
      <section className="rounded-[20px] border border-[#1D2942] bg-[#0D1321]/78 p-6 sm:p-7 lg:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="w-full max-w-3xl">
            <div className="mb-5 flex gap-2">
              <SkeletonBlock className="h-7 w-28 rounded-full" />
              <SkeletonBlock className="h-7 w-24 rounded-full" />
            </div>
            <SkeletonBlock className="h-11 w-full max-w-2xl" />
            <SkeletonBlock className="mt-4 h-5 w-full max-w-xl" />
            <SkeletonBlock className="mt-3 h-5 w-4/5 max-w-lg" />
          </div>
          <SkeletonBlock className="h-10 w-full sm:w-32" />
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Card key={index} className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <SkeletonBlock className="h-4 w-28" />
                <SkeletonBlock className="mt-4 h-8 w-20" />
              </div>
              <SkeletonBlock className="h-10 w-10 rounded-xl" />
            </div>
          </Card>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.85fr)]">
        <Card className="p-5 sm:p-6">
          <SkeletonBlock className="h-6 w-44" />
          <SkeletonBlock className="mt-2 h-4 w-56" />
          <div className="mt-7 rounded-2xl border border-[#162036] bg-[#0A1020]/80 p-5">
            <SkeletonBlock className="h-5 w-24" />
            <SkeletonBlock className="mt-3 h-8 w-full max-w-xl" />
            <SkeletonBlock className="mt-6 h-2 w-full rounded-full" />
            <div className="mt-6 grid gap-3 md:grid-cols-3">
              <SkeletonBlock className="h-20" />
              <SkeletonBlock className="h-20" />
              <SkeletonBlock className="h-20" />
            </div>
          </div>
        </Card>

        <Card className="p-5 sm:p-6">
          <SkeletonBlock className="h-6 w-36" />
          <SkeletonBlock className="mt-2 h-4 w-44" />
          <div className="mt-6 space-y-4">
            {Array.from({ length: 5 }).map((_, index) => (
              <SkeletonBlock key={index} className="h-5 w-full" />
            ))}
          </div>
        </Card>
      </section>
    </div>
  );
}

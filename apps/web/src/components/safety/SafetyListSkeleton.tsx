export default function SafetyListSkeleton() {
  return (
    <div className="space-y-4" aria-label="Loading safety data">
      {[0, 1, 2].map((item) => (
        <div key={item} className="rounded-2xl border border-[#1D2942] bg-[#0D1321]/78 p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-3">
              <div className="h-4 w-32 animate-pulse rounded bg-[#1D2942]" />
              <div className="h-5 w-80 max-w-full animate-pulse rounded bg-[#1D2942]/80" />
              <div className="h-3 w-56 animate-pulse rounded bg-[#1D2942]/60" />
            </div>
            <div className="h-7 w-24 animate-pulse rounded-full bg-[#1D2942]" />
          </div>
        </div>
      ))}
    </div>
  );
}

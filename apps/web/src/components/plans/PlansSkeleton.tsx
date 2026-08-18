import Card from "@/components/ui/Card";

function Block({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-[#1D2942]/60 ${className}`} />;
}

export default function PlansSkeleton() {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {Array.from({ length: 4 }).map((_, index) => (
        <Card key={index} className="p-5">
          <Block className="h-5 w-3/4" />
          <Block className="mt-3 h-4 w-32" />
          <Block className="mt-5 h-2 w-full rounded-full" />
          <div className="mt-5 flex gap-2">
            <Block className="h-9 w-24" />
            <Block className="h-9 w-20" />
          </div>
        </Card>
      ))}
    </div>
  );
}

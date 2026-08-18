import MemoryDetails from "@/components/memory/MemoryDetails";

type MemoryDetailsPageProps = {
  params: Promise<{ memoryId: string }>;
};

export default async function MemoryDetailsPage({ params }: MemoryDetailsPageProps) {
  const { memoryId } = await params;
  return <MemoryDetails memoryId={memoryId} />;
}

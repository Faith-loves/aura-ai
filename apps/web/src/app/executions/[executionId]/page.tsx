import ExecutionDetails from "@/components/executions/ExecutionDetails";

export default async function ExecutionDetailsPage({
  params,
}: {
  params: Promise<{ executionId: string }>;
}) {
  const { executionId } = await params;

  return <ExecutionDetails executionId={executionId} />;
}

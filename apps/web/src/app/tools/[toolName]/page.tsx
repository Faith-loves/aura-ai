import ToolDetails from "@/components/tools/ToolDetails";

type ToolDetailsPageProps = {
  params: Promise<{ toolName: string }>;
};

export default async function ToolDetailsPage({ params }: ToolDetailsPageProps) {
  const { toolName } = await params;
  return <ToolDetails toolName={toolName} />;
}

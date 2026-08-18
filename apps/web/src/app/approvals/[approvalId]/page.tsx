import ApprovalDetails from "@/components/safety/ApprovalDetails";

type ApprovalDetailsPageProps = {
  params: Promise<{ approvalId: string }>;
};

export default async function ApprovalDetailsPage({ params }: ApprovalDetailsPageProps) {
  const { approvalId } = await params;
  return <ApprovalDetails approvalId={approvalId} />;
}

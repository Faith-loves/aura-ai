"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  CheckCircle2,
  Clock,
  ExternalLink,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import {
  Suspense,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import type {
  ReactNode,
} from "react";

import ApprovalStatusBadge from "@/components/safety/ApprovalStatusBadge";
import RiskBadge from "@/components/safety/RiskBadge";
import SafetyListSkeleton from "@/components/safety/SafetyListSkeleton";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";
import PageHeader from "@/components/ui/PageHeader";
import StatusBadge from "@/components/ui/StatusBadge";

import {
  getApprovals,
} from "@/lib/api/safety";

import type {
  ApprovalResponse,
  ApprovalStatus,
} from "@/types/api";


type Filter =
  | "all"
  | ApprovalStatus;


const filters: {
  value: Filter;
  label: string;
}[] = [
  {
    value: "all",
    label: "All",
  },
  {
    value: "pending",
    label: "Pending",
  },
  {
    value: "approved",
    label: "Approved",
  },
  {
    value: "rejected",
    label: "Rejected",
  },
];


function formatLabel(
  value: string
) {
  return value
    .split("_")
    .map(
      (part) =>
        `${part
          .charAt(0)
          .toUpperCase()}${part.slice(
          1
        )}`
    )
    .join(" ");
}


function shortId(
  value: string | null
) {
  if (!value) {
    return "Not linked";
  }

  return value.length > 12
    ? `${value.slice(
        0,
        8
      )}...${value.slice(
        -4
      )}`
    : value;
}


function formatDate(
  value: string | null
) {
  if (!value) {
    return "Not resolved";
  }

  const date =
    new Date(value);

  return Number.isNaN(
    date.getTime()
  )
    ? "Unavailable"
    : date.toLocaleString();
}


function orderApprovals(
  approvals: ApprovalResponse[]
) {
  return [
    ...approvals,
  ].sort(
    (
      left,
      right
    ) =>
      new Date(
        right.requested_at
      ).getTime()
      - new Date(
        left.requested_at
      ).getTime()
  );
}


export default function ApprovalsWorkspace() {
  return (
    <Suspense
      fallback={
        <SafetyListSkeleton />
      }
    >
      <ApprovalsWorkspaceInner />
    </Suspense>
  );
}


function ApprovalsWorkspaceInner() {
  const searchParams =
    useSearchParams();

  const highlightedApprovalId =
    searchParams.get(
      "approval"
    );

  const [
    approvals,
    setApprovals,
  ] = useState<
    ApprovalResponse[]
  >([]);

  const [
    filter,
    setFilter,
  ] = useState<Filter>(
    "all"
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const [
    lastUpdated,
    setLastUpdated,
  ] = useState<
    Date | null
  >(null);


  const loadApprovals =
    useCallback(
      async ({
        refresh = false,
      }: {
        refresh?: boolean;
      } = {}) => {
        if (refresh) {
          setRefreshing(true);
        } else {
          setLoading(true);
        }

        setError(null);

        try {
          const nextApprovals =
            orderApprovals(
              await getApprovals()
            );

          setApprovals(
            nextApprovals
          );

          setFilter(
            highlightedApprovalId
              ? "all"
              : nextApprovals.some(
                  (approval) =>
                    approval.status
                    === "pending"
                )
                ? "pending"
                : "all"
          );

          setLastUpdated(
            new Date()
          );
        } catch (
          nextError
        ) {
          setError(
            nextError
              instanceof Error
              ? nextError.message
              : "Unable to load approvals."
          );
        } finally {
          setLoading(false);
          setRefreshing(false);
        }
      },
      [
        highlightedApprovalId,
      ]
    );


  useEffect(() => {
    const timeoutId =
      window.setTimeout(
        () => {
          void loadApprovals();
        },
        0
      );

    return () =>
      window.clearTimeout(
        timeoutId
      );
  }, [loadApprovals]);


  const pendingCount =
    approvals.filter(
      (approval) =>
        approval.status
        === "pending"
    ).length;


  useEffect(() => {
    if (
      loading
      || !highlightedApprovalId
    ) {
      return;
    }

    const timeoutId =
      window.setTimeout(
        () => {
          document
            .getElementById(
              `approval-${highlightedApprovalId}`
            )
            ?.scrollIntoView({
              behavior:
                "smooth",
              block:
                "center",
            });
        },
        50
      );

    return () =>
      window.clearTimeout(
        timeoutId
      );
  }, [
    highlightedApprovalId,
    loading,
  ]);


  const visibleApprovals =
    useMemo(
      () => {
        if (
          filter === "all"
        ) {
          return approvals;
        }

        return approvals.filter(
          (approval) =>
            approval.status
            === filter
        );
      },
      [
        approvals,
        filter,
      ]
    );


  return (
    <div
      className="
        mx-auto
        flex
        w-full
        max-w-6xl
        flex-col
        gap-6
      "
    >
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
        <PageHeader
          eyebrow="AURA / Approvals"
          title="Approvals"
          description="
            Review actions AURA paused
            before execution.
          "
          badges={
            <StatusBadge
              label={`${pendingCount} Pending`}
              tone={
                pendingCount > 0
                  ? "warning"
                  : "success"
              }
              pulse={
                pendingCount > 0
              }
            />
          }
          actions={
            <>
              <div
                className="
                  hidden
                  text-right
                  sm:block
                "
              >
                <p
                  className="
                    m-0
                    text-[10px]
                    font-medium
                    uppercase
                    tracking-[0.12em]
                    text-[#475569]
                  "
                >
                  Last updated
                </p>

                <p
                  className="
                    mb-0
                    mt-1
                    text-xs
                    text-[#64748B]
                  "
                >
                  {lastUpdated
                    ? lastUpdated
                        .toLocaleTimeString()
                    : "Not yet"}
                </p>
              </div>

              <Button
                type="button"
                variant="secondary"
                aria-label="Refresh approvals"
                disabled={
                  refreshing
                }
                onClick={() =>
                  void loadApprovals({
                    refresh: true,
                  })
                }
              >
                <RefreshCw
                  size={16}
                  className={
                    refreshing
                      ? "animate-spin"
                      : ""
                  }
                />

                {refreshing
                  ? "Refreshing..."
                  : "Refresh"}
              </Button>
            </>
          }
        />
      </section>

      {highlightedApprovalId && (
        <div
          role="status"
          className="
            flex
            flex-col
            gap-2
            rounded-2xl
            border
            border-[#7C5CFC]/35
            bg-[#7C5CFC]/10
            px-4
            py-3
            text-sm
            text-[#C4B5FD]
            sm:flex-row
            sm:items-center
            sm:justify-between
          "
        >
          <span>
            Showing approval
            linked from an
            execution.
          </span>

          <code
            className="
              aura-truncate-id
              text-xs
              text-[#A78BFA]
            "
            title={
              highlightedApprovalId
            }
          >
            {shortId(
              highlightedApprovalId
            )}
          </code>
        </div>
      )}

      <div
        className="
          flex
          flex-wrap
          gap-2
        "
        role="tablist"
        aria-label="Approval filters"
      >
        {filters.map(
          (item) => {
            const active =
              filter
              === item.value;

            return (
              <button
                key={
                  item.value
                }
                type="button"
                role="tab"
                aria-selected={
                  active
                }
                onClick={() =>
                  setFilter(
                    item.value
                  )
                }
                className={`
                  rounded-full
                  border
                  px-4
                  py-2
                  text-sm
                  font-medium
                  transition
                  focus-visible:outline-none
                  focus-visible:ring-2
                  focus-visible:ring-[#7C5CFC]
                  ${
                    active
                      ? "border-[#7C5CFC] bg-[#7C5CFC]/18 text-white"
                      : "border-[#26334D] bg-[#111A2E] text-[#94A3B8] hover:border-[#334155] hover:text-white"
                  }
                `}
              >
                {item.label}

                {item.value
                  === "pending"
                  && pendingCount
                  > 0 && (
                  <span
                    className="
                      ml-2
                      inline-flex
                      min-w-5
                      items-center
                      justify-center
                      rounded-full
                      bg-[#F59E0B]/15
                      px-1.5
                      py-0.5
                      text-[10px]
                      text-[#FBBF24]
                    "
                  >
                    {
                      pendingCount
                    }
                  </span>
                )}
              </button>
            );
          }
        )}
      </div>

      {loading ? (
        <SafetyListSkeleton />
      ) : error ? (
        <ErrorState
          title="Approvals unavailable"
          description="
            AURA could not load
            approval requests from the backend.
          "
          error={error}
          onRetry={() =>
            void loadApprovals({
              refresh: true,
            })
          }
          retrying={
            refreshing
          }
        />
      ) : approvals.length
        === 0 ? (
        <EmptyState
          title="No approval requests"
          description="
            AURA has not paused
            any actions for manual review.
          "
          icon={
            <ShieldCheck
              size={25}
              strokeWidth={
                1.8
              }
            />
          }
        />
      ) : visibleApprovals
          .length === 0 ? (
        <EmptyState
          title={
            filter
            === "pending"
              ? "No pending approvals"
              : `No ${formatLabel(
                  filter
                ).toLowerCase()} approvals`
          }
          description={
            filter
            === "pending"
              ? "Nothing currently requires your attention."
              : "No approval requests match this filter."
          }
          icon={
            <CheckCircle2
              size={25}
              strokeWidth={
                1.8
              }
            />
          }
          action={
            <Button
              type="button"
              variant="secondary"
              onClick={() =>
                setFilter(
                  "all"
                )
              }
            >
              View All
            </Button>
          }
        />
      ) : (
        <section
          aria-label="Approval requests"
          className="
            space-y-4
          "
        >
          {visibleApprovals.map(
            (
              approval
            ) => {
              const highlighted =
                approval.id
                === highlightedApprovalId;

              return (
                <Card
                  key={
                    approval.id
                  }
                  id={`approval-${approval.id}`}
                  className={`
                    p-5
                    transition
                    ${
                      highlighted
                        ? "border-[#7C5CFC] shadow-lg shadow-[#7C5CFC]/10"
                        : ""
                    }
                  `}
                >
                  <div
                    className="
                      flex
                      flex-col
                      gap-4
                      lg:flex-row
                      lg:items-start
                      lg:justify-between
                    "
                  >
                    <div
                      className="
                        min-w-0
                        flex-1
                      "
                    >
                      <div
                        className="
                          flex
                          flex-wrap
                          items-center
                          gap-2
                        "
                      >
                        <RiskBadge
                          risk={
                            approval.risk_level
                          }
                        />

                        <ApprovalStatusBadge
                          status={
                            approval.status
                          }
                        />

                        {highlighted && (
                          <StatusBadge
                            label="Linked"
                            tone="purple"
                            dot={
                              false
                            }
                          />
                        )}
                      </div>

                      <h2
                        className="
                          mb-0
                          mt-4
                          truncate
                          text-xl
                          font-semibold
                          tracking-[-0.02em]
                          text-white
                        "
                        title={
                          approval.tool_name
                          ?? "Unspecified tool"
                        }
                      >
                        {approval.tool_name
                          ?? "Unspecified tool"}
                      </h2>

                      <p
                        className="
                          mb-0
                          mt-2
                          line-clamp-3
                          max-w-3xl
                          text-sm
                          leading-6
                          text-[#CBD5E1]
                        "
                      >
                        {approval.reason}
                      </p>
                    </div>

                    <Link
                      href={`/approvals/${approval.id}`}
                      className="
                        inline-flex
                        shrink-0
                      "
                    >
                      <Button
                        variant="secondary"
                      >
                        <ExternalLink
                          size={15}
                        />

                        View Details
                      </Button>
                    </Link>
                  </div>

                  <div
                    className="
                      mt-5
                      grid
                      gap-3
                      sm:grid-cols-2
                      xl:grid-cols-4
                    "
                  >
                    <Info
                      icon={
                        <Clock
                          size={15}
                        />
                      }
                      label="Requested"
                      value={formatDate(
                        approval.requested_at
                      )}
                    />

                    <Info
                      label="Execution"
                      value={shortId(
                        approval.execution_id
                      )}
                      title={
                        approval.execution_id
                        ?? undefined
                      }
                    />

                    <Info
                      label="Plan"
                      value={shortId(
                        approval.plan_id
                      )}
                      title={
                        approval.plan_id
                        ?? undefined
                      }
                    />

                    <Info
                      label="Step"
                      value={shortId(
                        approval.step_id
                      )}
                      title={
                        approval.step_id
                        ?? undefined
                      }
                    />
                  </div>

                  {approval.resolved_at && (
                    <div
                      className="
                        mt-4
                        flex
                        flex-wrap
                        items-center
                        gap-2
                        border-t
                        border-[#162036]
                        pt-4
                        text-xs
                        text-[#64748B]
                      "
                    >
                      <span>
                        Resolved{" "}
                        {formatDate(
                          approval.resolved_at
                        )}
                      </span>

                      {approval.resolved_by && (
                        <>
                          <span
                            aria-hidden="true"
                            className="
                              h-1
                              w-1
                              rounded-full
                              bg-[#334155]
                            "
                          />

                          <span>
                            by{" "}
                            {
                              approval.resolved_by
                            }
                          </span>
                        </>
                      )}
                    </div>
                  )}
                </Card>
              );
            }
          )}
        </section>
      )}
    </div>
  );
}


function Info({
  label,
  value,
  icon,
  title,
}: {
  label: string;
  value: string;
  icon?: ReactNode;
  title?: string;
}) {
  return (
    <div
      className="
        min-w-0
        rounded-xl
        border
        border-[#162036]
        bg-[#0A1020]
        p-3
      "
    >
      <p
        className="
          m-0
          flex
          items-center
          gap-1.5
          text-[10px]
          font-medium
          uppercase
          tracking-[0.14em]
          text-[#64748B]
        "
      >
        {icon}

        {label}
      </p>

      <p
        className="
          mb-0
          mt-2
          truncate
          text-sm
          text-[#CBD5E1]
        "
        title={
          title
          ?? value
        }
      >
        {value}
      </p>
    </div>
  );
}
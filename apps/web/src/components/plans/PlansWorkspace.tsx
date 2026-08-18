"use client";

import Link from "next/link";
import {
  FilePlus2,
  RefreshCw,
  Route,
  Trash2,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import ConfirmDialog from "@/components/ui/ConfirmDialog";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";
import PageHeader from "@/components/ui/PageHeader";
import StatusBadge from "@/components/ui/StatusBadge";
import {
  useToast,
} from "@/components/ui/ToastProvider";

import {
  deletePlan,
  getPlans,
} from "@/lib/api/plans";

import type {
  PlanResponse,
  PlanStatus,
} from "@/types/api";

import CreatePlanDialog from "./CreatePlanDialog";
import PlansSkeleton from "./PlansSkeleton";


function planProgress(
  plan: PlanResponse
) {
  const total =
    plan.steps.length;

  const complete =
    plan.steps.filter(
      (step) =>
        [
          "completed",
          "skipped",
        ].includes(
          step.status
        )
    ).length;

  const percent =
    total > 0
      ? Math.round(
          (
            complete
            / total
          )
          * 100
        )
      : 0;

  return {
    total,
    complete,
    percent,
  };
}


function statusTone(
  status: PlanStatus
):
  | "neutral"
  | "success"
  | "warning"
  | "danger"
  | "info"
  | "purple" {
  if (
    status === "completed"
  ) {
    return "success";
  }

  if (
    status === "failed"
    || status === "cancelled"
  ) {
    return "danger";
  }

  if (
    status === "in_progress"
  ) {
    return "info";
  }

  return "purple";
}


function statusLabel(
  status: string
) {
  return status
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


export default function PlansWorkspace() {
  const {
    showToast,
  } = useToast();

  const [
    plans,
    setPlans,
  ] = useState<
    PlanResponse[]
  >([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const [
    dialogOpen,
    setDialogOpen,
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

  const [
    planToDelete,
    setPlanToDelete,
  ] = useState<
    PlanResponse | null
  >(null);

  const [
    deleting,
    setDeleting,
  ] = useState(false);


  const loadPlans =
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
          const nextPlans =
            await getPlans();

          setPlans(
            nextPlans
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
              : "Unable to load plans."
          );
        } finally {
          setLoading(false);
          setRefreshing(false);
        }
      },
      []
    );


  useEffect(() => {
    const timeoutId =
      window.setTimeout(
        () => {
          void loadPlans();
        },
        0
      );

    return () =>
      window.clearTimeout(
        timeoutId
      );
  }, [loadPlans]);


  async function handleDeleteConfirm() {
    if (!planToDelete) {
      return;
    }

    setDeleting(true);

    try {
      await deletePlan(
        planToDelete.id
      );

      setPlans(
        (
          currentPlans
        ) =>
          currentPlans.filter(
            (
              candidate
            ) =>
              candidate.id
              !== planToDelete.id
          )
      );

      showToast({
        type: "success",
        title:
          "Plan deleted",
        description:
          "The plan was removed successfully.",
      });

      setPlanToDelete(
        null
      );
    } catch (
      nextError
    ) {
      showToast({
        type: "error",
        title:
          "Unable to delete plan",
        description:
          nextError
            instanceof Error
            ? nextError.message
            : "AURA could not delete the selected plan.",
      });
    } finally {
      setDeleting(false);
    }
  }


  function handlePlanCreated(
    plan: PlanResponse
  ) {
    setPlans(
      (
        currentPlans
      ) => [
        plan,
        ...currentPlans,
      ]
    );

    setLastUpdated(
      new Date()
    );

    showToast({
      type: "success",
      title:
        "Plan created",
      description:
        "AURA created the plan successfully.",
    });
  }


  return (
    <div
      className="
        mx-auto
        flex
        w-full
        max-w-7xl
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
          eyebrow="AURA / Plans"
          title="Plans"
          description="
            Structured goals and execution
            strategies generated by AURA.
          "
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
                onClick={() =>
                  void loadPlans({
                    refresh:
                      true,
                  })
                }
                disabled={
                  refreshing
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

              <Button
                type="button"
                onClick={() =>
                  setDialogOpen(
                    true
                  )
                }
              >
                <FilePlus2
                  size={16}
                />

                Create Plan
              </Button>
            </>
          }
        />
      </section>

      {loading ? (
        <PlansSkeleton />
      ) : error ? (
        <ErrorState
          title="Plans unavailable"
          description="
            AURA could not load your
            plans from the backend.
          "
          error={error}
          onRetry={() =>
            void loadPlans({
              refresh: true,
            })
          }
          retrying={
            refreshing
          }
        />
      ) : plans.length === 0 ? (
        <EmptyState
          title="No plans yet"
          description="
            Create a plan to turn a goal
            into structured executable
            steps.
          "
          icon={
            <Route
              size={24}
              strokeWidth={
                1.8
              }
            />
          }
          action={
            <Button
              type="button"
              onClick={() =>
                setDialogOpen(
                  true
                )
              }
            >
              <FilePlus2
                size={16}
              />

              Create Plan
            </Button>
          }
        />
      ) : (
        <section
          aria-label="AURA plans"
          className="
            grid
            gap-4
            lg:grid-cols-2
          "
        >
          {plans.map(
            (plan) => {
              const progress =
                planProgress(
                  plan
                );

              return (
                <Card
                  key={
                    plan.id
                  }
                  className="
                    aura-card-hover
                    flex
                    flex-col
                    p-5
                  "
                >
                  <div
                    className="
                      flex
                      flex-col
                      gap-4
                      sm:flex-row
                      sm:items-start
                      sm:justify-between
                    "
                  >
                    <div
                      className="
                        min-w-0
                        flex-1
                      "
                    >
                      <h2
                        className="
                          m-0
                          line-clamp-2
                          text-lg
                          font-semibold
                          leading-6
                          text-white
                        "
                      >
                        {
                          plan.goal
                        }
                      </h2>

                      <p
                        className="
                          aura-truncate-id
                          mb-0
                          mt-1.5
                          text-xs
                          text-[#64748B]
                        "
                        title={
                          plan.id
                        }
                      >
                        Plan ID{" "}
                        {
                          plan.id
                        }
                      </p>
                    </div>

                    <StatusBadge
                      label={statusLabel(
                        plan.status
                      )}
                      tone={statusTone(
                        plan.status
                      )}
                      pulse={
                        plan.status
                        ===
                        "in_progress"
                      }
                    />
                  </div>

                  <div
                    className="
                      mt-5
                      flex
                      flex-wrap
                      items-center
                      gap-x-4
                      gap-y-2
                      text-sm
                      text-[#94A3B8]
                    "
                  >
                    <span>
                      {
                        progress.total
                      }{" "}
                      {progress.total
                      === 1
                        ? "step"
                        : "steps"}
                    </span>

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
                      {
                        progress.complete
                      }{" "}
                      /{" "}
                      {
                        progress.total
                      }{" "}
                      complete
                    </span>

                    <span
                      className="
                        ml-auto
                        text-xs
                        font-medium
                        text-[#CBD5E1]
                      "
                    >
                      {
                        progress.percent
                      }
                      %
                    </span>
                  </div>

                  <div
                    className="
                      mt-3
                      h-2
                      overflow-hidden
                      rounded-full
                      bg-[#162036]
                    "
                    role="progressbar"
                    aria-valuemin={
                      0
                    }
                    aria-valuemax={
                      100
                    }
                    aria-valuenow={
                      progress.percent
                    }
                    aria-label={`Plan progress ${progress.percent}%`}
                  >
                    <div
                      className="
                        h-full
                        rounded-full
                        bg-gradient-to-r
                        from-[#7C5CFC]
                        to-[#2DD4BF]
                        transition-[width]
                        duration-300
                      "
                      style={{
                        width:
                          `${progress.percent}%`,
                      }}
                    />
                  </div>

                  <div
                    className="
                      mt-auto
                      flex
                      flex-wrap
                      gap-2
                      pt-5
                    "
                  >
                    <Link
                      href={`/plans/${plan.id}`}
                      className="
                        inline-flex
                      "
                    >
                      <Button
                        variant="secondary"
                      >
                        View Plan
                      </Button>
                    </Link>

                    <Button
                      type="button"
                      variant="danger"
                      onClick={() =>
                        setPlanToDelete(
                          plan
                        )
                      }
                    >
                      <Trash2
                        size={15}
                      />

                      Delete
                    </Button>
                  </div>
                </Card>
              );
            }
          )}
        </section>
      )}

      <CreatePlanDialog
        open={dialogOpen}
        onClose={() =>
          setDialogOpen(
            false
          )
        }
        onCreated={
          handlePlanCreated
        }
      />

      <ConfirmDialog
        open={
          planToDelete
          !== null
        }
        title="Delete plan?"
        description={
          planToDelete
            ? `This will permanently remove "${planToDelete.goal}" from AURA's plan records. This action does not delete AURA memory.`
            : "This will permanently remove the selected plan."
        }
        confirmLabel="Delete Plan"
        cancelLabel="Keep Plan"
        variant="danger"
        loading={deleting}
        onConfirm={() =>
          void handleDeleteConfirm()
        }
        onCancel={() => {
          if (!deleting) {
            setPlanToDelete(
              null
            );
          }
        }}
      />
    </div>
  );
}
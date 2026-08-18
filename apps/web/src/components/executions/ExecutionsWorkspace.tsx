"use client";

import Link from "next/link";
import {
  PlayCircle,
  RefreshCw,
  Rocket,
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
  deleteExecution,
  getExecutions,
} from "@/lib/api/executions";

import type {
  ExecutionResponse,
  ExecutionStatus,
} from "@/types/api";

import CreateExecutionDialog from "./CreateExecutionDialog";
import ExecutionsSkeleton from "./ExecutionsSkeleton";


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


function statusTone(
  status: ExecutionStatus
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
    status === "running"
  ) {
    return "info";
  }

  if (
    status === "paused"
  ) {
    return "warning";
  }

  return "purple";
}


function getProgress(
  execution: ExecutionResponse
) {
  const total =
    execution.step_executions.length;

  const complete =
    execution.step_executions.filter(
      (step) =>
        [
          "completed",
          "skipped",
        ].includes(
          step.status
        )
    ).length;

  return {
    total,
    complete,
    percent:
      total > 0
        ? Math.round(
            (
              complete
              / total
            )
            * 100
          )
        : 0,
  };
}


function getCurrentStep(
  execution: ExecutionResponse
) {
  if (
    execution.current_step_id
  ) {
    return (
      execution.step_executions.find(
        (step) =>
          step.plan_step_id
          === execution.current_step_id
          || step.id
          === execution.current_step_id
      )?.title
      ?? "Current step unavailable"
    );
  }

  return (
    execution.step_executions.find(
      (step) =>
        [
          "running",
          "ready",
          "pending",
        ].includes(
          step.status
        )
    )?.title
    ?? "No active step"
  );
}


function formatDate(
  value: string | null
) {
  if (!value) {
    return "Not started";
  }

  const date =
    new Date(value);

  return Number.isNaN(
    date.getTime()
  )
    ? "Unavailable"
    : date.toLocaleString();
}


export default function ExecutionsWorkspace() {
  const {
    showToast,
  } = useToast();

  const [
    executions,
    setExecutions,
  ] = useState<
    ExecutionResponse[]
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
    executionToDelete,
    setExecutionToDelete,
  ] = useState<
    ExecutionResponse | null
  >(null);

  const [
    deleting,
    setDeleting,
  ] = useState(false);


  const loadExecutions =
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
          const nextExecutions =
            await getExecutions();

          setExecutions(
            nextExecutions
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
              : "Unable to load executions."
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
          void loadExecutions();
        },
        0
      );

    return () =>
      window.clearTimeout(
        timeoutId
      );
  }, [loadExecutions]);


  async function handleDeleteConfirm() {
    if (!executionToDelete) {
      return;
    }

    setDeleting(true);

    try {
      await deleteExecution(
        executionToDelete.id
      );

      setExecutions(
        (
          currentExecutions
        ) =>
          currentExecutions.filter(
            (
              candidate
            ) =>
              candidate.id
              !== executionToDelete.id
          )
      );

      showToast({
        type: "success",
        title:
          "Execution deleted",
        description:
          "The execution record was removed successfully.",
      });

      setExecutionToDelete(
        null
      );
    } catch (
      nextError
    ) {
      showToast({
        type: "error",
        title:
          "Unable to delete execution",
        description:
          nextError
            instanceof Error
            ? nextError.message
            : "AURA could not delete the selected execution.",
      });
    } finally {
      setDeleting(false);
    }
  }


  function handleExecutionCreated(
    execution: ExecutionResponse
  ) {
    setExecutions(
      (
        currentExecutions
      ) => [
        execution,
        ...currentExecutions,
      ]
    );

    setLastUpdated(
      new Date()
    );

    showToast({
      type: "success",
      title:
        "Execution created",
      description:
        "AURA created the execution successfully.",
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
          eyebrow="AURA / Executions"
          title="Executions"
          description="
            Monitor and control
            autonomous AURA runs.
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
                  void loadExecutions({
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
                <Rocket
                  size={16}
                />

                New Execution
              </Button>
            </>
          }
        />
      </section>

      {loading ? (
        <ExecutionsSkeleton />
      ) : error ? (
        <ErrorState
          title="Executions unavailable"
          description="
            AURA could not load
            execution records from the backend.
          "
          error={error}
          onRetry={() =>
            void loadExecutions({
              refresh: true,
            })
          }
          retrying={
            refreshing
          }
        />
      ) : executions.length === 0 ? (
        <EmptyState
          title="No executions yet"
          description="
            Create an execution from one
            of your plans to let AURA
            carry out the work.
          "
          icon={
            <PlayCircle
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
              <Rocket
                size={16}
              />

              New Execution
            </Button>
          }
        />
      ) : (
        <section
          aria-label="AURA executions"
          className="
            grid
            gap-4
            lg:grid-cols-2
          "
        >
          {executions.map(
            (
              execution
            ) => {
              const currentProgress =
                getProgress(
                  execution
                );

              return (
                <Card
                  key={
                    execution.id
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
                          execution.goal
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
                          execution.plan_id
                        }
                      >
                        Plan{" "}
                        {
                          execution.plan_id
                        }
                      </p>
                    </div>

                    <StatusBadge
                      label={statusLabel(
                        execution.status
                      )}
                      tone={statusTone(
                        execution.status
                      )}
                      pulse={
                        execution.status
                        ===
                        "running"
                      }
                    />
                  </div>

                  <div
                    className="
                      mt-5
                      grid
                      gap-3
                      text-sm
                      text-[#94A3B8]
                      sm:grid-cols-2
                    "
                  >
                    <div>
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
                        Progress
                      </p>

                      <p
                        className="
                          mb-0
                          mt-1
                          text-sm
                          text-[#CBD5E1]
                        "
                      >
                        {
                          currentProgress.complete
                        }{" "}
                        /{" "}
                        {
                          currentProgress.total
                        }{" "}
                        steps
                      </p>
                    </div>

                    <div>
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
                        Started
                      </p>

                      <p
                        className="
                          mb-0
                          mt-1
                          truncate
                          text-sm
                          text-[#CBD5E1]
                        "
                        title={formatDate(
                          execution.started_at
                        )}
                      >
                        {formatDate(
                          execution.started_at
                        )}
                      </p>
                    </div>
                  </div>

                  <div
                    className="
                      mt-4
                      rounded-xl
                      border
                      border-[#162036]
                      bg-[#090F1C]
                      px-3
                      py-3
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
                      Current Step
                    </p>

                    <p
                      className="
                        mb-0
                        mt-1.5
                        line-clamp-2
                        text-sm
                        font-medium
                        text-[#CBD5E1]
                      "
                    >
                      {getCurrentStep(
                        execution
                      )}
                    </p>
                  </div>

                  {execution.error && (
                    <div
                      role="alert"
                      className="
                        mt-4
                        rounded-xl
                        border
                        border-[#EF4444]/25
                        bg-[#EF4444]/[0.06]
                        px-3
                        py-3
                      "
                    >
                      <p
                        className="
                          m-0
                          text-[10px]
                          font-semibold
                          uppercase
                          tracking-[0.12em]
                          text-[#F87171]
                        "
                      >
                        Execution Error
                      </p>

                      <p
                        className="
                          mb-0
                          mt-1.5
                          line-clamp-3
                          text-sm
                          leading-5
                          text-[#FCA5A5]
                        "
                      >
                        {
                          execution.error
                        }
                      </p>

                      {execution.error_code && (
                        <p
                          className="
                            aura-truncate-id
                            mb-0
                            mt-2
                            text-[11px]
                            text-[#7F1D1D]
                          "
                          title={
                            execution.error_code
                          }
                        >
                          {
                            execution.error_code
                          }
                        </p>
                      )}
                    </div>
                  )}

                  <div
                    className="
                      mt-4
                      flex
                      items-center
                      gap-3
                    "
                  >
                    <div
                      className="
                        h-2
                        flex-1
                        overflow-hidden
                        rounded-full
                        bg-[#162036]
                      "
                      role="progressbar"
                      aria-label={`Execution progress ${currentProgress.percent}%`}
                      aria-valuemin={
                        0
                      }
                      aria-valuemax={
                        100
                      }
                      aria-valuenow={
                        currentProgress.percent
                      }
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
                            `${currentProgress.percent}%`,
                        }}
                      />
                    </div>

                    <span
                      className="
                        min-w-9
                        text-right
                        text-xs
                        font-medium
                        text-[#CBD5E1]
                      "
                    >
                      {
                        currentProgress.percent
                      }
                      %
                    </span>
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
                      href={`/executions/${execution.id}`}
                      className="
                        inline-flex
                      "
                    >
                      <Button
                        variant="secondary"
                      >
                        View Execution
                      </Button>
                    </Link>

                    <Button
                      type="button"
                      variant="danger"
                      onClick={() =>
                        setExecutionToDelete(
                          execution
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

      <CreateExecutionDialog
        open={dialogOpen}
        onClose={() =>
          setDialogOpen(
            false
          )
        }
        onCreated={
          handleExecutionCreated
        }
      />

      <ConfirmDialog
        open={
          executionToDelete
          !== null
        }
        title="Delete execution?"
        description={
          executionToDelete
            ? `This permanently removes the execution record for "${executionToDelete.goal}". The original plan is not deleted.`
            : "This permanently removes the selected execution record."
        }
        confirmLabel="Delete Execution"
        cancelLabel="Keep Execution"
        variant="danger"
        loading={deleting}
        onConfirm={() =>
          void handleDeleteConfirm()
        }
        onCancel={() => {
          if (!deleting) {
            setExecutionToDelete(
              null
            );
          }
        }}
      />
    </div>
  );
}
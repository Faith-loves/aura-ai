"use client";

import {
  useRouter,
} from "next/navigation";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Brain,
  Cpu,
  Database,
  Gauge,
  PlayCircle,
  Plus,
  RefreshCw,
  ShieldCheck,
  Wrench,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";
import PageHeader from "@/components/ui/PageHeader";
import StatusBadge from "@/components/ui/StatusBadge";

import {
  useInterfacePreferences,
} from "@/hooks/useInterfacePreferences";
import {
  getDashboardData,
} from "@/lib/api/dashboard-data";

import type {
  DashboardData,
  DashboardSubsystemStatus,
} from "@/types/dashboard";

import DashboardSkeleton from "./DashboardSkeleton";


const metricIcons = [
  Brain,
  PlayCircle,
  Database,
  Wrench,
];

const DASHBOARD_ACTIVE_REFRESH_MS =
  7000;

const DASHBOARD_TERMINAL_STATUSES =
  new Set([
    "completed",
    "failed",
    "cancelled",
  ]);


function formatUpdatedAt(
  date: Date | null
) {
  if (!date) {
    return "Not updated yet";
  }

  return date.toLocaleTimeString(
    [],
    {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }
  );
}


function executionTone(
  status: string
):
  | "neutral"
  | "success"
  | "warning"
  | "danger"
  | "info"
  | "purple" {
  if (status === "running") {
    return "info";
  }

  if (status === "paused") {
    return "warning";
  }

  if (
    status === "failed"
    || status === "cancelled"
  ) {
    return "danger";
  }

  if (
    status === "completed"
  ) {
    return "success";
  }

  return "purple";
}


function subsystemTone(
  status: DashboardSubsystemStatus
):
  | "success"
  | "warning"
  | "danger" {
  if (
    status === "healthy"
  ) {
    return "success";
  }

  if (
    status === "degraded"
  ) {
    return "warning";
  }

  return "danger";
}


function HeaderStatus({
  data,
}: {
  data: DashboardData;
}) {
  if (
    data.backendStatus
    === "healthy"
  ) {
    return (
      <StatusBadge
        label="Operational"
        tone="success"
      />
    );
  }

  if (
    data.backendStatus
    === "degraded"
  ) {
    return (
      <StatusBadge
        label="Degraded"
        tone="warning"
      />
    );
  }

  return (
    <StatusBadge
      label="Backend offline"
      tone="danger"
    />
  );
}


function DegradedNotice({
  data,
}: {
  data: DashboardData;
}) {
  if (
    data.unavailableSections
      .length === 0
  ) {
    return null;
  }

  return (
    <div
      role="status"
      className="
        flex
        items-start
        gap-3
        rounded-2xl
        border
        border-[#F59E0B]/25
        bg-[#F59E0B]/[0.07]
        px-4
        py-3
        text-sm
        text-[#FCD34D]
      "
    >
      <AlertTriangle
        size={17}
        className="
          mt-0.5
          shrink-0
        "
      />

      <div>
        <p
          className="
            m-0
            font-medium
          "
        >
          Some AURA subsystems are unavailable
        </p>

        <p
          className="
            mb-0
            mt-1
            text-xs
            leading-5
            text-[#D6B867]
          "
        >
          {data.unavailableSections.join(
            ", "
          )}
        </p>
      </div>
    </div>
  );
}


export default function DashboardView() {
  const router =
    useRouter();

  const {
    preferences,
  } = useInterfacePreferences();

  const [
    data,
    setData,
  ] = useState<
    DashboardData | null
  >(null);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const [
    lastUpdated,
    setLastUpdated,
  ] = useState<
    Date | null
  >(null);


  const loadDashboard =
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

        try {
          const nextData =
            await getDashboardData();

          setData(
            nextData
          );

          setError(
            null
          );

          setLastUpdated(
            new Date()
          );
        } catch (
          nextError
        ) {
          const message =
            nextError
              instanceof Error
              ? nextError.message
              : "Unable to load AURA dashboard data.";

          setError(
            message
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
          void loadDashboard();
        },
        0
      );

    return () =>
      window.clearTimeout(
        timeoutId
      );
  }, [loadDashboard]);


  useEffect(() => {
    const activeExecution =
      data?.activeExecution;

    if (
      !preferences
        .dashboardAutoRefresh
      || !activeExecution
      || DASHBOARD_TERMINAL_STATUSES
        .has(
          activeExecution.status
        )
    ) {
      return;
    }

    const intervalId =
      window.setInterval(
        () => {
          void loadDashboard({
            refresh: true,
          });
        },
        DASHBOARD_ACTIVE_REFRESH_MS
      );

    return () =>
      window.clearInterval(
        intervalId
      );
  }, [
    data?.activeExecution,
    loadDashboard,
    preferences
      .dashboardAutoRefresh,
  ]);


  const completelyUnavailable =
    useMemo(
      () =>
        !loading
        && !data
        && error !== null,
      [
        data,
        error,
        loading,
      ]
    );


  if (
    loading
    && !data
  ) {
    return (
      <DashboardSkeleton />
    );
  }


  if (
    completelyUnavailable
  ) {
    return (
      <div
        className="
          mx-auto
          flex
          min-h-[calc(100vh-130px)]
          w-full
          max-w-7xl
          items-center
          justify-center
        "
      >
        <ErrorState
          title="AURA backend is unavailable"
          description="
            Check that the FastAPI server
            is running and reachable from
            the configured AURA API URL.
          "
          error={error}
          onRetry={() =>
            void loadDashboard({
              refresh: true,
            })
          }
          retrying={
            refreshing
          }
        />
      </div>
    );
  }


  if (!data) {
    return null;
  }


  const activeExecution =
    data.activeExecution;


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
          overflow-hidden
          rounded-[20px]
          border
          border-[#1D2942]
          bg-[#0D1321]/78
          p-5
          shadow-2xl
          shadow-black/20
          sm:p-7
          lg:p-8
        "
      >
        <PageHeader
          eyebrow="AURA Runtime"
          title="Your autonomous intelligence workspace."
          description="
            Give AURA a goal, inspect its plan,
            monitor execution, and stay in control
            of every important action.
          "
          badges={
            <HeaderStatus
              data={data}
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
                  {formatUpdatedAt(
                    lastUpdated
                  )}
                </p>
              </div>

              <Button
                type="button"
                variant="secondary"
                disabled={
                  refreshing
                }
                onClick={() =>
                  void loadDashboard({
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

              <Button
                type="button"
                onClick={() =>
                  router.push(
                    "/chat"
                  )
                }
              >
                <Plus size={17} />

                New Task
              </Button>
            </>
          }
        />
      </section>

      <DegradedNotice
        data={data}
      />

      <section
        aria-label="AURA metrics"
        className="
          grid
          gap-4
          sm:grid-cols-2
          xl:grid-cols-4
        "
      >
        {data.metrics.map(
          (
            metric,
            index
          ) => {
            const Icon =
              metricIcons[
                index
              ]
              ?? Activity;

            return (
              <Card
                key={
                  metric.label
                }
                className="
                  aura-card-hover
                  p-5
                "
              >
                <div
                  className="
                    flex
                    items-start
                    justify-between
                    gap-4
                  "
                >
                  <div>
                    <p
                      className="
                        m-0
                        text-sm
                        font-medium
                        text-[#94A3B8]
                      "
                    >
                      {metric.label}
                    </p>

                    <div
                      className="
                        mt-4
                        flex
                        items-end
                        gap-3
                      "
                    >
                      <span
                        className="
                          text-3xl
                          font-semibold
                          leading-none
                          tracking-tight
                          text-white
                        "
                      >
                        {metric.value}
                      </span>

                      <span
                        className="
                          pb-1
                          text-xs
                          font-medium
                          text-[#64748B]
                        "
                      >
                        {metric.detail}
                      </span>
                    </div>
                  </div>

                  <div
                    className="
                      flex
                      flex-col
                      items-end
                      gap-2
                    "
                  >
                    <div
                      className="
                        flex
                        h-10
                        w-10
                        items-center
                        justify-center
                        rounded-xl
                        border
                        border-[#26334D]
                        bg-[#111A2E]
                        text-[#9B87FF]
                      "
                    >
                      <Icon
                        size={19}
                      />
                    </div>

                    <StatusBadge
                      label={
                        metric.status
                      }
                      tone={subsystemTone(
                        metric.status
                      )}
                    />
                  </div>
                </div>
              </Card>
            );
          }
        )}
      </section>

      <section
        className="
          grid
          gap-6
          xl:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.85fr)]
        "
      >
        <Card
          className="
            p-5
            sm:p-6
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
            <div>
              <div
                className="
                  flex
                  items-center
                  gap-2
                  text-[#F8FAFC]
                "
              >
                <Activity
                  size={18}
                  className="
                    text-[#9B87FF]
                  "
                />

                <h2
                  className="
                    m-0
                    text-lg
                    font-semibold
                  "
                >
                  Active Execution
                </h2>
              </div>

              <p
                className="
                  mb-0
                  mt-1
                  text-sm
                  text-[#64748B]
                "
              >
                Latest autonomous workflow
              </p>
            </div>

            {activeExecution ? (
              <StatusBadge
                label={
                  activeExecution
                    .statusLabel
                }
                tone={executionTone(
                  activeExecution.status
                )}
                pulse={
                  activeExecution.status
                  === "running"
                }
              />
            ) : (
              <StatusBadge
                label="No executions"
                tone="neutral"
              />
            )}
          </div>

          {activeExecution ? (
            <div
              className="
                mt-7
                rounded-2xl
                border
                border-[#162036]
                bg-[#0A1020]/80
                p-5
              "
            >
              <div
                className="
                  flex
                  flex-col
                  gap-4
                  lg:flex-row
                  lg:items-center
                  lg:justify-between
                "
              >
                <div>
                  <p
                    className="
                      m-0
                      text-sm
                      text-[#64748B]
                    "
                  >
                    Task
                  </p>

                  <h3
                    className="
                      mb-0
                      mt-2
                      max-w-2xl
                      text-xl
                      font-semibold
                      tracking-tight
                      text-white
                    "
                  >
                    {
                      activeExecution.goal
                    }
                  </h3>
                </div>

                <div
                  className="
                    flex
                    shrink-0
                    flex-wrap
                    items-center
                    gap-2
                  "
                >
                  <div
                    className="
                      flex
                      items-center
                      gap-2
                      rounded-full
                      border
                      border-[#26334D]
                      bg-[#111A2E]
                      px-3
                      py-2
                      text-xs
                      text-[#94A3B8]
                    "
                  >
                    <Gauge
                      size={14}
                      className="
                        text-[#2DD4BF]
                      "
                    />

                    {
                      activeExecution
                        .elapsedLabel
                    }
                  </div>

                  <Button
                    type="button"
                    variant="secondary"
                    className="
                      h-8
                      px-3
                      text-xs
                    "
                    onClick={() =>
                      router.push(
                        `/executions/${activeExecution.id}`
                      )
                    }
                  >
                    View Execution
                  </Button>
                </div>
              </div>

              <div className="mt-6">
                <div
                  className="
                    mb-2
                    flex
                    items-center
                    justify-between
                    text-xs
                    font-medium
                  "
                >
                  <span
                    className="
                      text-[#64748B]
                    "
                  >
                    Progress
                  </span>

                  <span
                    className="
                      text-[#CBD5E1]
                    "
                  >
                    {
                      activeExecution
                        .progress
                    }
                    %
                  </span>
                </div>

                <div
                  role="progressbar"
                  aria-label={`Execution progress ${activeExecution.progress}%`}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={
                    activeExecution.progress
                  }
                  className="
                    h-2
                    overflow-hidden
                    rounded-full
                    bg-[#162036]
                  "
                >
                  <div
                    className="
                      h-full
                      rounded-full
                      bg-gradient-to-r
                      from-[#7C5CFC]
                      to-[#2DD4BF]
                      shadow-[0_0_18px_rgba(124,92,252,0.28)]
                      transition-[width]
                      duration-300
                    "
                    style={{
                      width:
                        `${activeExecution.progress}%`,
                    }}
                  />
                </div>
              </div>

              <div
                className="
                  mt-6
                  grid
                  gap-3
                  md:grid-cols-3
                "
              >
                <ExecutionState
                  label="Plan"
                  value={
                    activeExecution
                      .planLabel
                  }
                />

                <ExecutionState
                  label="Current"
                  value={
                    activeExecution
                      .currentLabel
                  }
                />

                <ExecutionState
                  label="Safety"
                  value={
                    activeExecution
                      .safetyLabel
                  }
                />
              </div>
            </div>
          ) : (
            <div className="mt-7">
              <EmptyState
                title="No executions yet"
                description="
                  Start a task when you are ready
                  to see AURA planning and execution
                  telemetry here.
                "
                icon={
                  <PlayCircle
                    size={25}
                    strokeWidth={1.8}
                  />
                }
                action={
                  <Button
                    type="button"
                    onClick={() =>
                      router.push(
                        "/chat"
                      )
                    }
                  >
                    <Plus
                      size={16}
                    />

                    Start a Task
                  </Button>
                }
                className="min-h-[250px]"
              />
            </div>
          )}
        </Card>

        <Card
          className="
            p-5
            sm:p-6
          "
        >
          <div
            className="
              flex
              items-start
              justify-between
              gap-4
            "
          >
            <div>
              <div
                className="
                  flex
                  items-center
                  gap-2
                  text-[#F8FAFC]
                "
              >
                <Cpu
                  size={18}
                  className="
                    text-[#9B87FF]
                  "
                />

                <h2
                  className="
                    m-0
                    text-lg
                    font-semibold
                  "
                >
                  System Status
                </h2>
              </div>

              <p
                className="
                  mb-0
                  mt-1
                  text-sm
                  text-[#64748B]
                "
              >
                Runtime health overview
              </p>
            </div>

            <StatusBadge
              label={
                data.safetyActive
                  ? "Protected"
                  : "Attention"
              }
              tone={
                data.safetyActive
                  ? "success"
                  : "warning"
              }
            />
          </div>

          <div
            className="
              mt-6
              divide-y
              divide-[#162036]
            "
          >
            {data.systemStatus.map(
              (item) => (
                <div
                  key={
                    item.label
                  }
                  className="
                    flex
                    items-center
                    justify-between
                    gap-4
                    py-3
                    first:pt-0
                    last:pb-0
                  "
                >
                  <div
                    className="
                      flex
                      min-w-0
                      items-center
                      gap-3
                    "
                  >
                    <StatusBadge
                      label={
                        item.label
                      }
                      tone={subsystemTone(
                        item.status
                      )}
                    />
                  </div>

                  <span
                    className="
                      min-w-0
                      truncate
                      text-right
                      text-sm
                      font-medium
                      text-[#F8FAFC]
                    "
                    title={
                      item.value
                    }
                  >
                    {item.value}
                  </span>
                </div>
              )
            )}
          </div>

          <button
            type="button"
            onClick={() =>
              router.push(
                "/approvals"
              )
            }
            className="
              mt-6
              flex
              w-full
              items-center
              justify-between
              gap-3
              rounded-xl
              border
              border-[#162036]
              bg-[#0A1020]
              p-4
              text-left
              transition
              hover:border-[#7C5CFC]/30
              hover:bg-[#0D1321]
              focus-visible:outline-none
              focus-visible:ring-2
              focus-visible:ring-[#7C5CFC]
            "
          >
            <div>
              <p
                className="
                  m-0
                  text-xs
                  font-medium
                  uppercase
                  tracking-[0.14em]
                  text-[#64748B]
                "
              >
                Control
              </p>

              <p
                className="
                  mb-0
                  mt-2
                  text-sm
                  text-[#CBD5E1]
                "
              >
                {data.pendingApprovalCount
                  === null
                  ? "Human approvals unavailable."
                  : `${data.pendingApprovalCount} pending approval${
                      data.pendingApprovalCount === 1
                        ? ""
                        : "s"
                    }.`}
              </p>
            </div>

            <ArrowRight
              size={17}
              className="
                shrink-0
                text-[#7C5CFC]
              "
            />
          </button>
        </Card>
      </section>
    </div>
  );
}


function ExecutionState({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div
      className="
        rounded-xl
        border
        border-[#162036]
        bg-[#0D1321]
        p-4
      "
    >
      <p
        className="
          m-0
          text-xs
          font-medium
          uppercase
          tracking-[0.14em]
          text-[#64748B]
        "
      >
        {label}
      </p>

      <p
        className="
          mb-0
          mt-2
          line-clamp-2
          text-sm
          font-medium
          text-[#F8FAFC]
        "
        title={value}
      >
        {value}
      </p>
    </div>
  );
}
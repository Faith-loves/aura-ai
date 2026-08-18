"use client";

import Link from "next/link";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  RefreshCw,
  Search,
  Shield,
  Wrench,
  XCircle,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import RiskBadge from "@/components/safety/RiskBadge";
import SafetyListSkeleton from "@/components/safety/SafetyListSkeleton";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";
import PageHeader from "@/components/ui/PageHeader";
import StatusBadge from "@/components/ui/StatusBadge";

import {
  getAuditLog,
} from "@/lib/api/safety";

import type {
  AuditEventType,
  AuditResponse,
  JsonValue,
} from "@/types/api";


type AuditFilter =
  | "all"
  | "approvals"
  | "safety"
  | "executions"
  | "tools"
  | "failures";


const filterOptions: {
  value: AuditFilter;
  label: string;
}[] = [
    {
      value: "all",
      label: "All Events",
    },
    {
      value: "approvals",
      label: "Approvals",
    },
    {
      value: "safety",
      label: "Safety",
    },
    {
      value: "executions",
      label: "Executions",
    },
    {
      value: "tools",
      label: "Tool Activity",
    },
    {
      value: "failures",
      label: "Failures",
    },
  ];


const eventLabels:
  Record<
    AuditEventType,
    string
  > = {
  safety_allowed:
    "Safety Allowed",

  safety_denied:
    "Safety Denied",

  approval_required:
    "Approval Required",

  approval_created:
    "Approval Created",

  approval_approved:
    "Approval Approved",

  approval_rejected:
    "Approval Rejected",

  tool_execution_started:
    "Tool Execution Started",

  tool_execution_succeeded:
    "Tool Execution Succeeded",

  tool_execution_failed:
    "Tool Execution Failed",

  execution_paused:
    "Execution Paused",

  execution_resumed:
    "Execution Resumed",

  execution_failed:
    "Execution Failed",
};


function formatDate(
  value: string
) {
  const date =
    new Date(value);

  return Number.isNaN(
    date.getTime()
  )
    ? "Unavailable"
    : date.toLocaleString();
}


function shortId(
  value: string | null
) {
  if (!value) {
    return null;
  }

  return value.length > 14
    ? `${value.slice(
      0,
      8
    )}...${value.slice(
      -4
    )}`
    : value;
}


function formatJson(
  value:
    Record<
      string,
      JsonValue
    >
) {
  if (
    !value
    || Object.keys(
      value
    ).length === 0
  ) {
    return "No metadata";
  }

  return JSON.stringify(
    value,
    null,
    2
  );
}


function eventTone(
  event: AuditResponse
):
  | "danger"
  | "warning"
  | "success"
  | "info" {
  if (
    event.success === false
    || event.error
    || [
      "safety_denied",
      "approval_rejected",
      "tool_execution_failed",
      "execution_failed",
    ].includes(
      event.event_type
    )
  ) {
    return "danger";
  }

  if (
    [
      "approval_required",
      "approval_created",
      "execution_paused",
    ].includes(
      event.event_type
    )
  ) {
    return "warning";
  }

  if (
    event.success === true
    || [
      "safety_allowed",
      "approval_approved",
      "tool_execution_succeeded",
      "execution_resumed",
    ].includes(
      event.event_type
    )
  ) {
    return "success";
  }

  return "info";
}


function eventIcon(
  event: AuditResponse
) {
  const tone =
    eventTone(event);

  if (
    tone === "danger"
  ) {
    return (
      <XCircle
        size={18}
      />
    );
  }

  if (
    tone === "warning"
  ) {
    return (
      <AlertTriangle
        size={18}
      />
    );
  }

  if (
    event.event_type.startsWith(
      "tool_"
    )
  ) {
    return (
      <Wrench
        size={18}
      />
    );
  }

  if (
    tone === "success"
  ) {
    return (
      <CheckCircle2
        size={18}
      />
    );
  }

  return (
    <Shield
      size={18}
    />
  );
}


function matchesFilter(
  event: AuditResponse,
  filter: AuditFilter
) {
  if (
    filter === "all"
  ) {
    return true;
  }

  if (
    filter === "approvals"
  ) {
    return event
      .event_type
      .startsWith(
        "approval_"
      );
  }

  if (
    filter === "safety"
  ) {
    return event
      .event_type
      .startsWith(
        "safety_"
      );
  }

  if (
    filter === "executions"
  ) {
    return event
      .event_type
      .startsWith(
        "execution_"
      );
  }

  if (
    filter === "tools"
  ) {
    return event
      .event_type
      .startsWith(
        "tool_"
      );
  }

  return (
    event.success === false
    || Boolean(
      event.error
    )
    || event
      .event_type
      .includes(
        "failed"
      )
    || event.event_type
    === "safety_denied"
  );
}


function matchesSearch(
  event: AuditResponse,
  search: string
) {
  const query =
    search
      .trim()
      .toLowerCase();

  if (!query) {
    return true;
  }

  return [
    event.message,
    event.tool_name,
    event.execution_id,
    event.approval_id,
    event.error,
    event.plan_id,
    event.step_id,
  ]
    .filter(Boolean)
    .some(
      (value) =>
        value
          ?.toLowerCase()
          .includes(
            query
          )
    );
}


function toneClass(
  tone:
    | "danger"
    | "warning"
    | "success"
    | "info"
) {
  if (
    tone === "danger"
  ) {
    return (
      "border-[#EF4444]/35 "
      + "bg-[#EF4444]/10 "
      + "text-[#FCA5A5]"
    );
  }

  if (
    tone === "warning"
  ) {
    return (
      "border-[#F59E0B]/35 "
      + "bg-[#F59E0B]/10 "
      + "text-[#FCD34D]"
    );
  }

  if (
    tone === "success"
  ) {
    return (
      "border-[#22C55E]/30 "
      + "bg-[#22C55E]/10 "
      + "text-[#86EFAC]"
    );
  }

  return (
    "border-[#38BDF8]/30 "
    + "bg-[#38BDF8]/10 "
    + "text-[#7DD3FC]"
  );
}


export default function AuditWorkspace() {
  const [
    events,
    setEvents,
  ] = useState<
    AuditResponse[]
  >([]);

  const [
    filter,
    setFilter,
  ] = useState<
    AuditFilter
  >("all");

  const [
    search,
    setSearch,
  ] = useState("");

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


  const loadEvents =
    useCallback(
      async ({
        refresh = false,
      }: {
        refresh?: boolean;
      } = {}) => {
        if (refresh) {
          setRefreshing(
            true
          );
        } else {
          setLoading(
            true
          );
        }

        setError(
          null
        );

        try {
          const nextEvents =
            await getAuditLog();

          setEvents(
            [
              ...nextEvents,
            ].sort(
              (
                left,
                right
              ) =>
                new Date(
                  right.created_at
                ).getTime()
                - new Date(
                  left.created_at
                ).getTime()
            )
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
              : "Unable to load audit events."
          );
        } finally {
          setLoading(
            false
          );

          setRefreshing(
            false
          );
        }
      },
      []
    );


  useEffect(() => {
    const timeoutId =
      window.setTimeout(
        () => {
          void loadEvents();
        },
        0
      );

    return () =>
      window.clearTimeout(
        timeoutId
      );
  }, [loadEvents]);


  const visibleEvents =
    useMemo(
      () =>
        events.filter(
          (event) =>
            matchesFilter(
              event,
              filter
            )
            && matchesSearch(
              event,
              search
            )
        ),
      [
        events,
        filter,
        search,
      ]
    );


  const failureCount =
    useMemo(
      () =>
        events.filter(
          (event) =>
            matchesFilter(
              event,
              "failures"
            )
        ).length,
      [events]
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
          eyebrow="AURA / Audit"
          title="Audit Log"
          description="
            Trace safety decisions,
            approvals, and execution events.
          "
          badges={
            <>
              <StatusBadge
                label={`${events.length} Events`}
                tone="info"
                dot={false}
              />

              {failureCount > 0 && (
                <StatusBadge
                  label={`${failureCount} ${failureCount
                      === 1
                      ? "Failure"
                      : "Failures"
                    }`}
                  tone="danger"
                />
              )}
            </>
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
                onClick={() =>
                  void loadEvents({
                    refresh: true,
                  })
                }
                disabled={
                  refreshing
                }
                aria-label="Refresh audit log"
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

      <Card
        className="
          p-4
          sm:p-5
        "
      >
        <div
          className="
            grid
            gap-3
            lg:grid-cols-[1fr_240px]
          "
        >
          <label
            className="
              relative
              block
            "
          >
            <span className="sr-only">
              Search events
            </span>

            <Search
              size={16}
              className="
                pointer-events-none
                absolute
                left-3
                top-1/2
                -translate-y-1/2
                text-[#64748B]
              "
            />

            <input
              value={
                search
              }
              onChange={(
                event
              ) =>
                setSearch(
                  event
                    .target
                    .value
                )
              }
              placeholder="Search events..."
              className="
                aura-input
                h-11
                pl-10
                pr-4
                text-sm
              "
            />
          </label>

          <label>
            <span className="sr-only">
              Filter events
            </span>

            <select
              value={filter}
              onChange={(event) =>
                setFilter(
                  event.target.value as AuditFilter
                )
              }
              className="
      aura-input
      h-11
      px-4
      text-sm
    "
            >
              {filterOptions.map(
                (option) => (
                  <option
                    key={option.value}
                    value={option.value}
                  >
                    {option.label}
                  </option>
                )
              )}
            </select>
          </label>
        </div>

        {(search.trim()
          || filter
          !== "all") && (
            <div
              className="
              mt-4
              flex
              flex-wrap
              items-center
              justify-between
              gap-3
              border-t
              border-[#162036]
              pt-4
            "
            >
              <p
                className="
                m-0
                text-xs
                text-[#64748B]
              "
              >
                Showing{" "}
                {
                  visibleEvents.length
                }{" "}
                of{" "}
                {
                  events.length
                }{" "}
                events
              </p>

              <Button
                type="button"
                variant="ghost"
                onClick={() => {
                  setSearch(
                    ""
                  );

                  setFilter(
                    "all"
                  );
                }}
              >
                Clear Filters
              </Button>
            </div>
          )}
      </Card>

      {loading ? (
        <SafetyListSkeleton />
      ) : error ? (
        <ErrorState
          title="Audit log unavailable"
          description="
            AURA could not load
            the current audit history.
          "
          error={error}
          onRetry={() =>
            void loadEvents({
              refresh: true,
            })
          }
          retrying={
            refreshing
          }
        />
      ) : visibleEvents
        .length === 0 ? (
        <EmptyState
          title={
            events.length
              === 0
              ? "No audit events"
              : "No matching events"
          }
          description={
            events.length
              === 0
              ? "AURA has not recorded any safety, approval, execution, or tool events yet."
              : "No audit events match the current search and filter."
          }
          icon={
            <Clock3
              size={25}
              strokeWidth={
                1.8
              }
            />
          }
          action={
            events.length
              > 0 ? (
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  setSearch(
                    ""
                  );

                  setFilter(
                    "all"
                  );
                }}
              >
                Clear Filters
              </Button>
            ) : undefined
          }
        />
      ) : (
        <section
          aria-label="AURA audit events"
          className="
            space-y-3
          "
        >
          {visibleEvents.map(
            (event) => {
              const tone =
                eventTone(
                  event
                );

              return (
                <article
                  key={
                    event.id
                  }
                  className="
                    relative
                    rounded-2xl
                    border
                    border-[#1D2942]
                    bg-[#0D1321]/78
                    p-4
                    transition
                    hover:border-[#26334D]
                    sm:p-5
                  "
                >
                  <div
                    className="
                      flex
                      gap-3
                      sm:gap-4
                    "
                  >
                    <div
                      className={`
                        mt-1
                        flex
                        h-9
                        w-9
                        shrink-0
                        items-center
                        justify-center
                        rounded-full
                        border
                        ${toneClass(
                        tone
                      )}
                      `}
                    >
                      {eventIcon(
                        event
                      )}
                    </div>

                    <div
                      className="
                        min-w-0
                        flex-1
                      "
                    >
                      <div
                        className="
                          flex
                          flex-col
                          gap-2
                          sm:flex-row
                          sm:items-start
                          sm:justify-between
                        "
                      >
                        <div>
                          <h2
                            className="
                              m-0
                              text-base
                              font-semibold
                              text-white
                            "
                          >
                            {
                              eventLabels[
                              event
                                .event_type
                              ]
                            }
                          </h2>

                          <StatusBadge
                            label={
                              event.event_type
                            }
                            tone={
                              tone
                            }
                            dot={
                              false
                            }
                          />
                        </div>

                        <time
                          dateTime={
                            event.created_at
                          }
                          className="
                            shrink-0
                            text-xs
                            text-[#64748B]
                          "
                        >
                          {formatDate(
                            event.created_at
                          )}
                        </time>
                      </div>

                      <p
                        className="
                          mb-0
                          mt-3
                          text-sm
                          leading-6
                          text-[#CBD5E1]
                        "
                      >
                        {
                          event.message
                        }
                      </p>

                      <div
                        className="
                          mt-4
                          flex
                          flex-wrap
                          items-center
                          gap-2
                          text-xs
                          text-[#94A3B8]
                        "
                      >
                        {event.tool_name && (
                          <span
                            className="
                              rounded-full
                              border
                              border-[#162036]
                              bg-[#111A2E]
                              px-2.5
                              py-1
                            "
                          >
                            Tool{" "}
                            {
                              event.tool_name
                            }
                          </span>
                        )}

                        {event.risk_level && (
                          <RiskBadge
                            risk={
                              event.risk_level
                            }
                          />
                        )}

                        {event.success
                          !== null && (
                            <StatusBadge
                              label={
                                event.success
                                  ? "Success"
                                  : "Failure"
                              }
                              tone={
                                event.success
                                  ? "success"
                                  : "danger"
                              }
                            />
                          )}

                        {event.execution_id && (
                          <Link
                            href={`/executions/${event.execution_id}`}
                            title={
                              event.execution_id
                            }
                            className="
                              rounded-full
                              border
                              border-[#7C5CFC]/10
                              bg-[#111A2E]
                              px-2.5
                              py-1
                              text-[#C4B5FD]
                              transition
                              hover:border-[#7C5CFC]/30
                              hover:text-white
                              focus-visible:outline-none
                              focus-visible:ring-2
                              focus-visible:ring-[#7C5CFC]
                            "
                          >
                            Execution{" "}
                            {shortId(
                              event.execution_id
                            )}
                          </Link>
                        )}

                        {event.approval_id && (
                          <Link
                            href={`/approvals/${event.approval_id}`}
                            title={
                              event.approval_id
                            }
                            className="
                              rounded-full
                              border
                              border-[#7C5CFC]/10
                              bg-[#111A2E]
                              px-2.5
                              py-1
                              text-[#C4B5FD]
                              transition
                              hover:border-[#7C5CFC]/30
                              hover:text-white
                              focus-visible:outline-none
                              focus-visible:ring-2
                              focus-visible:ring-[#7C5CFC]
                            "
                          >
                            Approval{" "}
                            {shortId(
                              event.approval_id
                            )}
                          </Link>
                        )}
                      </div>

                      {event.error && (
                        <div
                          role="alert"
                          className="
                            mt-4
                            rounded-xl
                            border
                            border-[#EF4444]/30
                            bg-[#EF4444]/10
                            px-3
                            py-2.5
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
                            Error
                          </p>

                          <p
                            className="
                              mb-0
                              mt-1
                              text-sm
                              leading-5
                              text-[#FCA5A5]
                            "
                          >
                            {
                              event.error
                            }
                          </p>
                        </div>
                      )}

                      <details
                        className="
                          mt-4
                          rounded-xl
                          border
                          border-[#162036]
                          bg-[#0A1020]
                          p-3
                          text-sm
                        "
                      >
                        <summary
                          className="
                            cursor-pointer
                            select-none
                            text-[#CBD5E1]
                            focus-visible:outline-none
                            focus-visible:ring-2
                            focus-visible:ring-[#7C5CFC]
                          "
                        >
                          Technical details
                        </summary>

                        <pre
                          className="
                            aura-code
                            mt-3
                            max-h-64
                          "
                        >
                          {formatJson(
                            event.metadata
                          )}
                        </pre>
                      </details>
                    </div>
                  </div>
                </article>
              );
            }
          )}
        </section>
      )}
    </div>
  );
}
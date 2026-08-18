"use client";

import Link from "next/link";
import {
  RefreshCw,
  Search,
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
import LoadingButton from "@/components/ui/LoadingButton";
import PageHeader from "@/components/ui/PageHeader";
import Skeleton from "@/components/ui/Skeleton";
import StatusBadge from "@/components/ui/StatusBadge";
import {
  useToast,
} from "@/components/ui/ToastProvider";

import {
  getTools,
  searchTools,
} from "@/lib/api/tools";

import type {
  ToolResponse,
} from "@/types/api";

import {
  label,
  toolSafetyLabel,
} from "./tool-utils";


function safetyTone(
  tool: ToolResponse
):
  | "success"
  | "warning"
  | "danger" {
  if (tool.dangerous) {
    return "danger";
  }

  if (
    tool.requires_confirmation
  ) {
    return "warning";
  }

  return "success";
}


function ToolsSkeleton() {
  return (
    <div
      className="
        grid
        gap-4
        lg:grid-cols-2
      "
      aria-busy="true"
      aria-label="Loading tools"
    >
      {[0, 1, 2, 3].map(
        (item) => (
          <Card
            key={item}
            className="p-5"
          >
            <div
              className="
                flex
                items-start
                justify-between
                gap-4
              "
            >
              <div
                className="
                  min-w-0
                  flex-1
                "
              >
                <Skeleton
                  className="
                    h-6
                    w-36
                  "
                />

                <Skeleton
                  className="
                    mt-4
                    h-4
                    w-full
                  "
                />

                <Skeleton
                  className="
                    mt-2
                    h-4
                    w-4/5
                  "
                />
              </div>

              <Skeleton
                className="
                  h-6
                  w-24
                  rounded-full
                "
              />
            </div>

            <div
              className="
                mt-5
                flex
                gap-2
              "
            >
              <Skeleton
                className="
                  h-6
                  w-20
                  rounded-full
                "
              />

              <Skeleton
                className="
                  h-6
                  w-16
                  rounded-full
                "
              />

              <Skeleton
                className="
                  h-6
                  w-24
                  rounded-full
                "
              />
            </div>

            <Skeleton
              className="
                mt-6
                h-10
                w-28
                rounded-xl
              "
            />
          </Card>
        )
      )}
    </div>
  );
}


export default function ToolsWorkspace() {
  const {
    showToast,
  } = useToast();

  const [
    tools,
    setTools,
  ] = useState<
    ToolResponse[]
  >([]);

  const [
    query,
    setQuery,
  ] = useState("");

  const [
    searchActive,
    setSearchActive,
  ] = useState(false);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const [
    searching,
    setSearching,
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


  const loadTools =
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
          const nextTools =
            await getTools();

          setTools(
            nextTools
          );

          setSearchActive(
            false
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
              : "Unable to load tools."
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
          void loadTools();
        },
        0
      );

    return () =>
      window.clearTimeout(
        timeoutId
      );
  }, [loadTools]);


  async function handleSearch() {
    const trimmed =
      query.trim();

    if (!trimmed) {
      await loadTools({
        refresh: true,
      });

      return;
    }

    setSearching(true);

    try {
      const results =
        await searchTools(
          trimmed
        );

      setTools(
        results
      );

      setSearchActive(
        true
      );

      if (
        results.length === 0
      ) {
        showToast({
          type: "info",
          title:
            "No tools found",
          description:
            "Try another tool name, category, or capability.",
        });
      }
    } catch (
      nextError
    ) {
      showToast({
        type: "error",
        title:
          "Tool search failed",
        description:
          nextError
            instanceof Error
            ? nextError.message
            : "AURA could not search its tools.",
      });
    } finally {
      setSearching(false);
    }
  }


  async function clearSearch() {
    setQuery("");

    await loadTools({
      refresh: true,
    });
  }


  const summary =
    useMemo(
      () => ({
        registered:
          tools.length,

        standard:
          tools.filter(
            (tool) =>
              !tool.dangerous
              && !tool
                .requires_confirmation
          ).length,

        confirmation:
          tools.filter(
            (tool) =>
              tool
                .requires_confirmation
          ).length,

        dangerous:
          tools.filter(
            (tool) =>
              tool.dangerous
          ).length,
      }),
      [tools]
    );


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
          eyebrow="AURA / Tools"
          title="Tools"
          description="
            Explore the capabilities
            AURA can use during autonomous work.
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
                disabled={
                  refreshing
                }
                onClick={() =>
                  void loadTools({
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

      <section
        aria-label="Tool summary"
        className="
          grid
          gap-4
          sm:grid-cols-2
          xl:grid-cols-4
        "
      >
        <SummaryCard
          label="Registered Tools"
          value={
            loading
              ? "..."
              : String(
                  summary.registered
                )
          }
        />

        <SummaryCard
          label="Standard"
          value={
            loading
              ? "..."
              : String(
                  summary.standard
                )
          }
        />

        <SummaryCard
          label="Confirmation Required"
          value={
            loading
              ? "..."
              : String(
                  summary.confirmation
                )
          }
        />

        <SummaryCard
          label="Dangerous"
          value={
            loading
              ? "..."
              : String(
                  summary.dangerous
                )
          }
        />
      </section>

      <Card
        className="
          p-4
          sm:p-5
        "
      >
        <form
          className="
            grid
            gap-3
            lg:grid-cols-[1fr_auto]
          "
          onSubmit={(
            event
          ) => {
            event.preventDefault();

            void handleSearch();
          }}
        >
          <label
            className="
              relative
              block
            "
          >
            <span className="sr-only">
              Search tools and capabilities
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
              value={query}
              onChange={(
                event
              ) =>
                setQuery(
                  event.target
                    .value
                )
              }
              placeholder="Search tools and capabilities..."
              className="
                aura-input
                h-11
                pl-10
                pr-4
                text-sm
              "
            />
          </label>

          <div
            className="
              flex
              flex-wrap
              gap-2
            "
          >
            <LoadingButton
              type="submit"
              loading={
                searching
              }
              loadingText="Searching..."
            >
              Search
            </LoadingButton>

            {searchActive && (
              <Button
                type="button"
                variant="secondary"
                onClick={() =>
                  void clearSearch()
                }
              >
                Clear
              </Button>
            )}
          </div>
        </form>

        {searchActive && (
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
              {tools.length}{" "}
              {tools.length === 1
                ? "tool"
                : "tools"}{" "}
              found for{" "}
              <span
                className="
                  font-medium
                  text-[#CBD5E1]
                "
              >
                &quot;
                {query.trim()}
                &quot;
              </span>
            </p>
          </div>
        )}
      </Card>

      {loading ? (
        <ToolsSkeleton />
      ) : error ? (
        <ErrorState
          title="Tools unavailable"
          description="
            AURA could not load its
            registered tools from the backend.
          "
          error={error}
          onRetry={() =>
            void loadTools({
              refresh: true,
            })
          }
          retrying={
            refreshing
          }
        />
      ) : tools.length === 0 ? (
        <EmptyState
          title={
            searchActive
              ? "No matching tools"
              : "No tools found"
          }
          description={
            searchActive
              ? "No registered tools match your current search. Try another capability or tool name."
              : "AURA currently has no registered tools available."
          }
          icon={
            <Wrench
              size={25}
              strokeWidth={
                1.8
              }
            />
          }
          action={
            searchActive ? (
              <Button
                type="button"
                variant="secondary"
                onClick={() =>
                  void clearSearch()
                }
              >
                Clear Search
              </Button>
            ) : undefined
          }
        />
      ) : (
        <section
          aria-label="AURA tools"
          className="
            grid
            gap-4
            lg:grid-cols-2
          "
        >
          {tools.map(
            (tool) => (
              <ToolCard
                key={
                  tool.name
                }
                tool={tool}
              />
            )
          )}
        </section>
      )}
    </div>
  );
}


function SummaryCard({
  label: cardLabel,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <Card
      className="
        aura-card-hover
        p-5
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
        {cardLabel}
      </p>

      <p
        className="
          mb-0
          mt-2
          text-2xl
          font-semibold
          tracking-[-0.03em]
          text-white
        "
      >
        {value}
      </p>
    </Card>
  );
}


function ToolCard({
  tool,
}: {
  tool: ToolResponse;
}) {
  return (
    <Card
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
              truncate
              text-xl
              font-semibold
              tracking-[-0.02em]
              text-white
            "
            title={
              tool.name
            }
          >
            {tool.name}
          </h2>

          <p
            className="
              mb-0
              mt-2
              line-clamp-3
              text-sm
              leading-6
              text-[#CBD5E1]
            "
          >
            {
              tool.description
            }
          </p>
        </div>

        <StatusBadge
          label={toolSafetyLabel(
            tool
          )}
          tone={safetyTone(
            tool
          )}
          dot
        />
      </div>

      <div
        className="
          mt-5
          flex
          flex-wrap
          gap-2
        "
      >
        <StatusBadge
          label={label(
            tool.category
          )}
          tone="info"
          dot={false}
        />

        <StatusBadge
          label={`v${tool.version}`}
          tone="neutral"
          dot={false}
        />

        <StatusBadge
          label={`${tool.parameters.length} ${
            tool.parameters.length
            === 1
              ? "parameter"
              : "parameters"
          }`}
          tone="neutral"
          dot={false}
        />
      </div>

      {tool.tags.length
        > 0 && (
        <div
          className="
            mt-4
            flex
            flex-wrap
            gap-2
          "
        >
          {tool.tags.map(
            (tag) => (
              <span
                key={tag}
                className="
                  rounded-full
                  border
                  border-[#162036]
                  bg-[#111A2E]
                  px-2.5
                  py-1
                  text-xs
                  text-[#94A3B8]
                "
              >
                {tag}
              </span>
            )
          )}
        </div>
      )}

      <div
        className="
          mt-auto
          pt-5
        "
      >
        <Link
          href={`/tools/${encodeURIComponent(
            tool.name
          )}`}
          className="
            inline-flex
          "
        >
          <Button
            variant="secondary"
          >
            View Tool
          </Button>
        </Link>
      </div>
    </Card>
  );
}
"use client";

import Link from "next/link";
import {
  Brain,
  FilePlus2,
  RefreshCw,
  Search,
  Trash2,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import CreateMemoryDialog from "@/components/memory/CreateMemoryDialog";
import MemoryMaintenance from "@/components/memory/MemoryMaintenance";
import {
  MEMORY_TYPES,
  formatNumber,
  hasMetadata,
  label,
  shortId,
} from "@/components/memory/memory-utils";

import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import ConfirmDialog from "@/components/ui/ConfirmDialog";
import EmptyState from "@/components/ui/EmptyState";
import ErrorState from "@/components/ui/ErrorState";
import LoadingButton from "@/components/ui/LoadingButton";
import PageHeader from "@/components/ui/PageHeader";
import Skeleton from "@/components/ui/Skeleton";
import {
  useToast,
} from "@/components/ui/ToastProvider";

import {
  deleteMemory,
  getMemories,
  getMemoryStats,
  searchMemories,
} from "@/lib/api/memory";

import type {
  MemoryResponse,
  MemorySearchResult,
  MemoryStatsResponse,
  MemoryType,
} from "@/types/api";


type DisplayMemory = {
  memory: MemoryResponse;
  score?: number;
};


function sortedMemories(
  memories: MemoryResponse[]
) {
  return [...memories].sort(
    (left, right) =>
      right.importance - left.importance
      || right.access_count - left.access_count
  );
}


function MemoryCardsSkeleton() {
  return (
    <div
      className="space-y-4"
      aria-busy="true"
      aria-label="Loading memories"
    >
      {[0, 1, 2].map((item) => (
        <Card
          key={item}
          className="p-5"
        >
          <div
            className="
              flex
              flex-col
              gap-5
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
              <div className="flex gap-2">
                <Skeleton
                  className="
                    h-6
                    w-28
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
                  mt-5
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

              <Skeleton
                className="
                  mt-5
                  h-3
                  w-48
                "
              />
            </div>

            <div className="flex gap-2">
              <Skeleton
                className="
                  h-10
                  w-20
                  rounded-xl
                "
              />

              <Skeleton
                className="
                  h-10
                  w-24
                  rounded-xl
                "
              />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}


export default function MemoryWorkspace() {
  const {
    showToast,
  } = useToast();

  const [
    memories,
    setMemories,
  ] = useState<MemoryResponse[]>([]);

  const [
    stats,
    setStats,
  ] = useState<MemoryStatsResponse | null>(
    null
  );

  const [
    searchResults,
    setSearchResults,
  ] = useState<MemorySearchResult[] | null>(
    null
  );

  const [
    query,
    setQuery,
  ] = useState("");

  const [
    memoryType,
    setMemoryType,
  ] = useState<MemoryType | "all">(
    "all"
  );

  const [
    limit,
    setLimit,
  ] = useState(10);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    searching,
    setSearching,
  ] = useState(false);

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
  ] = useState<string | null>(
    null
  );

  const [
    lastUpdated,
    setLastUpdated,
  ] = useState<Date | null>(
    null
  );

  const [
    memoryToDelete,
    setMemoryToDelete,
  ] = useState<MemoryResponse | null>(
    null
  );

  const [
    deleting,
    setDeleting,
  ] = useState(false);


  const loadMemory = useCallback(
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
        const [
          nextMemories,
          nextStats,
        ] = await Promise.all([
          getMemories(),
          getMemoryStats(),
        ]);

        setMemories(
          sortedMemories(
            nextMemories
          )
        );

        setStats(
          nextStats
        );

        setLastUpdated(
          new Date()
        );
      } catch (nextError) {
        setError(
          nextError instanceof Error
            ? nextError.message
            : "Unable to load memory."
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
          void loadMemory();
        },
        0
      );

    return () =>
      window.clearTimeout(
        timeoutId
      );
  }, [loadMemory]);


  async function handleSearch() {
    const trimmed =
      query.trim();

    if (!trimmed) {
      setSearchResults(
        null
      );

      return;
    }

    setSearching(true);

    try {
      const results =
        await searchMemories({
          query: trimmed,
          limit,
          memory_type:
            memoryType === "all"
              ? null
              : memoryType,
        });

      setSearchResults(
        results
      );

      if (
        results.length === 0
      ) {
        showToast({
          type: "info",
          title:
            "No matches found",
          description:
            "Try another search term or memory type.",
        });
      }
    } catch (nextError) {
      showToast({
        type: "error",
        title:
          "Memory search failed",
        description:
          nextError instanceof Error
            ? nextError.message
            : "AURA could not search memory.",
      });
    } finally {
      setSearching(false);
    }
  }


  function clearSearch() {
    setSearchResults(
      null
    );

    setQuery("");

    setMemoryType(
      "all"
    );
  }


  async function handleDeleteConfirm() {
    if (!memoryToDelete) {
      return;
    }

    setDeleting(true);

    try {
      await deleteMemory(
        memoryToDelete.id
      );

      setMemories(
        (current) =>
          current.filter(
            (candidate) =>
              candidate.id
              !== memoryToDelete.id
          )
      );

      setSearchResults(
        (current) =>
          current
            ? current.filter(
                (candidate) =>
                  candidate.memory.id
                  !== memoryToDelete.id
              )
            : current
      );

      showToast({
        type: "success",
        title:
          "Memory deleted",
        description:
          "The stored memory was permanently removed from AURA.",
      });

      setMemoryToDelete(
        null
      );

      void loadMemory({
        refresh: true,
      });
    } catch (nextError) {
      showToast({
        type: "error",
        title:
          "Unable to delete memory",
        description:
          nextError instanceof Error
            ? nextError.message
            : "AURA could not delete this memory.",
      });
    } finally {
      setDeleting(false);
    }
  }


  function handleMemoryCreated(
    memory: MemoryResponse
  ) {
    setMemories(
      (current) =>
        sortedMemories([
          memory,
          ...current,
        ])
    );

    setLastUpdated(
      new Date()
    );

    showToast({
      type: "success",
      title:
        "Memory added",
      description:
        "AURA stored the new memory successfully.",
    });

    void loadMemory({
      refresh: true,
    });
  }


  const displayMemories =
    useMemo<DisplayMemory[]>(
      () => {
        if (
          searchResults
        ) {
          return searchResults.map(
            (result) => ({
              memory:
                result.memory,
              score:
                result.score,
            })
          );
        }

        return memories.map(
          (memory) => ({
            memory,
          })
        );
      },
      [
        memories,
        searchResults,
      ]
    );


  const typeCount =
    stats
      ? Object.keys(
          stats.by_type
        ).length
      : 0;

  const metadataCount =
    memories.filter(
      (memory) =>
        hasMetadata(
          memory.metadata
        )
    ).length;


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
          eyebrow="AURA / Memory"
          title="Memory"
          description="
            Inspect and manage the context
            AURA retains across work.
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
                  void loadMemory({
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
                  setDialogOpen(
                    true
                  )
                }
              >
                <FilePlus2
                  size={16}
                />

                Add Memory
              </Button>
            </>
          }
        />
      </section>

      <section
        aria-label="Memory summary"
        className="
          grid
          gap-4
          sm:grid-cols-2
          xl:grid-cols-4
        "
      >
        <SummaryCard
          label="Total Memories"
          value={
            stats
              ? String(
                  stats.total
                )
              : loading
                ? "..."
                : "0"
          }
        />

        <SummaryCard
          label="Memory Types"
          value={
            stats
              ? String(
                  typeCount
                )
              : loading
                ? "..."
                : "0"
          }
        />

        <SummaryCard
          label="Average Importance"
          value={
            stats
              ? formatNumber(
                  stats
                    .average_importance
                )
              : loading
                ? "..."
                : "0"
          }
        />

        <SummaryCard
          label="With Metadata"
          value={
            loading
              ? "..."
              : String(
                  metadataCount
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
            xl:grid-cols-[1fr_190px_140px_auto]
          "
          onSubmit={(event) => {
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
              Search AURA memory
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
              onChange={(event) =>
                setQuery(
                  event.target.value
                )
              }
              placeholder="Search AURA memory..."
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
              Memory type filter
            </span>

            <select
              value={memoryType}
              onChange={(event) =>
                setMemoryType(
                  event.target.value as MemoryType | "all"
                )
              }
              className="
                aura-input
                h-11
                px-4
                text-sm
              "
            >
              <option value="all">
                All types
              </option>

              {MEMORY_TYPES.map(
                (type) => (
                  <option
                    key={type}
                    value={type}
                  >
                    {label(
                      type
                    )}
                  </option>
                )
              )}
            </select>
          </label>

          <label>
            <span className="sr-only">
              Search result limit
            </span>

            <input
              type="number"
              min="1"
              max="50"
              value={limit}
              onChange={(event) => {
                const value =
                  Number(
                    event.target.value
                  );

                setLimit(
                  Number.isFinite(
                    value
                  )
                    ? Math.min(
                        50,
                        Math.max(
                          1,
                          value
                        )
                      )
                    : 10
                );
              }}
              className="
                aura-input
                h-11
                px-4
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
              disabled={
                !query.trim()
              }
            >
              Search
            </LoadingButton>

            {searchResults
              !== null && (
              <Button
                type="button"
                variant="secondary"
                onClick={
                  clearSearch
                }
              >
                Clear
              </Button>
            )}
          </div>
        </form>

        {searchResults
          !== null && (
          <div
            className="
              mt-4
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
              {searchResults.length}{" "}
              {searchResults.length
              === 1
                ? "result"
                : "results"}{" "}
              for{" "}
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
        <MemoryCardsSkeleton />
      ) : error ? (
        <ErrorState
          title="Memory unavailable"
          description="
            AURA could not load its stored
            memory from the backend.
          "
          error={error}
          onRetry={() =>
            void loadMemory({
              refresh: true,
            })
          }
          retrying={
            refreshing
          }
        />
      ) : displayMemories.length === 0 ? (
        <EmptyState
          title={
            searchResults !== null
              ? "No matching memories"
              : "No memories yet"
          }
          description={
            searchResults !== null
              ? "Try a different search query, memory type, or result limit."
              : "Useful context AURA stores during work will appear here."
          }
          icon={
            <Brain
              size={25}
              strokeWidth={1.8}
            />
          }
          action={
            searchResults !== null ? (
              <Button
                type="button"
                variant="secondary"
                onClick={
                  clearSearch
                }
              >
                Clear Search
              </Button>
            ) : (
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

                Add Memory
              </Button>
            )
          }
        />
      ) : (
        <section
          aria-label="AURA memories"
          className="space-y-4"
        >
          {displayMemories.map(
            ({
              memory,
              score,
            }) => (
              <MemoryCard
                key={memory.id}
                memory={memory}
                score={score}
                onDelete={() =>
                  setMemoryToDelete(
                    memory
                  )
                }
              />
            )
          )}
        </section>
      )}

      <section
        className="
          grid
          gap-6
          xl:grid-cols-2
        "
      >
        <StatsPanel
          stats={stats}
        />

        <MemoryMaintenance
          onChanged={() => {
            showToast({
              type: "success",
              title:
                "Memory updated",
              description:
                "AURA memory maintenance completed.",
            });

            void loadMemory({
              refresh: true,
            });
          }}
        />
      </section>

      <CreateMemoryDialog
        open={dialogOpen}
        onClose={() =>
          setDialogOpen(
            false
          )
        }
        onCreated={
          handleMemoryCreated
        }
      />

      <ConfirmDialog
        open={
          memoryToDelete !== null
        }
        title="Delete memory?"
        description={
          memoryToDelete
            ? `This permanently removes the selected ${label(memoryToDelete.memory_type).toLowerCase()} memory from AURA. This action cannot be undone.`
            : "This permanently removes the selected memory from AURA."
        }
        confirmLabel="Delete Memory"
        cancelLabel="Keep Memory"
        variant="danger"
        loading={deleting}
        onConfirm={() =>
          void handleDeleteConfirm()
        }
        onCancel={() => {
          if (!deleting) {
            setMemoryToDelete(
              null
            );
          }
        }}
      />
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


function MemoryCard({
  memory,
  score,
  onDelete,
}: {
  memory: MemoryResponse;
  score?: number;
  onDelete: () => void;
}) {
  return (
    <Card
      className="
        aura-card-hover
        p-5
      "
    >
      <div
        className="
          flex
          flex-col
          gap-5
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
            <Badge
              variant="purple"
            >
              {label(
                memory.memory_type
              )}
            </Badge>

            <Badge
              variant="info"
            >
              Importance{" "}
              {memory.importance.toFixed(
                2
              )}
            </Badge>

            {score !== undefined && (
              <Badge
                variant="success"
              >
                Relevance{" "}
                {score.toFixed(
                  2
                )}
              </Badge>
            )}

            {hasMetadata(
              memory.metadata
            ) && (
              <Badge variant="default">
                Metadata
              </Badge>
            )}
          </div>

          <p
            className="
              mb-0
              mt-4
              line-clamp-3
              text-sm
              leading-6
              text-[#CBD5E1]
            "
          >
            {memory.content}
          </p>

          <div
            className="
              mt-4
              flex
              flex-wrap
              items-center
              gap-x-3
              gap-y-1
              text-xs
              text-[#64748B]
            "
          >
            <span
              title={memory.id}
            >
              ID{" "}
              {shortId(
                memory.id
              )}
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
              Accessed{" "}
              {memory.access_count}{" "}
              {memory.access_count === 1
                ? "time"
                : "times"}
            </span>
          </div>
        </div>

        <div
          className="
            flex
            shrink-0
            flex-wrap
            gap-2
          "
        >
          <Link
            href={`/memory/${memory.id}`}
            className="inline-flex"
          >
            <Button variant="secondary">
              View
            </Button>
          </Link>

          <Button
            type="button"
            variant="danger"
            onClick={
              onDelete
            }
          >
            <Trash2 size={15} />

            Delete
          </Button>
        </div>
      </div>
    </Card>
  );
}


function StatsPanel({
  stats,
}: {
  stats:
    | MemoryStatsResponse
    | null;
}) {
  return (
    <Card
      className="
        p-5
        sm:p-6
      "
    >
      <h2
        className="
          m-0
          text-lg
          font-semibold
          text-white
        "
      >
        Memory Statistics
      </h2>

      <p
        className="
          mb-0
          mt-1
          text-sm
          text-[#94A3B8]
        "
      >
        Real aggregate data
        from AURA memory.
      </p>

      {!stats ? (
        <div
          className="
            mt-5
            space-y-3
          "
        >
          <Skeleton
            className="
              h-20
              w-full
              rounded-xl
            "
          />

          <Skeleton
            className="
              h-20
              w-full
              rounded-xl
            "
          />
        </div>
      ) : (
        <div
          className="
            mt-5
            space-y-6
          "
        >
          <div
            className="
              grid
              gap-3
              sm:grid-cols-2
            "
          >
            {Object.entries(
              stats.by_type
            ).map(
              ([
                type,
                count,
              ]) => (
                <div
                  key={type}
                  className="
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
                      text-xs
                      font-medium
                      uppercase
                      tracking-[0.14em]
                      text-[#64748B]
                    "
                  >
                    {label(
                      type
                    )}
                  </p>

                  <p
                    className="
                      mb-0
                      mt-2
                      text-lg
                      font-semibold
                      text-white
                    "
                  >
                    {count}
                  </p>
                </div>
              )
            )}
          </div>

          <div>
            <h3
              className="
                m-0
                text-sm
                font-semibold
                text-[#CBD5E1]
              "
            >
              Most accessed
            </h3>

            <div
              className="
                mt-3
                space-y-2
              "
            >
              {stats.most_accessed.length === 0 ? (
                <p
                  className="
                    m-0
                    text-sm
                    text-[#64748B]
                  "
                >
                  No accessed memories yet.
                </p>
              ) : (
                stats.most_accessed.map(
                  (item) => (
                    <div
                      key={item.id}
                      className="
                        rounded-xl
                        border
                        border-[#162036]
                        bg-[#0A1020]
                        px-3
                        py-2.5
                      "
                    >
                      <p
                        className="
                          m-0
                          truncate
                          text-sm
                          text-[#94A3B8]
                        "
                        title={item.content}
                      >
                        {item.content}
                      </p>

                      <p
                        className="
                          mb-0
                          mt-1
                          text-[11px]
                          text-[#475569]
                        "
                      >
                        {item.access_count} accesses
                      </p>
                    </div>
                  )
                )
              )}
            </div>
          </div>

          <div>
            <h3
              className="
                m-0
                text-sm
                font-semibold
                text-[#CBD5E1]
              "
            >
              Oldest
            </h3>

            <div
              className="
                mt-3
                space-y-2
              "
            >
              {stats.oldest.length === 0 ? (
                <p
                  className="
                    m-0
                    text-sm
                    text-[#64748B]
                  "
                >
                  No memories yet.
                </p>
              ) : (
                stats.oldest.map(
                  (item) => (
                    <p
                      key={item.id}
                      className="
                        m-0
                        truncate
                        rounded-xl
                        border
                        border-[#162036]
                        bg-[#0A1020]
                        px-3
                        py-2.5
                        text-sm
                        text-[#94A3B8]
                      "
                      title={item.content}
                    >
                      {item.content}
                    </p>
                  )
                )
              )}
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
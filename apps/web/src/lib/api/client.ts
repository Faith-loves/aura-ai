const API_BASE_URL =
  process.env.NEXT_PUBLIC_AURA_API_URL ??
  "http://127.0.0.1:8000";

type ApiFetchOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  headers?: HeadersInit;
  body?: BodyInit | null;
  signal?: AbortSignal;
};

function buildApiUrl(path: string) {
  const baseUrl = API_BASE_URL.endsWith("/")
    ? API_BASE_URL
    : `${API_BASE_URL}/`;
  const normalizedPath = path.startsWith("/") ? path.slice(1) : path;

  return new URL(normalizedPath, baseUrl).toString();
}

async function readErrorMessage(response: Response) {
  const fallback = `${response.status} ${response.statusText}`.trim();

  try {
    const payload = (await response.json()) as { detail?: unknown; message?: unknown };
    const message = payload.detail ?? payload.message;

    if (typeof message === "string") {
      return message;
    }

    if (message !== undefined) {
      return JSON.stringify(message);
    }
  } catch {
    try {
      const text = await response.text();
      return text || fallback;
    } catch {
      return fallback;
    }
  }

  return fallback;
}

export async function apiFetch<T>(
  path: string,
  options: ApiFetchOptions = {},
): Promise<T> {
  const response = await fetch(buildApiUrl(path), {
    method: options.method ?? "GET",
    headers: {
      Accept: "application/json",
      ...options.headers,
    },
    body: options.body,
    signal: options.signal,
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(`AURA API request failed for ${path}: ${message}`);
  }

  return (await response.json()) as T;
}

export { API_BASE_URL };

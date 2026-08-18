import type {
  AuraRunRequest,
  AuraRunResponse,
} from "@/types/api";

import {
  apiFetch,
} from "./client";

export function runAura(request: AuraRunRequest) {
  return apiFetch<AuraRunResponse>("/run", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });
}

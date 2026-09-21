export interface HealthResponse {
  status: 'healthy' | 'degraded';
  service: string;
  version: string;
  environment: string;
  dependencies: Record<string, 'up' | 'down'>;
}

export function getApiBaseUrl(): string {
  return (process.env.API_INTERNAL_URL ?? 'http://api:8000').replace(/\/$/, '');
}

export async function fetchHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${getApiBaseUrl()}/health`, { cache: 'no-store' });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as HealthResponse;
  } catch {
    return null;
  }
}

import { StatusCard } from '@/components/StatusCard';
import { fetchHealth } from '@/lib/api';

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  const health = await fetchHealth();
  const dependencies = health?.dependencies ?? {};

  return (
    <main className="shell">
      <header className="hero">
        <p className="eyebrow">BROBOND</p>
        <h1>AI Sales Engine</h1>
        <p className="subtitle">
          Enterprise infrastructure for AI-assisted lead qualification and pipeline automation.
        </p>
      </header>

      <section className="grid">
        <StatusCard
          label="API"
          value={health ? `${health.status} · v${health.version}` : 'unreachable'}
          healthy={health?.status === 'healthy'}
        />
        {Object.entries(dependencies).map(([name, state]) => (
          <StatusCard key={name} label={name} value={state} healthy={state === 'up'} />
        ))}
      </section>

      <section className="links">
        <a href="/api/backend/docs" target="_blank" rel="noreferrer">
          API Swagger
        </a>
        <a href="/api/backend/health" target="_blank" rel="noreferrer">
          Health JSON
        </a>
      </section>
    </main>
  );
}

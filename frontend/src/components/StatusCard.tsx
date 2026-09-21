interface StatusCardProps {
  label: string;
  value: string;
  healthy: boolean;
}

export function StatusCard({ label, value, healthy }: StatusCardProps) {
  return (
    <div className="card">
      <span className={`dot ${healthy ? 'dot-up' : 'dot-down'}`} aria-hidden />
      <div>
        <p className="card-label">{label}</p>
        <p className="card-value">{value}</p>
      </div>
    </div>
  );
}

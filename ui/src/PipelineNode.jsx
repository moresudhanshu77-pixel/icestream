import { Handle, Position } from "reactflow";

const COLORS = {
  healthy: "#16a34a",
  warning: "#f59e0b",
  quarantined: "#dc2626",
};

export default function PipelineNode({ data }) {
  const color = COLORS[data.status] ?? COLORS.healthy;

  return (
    <div
      style={{
        padding: "14px 20px",
        borderRadius: 10,
        minWidth: 160,
        border: `2px solid ${color}`,
        background: "#0f172a",
        color: "#e2e8f0",
        boxShadow: data.status === "quarantined" ? `0 0 16px ${color}` : "none",
        transition: "box-shadow 0.3s ease, border-color 0.3s ease",
      }}
    >
      <Handle type="target" position={Position.Left} />
      <div style={{ fontWeight: 600 }}>{data.label}</div>
      <div style={{ fontSize: 12, opacity: 0.7 }}>{data.sub}</div>
      <div style={{ fontSize: 11, marginTop: 6, color }}>
        ● {data.status}
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
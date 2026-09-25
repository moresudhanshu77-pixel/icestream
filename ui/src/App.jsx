import { useState, useMemo } from "react";
import ReactFlow, { Background, Controls, MarkerType } from "reactflow";
import "reactflow/dist/style.css";
import PipelineNode from "./PipelineNode";

const nodeTypes = { pipeline: PipelineNode };

export default function App() {
  // Week 3 replaces this state with live updates from the circuit breaker via WebSockets.
  const [status, setStatus] = useState({
    ingest: "healthy",
    process: "healthy",
    serve: "healthy",
  });

  const nodes = useMemo(
    () => [
      {
        id: "ingest",
        type: "pipeline",
        position: { x: 50, y: 120 },
        data: { label: "Ingest", sub: "Kafka: checkout.events", status: status.ingest },
      },
      {
        id: "process",
        type: "pipeline",
        position: { x: 350, y: 120 },
        data: { label: "Process", sub: "Flink -> Iceberg", status: status.process },
      },
      {
        id: "serve",
        type: "pipeline",
        position: { x: 650, y: 120 },
        data: { label: "Serve", sub: "Analytics / BI", status: status.serve },
      },
    ],
    [status]
  );

  const edges = useMemo(
    () =>
      [
        ["ingest", "process"],
        ["process", "serve"],
      ].map(([source, target]) => {
        const broken = status[target] === "quarantined";
        return {
          id: `${source}-${target}`,
          source,
          target,
          animated: !broken,
          style: {
            stroke: broken ? "#dc2626" : "#38bdf8",
            strokeWidth: 2,
            strokeDasharray: broken ? "6 4" : undefined,
          },
          markerEnd: { type: MarkerType.ArrowClosed },
        };
      }),
    [status]
  );

  const toggleProcess = () => {
    setStatus((s) => ({
      ...s,
      process: s.process === "healthy" ? "quarantined" : "healthy",
    }));
  };

  return (
    <div style={{ height: "100vh", background: "#020617" }}>
      <div style={{ position: "absolute", zIndex: 10, margin: 16 }}>
        <button
          onClick={toggleProcess}
          style={{
            padding: "8px 14px",
            borderRadius: 6,
            border: "1px solid #334155",
            background: "#0f172a",
            color: "#e2e8f0",
            cursor: "pointer",
          }}
        >
          Toggle Process node (demo)
        </button>
      </div>
      <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView>
        <Background color="#1e293b" />
        <Controls />
      </ReactFlow>
    </div>
  );
}
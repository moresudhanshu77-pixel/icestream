import ReactFlow, { Background, Controls } from "reactflow";
import "reactflow/dist/style.css";

const nodes = [
  { id: "1", position: { x: 100, y: 100 }, data: { label: "React Flow is working" } },
];

export default function App() {
  return (
    <div style={{ height: "100vh" }}>
      <ReactFlow nodes={nodes} edges={[]} fitView>
        <Background color="#1e293b" />
        <Controls />
      </ReactFlow>
    </div>
  );
}
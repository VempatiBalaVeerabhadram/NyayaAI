import React, { useEffect, useRef, useState } from 'react';
import { Network, ZoomIn, ZoomOut, RotateCcw, Info } from 'lucide-react';

const NODE_COLORS = {
  Act: '#10b981', // Emerald
  Section: '#a855f7', // Purple
  Case: '#3b82f6', // Electric Blue
  Judge: '#f59e0b', // Amber
  Court: '#06b6d4', // Cyan
  LegalIssue: '#ef4444', // Red
  Document: '#64748b', // Slate
};

export default function GraphCanvas({ nodes = [], relationships = [], onSelectNode }) {
  const canvasRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Node positions in simulation space
  const nodePositions = useRef(new Map());

  // Initialize simulated radial/force layout
  useEffect(() => {
    if (!nodes.length) return;

    const width = 800;
    const height = 600;
    const centerX = width / 2;
    const centerY = height / 2;

    const posMap = new Map();
    const count = nodes.length;

    nodes.forEach((node, index) => {
      // Group by label in concentric circles or clusters
      let radius = 180;
      if (node.label === 'Act') radius = 60;
      else if (node.label === 'Section') radius = 140;
      else if (node.label === 'Case') radius = 220;
      else if (node.label === 'Judge') radius = 290;

      const angle = (index / count) * 2 * Math.PI + (node.label.charCodeAt(0) % 5);
      const x = centerX + radius * Math.cos(angle) + (Math.random() * 20 - 10);
      const y = centerY + radius * Math.sin(angle) + (Math.random() * 20 - 10);

      posMap.set(node.id, {
        id: node.id,
        label: node.label,
        name: node.properties?.name || node.properties?.title || node.id,
        x,
        y,
        radius: node.label === 'Act' ? 14 : node.label === 'Case' ? 11 : 8,
        color: NODE_COLORS[node.label] || '#94a3b8',
      });
    });

    nodePositions.current = posMap;
    draw();
  }, [nodes, relationships]);

  const draw = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);
    ctx.save();

    // Pan & Zoom transform
    ctx.translate(offset.x + width / 2, offset.y + height / 2);
    ctx.scale(zoom, zoom);
    ctx.translate(-width / 2, -height / 2);

    // 1. Draw Relationships (Edges)
    relationships.forEach((rel) => {
      const source = nodePositions.current.get(rel.source_id);
      const target = nodePositions.current.get(rel.target_id);

      if (source && target) {
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.strokeStyle =
          selectedNode && (selectedNode.id === source.id || selectedNode.id === target.id)
            ? '#38bdf8'
            : 'rgba(100, 116, 139, 0.25)';
        ctx.lineWidth =
          selectedNode && (selectedNode.id === source.id || selectedNode.id === target.id) ? 2 : 1;
        ctx.stroke();

        // Edge label if hovered / selected
        if (selectedNode && (selectedNode.id === source.id || selectedNode.id === target.id)) {
          const midX = (source.x + target.x) / 2;
          const midY = (source.y + target.y) / 2;
          ctx.fillStyle = '#94a3b8';
          ctx.font = '9px monospace';
          ctx.fillText(rel.type, midX, midY);
        }
      }
    });

    // 2. Draw Nodes
    nodePositions.current.forEach((node) => {
      const isSelected = selectedNode && selectedNode.id === node.id;

      // Glow effect for selected
      if (isSelected) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius + 6, 0, 2 * Math.PI);
        ctx.fillStyle = 'rgba(59, 130, 246, 0.4)';
        ctx.fill();
      }

      // Outer circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, 2 * Math.PI);
      ctx.fillStyle = node.color;
      ctx.shadowColor = node.color;
      ctx.shadowBlur = isSelected ? 12 : 4;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Border
      ctx.strokeStyle = '#0f172a';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Node Label text
      ctx.fillStyle = isSelected ? '#ffffff' : '#cbd5e1';
      ctx.font = `${isSelected ? 'bold 11px' : '10px'} sans-serif`;
      ctx.textAlign = 'center';
      const shortName = node.name.length > 20 ? node.name.slice(0, 18) + '…' : node.name;
      ctx.fillText(shortName, node.x, node.y + node.radius + 12);
    });

    ctx.restore();
  };

  useEffect(() => {
    draw();
  }, [zoom, offset, selectedNode]);

  // Handle canvas click to select node
  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Convert mouse to world coords
    const width = canvas.width;
    const height = canvas.height;
    const worldX = (mouseX - (offset.x + width / 2)) / zoom + width / 2;
    const worldY = (mouseY - (offset.y + height / 2)) / zoom + height / 2;

    let clicked = null;
    nodePositions.current.forEach((node) => {
      const dist = Math.hypot(node.x - worldX, node.y - worldY);
      if (dist <= node.radius + 4) {
        clicked = node;
      }
    });

    setSelectedNode(clicked);
    if (onSelectNode) onSelectNode(clicked);
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setOffset({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div className="relative w-full h-full bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden flex flex-col">
      {/* Controls Bar */}
      <div className="absolute top-4 right-4 z-10 flex items-center gap-1.5 p-1.5 rounded-xl bg-slate-900/90 border border-slate-700/80 backdrop-blur-md shadow-lg">
        <button
          onClick={() => setZoom((z) => Math.min(z + 0.2, 2.5))}
          className="p-1.5 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(z - 0.2, 0.4))}
          className="p-1.5 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={() => {
            setZoom(1);
            setOffset({ x: 0, y: 0 });
          }}
          className="p-1.5 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 p-3 rounded-xl bg-slate-900/90 border border-slate-800/90 backdrop-blur-md text-xs flex items-center gap-3 flex-wrap shadow-lg">
        {Object.entries(NODE_COLORS).map(([label, color]) => (
          <div key={label} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }}></span>
            <span className="text-slate-300 text-[11px]">{label}</span>
          </div>
        ))}
      </div>

      {/* Main Canvas */}
      <canvas
        ref={canvasRef}
        width={900}
        height={620}
        onClick={handleCanvasClick}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        className="w-full h-full cursor-grab active:cursor-grabbing flex-grow"
      />
    </div>
  );
}

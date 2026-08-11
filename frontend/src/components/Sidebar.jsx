import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  FileText,
  Gauge,
  Factory,
  Settings,
  Wrench
} from "lucide-react";
import { NavLink } from "react-router-dom";
import "../styles/sidebar.css";

const navItems = [
  { label: "Overview", to: "/", icon: Gauge },
  { label: "Machines", to: "/machines", icon: Factory },
  { label: "Live Monitor", to: "/live-monitor", icon: Activity },
  { label: "Analytics", to: "/analytics", icon: BarChart3 },
  { label: "AI Prediction", to: "/ai-prediction", icon: Bot },
  { label: "Alerts", to: "/alerts", icon: AlertTriangle },
  { label: "Reports", to: "/reports", icon: FileText },
  { label: "Maintenance", to: "/maintenance", icon: Wrench },
  { label: "Settings", to: "/settings", icon: Settings }
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">PX</div>
        <div>
          <strong>PredictX AI</strong>
          <span>Predictive Maintenance</span>
        </div>
      </div>

      <nav className="nav-list">
        {navItems.map(({ label, to, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="system-status">
        <span>System Status</span>
        <strong>
          <i /> Online
        </strong>
        <small>Backend monitoring enabled</small>
      </div>
    </aside>
  );
}

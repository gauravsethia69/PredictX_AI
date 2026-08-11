import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Layout from "./components/Layout";
import { MachineProvider } from "./context/MachineContext";

import Dashboard from "./pages/Dashboard";
import Machines from "./pages/Machines";
import LiveMonitor from "./pages/LiveMonitor";
import Analytics from "./pages/Analytics";
import AIPrediction from "./pages/AIPrediction";
import Alerts from "./pages/Alerts";
import Reports from "./pages/Reports";
import Maintenance from "./pages/Maintenance";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <BrowserRouter>
      <MachineProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />

            <Route
              path="/machines"
              element={<Machines />}
            />

            <Route
              path="/live-monitor"
              element={<LiveMonitor />}
            />

            <Route
              path="/analytics"
              element={<Analytics />}
            />

            <Route
              path="/ai-prediction"
              element={<AIPrediction />}
            />

            <Route
              path="/alerts"
              element={<Alerts />}
            />

            <Route
              path="/reports"
              element={<Reports />}
            />

            <Route
              path="/maintenance"
              element={<Maintenance />}
            />

            <Route
              path="/settings"
              element={<Settings />}
            />

            <Route
              path="*"
              element={<Navigate to="/" replace />}
            />
          </Route>
        </Routes>
      </MachineProvider>
    </BrowserRouter>
  );
}
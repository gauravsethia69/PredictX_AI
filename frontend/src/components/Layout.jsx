import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import "../styles/layout.css";

export default function Layout() {
  return (
    <div className="app-shell">
      <Sidebar />

      <section className="main-shell">
        <Topbar />

        <main className="page-content">
          <Outlet />
        </main>
      </section>
    </div>
  );
}
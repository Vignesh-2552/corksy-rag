import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import { App } from "@/app/App";
import { AppShell } from "@/components/layout/AppShell";
import { TooltipProvider } from "@/components/ui/tooltip";

import "@/app/index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <TooltipProvider>
      <BrowserRouter>
        <AppShell>
          <App />
        </AppShell>
      </BrowserRouter>
    </TooltipProvider>
  </StrictMode>,
);

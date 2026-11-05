
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import Demo from "./demo.jsx";

console.log("main.jsx loaded");

createRoot(document.getElementById("root")).render(
    <div>
        <App />
    </div>
);

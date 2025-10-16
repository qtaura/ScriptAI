import { useEffect } from "react";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { ModelComparison } from "./components/ModelComparison";
import { HowItWorks } from "./components/HowItWorks";
import { CodeGenerator } from "./components/CodeGenerator";
import { Features } from "./components/Features";
import { DualInterface } from "./components/DualInterface";
import { Footer } from "./components/Footer";
import { MetricsPanel } from "./components/MetricsPanel";

export default function App() {
  useEffect(() => {
    document.title = "ScriptAI - AI-Powered Code Generation Platform";

    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.setAttribute(
        "content",
        "Transform natural language into production-ready code. Multi-model AI support with OpenAI, HuggingFace, and local models. Generate scripts in 50+ languages."
      );
    } else {
      const meta = document.createElement("meta");
      meta.name = "description";
      meta.content = "Transform natural language into production-ready code. Multi-model AI support with OpenAI, HuggingFace, and local models. Generate scripts in 50+ languages.";
      document.head.appendChild(meta);
    }
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <Hero />
        <ModelComparison />
        <CodeGenerator />
        <HowItWorks />
        <Features />
        <DualInterface />
        <MetricsPanel />
      </main>
      <Footer />
    </div>
  );
}
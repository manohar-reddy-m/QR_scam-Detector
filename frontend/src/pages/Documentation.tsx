import React from 'react';
import {
  BookOpen,
  ShieldAlert,
  Layers,
  Cpu,
  Lock,
} from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';

export const Documentation: React.FC = () => {
  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-white font-sans flex items-center gap-2.5">
          <BookOpen className="w-6 h-6 text-cyan-400" />
          <span>Platform Documentation & Threat Intelligence Guide</span>
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Technical specifications, threat models, risk calculation formulas, and architectural references.
        </p>
      </div>

      {/* 1. System Vision & Architecture */}
      <Card>
        <CardHeader
          title="1. System Architecture & Separation of Concerns"
          subtitle="Design principles ensuring modularity and non-blocking security"
          icon={<Layers className="w-5 h-5 text-blue-400" />}
        />
        <div className="space-y-4 text-xs text-gray-300 font-sans leading-relaxed">
          <p>
            <strong>QR Sentinel</strong> is built with strict architectural separation between optical Computer Vision decoders and threat intelligence classification. A URL classifier is never conflated with an optical QR classifier.
          </p>
          <div className="p-4 rounded-xl bg-navy-950 border border-navy-800 font-mono text-xs text-cyan-300">
            <pre className="overflow-x-auto">
{`React Client (TypeScript + Tailwind CSS + TanStack Query)
    │
    ▼
FastAPI Gateway (Uvicorn / Pydantic v2 / Structured JSON Logging)
    ├── Input Validation (Magic Bytes: PNG, JPEG, WEBP; Max 10MB)
    ├── Image Preprocessor (Grayscale, OTSU Threshold, Contrast, Denoise)
    ├── QR Decoding Pipeline (PyZBar primary ➔ OpenCV fallback)
    ├── URL Normalization & Feature Extractor (19 Statistical Dimensions)
    ├── ML Threat Classifier (Random Forest + Isotonic Calibration)
    ├── Risk Assessment Engine (Hybrid: 65% ML Score + 35% Deterministic Rules)
    └── Explainability & Security Recommendation Engine`}
            </pre>
          </div>
        </div>
      </Card>

      {/* 2. Core Security Objectives & Threat Model */}
      <Card>
        <CardHeader
          title="2. Threat Model & Attack Vectors"
          subtitle="Real-world vulnerabilities addressed by QR Sentinel"
          icon={<ShieldAlert className="w-5 h-5 text-rose-400" />}
        />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-sans">
          <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 space-y-1">
            <h4 className="font-bold text-white font-mono uppercase text-xs">Quishing (QR Phishing)</h4>
            <p className="text-gray-400">
              Attackers print fake QR codes in public areas (parking meters, restaurant menus, bank flyers) redirecting users to fake credential-harvesting portals.
            </p>
          </div>
          <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 space-y-1">
            <h4 className="font-bold text-white font-mono uppercase text-xs">Fake Payment Destinations</h4>
            <p className="text-gray-400">
              Tampered UPI payloads (e.g. <code>upi://pay?pa=thief@bank</code>) replace vendor QR codes, routing payments to fraudulent bank accounts.
            </p>
          </div>
          <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 space-y-1">
            <h4 className="font-bold text-white font-mono uppercase text-xs">URL Shorteners & Obfuscation</h4>
            <p className="text-gray-400">
              Services like bit.ly, tinyurl, and percent-encoded hex sequences hide the ultimate destination from the scanner preview.
            </p>
          </div>
          <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 space-y-1">
            <h4 className="font-bold text-white font-mono uppercase text-xs">Sticker Replacement Attacks</h4>
            <p className="text-gray-400">
              Physical stickers overlaid directly on legitimate signage. Detected via our dual-QR comparison tool.
            </p>
          </div>
        </div>
      </Card>

      {/* 3. Risk Engine Formula */}
      <Card>
        <CardHeader
          title="3. Reliability-Aware Risk Scoring"
          subtitle="Mathematical formulation for threat aggregation"
          icon={<Cpu className="w-5 h-5 text-purple-400" />}
        />
        <div className="space-y-3 text-xs text-gray-300 font-sans leading-relaxed">
          <p>
            QR Sentinel avoids simplistic binary classifications. Instead, a composite threat score <span className="font-mono text-cyan-300">S ∈ [0.0, 1.0]</span> is calculated:
          </p>
          <div className="p-3.5 rounded-lg bg-navy-950 border border-navy-800 font-mono text-xs text-white">
            Score = (0.65 × ML_Probability) + (0.35 × Deterministic_Rule_Score)
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-center font-mono">
            <div className="p-2 rounded bg-emerald-950/60 border border-emerald-800">
              <span className="text-emerald-400 font-bold block">LOW RISK</span>
              <span className="text-[11px] text-gray-400">Score &lt; 0.30</span>
            </div>
            <div className="p-2 rounded bg-amber-950/60 border border-amber-800">
              <span className="text-amber-400 font-bold block">MEDIUM RISK</span>
              <span className="text-[11px] text-gray-400">0.30 &le; Score &lt; 0.60</span>
            </div>
            <div className="p-2 rounded bg-rose-950/60 border border-rose-800">
              <span className="text-rose-400 font-bold block">HIGH RISK</span>
              <span className="text-[11px] text-gray-400">Score &ge; 0.60</span>
            </div>
            <div className="p-2 rounded bg-gray-900 border border-gray-700">
              <span className="text-gray-300 font-bold block">INCONCLUSIVE</span>
              <span className="text-[11px] text-gray-400">Unreadable / Out-of-Scope</span>
            </div>
          </div>
        </div>
      </Card>

      {/* 4. Security Hardening Policies */}
      <Card>
        <CardHeader
          title="4. Security Hardening & Zero-Execution Policy"
          subtitle="Defensive safeguards implemented in the codebase"
          icon={<Lock className="w-5 h-5 text-emerald-400" />}
        />
        <ul className="space-y-2 text-xs text-gray-300 font-sans list-disc list-inside">
          <li><strong>Zero Auto-Navigation:</strong> URLs are never opened, rendered in a browser frame, or fetched over the network.</li>
          <li><strong>Magic Byte Validation:</strong> Uploaded images are inspected for file headers (PNG, JPEG, WEBP) to prevent extension spoofing.</li>
          <li><strong>Safe Temp File Handling:</strong> Uploaded buffers are processed entirely in-memory using PIL and OpenCV.</li>
          <li><strong>Stack Trace Suppression:</strong> Production exception handlers return standardized JSON errors without exposing internal file paths.</li>
          <li><strong>No Arbitrary Code Execution:</strong> Payload strings are treated strictly as untrusted text.</li>
        </ul>
      </Card>
    </div>
  );
};

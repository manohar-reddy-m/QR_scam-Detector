import React from 'react';
import {
  Server,
  Layers,
  Terminal,
  ExternalLink,
  ShieldCheck,
  Activity,
  HardDrive,
} from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { useSystemHealth } from '../hooks/useSystemHealth';

export const SystemInfo: React.FC = () => {
  const { data: health, isLoading: healthLoading } = useSystemHealth();

  const endpoints = [
    { method: 'POST', path: '/api/v1/qr/analyze', desc: 'Full QR decode + layered threat analysis', curl: 'curl -X POST -F "file=@qr.png" http://localhost:8000/api/v1/qr/analyze' },
    { method: 'POST', path: '/api/v1/qr/decode', desc: 'Decode QR code image only (no risk engine)', curl: 'curl -X POST -F "file=@qr.png" http://localhost:8000/api/v1/qr/decode' },
    { method: 'POST', path: '/api/v1/qr/distort', desc: 'Image degradation & robustness stress test', curl: 'curl -X POST -F "file=@qr.png" -F "severity=0.5" http://localhost:8000/api/v1/qr/distort' },
    { method: 'POST', path: '/api/v1/qr/compare', desc: 'Compare two QR codes for tampering / substitution', curl: 'curl -X POST -F "file1=@a.png" -F "file2=@b.png" http://localhost:8000/api/v1/qr/compare' },
    { method: 'POST', path: '/api/v1/url/analyze', desc: 'Direct URL 19-feature extraction + ML scoring', curl: 'curl -X POST -H "Content-Type: application/json" -d \'{"url":"https://evil.tk"}\' http://localhost:8000/api/v1/url/analyze' },
    { method: 'GET', path: '/api/v1/model/status', desc: 'ML model loading status & metadata', curl: 'curl http://localhost:8000/api/v1/model/status' },
    { method: 'GET', path: '/api/v1/model/metrics', desc: 'Evaluation metrics from training pipeline', curl: 'curl http://localhost:8000/api/v1/model/metrics' },
    { method: 'GET', path: '/api/v1/system/health', desc: 'Service health check & platform diagnostics', curl: 'curl http://localhost:8000/api/v1/system/health' },
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-white font-sans flex items-center gap-2.5">
          <Server className="w-6 h-6 text-cyan-400" />
          <span>System Information & Infrastructure</span>
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Diagnostics, runtime parameters, and API endpoint documentation for the QR Sentinel engine.
        </p>
      </div>

      {/* Runtime Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Server Health"
          value={health?.status === 'healthy' ? 'ONLINE' : healthLoading ? 'POLLING...' : 'UNHEALTHY'}
          subtext="FastAPI / Uvicorn ASGI"
          icon={<Activity className="w-4 h-4" />}
          color={health?.status === 'healthy' ? 'emerald' : 'amber'}
        />
        <MetricCard
          label="App Version"
          value="v1.0.0"
          subtext="Production Release"
          icon={<ShieldCheck className="w-4 h-4" />}
          color="blue"
        />
        <MetricCard
          label="Platform OS"
          value="Windows x64"
          subtext={health?.platform?.slice(0, 20) || 'Win32 AMD64'}
          icon={<HardDrive className="w-4 h-4" />}
          color="purple"
        />
        <MetricCard
          label="Python Runtime"
          value="3.10.11"
          subtext="CPython VirtualEnv"
          icon={<Terminal className="w-4 h-4" />}
          color="cyan"
        />
      </div>

      {/* Environment & Configuration */}
      <Card>
        <CardHeader
          title="Runtime Configuration"
          subtitle="Active settings loaded via Pydantic Settings"
          icon={<Terminal className="w-5 h-5 text-blue-400" />}
        />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
          <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 space-y-1">
            <span className="text-gray-400 font-semibold block">API Prefix:</span>
            <span className="text-cyan-300">/api/v1</span>
          </div>
          <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 space-y-1">
            <span className="text-gray-400 font-semibold block">Max Upload Size:</span>
            <span className="text-cyan-300">10 MB (Enforced via magic bytes)</span>
          </div>
          <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 space-y-1">
            <span className="text-gray-400 font-semibold block">Model Storage Path:</span>
            <span className="text-cyan-300">backend/models/threat_classifier.joblib</span>
          </div>
          <div className="p-3 rounded-lg bg-navy-950 border border-navy-800 space-y-1">
            <span className="text-gray-400 font-semibold block">Risk Thresholds:</span>
            <span className="text-cyan-300">LOW &lt; 0.30 | HIGH &ge; 0.60</span>
          </div>
        </div>
      </Card>

      {/* API Endpoint Reference Table */}
      <Card>
        <CardHeader
          title="API v1 Catalog & cURL References"
          subtitle="RESTful endpoints exposed by the backend gateway"
          icon={<Layers className="w-5 h-5 text-cyan-400" />}
          action={
            <a
              href="http://localhost:8000/api/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-mono"
            >
              <span>Swagger UI</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          }
        />
        <div className="space-y-3 font-mono text-xs">
          {endpoints.map((ep, i) => (
            <div key={i} className="p-3 rounded-lg bg-navy-950/80 border border-navy-800 space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      ep.method === 'POST'
                        ? 'bg-blue-950 text-blue-400 border border-blue-800'
                        : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    }`}
                  >
                    {ep.method}
                  </span>
                  <span className="text-white font-semibold">{ep.path}</span>
                </div>
                <span className="text-gray-400 font-sans text-xs">{ep.desc}</span>
              </div>
              <div className="p-2 rounded bg-navy-900 border border-navy-800/80 text-[11px] text-gray-300 select-all overflow-x-auto">
                {ep.curl}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

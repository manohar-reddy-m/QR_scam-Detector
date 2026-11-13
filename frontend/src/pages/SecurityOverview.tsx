import React from 'react';
import { Link } from 'react-router-dom';
import { QrCode, Globe, ShieldCheck, AlertTriangle, Cpu, Server } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { useSystemHealth } from '../hooks/useSystemHealth';
import { useModelStatus } from '../hooks/useModelStatus';

export const SecurityOverview: React.FC = () => {
  const { data: health, isLoading: hl } = useSystemHealth();
  const { data: model, isLoading: ml } = useModelStatus();

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-xl font-semibold text-white">QR Sentinel</h1>
        <p className="text-sm text-gray-400 mt-1">
          AI-powered QR code threat detection — inspect payloads before interaction.
        </p>
      </div>

      {/* Quick actions */}
      <div className="flex gap-3">
        <Link to="/analyze">
          <Button variant="primary" icon={<QrCode className="w-4 h-4" />}>
            Scan QR Code
          </Button>
        </Link>
        <Link to="/url">
          <Button variant="secondary" icon={<Globe className="w-4 h-4" />}>
            Analyze URL
          </Button>
        </Link>
      </div>

      {/* Synthetic data notice */}
      <div className="flex items-start gap-3 text-xs text-amber-300 bg-amber-950/30 border border-amber-900/50 rounded-lg p-3">
        <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
        <span>
          ML model trained on synthetic data for research purposes. Rule-based heuristics operate independently and are reliable. ML probabilities should not be used as sole indicators in production.
        </span>
      </div>

      {/* Status metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard
          label="Engine"
          value={hl ? '—' : health?.status === 'healthy' ? 'Online' : 'Offline'}
          subtext="FastAPI + Uvicorn"
          icon={<Server className="w-4 h-4" />}
          color={health?.status === 'healthy' ? 'emerald' : 'rose'}
        />
        <MetricCard
          label="ML Model"
          value={ml ? '—' : model?.loaded ? 'Loaded' : 'Offline'}
          subtext={model?.model_type ?? 'Random Forest'}
          icon={<Cpu className="w-4 h-4" />}
          color={model?.loaded ? 'blue' : 'rose'}
        />
        <MetricCard
          label="Features"
          value={model?.num_features ?? 19}
          subtext="URL heuristic dimensions"
          color="cyan"
        />
        <MetricCard
          label="Safety"
          value="Zero-open"
          subtext="No auto-fetch · No redirects"
          icon={<ShieldCheck className="w-4 h-4" />}
          color="emerald"
        />
      </div>

      {/* How it works */}
      <Card>
        <h2 className="text-sm font-semibold text-white mb-4">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-4">
          {[
            { n: '1', title: 'Decode', body: 'QR image is decoded optically (pyzbar + OpenCV). Payload is extracted and classified by type.' },
            { n: '2', title: 'Extract', body: '19 URL features are extracted: IP host, TLD, subdomains, encoding, shorteners, punycode, etc.' },
            { n: '3', title: 'Classify', body: 'Random Forest classifier scores malicious probability. UPI and WiFi get dedicated non-URL logic.' },
            { n: '4', title: 'Report', body: 'LOW / MEDIUM / HIGH / INCONCLUSIVE verdict with explanation, triggered rules, and ML score.' },
          ].map(({ n, title, body }) => (
            <div key={n} className="space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded bg-navy-800 border border-navy-700 text-xs text-blue-400 font-mono font-bold flex items-center justify-center flex-shrink-0">{n}</span>
                <span className="text-sm font-medium text-white">{title}</span>
              </div>
              <p className="text-xs text-gray-400 leading-relaxed">{body}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Threat coverage */}
      <Card>
        <h2 className="text-sm font-semibold text-white mb-3">Threat Coverage</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {[
            'QR-based phishing (quishing)',
            'Malicious URL redirection',
            'Fake payment QR codes',
            'URL shortener obfuscation',
            'Raw IP host bypassing DNS',
            'Authority @ obfuscation',
            'Suspicious TLD domains',
            'Punycode homograph attacks',
            'Open WiFi network risk',
            'UPI scam keyword detection',
            'Executable payload delivery',
            'QR image tampering indicators',
          ].map((t) => (
            <div key={t} className="flex items-start gap-2 text-xs text-gray-300">
              <span className="text-emerald-500 mt-0.5 flex-shrink-0">✓</span>
              <span>{t}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

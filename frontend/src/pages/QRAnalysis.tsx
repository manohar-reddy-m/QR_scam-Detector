import React, { useState } from 'react';
import { QrCode, ShieldAlert, Copy, Check, RefreshCw, UploadCloud, Globe, Wifi, CreditCard, Mail, Phone, User, FileText } from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { FileUpload } from '../components/ui/FileUpload';
import { RiskBadge, PayloadTypeBadge } from '../components/ui/Badge';
import { RiskMeter } from '../components/ui/RiskMeter';
import { useQRAnalyze } from '../hooks/useQRAnalysis';
import { generateQRCode } from '../api/qr';import type { RiskIndicator } from '../types';

// Derive a human-friendly QR identity from the payload type + payload content
function getQRIdentity(payloadType: string, payload: string): {
  icon: React.ReactNode;
  label: string;
  detail: string;
} {
  const p = (payload ?? '').toLowerCase();
  const raw = payload ?? '';

  if (payloadType === 'UPI_PAYMENT' || p.startsWith('upi://')) {
    // Extract payee name from pn= param
    const pn = raw.match(/[?&]pn=([^&]+)/i)?.[1] ?? '';
    const pa = raw.match(/[?&]pa=([^&]+)/i)?.[1] ?? '';
    const am = raw.match(/[?&]am=([^&]+)/i)?.[1] ?? '';
    return {
      icon: <CreditCard className="w-4 h-4 text-amber-400" />,
      label: 'UPI Payment Request',
      detail: [pn && `Payee: ${pn}`, pa && `VPA: ${pa}`, am && `Amount: ₹${am}`].filter(Boolean).join(' · ') || 'Scan to pay via UPI',
    };
  }

  if (payloadType === 'WIFI' || p.startsWith('wifi:')) {
    const ssid = raw.match(/S:([^;]+)/i)?.[1] ?? 'Unknown';
    const enc  = raw.match(/T:([^;]+)/i)?.[1]?.toUpperCase() ?? 'Unknown';
    return {
      icon: <Wifi className="w-4 h-4 text-blue-400" />,
      label: 'Wi-Fi Network',
      detail: `Network: "${ssid}" · Security: ${enc === 'NOPASS' ? 'Open (no password)' : enc}`,
    };
  }

  if (payloadType === 'EMAIL' || p.startsWith('mailto:')) {
    const to = raw.replace(/^mailto:/i, '').split('?')[0];
    return {
      icon: <Mail className="w-4 h-4 text-cyan-400" />,
      label: 'Email Link',
      detail: `To: ${to || 'Unknown recipient'}`,
    };
  }

  if (payloadType === 'PHONE' || p.startsWith('tel:')) {
    const num = raw.replace(/^tel:/i, '');
    return {
      icon: <Phone className="w-4 h-4 text-emerald-400" />,
      label: 'Phone Number',
      detail: `Call: ${num}`,
    };
  }

  if (payloadType === 'VCARD' || p.startsWith('begin:vcard')) {
    const name = raw.match(/FN:([^\r\n]+)/i)?.[1] ?? '';
    return {
      icon: <User className="w-4 h-4 text-purple-400" />,
      label: 'Contact Card (vCard)',
      detail: name ? `Contact: ${name}` : 'Contains contact information',
    };
  }

  // URL types — identify the website
  if (payloadType === 'URL_HTTPS' || payloadType === 'URL_HTTP' || p.startsWith('http')) {
    try {
      const url = new URL(raw.includes('://') ? raw : `https://${raw}`);
      const hostname = url.hostname.replace(/^www\./, '');
      // Map known domains to friendly names
      const knownSites: Record<string, string> = {
        'google.com': 'Google', 'youtube.com': 'YouTube', 'youtu.be': 'YouTube',
        'facebook.com': 'Facebook', 'instagram.com': 'Instagram', 'twitter.com': 'Twitter',
        'x.com': 'X (Twitter)', 'linkedin.com': 'LinkedIn', 'github.com': 'GitHub',
        'amazon.com': 'Amazon', 'amazon.in': 'Amazon India', 'flipkart.com': 'Flipkart',
        'paypal.com': 'PayPal', 'paytm.com': 'Paytm', 'phonepe.com': 'PhonePe',
        'microsoft.com': 'Microsoft', 'microsoftonline.com': 'Microsoft 365',
        'apple.com': 'Apple', 'icloud.com': 'iCloud', 'netflix.com': 'Netflix',
        'spotify.com': 'Spotify', 'wikipedia.org': 'Wikipedia', 'whatsapp.com': 'WhatsApp',
        'jio.com': 'Jio', 'jiocinema.com': 'JioCinema', 'airtel.in': 'Airtel',
        'hdfcbank.com': 'HDFC Bank', 'icicibank.com': 'ICICI Bank', 'sbi.co.in': 'SBI',
      };
      // Find matching site name
      const siteName = Object.entries(knownSites).find(([d]) =>
        hostname === d || hostname.endsWith('.' + d)
      )?.[1] ?? hostname;

      const pathInfo = url.pathname && url.pathname !== '/' ? url.pathname.slice(0, 40) : '';
      return {
        icon: <Globe className="w-4 h-4 text-blue-400" />,
        label: `Website Link — ${siteName}`,
        detail: `${url.protocol === 'https:' ? '🔒 HTTPS' : '⚠️ HTTP'} · ${hostname}${pathInfo ? ` · ${pathInfo}` : ''}`,
      };
    } catch {
      return {
        icon: <Globe className="w-4 h-4 text-blue-400" />,
        label: 'Website Link',
        detail: raw.slice(0, 60),
      };
    }
  }

  return {
    icon: <FileText className="w-4 h-4 text-gray-400" />,
    label: 'Plain Text',
    detail: raw.length > 60 ? raw.slice(0, 60) + '…' : raw,
  };
}

async function dataUrlToFile(dataUrl: string, name: string): Promise<File> {
  const res = await fetch(dataUrl);
  const blob = await res.blob();
  return new File([blob], name, { type: 'image/png' });
}

type Tab = 'upload' | 'generator';

export const QRAnalysis: React.FC = () => {
  const [tab, setTab] = useState<Tab>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [genText, setGenText] = useState('https://www.google.com');
  const [genUrl, setGenUrl] = useState<string | null>(null);
  const [genLoading, setGenLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const mutation = useQRAnalyze();

  const runFile = (f: File) => mutation.mutate(f);

  const generate = async () => {
    if (!genText.trim()) return;
    setGenLoading(true);
    try {
      const r = await generateQRCode(genText.trim());
      setGenUrl(r.data_url);
      const f = await dataUrlToFile(r.data_url, 'generated.png');
      setFile(f);
      runFile(f);
    } finally { setGenLoading(false); }
  };

  const copyPayload = () => {
    const p = mutation.data?.decode.payload;
    if (!p) return;
    navigator.clipboard.writeText(p);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const result = mutation.data;

  const riskColor = {
    HIGH: 'rose', MEDIUM: 'amber', LOW: 'emerald', INCONCLUSIVE: 'none',
  } as const;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-white flex items-center gap-2">
          <QrCode className="w-5 h-5 text-blue-400" /> QR Code Analysis
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Decode and assess a QR code for phishing, obfuscation, and payload threats.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-navy-800 text-sm">
        {([
          { id: 'upload',    label: 'Upload Image',  icon: <UploadCloud className="w-3.5 h-3.5" />},
          { id: 'generator', label: 'QR Generator',  icon: <QrCode className="w-3.5 h-3.5" />    },
        ] as const).map(({ id, label, icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`flex items-center gap-1.5 px-4 py-2.5 font-medium transition-colors border-b-2 -mb-px ${
              tab === id
                ? 'border-blue-500 text-white'
                : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}
          >
            {icon}{label}
          </button>
        ))}
      </div>

      {/* Tab: Upload */}
      {tab === 'upload' && (
        <Card>
          <FileUpload
            onFileSelect={(f) => { setFile(f); }}
            selectedFile={file}
            onClear={() => { setFile(null); mutation.reset(); }}
            disabled={mutation.isPending}
          />
          <div className="mt-4 flex justify-end">
            <Button
              variant="primary"
              icon={<ShieldAlert className="w-4 h-4" />}
              onClick={() => file && runFile(file)}
              disabled={!file || mutation.isPending}
              loading={mutation.isPending}
            >
              Analyze
            </Button>
          </div>
        </Card>
      )}

      {/* Tab: Generator */}
      {tab === 'generator' && (
        <Card>
          <div className="space-y-4">
            <label className="block text-xs font-medium text-gray-300 uppercase tracking-wider">
              Encode Any Text or URL
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={genText}
                onChange={(e) => setGenText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && generate()}
                placeholder="https://example.com or upi://pay?pa=…"
                className="flex-1 bg-navy-950 border border-navy-700 rounded-md px-3 py-2 text-sm text-white placeholder-gray-600 focus:border-blue-500 focus:outline-none font-mono"
              />
              <Button variant="primary" onClick={generate} loading={genLoading || mutation.isPending} disabled={!genText.trim()}>
                Generate & Scan
              </Button>
            </div>

            {/* Quick payload templates */}
            <div className="flex flex-wrap gap-2">
              {[
                ['Safe Google',    'https://www.google.com/search?q=cybersecurity'],
                ['Phishing IP',    'http://192.168.1.1/admin/login.php'],
                ['Bad TLD',        'http://apple-verify.tk/account-update'],
                ['UPI (safe)',     'upi://pay?pa=merchant@oksbi&pn=Shop&am=200'],
                ['UPI (scam)',     'upi://pay?pa=help@fake&pn=KycRefund&am=5000'],
                ['Open WiFi',      'WIFI:S:Airport;T:nopass;;'],
              ].map(([label, val]) => (
                <button
                  key={label}
                  type="button"
                  onClick={() => setGenText(val)}
                  className="text-[11px] px-2 py-1 rounded bg-navy-800 border border-navy-700 text-gray-400 hover:text-white hover:border-navy-600 transition-colors"
                >
                  {label}
                </button>
              ))}
            </div>

            {genUrl && (
              <div className="flex items-center gap-4 pt-2">
                <div className="bg-white rounded p-2 flex-shrink-0">
                  <img src={genUrl} alt="Generated QR" className="w-28 h-28 object-contain" />
                </div>
                <p className="text-xs text-gray-400 font-mono break-all">{genText}</p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Error */}
      {mutation.isError && (
        <div className="text-sm text-rose-400 bg-rose-950/30 border border-rose-900/50 rounded-lg p-3">
          {mutation.error instanceof Error ? mutation.error.message : 'Analysis failed.'}
        </div>
      )}

      {/* Loading shimmer */}
      {mutation.isPending && (
        <div className="flex items-center gap-2 text-sm text-gray-400 py-2">
          <RefreshCw className="w-4 h-4 animate-spin" />
          Decoding and analyzing…
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Summary row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Verdict */}
            <Card glow={riskColor[result.threat.risk_level] as never} className="flex flex-col items-center justify-center py-6 text-center gap-3">
              <RiskMeter score={result.threat.risk_score} level={result.threat.risk_level} size={120} />
              <RiskBadge level={result.threat.risk_level} size="lg" />
            </Card>

            {/* Payload */}
            <Card className="md:col-span-2 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Decoded Payload</span>
                <div className="flex items-center gap-2">
                  <PayloadTypeBadge type={result.decode.payload_type} />
                  {result.decode.payload && (
                    <button onClick={copyPayload} className="p-1 text-gray-500 hover:text-white transition-colors">
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  )}
                </div>
              </div>

              {/* QR Identity */}
              {result.decode.payload && (() => {
                const id = getQRIdentity(result.decode.payload_type, result.decode.payload);
                return (
                  <div className="flex items-start gap-2.5 bg-navy-900 border border-navy-700 rounded-lg px-3 py-2.5">
                    <span className="mt-0.5 flex-shrink-0">{id.icon}</span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-white">{id.label}</p>
                      <p className="text-xs text-gray-400 mt-0.5 break-all">{id.detail}</p>
                    </div>
                  </div>
                );
              })()}

              <div className="font-mono text-xs text-blue-300 bg-navy-950 border border-navy-800 rounded px-3 py-2.5 break-all leading-relaxed max-h-24 overflow-y-auto">
                {result.decode.payload ?? <span className="text-gray-600 italic">No QR code detected.</span>}
              </div>

              <p className="text-xs text-gray-400 leading-relaxed bg-navy-950 border border-navy-800 rounded px-3 py-2.5">
                {result.threat.explanation}
              </p>

              <div className="flex flex-wrap gap-4 text-[11px] text-gray-500 font-mono pt-1 border-t border-navy-800">
                <span>Decoder: {result.decode.decoder_used}</span>
                <span>Confidence: {(result.decode.confidence * 100).toFixed(0)}%</span>
                {result.threat.ml_score !== null && (
                  <span>ML score: {(result.threat.ml_score * 100).toFixed(1)}%</span>
                )}
              </div>
            </Card>
          </div>

          {/* ML bar */}
          {result.threat.ml_score !== null && (
            <Card>
              <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">ML Threat Probability</h3>
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-gray-400">Malicious likelihood</span>
                  <span className="text-white">{(result.threat.ml_score * 100).toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-navy-950 border border-navy-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      result.threat.ml_score >= 0.7 ? 'bg-rose-500'
                      : result.threat.ml_score >= 0.3 ? 'bg-amber-500'
                      : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.max(2, result.threat.ml_score * 100)}%` }}
                  />
                </div>
              </div>
            </Card>
          )}

          {/* Indicators */}
          {result.threat.indicators.length > 0 && (
            <Card>
              <CardHeader
                title="Security Indicators"
                subtitle="Deterministic rule checks against decoded payload"
                icon={<ShieldAlert className="w-4 h-4" />}
              />
              <div className="divide-y divide-navy-800">
                {result.threat.indicators.map((ind: RiskIndicator, i: number) => (
                  <div key={i} className={`flex items-start justify-between gap-4 py-2.5 ${ind.triggered ? '' : 'opacity-40'}`}>
                    <div className="flex-1 min-w-0">
                      <span className="text-xs font-mono font-medium text-white">{ind.name}</span>
                      <p className="text-xs text-gray-400 mt-0.5 leading-relaxed">{ind.description}</p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className={`text-[10px] font-mono ${
                        ind.severity === 'HIGH' ? 'text-rose-400'
                        : ind.severity === 'MEDIUM' ? 'text-amber-400'
                        : 'text-blue-400'
                      }`}>{ind.severity}</span>
                      <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                        ind.triggered
                          ? 'bg-rose-950/50 text-rose-300 border-rose-800/60'
                          : 'bg-navy-800 text-gray-500 border-navy-700'
                      }`}>
                        {ind.triggered ? 'TRIGGERED' : 'CLEAR'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

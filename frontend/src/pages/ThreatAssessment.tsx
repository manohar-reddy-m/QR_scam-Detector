import React, { useState } from 'react';
import {
  Globe,
  Search,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ShieldAlert,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Layers,
  Lock,
  Unlock,
} from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { RiskBadge } from '../components/ui/Badge';
import { RiskMeter } from '../components/ui/RiskMeter';
import { useURLAnalyze } from '../hooks/useURLAnalysis';

export const ThreatAssessment: React.FC = () => {
  const [urlInput, setUrlInput] = useState('');
  const [showTechnical, setShowTechnical] = useState(false);
  const urlMutation = useURLAnalyze();

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) return;
    urlMutation.mutate(urlInput.trim());
  };

  const loadSample = (sample: string) => {
    setUrlInput(sample);
    urlMutation.mutate(sample);
  };

  const result = urlMutation.data;

  const getHostname = (urlStr: string) => {
    try {
      const u = new URL(urlStr.startsWith('http') ? urlStr : `https://${urlStr}`);
      return u.hostname;
    } catch {
      return urlStr;
    }
  };

  const hostname = result ? getHostname(result.url) : '';

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Page Title */}
      <div>
        <h1 className="text-xl font-semibold text-white flex items-center gap-2">
          <Globe className="w-5 h-5 text-blue-400" />
          <span>URL Threat Intelligence</span>
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Inspect any link or website destination to verify whether it is safe or carries active threats.
        </p>
      </div>

      {/* Input Card */}
      <Card>
        <form onSubmit={handleAnalyze} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-300 mb-2">
              Website or Link to Check
            </label>
            <div className="relative flex items-center">
              <input
                type="text"
                placeholder="Enter a website or link (e.g. google.com, paypal.com, or any suspicious URL)"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                className="w-full px-4 py-3 bg-navy-950 border border-navy-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors pr-28 font-mono"
                disabled={urlMutation.isPending}
              />
              <div className="absolute right-2">
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={!urlInput.trim() || urlMutation.isPending}
                  loading={urlMutation.isPending}
                  icon={<Search className="w-3.5 h-3.5" />}
                >
                  Check Link
                </Button>
              </div>
            </div>
          </div>

          {/* Quick preset samples */}
          <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
            <span className="text-gray-500 font-mono text-[11px]">Quick Tests:</span>
            <button
              type="button"
              onClick={() => loadSample('https://www.google.com')}
              className="px-2.5 py-1 rounded bg-navy-800 hover:bg-navy-700 text-emerald-300 font-mono text-[11px] border border-navy-700 transition-colors"
            >
              ✓ google.com (Safe)
            </button>
            <button
              type="button"
              onClick={() => loadSample('https://www.youtube.com/@TED')}
              className="px-2.5 py-1 rounded bg-navy-800 hover:bg-navy-700 text-emerald-300 font-mono text-[11px] border border-navy-700 transition-colors"
            >
              ✓ youtube.com/@TED (Safe)
            </button>
            <button
              type="button"
              onClick={() => loadSample('https://paypal-security-update.com/login')}
              className="px-2.5 py-1 rounded bg-navy-800 hover:bg-navy-700 text-rose-300 font-mono text-[11px] border border-navy-700 transition-colors"
            >
              ✕ paypal-security.com (Phishing)
            </button>
            <button
              type="button"
              onClick={() => loadSample('https://paypa1.com/secure')}
              className="px-2.5 py-1 rounded bg-navy-800 hover:bg-navy-700 text-rose-300 font-mono text-[11px] border border-navy-700 transition-colors"
            >
              ✕ paypa1.com (Typosquat)
            </button>
            <button
              type="button"
              onClick={() => loadSample('http://45.33.32.156/payload.exe')}
              className="px-2.5 py-1 rounded bg-navy-800 hover:bg-navy-700 text-rose-300 font-mono text-[11px] border border-navy-700 transition-colors"
            >
              ✕ 45.33.32.156 (Malware IP)
            </button>
            <button
              type="button"
              onClick={() => loadSample('https://bit.ly/3xY9ZzQ')}
              className="px-2.5 py-1 rounded bg-navy-800 hover:bg-navy-700 text-amber-300 font-mono text-[11px] border border-navy-700 transition-colors"
            >
              ⚠ bit.ly (Shortener)
            </button>
          </div>
        </form>
      </Card>

      {/* Error Message */}
      {urlMutation.isError && (
        <div className="p-4 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold">Analysis Failed</h4>
            <p className="text-xs text-rose-200 mt-1">
              {urlMutation.error instanceof Error ? urlMutation.error.message : 'Invalid URL input.'}
            </p>
          </div>
        </div>
      )}

      {/* Result Display */}
      {result && (
        <div className="space-y-4 animate-fadeIn">
          {/* Main Verdict Banner */}
          <div
            className={`p-4 rounded-lg border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
              result.risk_level === 'LOW'
                ? 'bg-emerald-950/30 border-emerald-800/60 text-emerald-300'
                : result.risk_level === 'HIGH'
                ? 'bg-rose-950/30 border-rose-800/60 text-rose-300'
                : 'bg-amber-950/30 border-amber-800/60 text-amber-300'
            }`}
          >
            <div className="flex items-start gap-3">
              {result.risk_level === 'LOW' && (
                <ShieldCheck className="w-7 h-7 text-emerald-400 flex-shrink-0 mt-0.5" />
              )}
              {result.risk_level === 'HIGH' && (
                <ShieldAlert className="w-7 h-7 text-rose-400 flex-shrink-0 mt-0.5" />
              )}
              {result.risk_level === 'MEDIUM' && (
                <AlertTriangle className="w-7 h-7 text-amber-400 flex-shrink-0 mt-0.5" />
              )}
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-bold tracking-wide">
                    {result.risk_level === 'LOW' && 'SAFE — NO THREAT DETECTED'}
                    {result.risk_level === 'HIGH' && 'THREAT DETECTED — DANGEROUS LINK'}
                    {result.risk_level === 'MEDIUM' && 'CAUTION — SUSPICIOUS LINK'}
                  </h2>
                </div>
                <p className="text-xs mt-1 text-gray-300 leading-relaxed max-w-2xl">
                  {result.explanation}
                </p>
              </div>
            </div>

            <div className="flex sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto gap-2 border-t sm:border-t-0 pt-2 sm:pt-0 border-navy-800">
              <span className="text-[11px] font-mono text-gray-400 uppercase tracking-wider">Verdict</span>
              <RiskBadge level={result.risk_level} size="lg" />
            </div>
          </div>

          {/* Destination Details & Threat Score */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Website Identity Card */}
            <Card className="md:col-span-2 space-y-3">
              <div>
                <span className="text-[11px] font-mono uppercase tracking-wider text-gray-400 block mb-1">
                  Destination Website
                </span>
                <div className="flex items-center gap-2 text-base font-semibold text-white">
                  <span className="text-blue-400 font-mono">{hostname}</span>
                  {result.features.has_https ? (
                    <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded font-mono">
                      <Lock className="w-3 h-3" /> HTTPS
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] text-rose-400 bg-rose-950/60 border border-rose-800/60 px-2 py-0.5 rounded font-mono">
                      <Unlock className="w-3 h-3" /> HTTP (Insecure)
                    </span>
                  )}
                </div>
                <div className="p-2.5 mt-2 rounded bg-navy-950 border border-navy-800 font-mono text-xs text-gray-300 break-all select-all">
                  {result.url}
                </div>
              </div>

              {/* Security Checklist */}
              <div className="pt-2 border-t border-navy-800 grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center gap-2 text-gray-300">
                  {result.features.has_https ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  ) : (
                    <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                  )}
                  <span>{result.features.has_https ? 'HTTPS Encrypted' : 'Unencrypted Connection'}</span>
                </div>

                <div className="flex items-center gap-2 text-gray-300">
                  {result.features.has_ip_host ? (
                    <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  )}
                  <span>{result.features.has_ip_host ? 'Raw IP (Bypasses DNS)' : 'Standard Domain Name'}</span>
                </div>

                <div className="flex items-center gap-2 text-gray-300">
                  {result.features.is_shortened_url ? (
                    <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  )}
                  <span>{result.features.is_shortened_url ? 'URL Shortener Service' : 'Direct Link'}</span>
                </div>

                <div className="flex items-center gap-2 text-gray-300">
                  {result.features.has_suspicious_tld || result.features.has_punycode ? (
                    <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  )}
                  <span>
                    {result.features.has_suspicious_tld
                      ? 'Suspicious TLD'
                      : result.features.has_punycode
                      ? 'Punycode Spoofing'
                      : 'Authentic TLD'}
                  </span>
                </div>
              </div>
            </Card>

            {/* Threat Meter */}
            <Card className="flex flex-col items-center justify-center text-center p-5">
              <RiskMeter score={result.risk_score} level={result.risk_level} />
              <div className="mt-3">
                <span className="text-xs font-mono text-gray-400 block">
                  {result.risk_level === 'LOW' && '0% Threat · Clean Destination'}
                  {result.risk_level === 'HIGH' && `${Math.round(result.risk_score * 100)}% Threat · High Danger`}
                  {result.risk_level === 'MEDIUM' && `${Math.round(result.risk_score * 100)}% Threat · Caution`}
                </span>
              </div>
            </Card>
          </div>

          {/* Triggered Threat Factors (if any) */}
          {result.indicators.some((i) => i.triggered) && (
            <Card>
              <h3 className="text-xs font-semibold text-rose-400 uppercase tracking-wider font-mono mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                <span>Detected Threat Factors ({result.indicators.filter((i) => i.triggered).length})</span>
              </h3>
              <div className="space-y-2">
                {result.indicators
                  .filter((i) => i.triggered)
                  .map((ind, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded bg-navy-950 border border-navy-800 flex items-start justify-between gap-3 text-xs"
                    >
                      <div>
                        <span className="font-semibold font-mono text-white">{ind.name}</span>
                        <p className="text-gray-400 mt-0.5">{ind.description}</p>
                      </div>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold flex-shrink-0 ${
                          ind.severity === 'HIGH'
                            ? 'bg-rose-950 text-rose-400 border border-rose-800'
                            : 'bg-amber-950 text-amber-400 border border-amber-800'
                        }`}
                      >
                        {ind.severity}
                      </span>
                    </div>
                  ))}
              </div>
            </Card>
          )}

          {/* Technical Details Accordion */}
          <div className="pt-2">
            <button
              type="button"
              onClick={() => setShowTechnical(!showTechnical)}
              className="text-xs text-gray-400 hover:text-gray-200 font-mono flex items-center gap-1.5 transition-colors"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>{showTechnical ? 'Hide Technical Features' : 'Show 19 Technical Features (Advanced)'}</span>
              {showTechnical ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            {showTechnical && (
              <Card className="mt-3">
                <CardHeader
                  title="19 Extracted Feature Dimensions"
                  subtitle="Raw vector passed to ML classification and rule engine"
                />
                <div className="overflow-x-auto">
                  <table className="w-full text-xs font-mono text-left">
                    <thead>
                      <tr className="border-b border-navy-800 text-gray-400 uppercase text-[10px]">
                        <th className="py-2 px-3">Feature Name</th>
                        <th className="py-2 px-3">Value</th>
                        <th className="py-2 px-3">Security Meaning</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-navy-800/60">
                      {Object.entries(result.features).map(([key, val]) => (
                        <tr key={key} className="hover:bg-navy-900/50">
                          <td className="py-2 px-3 font-semibold text-gray-300">{key}</td>
                          <td className="py-2 px-3">
                            <span
                              className={`px-1.5 py-0.5 rounded text-[11px] font-bold ${
                                typeof val === 'boolean'
                                  ? val
                                    ? 'bg-amber-950 text-amber-400 border border-amber-800'
                                    : 'bg-navy-950 text-gray-500 border border-navy-800'
                                  : 'text-blue-400'
                              }`}
                            >
                              {String(val)}
                            </span>
                          </td>
                          <td className="py-2 px-3 text-gray-400 font-sans text-[11px]">
                            {key === 'has_https' && 'Ensures transport layer encryption'}
                            {key === 'has_ip_host' && 'Direct IP address bypasses domain reputation'}
                            {key === 'is_shortened_url' && 'Hides destination behind redirect service'}
                            {key === 'has_suspicious_tld' && 'Matches top-level domains known for malware'}
                            {key === 'has_punycode' && 'Internationalized domain homograph attack vector'}
                            {key === 'num_subdomains' && 'Excessive subdomains suggest spoofing'}
                            {key === 'num_at' && 'Misleads browser credentials parser'}
                            {key === 'has_double_slash' && 'Path traversal redirect pattern'}
                            {key === 'url_length' && 'Total string character length'}
                            {key === 'hostname_length' && 'Host portion character length'}
                            {key === 'num_dots' && 'Separators in domain, subdomains, and filename'}
                            {key === 'num_hyphens' && 'Hyphenated lookalike domain names'}
                            {key === 'num_question_marks' && 'Query parameter delimiters'}
                            {key === 'num_ampersands' && 'Parameter concatenation markers'}
                            {key === 'num_percent_encoded' && 'URL-encoded hex obfuscation count'}
                            {key === 'path_length' && 'Subfolder depth & resource path size'}
                            {key === 'query_length' && 'Query string character count'}
                            {key === 'special_char_ratio' && 'Density of non-alphanumeric characters'}
                            {key === 'digit_ratio' && 'Density of numeric digits in string'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useState } from 'react';
import {
  FlaskConical,
  Sliders,
  CheckCircle2,
  XCircle,
  ShieldAlert,
  Layers,
  GitCompare,
} from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { FileUpload } from '../components/ui/FileUpload';
import { useQRDistort, useQRCompare } from '../hooks/useQRAnalysis';
import type { QRDistortResult } from '../types';

export const RobustnessLab: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'distortion' | 'compare'>('distortion');

  // Distortion tab states
  const [file, setFile] = useState<File | null>(null);
  const [severity, setSeverity] = useState<number>(0.5);
  const distortMutation = useQRDistort();

  // Compare tab states
  const [file1, setFile1] = useState<File | null>(null);
  const [file2, setFile2] = useState<File | null>(null);
  const compareMutation = useQRCompare();

  const handleRunDistort = () => {
    if (!file) return;
    distortMutation.mutate({ file, severity });
  };

  const handleRunCompare = () => {
    if (!file1 || !file2) return;
    compareMutation.mutate({ file1, file2 });
  };

  const distortResult = distortMutation.data;
  const compareResult = compareMutation.data;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-white font-sans flex items-center gap-2.5">
          <FlaskConical className="w-6 h-6 text-cyan-400" />
          <span>QR Image Robustness & Attack Laboratory</span>
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Evaluate QR decodability under physical degradations (blur, noise, rotation, compression) and detect malicious sticker replacement attacks.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-navy-800 space-x-4">
        <button
          onClick={() => setActiveTab('distortion')}
          className={`pb-3 text-sm font-mono font-medium transition-colors flex items-center gap-2 border-b-2 ${
            activeTab === 'distortion'
              ? 'border-cyan-400 text-cyan-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <Sliders className="w-4 h-4" />
          <span>Controlled Degradation Lab</span>
        </button>
        <button
          onClick={() => setActiveTab('compare')}
          className={`pb-3 text-sm font-mono font-medium transition-colors flex items-center gap-2 border-b-2 ${
            activeTab === 'compare'
              ? 'border-cyan-400 text-cyan-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <GitCompare className="w-4 h-4" />
          <span>Sticker Tampering / Replacement Detector</span>
        </button>
      </div>

      {/* TAB 1: DISTORTION LAB */}
      {activeTab === 'distortion' && (
        <div className="space-y-6 animate-fadeIn">
          <Card>
            <CardHeader
              title="Upload QR Code & Set Degradation Severity"
              subtitle="Test decodability across 6 synthetic degradation vectors"
              icon={<Sliders className="w-5 h-5 text-blue-400" />}
            />
            <div className="space-y-5">
              <FileUpload
                onFileSelect={(f) => setFile(f)}
                selectedFile={file}
                onClear={() => {
                  setFile(null);
                  distortMutation.reset();
                }}
                disabled={distortMutation.isPending}
              />

              {/* Severity Slider */}
              <div className="p-4 rounded-xl bg-navy-950 border border-navy-800 space-y-2">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-gray-300 font-semibold uppercase">Degradation Severity:</span>
                  <span className="text-cyan-400 font-bold font-mono text-sm">
                    {(severity * 100).toFixed(0)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.05"
                  value={severity}
                  onChange={(e) => setSeverity(parseFloat(e.target.value))}
                  className="w-full h-2 bg-navy-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                  disabled={distortMutation.isPending}
                />
                <div className="flex justify-between text-[10px] font-mono text-gray-500">
                  <span>Mild (10%)</span>
                  <span>Moderate (50%)</span>
                  <span>Severe (100%)</span>
                </div>
              </div>

              <div className="flex justify-end">
                <Button
                  variant="cyber"
                  size="md"
                  onClick={handleRunDistort}
                  disabled={!file || distortMutation.isPending}
                  loading={distortMutation.isPending}
                  icon={<FlaskConical className="w-4 h-4" />}
                >
                  Run Distortion Stress Test
                </Button>
              </div>
            </div>
          </Card>

          {/* Results Display */}
          {distortResult && (
            <div className="space-y-6 animate-fadeIn">
              {/* Robustness Score Card */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="flex flex-col items-center justify-center p-6 text-center">
                  <span className="text-xs font-mono uppercase text-gray-400">Robustness Index</span>
                  <div className="text-4xl font-extrabold font-mono text-cyan-400 mt-2">
                    {(distortResult.robustness_score * 100).toFixed(0)}%
                  </div>
                  <span className="text-xs text-gray-400 mt-1">
                    {distortResult.distortion_results.filter((r: QRDistortResult) => r.still_decodable).length} of{' '}
                    {distortResult.distortion_results.length} variants decodable
                  </span>
                </Card>

                <Card className="md:col-span-2 flex flex-col justify-between">
                  <div>
                    <span className="text-xs font-mono uppercase tracking-wider text-gray-400">
                      Original Decoded Payload
                    </span>
                    <div className="p-3 mt-1.5 rounded-lg bg-navy-950 border border-navy-800 font-mono text-xs text-cyan-300 break-all select-all">
                      {distortResult.original_payload || 'Could not decode original image.'}
                    </div>
                  </div>
                  <p className="text-xs text-gray-400 mt-3">
                    Robustness measures whether optical QR redundancy (Reed-Solomon error correction) survives real-world physical weathering, low camera focus, and printing flaws.
                  </p>
                </Card>
              </div>

              {/* Degradation Breakdown Table */}
              <Card>
                <CardHeader
                  title="Distortion Variant Results"
                  subtitle={`Applied at ${(severity * 100).toFixed(0)}% severity level`}
                  icon={<Layers className="w-5 h-5 text-blue-400" />}
                />
                <div className="divide-y divide-navy-800">
                  {distortResult.distortion_results.map((dist: QRDistortResult, idx: number) => (
                    <div key={idx} className="py-3.5 flex items-center justify-between gap-4 text-xs font-mono">
                      <div className="flex items-center gap-3">
                        {dist.still_decodable ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                        ) : (
                          <XCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
                        )}
                        <div>
                          <div className="font-semibold text-white uppercase tracking-wider">
                            {dist.distortion_type}
                          </div>
                          <div className="text-[11px] text-gray-400 font-mono mt-0.5 truncate max-w-md">
                            {dist.still_decodable
                              ? `Payload: ${dist.decoded_payload}`
                              : 'Decode failed — damage exceeded error correction capacity'}
                          </div>
                        </div>
                      </div>
                      <span
                        className={`px-2.5 py-1 rounded text-xs font-semibold ${
                          dist.still_decodable
                            ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800'
                            : 'bg-rose-950/80 text-rose-400 border border-rose-800'
                        }`}
                      >
                        {dist.still_decodable ? 'DECODED' : 'UNREADABLE'}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: STICKER TAMPERING DETECTOR */}
      {activeTab === 'compare' && (
        <div className="space-y-6 animate-fadeIn">
          <Card>
            <CardHeader
              title="Dual-QR Comparison (Sticker Replacement Detection)"
              subtitle="Compare original benchmark QR with a scanned code from a physical venue"
              icon={<GitCompare className="w-5 h-5 text-blue-400" />}
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-xs font-mono uppercase text-gray-300 font-semibold mb-2">
                  Image A: Legitimate / Expected QR
                </h4>
                <FileUpload
                  onFileSelect={(f) => setFile1(f)}
                  selectedFile={file1}
                  onClear={() => setFile1(null)}
                  disabled={compareMutation.isPending}
                />
              </div>
              <div>
                <h4 className="text-xs font-mono uppercase text-gray-300 font-semibold mb-2">
                  Image B: Suspect / Scanned QR
                </h4>
                <FileUpload
                  onFileSelect={(f) => setFile2(f)}
                  selectedFile={file2}
                  onClear={() => setFile2(null)}
                  disabled={compareMutation.isPending}
                />
              </div>
            </div>

            <div className="flex justify-end pt-5">
              <Button
                variant="cyber"
                size="md"
                onClick={handleRunCompare}
                disabled={!file1 || !file2 || compareMutation.isPending}
                loading={compareMutation.isPending}
                icon={<GitCompare className="w-4 h-4" />}
              >
                Compare Payloads
              </Button>
            </div>
          </Card>

          {compareResult && (
            <Card className="animate-fadeIn p-6">
              <div className="flex items-start gap-4">
                {compareResult.same_payload ? (
                  <CheckCircle2 className="w-8 h-8 text-emerald-400 flex-shrink-0" />
                ) : (
                  <ShieldAlert className="w-8 h-8 text-rose-400 flex-shrink-0" />
                )}
                <div className="space-y-2 flex-1">
                  <h3 className="text-base font-bold font-mono text-white">
                    {compareResult.same_payload
                      ? '✓ INTEGRITY VERIFIED: Payloads Match'
                      : '✕ TAMPERING DETECTED: Payload Replacement Attack!'}
                  </h3>
                  <p className="text-xs text-gray-300 leading-relaxed font-sans">
                    {compareResult.same_payload
                      ? 'Both QR codes resolve to the exact identical payload. No payload substitution or sticker replacement detected.'
                      : 'WARNING: The two images encode different destinations. This indicates the suspected QR code was altered or covered with a malicious sticker.'}
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-3 font-mono text-xs">
                    <div className="p-3 rounded-lg bg-navy-950 border border-navy-800">
                      <span className="text-gray-400 font-bold block mb-1">Image A Payload:</span>
                      <span className="text-cyan-300 break-all">
                        {compareResult.qr1.payload || 'Failed to decode'}
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-navy-950 border border-navy-800">
                      <span className="text-gray-400 font-bold block mb-1">Image B Payload:</span>
                      <span className="text-rose-300 break-all">
                        {compareResult.qr2.payload || 'Failed to decode'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

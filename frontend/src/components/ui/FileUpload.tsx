import React, { useState, useRef } from 'react';
import { UploadCloud, X, AlertCircle } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
  disabled?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect, selectedFile, onClear, disabled = false,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const ref = useRef<HTMLInputElement>(null);

  const validate = (file: File) => {
    setError(null);
    if (!['image/png', 'image/jpeg', 'image/jpg', 'image/webp'].includes(file.type)) {
      setError('Unsupported format. Use PNG, JPEG, or WEBP.'); return;
    }
    if (file.size > 10 * 1024 * 1024) { setError('File exceeds 10 MB.'); return; }
    setPreviewUrl(URL.createObjectURL(file));
    onFileSelect(file);
  };

  const clear = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null); setError(null);
    if (ref.current) ref.current.value = '';
    onClear();
  };

  return (
    <div className="space-y-2">
      {!selectedFile ? (
        <div
          onDragOver={(e) => { e.preventDefault(); if (!disabled) setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setIsDragOver(false); if (!disabled && e.dataTransfer.files[0]) validate(e.dataTransfer.files[0]); }}
          onClick={() => !disabled && ref.current?.click()}
          className={`border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-colors flex flex-col items-center gap-3
            ${isDragOver ? 'border-blue-500 bg-blue-950/20' : 'border-navy-700 hover:border-navy-600 bg-navy-900/50'}
            ${disabled ? 'opacity-40 cursor-not-allowed' : ''}`}
        >
          <input ref={ref} type="file" accept="image/png,image/jpeg,image/webp" className="hidden" onChange={(e) => e.target.files?.[0] && validate(e.target.files[0])} disabled={disabled} />
          <UploadCloud className="w-8 h-8 text-gray-500" />
          <div>
            <p className="text-sm font-medium text-gray-300">Drop QR image here or click to browse</p>
            <p className="text-xs text-gray-500 mt-1">PNG · JPEG · WEBP · max 10 MB</p>
          </div>
        </div>
      ) : (
        <div className="border border-navy-700 rounded-lg bg-navy-900 p-3 flex items-center gap-3">
          {previewUrl && (
            <div className="w-14 h-14 rounded bg-white p-1 flex-shrink-0">
              <img src={previewUrl} alt="QR" className="w-full h-full object-contain" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <p className="text-sm text-white font-mono truncate">{selectedFile.name}</p>
            <p className="text-xs text-gray-500 mt-0.5">{(selectedFile.size / 1024).toFixed(1)} KB</p>
          </div>
          <button onClick={clear} disabled={disabled} className="p-1.5 text-gray-500 hover:text-white hover:bg-navy-800 rounded transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
      {error && (
        <div className="flex items-center gap-2 text-xs text-rose-400 bg-rose-950/30 border border-rose-900/60 rounded-md p-2.5">
          <AlertCircle className="w-4 h-4 flex-shrink-0" /><span>{error}</span>
        </div>
      )}
    </div>
  );
};

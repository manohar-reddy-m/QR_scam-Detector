/**
 * QR Sentinel — TypeScript Type Definitions
 * Matched 1:1 with backend Pydantic schemas
 */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'INCONCLUSIVE';

export type QRPayloadType =
  | 'URL_HTTP'
  | 'URL_HTTPS'
  | 'UPI_PAYMENT'
  | 'TEXT'
  | 'EMAIL'
  | 'PHONE'
  | 'WIFI'
  | 'VCARD'
  | 'UNKNOWN';

export interface RiskIndicator {
  name: string;
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  triggered: boolean;
}

export interface QRDecodeResult {
  decoded: boolean;
  payload: string | null;
  payload_type: QRPayloadType;
  confidence: number;
  decoder_used: string;
}

export interface ThreatAnalysisResult {
  risk_level: RiskLevel;
  risk_score: number;
  ml_score: number | null;
  indicators: RiskIndicator[];
  explanation: string;
}

export interface QRAnalyzeResponse {
  success: boolean;
  request_id?: string;
  decode: QRDecodeResult;
  threat: ThreatAnalysisResult;
  metadata?: Record<string, any>;
}

export interface QRDecodeOnlyResponse {
  success: boolean;
  decode: QRDecodeResult;
}

export interface QRDistortResult {
  distortion_type: string;
  severity: number;
  still_decodable: boolean;
  decoded_payload: string | null;
}

export interface QRDistortResponse {
  success: boolean;
  original_payload: string | null;
  distortion_results: QRDistortResult[];
  robustness_score: number;
}

export interface QRCompareResponse {
  success: boolean;
  same_payload: boolean;
  qr1: QRDecodeResult;
  qr2: QRDecodeResult;
}

export interface URLFeatures {
  url_length: number;
  hostname_length: number;
  num_subdomains: number;
  has_https: boolean;
  has_ip_host: boolean;
  num_dots: number;
  num_hyphens: number;
  num_at: number;
  num_question_marks: number;
  num_ampersands: number;
  num_percent_encoded: number;
  path_length: number;
  query_length: number;
  is_shortened_url: boolean;
  has_suspicious_tld: boolean;
  has_punycode: boolean;
  has_double_slash: boolean;
  special_char_ratio: number;
  digit_ratio: number;
}

export interface URLAnalyzeResponse {
  success: boolean;
  url: string;
  risk_level: RiskLevel;
  risk_score: number;
  ml_score: number | null;
  features: URLFeatures;
  indicators: RiskIndicator[];
  explanation: string;
}

export interface ModelStatusResponse {
  loaded: boolean;
  model_type?: string | null;
  training_dataset?: string | null;
  num_features?: number | null;
  feature_names?: string[] | null;
}

export interface ClassificationReportClass {
  precision: number;
  recall: number;
  'f1-score': number;
  support: number;
}

export interface ModelMetricsData {
  dataset_label: string;
  best_model: string;
  best_f1: number;
  warning: string;
  models: {
    RandomForest?: {
      f1: number;
      roc_auc: number;
      accuracy: number;
      classification_report?: Record<string, any>;
    };
    LogisticRegression?: {
      f1: number;
      roc_auc: number;
      accuracy: number;
      classification_report?: Record<string, any>;
    };
  };
}

export interface ModelMetricsResponse {
  available: boolean;
  metrics?: ModelMetricsData | null;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  python_version: string;
  platform: string;
  service: string;
  version: string;
}

export type DistortionType =
  | 'blur'
  | 'noise'
  | 'rotate'
  | 'compress'
  | 'brightness'
  | 'crop';

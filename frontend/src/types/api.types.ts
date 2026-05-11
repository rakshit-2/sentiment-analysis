// API Response Types

export interface TranscriptMetadata {
  title?: string;
  description?: string;
}

export interface Transcript {
  _id: string;
  uuid: string;
  transcript: string;
  source: 'manual' | 's3';
  type: 'voice' | 'digital';
  metadata: TranscriptMetadata;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

export interface MetricScore {
  score: number;
  evidence: string[];
  rationale: string;
}

export interface AskingToTellingMetric extends MetricScore {
  estimated_ratio: string;
}

export interface CallSummary {
  overall_call_sentiment?: string;
  lead_temperature?: string;
  meeting_likelihood?: number;
  follow_up_readiness?: number;
  // Digital journey fields
  session_temperature?: string;
  conversion_readiness?: number;
  journey_stage?: string;
  content_pieces_consumed?: number;
  high_intent_actions?: string[];
}

export interface PrimaryMetrics {
  live_tone_score: MetricScore;
  objection_recovery_arc: MetricScore;
  champion_signals: MetricScore;
  buying_commitment_momentum: MetricScore;
  competitive_mention_sentiment: MetricScore;
  call_closing_sentiment: MetricScore;
}

export interface ParameterMetrics {
  prospect_tone: MetricScore;
  pain_urgency: MetricScore;
  champion_strength: MetricScore;
  objection_temperature: MetricScore;
  buying_commitment: MetricScore;
  competitive_position: MetricScore;
  trust_openness: MetricScore;
  expansion_potential: MetricScore;
  decision_friction_indicators: MetricScore;
  asking_to_telling_ratio: AskingToTellingMetric;
  transparency_score: MetricScore;
}

export interface AnalysisResult {
  summary: CallSummary;
  primary_metrics?: PrimaryMetrics;
  parameter_metrics?: ParameterMetrics;
  notable_buying_signals: string[];
  objections_detected: string[];
  risks_detected: string[];
  next_best_action: string[];
  // Digital journey fields
  engagement_depth?: Record<string, unknown>;
  content_consumption?: Record<string, unknown>;
  time_investment?: Record<string, unknown>;
  drop_off_signals?: string[];
  conversion_signals?: string[];
  friction_points?: string[];
}

export interface ModelInfo {
  model: string;
  tokens_used?: number;
  cost?: number;
}

export interface Analysis {
  _id: string;
  uuid: string;
  transcript_id: string;
  result?: AnalysisResult;
  status: 'pending' | 'processing' | 'success' | 'failed';
  error_message?: string;
  model_info?: ModelInfo;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  analyzed_at?: string;
  deleted_at?: string;
  transcript?: Transcript;
}

export interface RecentAnalysesResponse {
  count: number;
  hours: number;
  analyses: Analysis[];
}

export interface TrendData {
  week: string;
  count: number;
  date: string;
}

export interface TrendsResponse {
  weeks: number;
  data: TrendData[];
}

export interface LeadTemperatureCounts {
  hot: number;
  warm: number;
  cold: number;
}

export interface SentimentCounts {
  positive: number;
  negative: number;
  neutral: number;
  mixed: number;
}

export interface MetricAverages {
  meeting_likelihood: number;
  follow_up_readiness: number;
}

export interface DetailedMetricData {
  week: string;
  date: string;
  total_analyses: number;
  lead_temperature: LeadTemperatureCounts;
  session_temperature?: Record<string, number>; // For digital transcripts
  sentiment: SentimentCounts;
  averages: MetricAverages;
  success_rate: number;
}

export interface DetailedMetricsResponse {
  weeks: number;
  data: DetailedMetricData[];
}

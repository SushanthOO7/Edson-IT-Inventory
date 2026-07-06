export type Device = {
  id: string;
  asset_tag?: string | null;
  serial_number?: string | null;
  device_name?: string | null;
  display_name?: string | null;
  manufacturer?: string | null;
  model?: string | null;
  model_category?: string | null;
  device_type?: string | null;
  mac_address?: string | null;
  department?: string | null;
  cost_center?: string | null;
  lifecycle_status: string;
  source_confidence: number;
  notes?: string | null;
  created_at: string;
  updated_at: string;
};

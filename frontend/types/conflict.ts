export type ConflictRead = {
  id: string;
  device_id: string;
  field_name: string;
  service_now_value?: string | null;
  intune_value?: string | null;
  local_value?: string | null;
  ocr_value?: string | null;
  conflict_type?: string | null;
  severity: string;
  status: string;
  resolved_value?: string | null;
  resolved_by?: string | null;
  resolved_at?: string | null;
  created_at: string;
};

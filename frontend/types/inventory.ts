export type OfficeInventory = {
  id: string;
  device_id: string;
  current_status: string;
  current_location?: string | null;
  assigned_user_name?: string | null;
  assigned_user_email?: string | null;
  checked_out_to?: string | null;
  checked_out_by?: string | null;
  checked_out_at?: string | null;
  expected_return_at?: string | null;
  checked_in_by?: string | null;
  checked_in_at?: string | null;
  condition?: string | null;
  notes?: string | null;
};

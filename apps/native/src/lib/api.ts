import { createApiClient } from "shared-types";
import { supabase } from "./supabase";

const API_URL = process.env.EXPO_PUBLIC_API_URL!;

export const apiClient = createApiClient({
  baseUrl: API_URL,
  getAccessToken: async () => {
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? null;
  },
});

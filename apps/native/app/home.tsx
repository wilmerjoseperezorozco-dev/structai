import { useEffect, useState } from "react";
import { ActivityIndicator, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { Redirect } from "expo-router";
import { useAuth } from "../src/lib/auth-context";
import { apiClient } from "../src/lib/api";
import { supabase } from "../src/lib/supabase";

type ApiStatus = "checking" | "ok" | "error";

export default function HomeScreen() {
  const { session, loading } = useAuth();
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) return;
    apiClient
      .health()
      .then(() => setApiStatus("ok"))
      .catch((err: Error) => {
        setApiStatus("error");
        setApiError(err.message);
      });
  }, [session]);

  if (!loading && !session) return <Redirect href="/login" />;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>StructAI</Text>
      <Text style={styles.email}>{session?.user.email}</Text>

      <View style={styles.card}>
        <Text style={styles.cardLabel}>Backend (apps/api)</Text>
        {apiStatus === "checking" && (
          <View style={styles.row}>
            <ActivityIndicator color="#38bdf8" size="small" />
            <Text style={styles.rowText}>Conectando…</Text>
          </View>
        )}
        {apiStatus === "ok" && <Text style={styles.ok}>✓ Conectado</Text>}
        {apiStatus === "error" && (
          <View>
            <Text style={styles.errorText}>✗ Sin conexión</Text>
            <Text style={styles.errorDetail}>{apiError}</Text>
            <Text style={styles.hint}>
              Revisa EXPO_PUBLIC_API_URL en .env.local — debe apuntar a la IP de tu backend local
              (uvicorn), no a localhost si estás en un dispositivo físico.
            </Text>
          </View>
        )}
      </View>

      <TouchableOpacity style={styles.button} onPress={() => supabase.auth.signOut()}>
        <Text style={styles.buttonText}>Cerrar sesión</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0f172a",
    paddingHorizontal: 24,
    paddingTop: 80,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    color: "#fff",
  },
  email: {
    fontSize: 13,
    color: "#94a3b8",
    marginTop: 4,
    marginBottom: 24,
  },
  card: {
    backgroundColor: "#1e293b",
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: "#334155",
    marginBottom: 24,
  },
  cardLabel: {
    fontSize: 12,
    color: "#94a3b8",
    fontWeight: "500",
    marginBottom: 8,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  rowText: {
    color: "#cbd5e1",
    fontSize: 13,
  },
  ok: {
    color: "#4ade80",
    fontSize: 13,
    fontWeight: "600",
  },
  errorText: {
    color: "#f87171",
    fontSize: 13,
    fontWeight: "600",
  },
  errorDetail: {
    color: "#94a3b8",
    fontSize: 11,
    marginTop: 4,
  },
  hint: {
    color: "#64748b",
    fontSize: 11,
    marginTop: 8,
    lineHeight: 16,
  },
  button: {
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: "center",
  },
  buttonText: {
    color: "#94a3b8",
    fontWeight: "600",
    fontSize: 13,
  },
});

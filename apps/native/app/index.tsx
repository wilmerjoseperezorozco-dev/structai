import { ActivityIndicator, View } from "react-native";
import { Redirect } from "expo-router";
import { useAuth } from "../src/lib/auth-context";

export default function Index() {
  const { session, loading } = useAuth();

  if (loading) {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: "#0f172a" }}>
        <ActivityIndicator color="#38bdf8" />
      </View>
    );
  }

  return <Redirect href={session ? "/home" : "/login"} />;
}

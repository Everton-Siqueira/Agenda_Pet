import { Redirect } from "expo-router";
import { View, ActivityIndicator } from "react-native";

export default function RootIndex() {
  // Redireciona o administrador diretamente para a tela da agenda interna
  return <Redirect href="/agenda" />;
}
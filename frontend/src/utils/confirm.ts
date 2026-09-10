import { Alert, Platform } from "react-native";

export function confirmAction(title: string, message: string, onConfirm: () => void) {
  if (Platform.OS === "web") {
    const confirmed =
      typeof window !== "undefined" ? window.confirm(`${title}\n\n${message}`) : false;
    if (confirmed) {
      onConfirm();
    }
    return;
  }

  Alert.alert(title, message, [
    { text: "Cancelar", style: "cancel" },
    { text: "Confirmar", style: "destructive", onPress: onConfirm },
  ]);
}

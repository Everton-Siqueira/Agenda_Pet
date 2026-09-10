import { Link, Stack } from "expo-router";
import { Text, View } from "react-native";

export default function NotFoundScreen() {
  return (
    <>
      <Stack.Screen options={{ title: "Página não encontrada", headerShown: true }} />
      <View className="flex-1 items-center justify-center bg-slate-50 px-6">
        <Text className="text-xl font-semibold text-slate-900">Essa tela não existe.</Text>
        <Link href="/" className="mt-4 text-base font-medium text-teal-800">
          Voltar ao início
        </Link>
      </View>
    </>
  );
}

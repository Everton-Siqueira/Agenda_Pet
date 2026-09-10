import { Redirect, router } from "expo-router";
import { useState } from "react";
import { Pressable, Text, View } from "react-native";
import { getErrorMessage } from "../src/api/client";
import { Screen } from "../src/components/Page";
import { Button, ErrorBanner, Input } from "../src/components/ui";
import { useAuth } from "../src/context/AuthContext";

export default function LoginScreen() {
  const { session, loading, loginByPhone, loginAsStaff } = useAuth();
  const [celular, setCelular] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!loading && session) {
    return <Redirect href="/(main)/agenda" />;
  }

  async function handleLogin() {
    setError(null);
    setSubmitting(true);
    try {
      await loginByPhone(celular);
      router.replace("/(main)/agenda");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStaff() {
    setError(null);
    await loginAsStaff("Equipe do petshop");
    router.replace("/(main)/agenda");
  }

  return (
    <Screen
      title="Agenda Pet"
      subtitle="Entre com o celular do tutor cadastrado na API ou acesse o painel da loja."
      loading={loading}
    >
      <View className="overflow-hidden rounded-[32px] bg-teal-800 px-6 py-8">
        <Text className="text-sm font-semibold uppercase tracking-widest text-teal-200">
          Petshop
        </Text>
        <Text className="mt-2 text-3xl font-bold text-white">Banho, tosa e agenda em um só lugar.</Text>
        <Text className="mt-3 text-base leading-6 text-teal-100">
          O login identifica o tutor em GET /tutor. O cadastro cria um novo registro via POST /tutor.
        </Text>
      </View>

      <View className="rounded-3xl border border-slate-100 bg-white p-5">
        <ErrorBanner message={error} />
        <View className="mt-2 gap-4">
          <Input
            label="Celular"
            placeholder="(11) 99999-0000"
            keyboardType="phone-pad"
            value={celular}
            onChangeText={setCelular}
          />
          <Button title="Entrar" onPress={handleLogin} loading={submitting} />
          <Button title="Entrar como equipe" variant="secondary" onPress={handleStaff} />
        </View>
      </View>

      <Pressable onPress={() => router.push("/cadastro")} className="items-center py-2">
        <Text className="text-sm text-slate-600">
          Ainda não tem cadastro? <Text className="font-semibold text-teal-800">Criar tutor</Text>
        </Text>
      </Pressable>
    </Screen>
  );
}

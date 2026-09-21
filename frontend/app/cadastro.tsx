import { router } from "expo-router";
import { useState } from "react";
import { Pressable, Text, View } from "react-native";
import { getErrorMessage } from "../src/api/client";
import { Screen } from "../src/components/Page";
import { Button, ErrorBanner, Input } from "../src/components/ui";
import { useAuth } from "../src/context/AuthContext";

export default function CadastroScreen() {
  const { registerTutor } = useAuth();
  const [nome, setNome] = useState("");
  const [celular, setCelular] = useState("");
  const [endereco, setEndereco] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    setError(null);

    if (!nome.trim() || !celular.trim() || !endereco.trim()) {
      setError("Preencha nome, celular e endereço.");
      return;
    }

    setSubmitting(true);
    try {
      await registerTutor({
        nome: nome.trim(),
        celular: celular.trim(),
        endereco: endereco.trim(),
      });
      router.replace("/(main)/agenda");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Screen title="Cadastro" subtitle="Cria um tutor no backend (POST /tutor) e já entra na agenda.">
      <View className="gap-4 rounded-3xl border border-slate-100 bg-white p-5">
        <ErrorBanner message={error} />
        <Input label="Nome" placeholder="Nome completo" value={nome} onChangeText={setNome} />
        <Input
          label="Celular"
          placeholder="(11) 99999-0000"
          keyboardType="phone-pad"
          value={celular}
          onChangeText={setCelular}
        />
        <Input
          label="Endereço"
          placeholder="Rua, número e bairro"
          value={endereco}
          onChangeText={setEndereco}
        />
        <Button title="Cadastrar e entrar" onPress={handleSubmit} loading={submitting} />
      </View>

      <Pressable onPress={() => router.back()} className="items-center py-2">
        <Text className="text-sm font-medium text-teal-800">Voltar para o login</Text>
      </Pressable>
    </Screen>
  );
}

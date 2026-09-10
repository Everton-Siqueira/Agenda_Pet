import { useCallback, useState } from "react";
import { Text, View } from "react-native";
import { useFocusEffect } from "expo-router";
import { getErrorMessage } from "../../src/api/client";
import { servicoApi } from "../../src/api/petshop";
import { Screen } from "../../src/components/Page";
import { Button, Card, EmptyState, ErrorBanner, Input } from "../../src/components/ui";
import { confirmAction } from "../../src/utils/confirm";
import { formatMoney } from "../../src/utils/format";
import type { Servico } from "../../src/types";

const emptyForm = { tipo_servico: "", valor: "" };

export default function ServicosScreen() {
  const [servicos, setServicos] = useState<Servico[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm);

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      setServicos(await servicoApi.list());
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  function openCreate() {
    setEditingId(null);
    setForm(emptyForm);
    setFormOpen(true);
  }

  function openEdit(servico: Servico) {
    setEditingId(servico.id);
    setForm({ tipo_servico: servico.tipo_servico, valor: String(servico.valor) });
    setFormOpen(true);
  }

  async function handleSave() {
    setError(null);
    if (!form.tipo_servico.trim() || !form.valor.trim()) {
      setError("Preencha o tipo e o valor.");
      return;
    }

    const payload = {
      tipo_servico: form.tipo_servico.trim(),
      valor: Number(form.valor.replace(",", ".")),
    };

    setSaving(true);
    try {
      if (editingId) {
        await servicoApi.update(editingId, payload);
      } else {
        await servicoApi.create(payload);
      }
      setFormOpen(false);
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  function handleDelete(id: number) {
    confirmAction("Excluir serviço", "O serviço será removido da API.", async () => {
      try {
        await servicoApi.remove(id);
        await load();
      } catch (err) {
        setError(getErrorMessage(err));
      }
    });
  }

  return (
    <Screen
      title="Serviços"
      subtitle="Tipos como Banho e Tosa, sem números no nome, via /servico."
      loading={loading}
      headerRight={
        <View className="w-32">
          <Button title={formOpen ? "Fechar" : "Novo"} onPress={() => (formOpen ? setFormOpen(false) : openCreate())} />
        </View>
      }
    >
      <ErrorBanner message={error} />

      {formOpen ? (
        <Card className="gap-4">
          <Text className="text-lg font-semibold text-slate-900">
            {editingId ? "Editar serviço" : "Novo serviço"}
          </Text>
          <Input
            label="Tipo do serviço"
            placeholder="Banho e Tosa"
            value={form.tipo_servico}
            onChangeText={(tipo_servico) => setForm((current) => ({ ...current, tipo_servico }))}
          />
          <Input
            label="Valor"
            placeholder="80.00"
            keyboardType="decimal-pad"
            value={form.valor}
            onChangeText={(valor) => setForm((current) => ({ ...current, valor }))}
          />
          <Button title={editingId ? "Salvar" : "Cadastrar serviço"} onPress={handleSave} loading={saving} />
        </Card>
      ) : null}

      {servicos.length === 0 ? (
        <EmptyState title="Nenhum serviço" subtitle="Cadastre banho, tosa ou outro serviço do petshop." />
      ) : (
        servicos.map((servico) => (
          <Card key={servico.id} className="gap-3">
            <View className="flex-row items-center justify-between">
              <Text className="text-lg font-semibold text-slate-900">{servico.tipo_servico}</Text>
              <Text className="text-base font-semibold text-teal-800">{formatMoney(servico.valor)}</Text>
            </View>
            <View className="flex-row gap-2">
              <View className="flex-1">
                <Button title="Editar" variant="secondary" onPress={() => openEdit(servico)} />
              </View>
              <View className="flex-1">
                <Button title="Excluir" variant="danger" onPress={() => handleDelete(servico.id)} />
              </View>
            </View>
          </Card>
        ))
      )}
    </Screen>
  );
}

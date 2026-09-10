import { useCallback, useState } from "react";
import { Text, View } from "react-native";
import { useFocusEffect } from "expo-router";
import { getErrorMessage } from "../../src/api/client";
import { tutorApi } from "../../src/api/petshop";
import { Screen } from "../../src/components/Page";
import { Button, Card, EmptyState, ErrorBanner, Input } from "../../src/components/ui";
import { confirmAction } from "../../src/utils/confirm";
import type { Tutor } from "../../src/types";

const emptyForm = { nome: "", celular: "", endereco: "" };

export default function TutoresScreen() {
  const [tutores, setTutores] = useState<Tutor[]>([]);
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
      setTutores(await tutorApi.list());
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

  function openEdit(tutor: Tutor) {
    setEditingId(tutor.id);
    setForm({ nome: tutor.nome, celular: tutor.celular, endereco: tutor.endereco });
    setFormOpen(true);
  }

  async function handleSave() {
    setError(null);
    if (!form.nome.trim() || !form.celular.trim() || !form.endereco.trim()) {
      setError("Preencha todos os campos.");
      return;
    }

    const payload = {
      nome: form.nome.trim(),
      celular: form.celular.trim(),
      endereco: form.endereco.trim(),
    };

    setSaving(true);
    try {
      if (editingId) {
        await tutorApi.update(editingId, payload);
      } else {
        await tutorApi.create(payload);
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
    confirmAction("Excluir tutor", "Pets vinculados a este tutor podem falhar no banco.", async () => {
      try {
        await tutorApi.remove(id);
        await load();
      } catch (err) {
        setError(getErrorMessage(err));
      }
    });
  }

  return (
    <Screen
      title="Tutores"
      subtitle="CRUD completo da rota /tutor."
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
            {editingId ? "Editar tutor" : "Novo tutor"}
          </Text>
          <Input label="Nome" value={form.nome} onChangeText={(nome) => setForm((current) => ({ ...current, nome }))} />
          <Input
            label="Celular"
            keyboardType="phone-pad"
            value={form.celular}
            onChangeText={(celular) => setForm((current) => ({ ...current, celular }))}
          />
          <Input
            label="Endereço"
            value={form.endereco}
            onChangeText={(endereco) => setForm((current) => ({ ...current, endereco }))}
          />
          <Button title={editingId ? "Salvar" : "Cadastrar"} onPress={handleSave} loading={saving} />
        </Card>
      ) : null}

      {tutores.length === 0 ? (
        <EmptyState title="Nenhum tutor" subtitle="Use esta tela ou a tela de cadastro inicial." />
      ) : (
        tutores.map((tutor) => (
          <Card key={tutor.id} className="gap-3">
            <Text className="text-lg font-semibold text-slate-900">{tutor.nome}</Text>
            <Text className="text-sm text-slate-500">{tutor.celular}</Text>
            <Text className="text-sm text-slate-500">{tutor.endereco}</Text>
            <View className="flex-row gap-2">
              <View className="flex-1">
                <Button title="Editar" variant="secondary" onPress={() => openEdit(tutor)} />
              </View>
              <View className="flex-1">
                <Button title="Excluir" variant="danger" onPress={() => handleDelete(tutor.id)} />
              </View>
            </View>
          </Card>
        ))
      )}
    </Screen>
  );
}

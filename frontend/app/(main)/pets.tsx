import { useCallback, useMemo, useState } from "react";
import { Text, View } from "react-native";
import { useFocusEffect } from "expo-router";
import { getErrorMessage } from "../../src/api/client";
import { petApi, tutorApi } from "../../src/api/petshop";
import { Screen } from "../../src/components/Page";
import { Button, Card, Chip, EmptyState, ErrorBanner, Input } from "../../src/components/ui";
import { confirmAction } from "../../src/utils/confirm";
import type { Pet, Tutor } from "../../src/types";

const emptyForm = { nome_pet: "", especie: "", id_tutor: "" };

export default function PetsScreen() {
  const [pets, setPets] = useState<Pet[]>([]);
  const [tutores, setTutores] = useState<Tutor[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm);

  const tutorMap = useMemo(() => new Map(tutores.map((tutor) => [tutor.id, tutor])), [tutores]);

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const [petList, tutorList] = await Promise.all([petApi.list(), tutorApi.list()]);
      setPets(petList);
      setTutores(tutorList);
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

  function openEdit(pet: Pet) {
    setEditingId(pet.id);
    setForm({
      nome_pet: pet.nome_pet,
      especie: pet.especie,
      id_tutor: String(pet.id_tutor),
    });
    setFormOpen(true);
  }

  async function handleSave() {
    setError(null);
    if (!form.nome_pet.trim() || !form.especie.trim() || !form.id_tutor) {
      setError("Preencha nome, espécie e tutor.");
      return;
    }

    const payload = {
      nome_pet: form.nome_pet.trim(),
      especie: form.especie.trim(),
      id_tutor: Number(form.id_tutor),
    };

    setSaving(true);
    try {
      if (editingId) {
        await petApi.update(editingId, payload);
      } else {
        await petApi.create(payload);
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
    confirmAction("Excluir pet", "O pet será removido da API.", async () => {
      try {
        await petApi.remove(id);
        await load();
      } catch (err) {
        setError(getErrorMessage(err));
      }
    });
  }

  return (
    <Screen
      title="Pets"
      subtitle="Cadastro em /pet, vinculado ao tutor."
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
          <Text className="text-lg font-semibold text-slate-900">{editingId ? "Editar pet" : "Novo pet"}</Text>
          <Input
            label="Nome do pet"
            placeholder="Thor"
            value={form.nome_pet}
            onChangeText={(nome_pet) => setForm((current) => ({ ...current, nome_pet }))}
          />
          <Input
            label="Espécie"
            placeholder="Cão, gato..."
            value={form.especie}
            onChangeText={(especie) => setForm((current) => ({ ...current, especie }))}
          />
          <Text className="text-sm font-medium text-slate-600">Tutor</Text>
          <View className="flex-row flex-wrap gap-2">
            {tutores.map((tutor) => (
              <Chip
                key={tutor.id}
                label={tutor.nome}
                selected={form.id_tutor === String(tutor.id)}
                onPress={() => setForm((current) => ({ ...current, id_tutor: String(tutor.id) }))}
              />
            ))}
          </View>
          <Button title={editingId ? "Salvar" : "Cadastrar pet"} onPress={handleSave} loading={saving} />
        </Card>
      ) : null}

      {pets.length === 0 ? (
        <EmptyState title="Nenhum pet cadastrado" subtitle="Cadastre um tutor primeiro e depois adicione o pet." />
      ) : (
        pets.map((pet) => (
          <Card key={pet.id} className="gap-3">
            <Text className="text-lg font-semibold text-slate-900">{pet.nome_pet}</Text>
            <Text className="text-sm text-slate-500">
              {pet.especie} · Tutor: {tutorMap.get(pet.id_tutor)?.nome ?? `#${pet.id_tutor}`}
            </Text>
            <View className="flex-row gap-2">
              <View className="flex-1">
                <Button title="Editar" variant="secondary" onPress={() => openEdit(pet)} />
              </View>
              <View className="flex-1">
                <Button title="Excluir" variant="danger" onPress={() => handleDelete(pet.id)} />
              </View>
            </View>
          </Card>
        ))
      )}
    </Screen>
  );
}

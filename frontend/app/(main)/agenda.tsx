import { useCallback, useMemo, useState } from "react";
import { Pressable, Text, View } from "react-native";
import { useFocusEffect } from "expo-router";
import { getErrorMessage } from "../../src/api/client";
import { atendimentoApi, petApi, servicoApi } from "../../src/api/petshop";
import { Screen } from "../../src/components/Page";
import { Button, Card, Chip, EmptyState, ErrorBanner, Input } from "../../src/components/ui";
import { confirmAction } from "../../src/utils/confirm";
import { formatDate, formatMoney, formatTime, TIME_SLOTS } from "../../src/utils/format";
import type { Atendimento, Pet, Servico } from "../../src/types";

const emptyForm = {
  id_pet: "",
  data_atendimento: "",
  horario_atendimento: "09:00",
  id_servico: "",
  valor: "",
};

export default function AgendaScreen() {
  const [atendimentos, setAtendimentos] = useState<Atendimento[]>([]);
  const [pets, setPets] = useState<Pet[]>([]);
  const [servicos, setServicos] = useState<Servico[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm);

  const petMap = useMemo(() => new Map(pets.map((pet) => [pet.id, pet])), [pets]);
  const servicoMap = useMemo(
    () => new Map(servicos.map((servico) => [servico.id, servico])),
    [servicos]
  );

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const [agenda, petList, servicoList] = await Promise.all([
        atendimentoApi.list(),
        petApi.list(),
        servicoApi.list(),
      ]);
      setAtendimentos(
        [...agenda].sort((a, b) =>
          `${b.data_atendimento}${b.horario_atendimento}`.localeCompare(
            `${a.data_atendimento}${a.horario_atendimento}`
          )
        )
      );
      setPets(petList);
      setServicos(servicoList);
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

  function openEdit(item: Atendimento) {
    setEditingId(item.id);
    setForm({
      id_pet: String(item.id_pet),
      data_atendimento: String(item.data_atendimento).slice(0, 10),
      horario_atendimento: formatTime(String(item.horario_atendimento)),
      id_servico: String(item.id_servico),
      valor: String(item.valor),
    });
    setFormOpen(true);
  }

  async function handleSave() {
    setError(null);
    const payload = {
      id_pet: Number(form.id_pet),
      data_atendimento: form.data_atendimento,
      horario_atendimento: `${form.horario_atendimento}:00`,
      id_servico: Number(form.id_servico),
      valor: Number(form.valor.replace(",", ".")),
    };

    if (!payload.id_pet || !payload.id_servico || !payload.data_atendimento || !payload.valor) {
      setError("Preencha pet, serviço, data e valor.");
      return;
    }

    setSaving(true);
    try {
      if (editingId) {
        await atendimentoApi.update(editingId, payload);
      } else {
        await atendimentoApi.create(payload);
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
    confirmAction("Excluir atendimento", "Essa ação não pode ser desfeita.", async () => {
      try {
        await atendimentoApi.remove(id);
        await load();
      } catch (err) {
        setError(getErrorMessage(err));
      }
    });
  }

  return (
    <Screen
      title="Agenda de pets"
      subtitle="Atendimentos da API /atendimento. Horários válidos: 09:00 às 18:00."
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
            {editingId ? "Editar atendimento" : "Novo atendimento"}
          </Text>
          <Text className="text-sm text-slate-500">Selecione o pet</Text>
          <View className="flex-row flex-wrap gap-2">
            {pets.map((pet) => (
              <Chip
                key={pet.id}
                label={`${pet.nome_pet} (#${pet.id})`}
                selected={form.id_pet === String(pet.id)}
                onPress={() => setForm((current) => ({ ...current, id_pet: String(pet.id) }))}
              />
            ))}
          </View>
          <Text className="text-sm text-slate-500">Selecione o serviço</Text>
          <View className="flex-row flex-wrap gap-2">
            {servicos.map((servico) => (
              <Chip
                key={servico.id}
                label={`${servico.tipo_servico} (${formatMoney(servico.valor)})`}
                selected={form.id_servico === String(servico.id)}
                onPress={() =>
                  setForm((current) => ({
                    ...current,
                    id_servico: String(servico.id),
                    valor: String(servico.valor),
                  }))
                }
              />
            ))}
          </View>
          <Input
            label="Data (AAAA-MM-DD)"
            placeholder="2026-09-10"
            value={form.data_atendimento}
            onChangeText={(data_atendimento) => setForm((current) => ({ ...current, data_atendimento }))}
          />
          <Text className="text-sm font-medium text-slate-600">Horário</Text>
          <View className="flex-row flex-wrap gap-2">
            {TIME_SLOTS.map((slot) => (
              <Chip
                key={slot}
                label={slot}
                selected={form.horario_atendimento === slot}
                onPress={() => setForm((current) => ({ ...current, horario_atendimento: slot }))}
              />
            ))}
          </View>
          <Input
            label="Valor"
            placeholder="50.00"
            keyboardType="decimal-pad"
            value={form.valor}
            onChangeText={(valor) => setForm((current) => ({ ...current, valor }))}
          />
          <Button title={editingId ? "Salvar alterações" : "Agendar"} onPress={handleSave} loading={saving} />
        </Card>
      ) : null}

      {atendimentos.length === 0 ? (
        <EmptyState
          title="Nenhum atendimento ainda"
          subtitle="Cadastre um pet e um serviço, depois crie o primeiro horário na agenda."
        />
      ) : (
        atendimentos.map((item) => {
          const pet = petMap.get(item.id_pet);
          const servico = servicoMap.get(item.id_servico);
          return (
            <Card key={item.id} className="gap-3">
              <View className="flex-row items-start justify-between gap-3">
                <View className="flex-1">
                  <Text className="text-lg font-semibold text-slate-900">
                    {pet?.nome_pet ?? `Pet #${item.id_pet}`}
                  </Text>
                  <Text className="mt-1 text-sm text-slate-500">
                    {servico?.tipo_servico ?? `Serviço #${item.id_servico}`} · {formatMoney(item.valor)}
                  </Text>
                </View>
                <View className="rounded-full bg-teal-50 px-3 py-1">
                  <Text className="text-xs font-semibold text-teal-800">
                    {formatDate(item.data_atendimento)} {formatTime(String(item.horario_atendimento))}
                  </Text>
                </View>
              </View>
              <View className="flex-row gap-2">
                <View className="flex-1">
                  <Button title="Editar" variant="secondary" onPress={() => openEdit(item)} />
                </View>
                <View className="flex-1">
                  <Button title="Excluir" variant="danger" onPress={() => handleDelete(item.id)} />
                </View>
              </View>
            </Card>
          );
        })
      )}

      <Pressable onPress={load} className="items-center py-2">
        <Text className="text-sm font-medium text-teal-800">Atualizar agenda</Text>
      </Pressable>
    </Screen>
  );
}

import { useCallback, useMemo, useState } from "react";
import { Pressable, Text, View, TextInput } from "react-native";
import { useFocusEffect } from "expo-router";
import { getErrorMessage } from "../../src/api/client";
import { atendimentoApi, petApi, servicoApi } from "../../src/api/petshop";
import { Screen } from "../../src/components/Page";
import { Button, Card, Chip, EmptyState, ErrorBanner, Input } from "../../src/components/ui";
import { confirmAction } from "../../src/utils/confirm";
import { formatMoney, TIME_SLOTS } from "../../src/utils/format";
import type { Atendimento, Pet, Servico } from "../../src/types";

const emptyForm = {
  id_pet: "",
  data_atendimento: "",
  horario_atendimento: "09:00",
  id_servico: "",
  valor: "",
  status: "pendente",
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
  const [busca, setBusca] = useState("");

  const petMap = useMemo(() => new Map(pets.map((pet) => [pet.id, pet])), [pets]);
  const servicoMap = useMemo(
    () => new Map(servicos.map((servico) => [servico.id, servico])),
    [servicos]
  );

  const petsOrdenados = useMemo(() => {
    return [...pets].sort((a, b) => a.nome_pet.localeCompare(b.nome_pet));
  }, [pets]);

  const servicosOrdenados = useMemo(() => {
    return [...servicos].sort((a, b) => a.tipo_servico.localeCompare(b.tipo_servico));
  }, [servicos]);

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const [agenda, petList, servicoList] = await Promise.all([
        atendimentoApi.list(),
        petApi.list(),
        servicoApi.list(),
      ]);
      
      setAtendimentos(agenda);
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
      data_atendimento: String(item.data_atendimento), 
      horario_atendimento: String(item.horario_atendimento).slice(0, 5),
      id_servico: String(item.id_servico),
      valor: String(item.valor),
      status: item.status ?? "pendente",
    });
    setFormOpen(true);
  }

  async function handleMudarStatus(id: number, novoStatus: string) {
    setError(null);
    try {
      await atendimentoApi.updateStatus(id, novoStatus);
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function handleSave() {
    setError(null);
    setSaving(true);

    const payload = {
      id_pet: Number(form.id_pet),
      data_atendimento: form.data_atendimento.trim(), 
      horario_atendimento: form.horario_atendimento.slice(0, 5), 
      id_servico: Number(form.id_servico),
      valor: Number(String(form.valor).replace(",", ".")),
      status: form.status,
    };

    if (!payload.id_pet || !payload.id_servico || !payload.data_atendimento || !payload.valor) {
      setError("Preencha pet, serviço, data e valor corretamente.");
      setSaving(false);
      return;
    }

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

  // 1. Filtra os agendamentos pela busca (Nome do Pet ou Serviço)
  const atendimentosFiltrados = atendimentos.filter((item) => {
    const nomePet = petMap.get(item.id_pet)?.nome_pet?.toLowerCase() ?? "";
    const tipoServico = servicoMap.get(item.id_servico)?.tipo_servico?.toLowerCase() ?? "";
    const termoBusca = busca.toLowerCase();
    return nomePet.includes(termoBusca) || tipoServico.includes(termoBusca);
  });

  // 2. Agrupa os atendimentos por data e ordena os horários
  const gruposPorData = useMemo(() => {
    const grupos: { [data: string]: Atendimento[] } = {};

    atendimentosFiltrados.forEach((item) => {
      const data = item.data_atendimento;
      if (!grupos[data]) {
        grupos[data] = [];
      }
      grupos[data].push(item);
    });

    Object.keys(grupos).forEach((data) => {
      grupos[data].sort((a, b) => a.horario_atendimento.localeCompare(b.horario_atendimento));
    });

    return Object.keys(grupos)
      .sort((a, b) => b.localeCompare(a))
      .map((data) => ({
        data,
        atendimentos: grupos[data],
      }));
  }, [atendimentosFiltrados]);

  return (
    <Screen
      title="Agenda de pets"
      subtitle="Gerenciamento interno de atendimentos."
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
          
          <Text className="text-sm text-slate-500">Selecione o pet (A-Z)</Text>
          <View className="flex-row flex-wrap gap-2">
            {petsOrdenados.map((pet) => (
              <Chip
                key={pet.id}
                label={`${pet.nome_pet} (#${pet.id})`}
                selected={form.id_pet === String(pet.id)}
                onPress={() => setForm((current) => ({ ...current, id_pet: String(pet.id) }))}
              />
            ))}
          </View>
          
          <Text className="text-sm text-slate-500">Selecione o serviço (A-Z)</Text>
          <View className="flex-row flex-wrap gap-2">
            {servicosOrdenados.map((servico) => (
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
          
          <View className="gap-1">
            <Text className="text-sm font-medium text-slate-600">Data (DD/MM/AAAA)</Text>
            <TextInput
              style={{ height: 45, borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 8, paddingHorizontal: 12, backgroundColor: '#ffffff' }}
              placeholder="18/09/2026 ou 18092026"
              value={form.data_atendimento}
              onChangeText={(txt) => setForm((current) => ({ ...current, data_atendimento: txt }))}
            />
          </View>
          
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
          
          <View className="gap-1">
            <Text className="text-sm font-medium text-slate-600">Valor</Text>
            <TextInput
              style={{ height: 45, borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 8, paddingHorizontal: 12, backgroundColor: '#ffffff' }}
              placeholder="70.00"
              keyboardType="decimal-pad"
              value={form.valor}
              onChangeText={(txt) => setForm((current) => ({ ...current, valor: txt }))}
            />
          </View>
          
          <Button title={editingId ? "Salvar alterações" : "Agendar"} onPress={handleSave} loading={saving} />
        </Card>
      ) : (
        <View className="mb-4">
          <Input
            placeholder="🔍 Buscar agendamento por pet ou serviço..."
            value={busca}
            onChangeText={setBusca}
            label={""}
          />
        </View>
      )}

      {atendimentos.length === 0 ? (
        <EmptyState
          title="Nenhum atendimento ainda"
          subtitle="Cadastre um pet e um serviço, depois crie o primeiro horário na agenda."
        />
      ) : gruposPorData.length === 0 ? (
        <EmptyState title="Nenhum agendamento encontrado" subtitle="Verifique os termos digitados e tente novamente." />
      ) : (
        gruposPorData.map((grupo) => (
          <View key={grupo.data} className="mb-6">
            <View className="bg-slate-100 px-3 py-2 rounded-lg mb-2 border-l-4 border-teal-600">
              <Text className="text-base font-bold text-slate-800">🗓️ Dia {grupo.data}</Text>
            </View>

            <Card className="p-2 gap-2">
              {grupo.atendimentos.map((item) => {
                const pet = petMap.get(item.id_pet);
                const servico = servicoMap.get(item.id_servico);
                return (
                  <View 
                    key={item.id} 
                    className="py-2.5 px-2 border-b border-slate-100 last:border-0 gap-2"
                  >
                    {/* Linha principal com informações do atendimento */}
                    <View className="flex-row items-center justify-between">
                      <View className="flex-row items-center flex-1 gap-2 flex-wrap">
                        <Text className="text-sm font-bold text-teal-700 w-12">
                          {item.horario_atendimento.slice(0, 5)}
                        </Text>
                        <Text className="text-sm font-semibold text-slate-900">
                          {pet?.nome_pet ?? `Pet #${item.id_pet}`}
                        </Text>
                        <Text className="text-xs text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
                          {servico?.tipo_servico ?? `Serviço #${item.id_servico}`}
                        </Text>
                        <Text className="text-xs font-semibold text-slate-600 ml-auto mr-2">
                          {formatMoney(item.valor)}
                        </Text>
                      </View>

                      {/* Ações de Editar / Excluir */}
                      <View className="flex-row gap-1">
                        <Pressable 
                          className="bg-slate-200 px-2.5 py-1 rounded" 
                          onPress={() => openEdit(item)}
                        >
                          <Text className="text-xs font-medium text-slate-700">Editar</Text>
                        </Pressable>
                        <Pressable 
                          className="bg-red-50 px-2.5 py-1 rounded border border-red-200" 
                          onPress={() => handleDelete(item.id)}
                        >
                          <Text className="text-xs font-medium text-red-600">Excluir</Text>
                        </Pressable>
                      </View>
                    </View>

                    {/* Linha com os botões rápidos de alteração de status */}
                    <View className="flex-row items-center gap-1.5 pt-1">
                      <Pressable
                        className={`px-2.5 py-1 rounded-md border ${
                          item.status === 'confirmado'
                            ? 'bg-emerald-600 border-emerald-600'
                            : 'bg-emerald-50 border-emerald-300'
                        }`}
                        onPress={() => handleMudarStatus(item.id, 'confirmado')}
                      >
                        <Text
                          className={`text-xs font-semibold ${
                            item.status === 'confirmado' ? 'text-white' : 'text-emerald-700'
                          }`}
                        >
                          {item.status === 'confirmado' ? '✓ Confirmado' : 'Confirmar'}
                        </Text>
                      </Pressable>

                      <Pressable
                        className={`px-2.5 py-1 rounded-md border ${
                          item.status === 'pendente'
                            ? 'bg-amber-500 border-amber-500'
                            : 'bg-amber-50 border-amber-300'
                        }`}
                        onPress={() => handleMudarStatus(item.id, 'pendente')}
                      >
                        <Text
                          className={`text-xs font-semibold ${
                            item.status === 'pendente' ? 'text-white' : 'text-amber-700'
                          }`}
                        >
                          Pendente
                        </Text>
                      </Pressable>

                      <Pressable
                        className={`px-2.5 py-1 rounded-md border ${
                          item.status === 'cancelado'
                            ? 'bg-rose-600 border-rose-600'
                            : 'bg-rose-50 border-rose-300'
                        }`}
                        onPress={() => handleMudarStatus(item.id, 'cancelado')}
                      >
                        <Text
                          className={`text-xs font-semibold ${
                            item.status === 'cancelado' ? 'text-white' : 'text-rose-700'
                          }`}
                        >
                          Cancelar
                        </Text>
                      </Pressable>
                    </View>
                  </View>
                );
              })}
            </Card>
          </View>
        ))
      )}
    </Screen>
  );
}
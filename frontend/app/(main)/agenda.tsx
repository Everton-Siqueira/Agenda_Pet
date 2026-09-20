import { useCallback, useMemo, useState } from "react";
import { Pressable, Text, View, TextInput, ScrollView } from "react-native";
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
      status: item.status || "pendente",
    });
    setFormOpen(true);
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
      status: form.status as "pendente" | "concluido" | "cancelado",
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

  async function handleConcluir(id: number) {
    try {
      setError(null);
      // Alterado para bater com a tipagem do seu sistema ('concluido')
      await atendimentoApi.updateStatus(id, "concluido");
      await load(); 
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  const atendimentosFiltrados = atendimentos.filter((item) => {
    const nomePet = petMap.get(item.id_pet)?.nome_pet?.toLowerCase() ?? "";
    const tipoServico = servicoMap.get(item.id_servico)?.tipo_servico?.toLowerCase() ?? "";
    const termoBusca = busca.toLowerCase();
    return nomePet.includes(termoBusca) || tipoServico.includes(termoBusca);
  });

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
        <ScrollView className="mb-4" showsVerticalScrollIndicator={false}>
          <Card className="gap-4 p-4">
            <Text className="text-lg font-semibold text-slate-900">
              {editingId ? "Editar atendimento" : "Novo atendimento"}
            </Text>
            
            <Text className="text-sm text-slate-500 font-medium">Selecione o pet (A-Z)</Text>
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
            
            <Text className="text-sm text-slate-500 font-medium">Selecione o serviço (A-Z)</Text>
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
                placeholder="18/09/2026"
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
              <Text className="text-sm font-medium text-slate-600">Valor Cobrado (R$)</Text>
              <TextInput
                style={{ height: 45, borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 8, paddingHorizontal: 12, backgroundColor: '#ffffff' }}
                placeholder="0.00"
                keyboardType="numeric"
                value={form.valor}
                onChangeText={(txt) => setForm((current) => ({ ...current, valor: txt }))}
              />
            </View>

            <Button title={saving ? "Salvando..." : "Salvar Agendamento"} onPress={handleSave} disabled={saving} />
          </Card>
        </ScrollView>
      ) : (
        <View className="flex-1 gap-4">
          <Input
              placeholder="Buscar por pet ou serviço..."
              value={busca}
              onChangeText={setBusca} label={""}          />

          {gruposPorData.length === 0 ? (
            <EmptyState title="Nenhum atendimento" subtitle="Nenhum atendimento agendado encontrado." />
          ) : (
            <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
              {gruposPorData.map((grupo) => (
                <View key={grupo.data} className="mb-6">
                  <Text className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">
                    {grupo.data}
                  </Text>
                  
                  <View className="gap-3">
                    {grupo.atendimentos.map((item) => {
                      const pet = petMap.get(item.id_pet);
                      const servico = servicoMap.get(item.id_servico);
                      const isRealizado = item.status === "concluido";

                      return (
                        <Card key={item.id} className="p-4 gap-3 bg-white border border-slate-100 shadow-sm">
                          <View className="flex-row justify-between items-start">
                            <View>
                              <Text className="text-base font-semibold text-slate-900">
                                {pet ? pet.nome_pet : `Pet #${item.id_pet}`}
                              </Text>
                              <Text className="text-sm text-slate-500">
                                {servico ? servico.tipo_servico : `Serviço #${item.id_servico}`}
                              </Text>
                            </View>
                            
                            <View className="items-end gap-1">
                              <Text className="text-sm font-bold text-slate-900">
                                {item.horario_atendimento.slice(0, 5)}
                              </Text>
                              <View className={`px-2 py-0.5 rounded-full ${isRealizado ? 'bg-emerald-100' : 'bg-amber-100'}`}>
                                <Text className={`text-xs font-medium ${isRealizado ? 'text-emerald-700' : 'text-amber-700'}`}>
                                  {isRealizado ? 'Realizado' : 'Pendente'}
                                </Text>
                              </View>
                            </View>
                          </View>

                          <View className="flex-row justify-between items-center border-t border-slate-100 pt-3">
                            <Text className="text-base font-bold text-slate-700">
                              {formatMoney(item.valor)}
                            </Text>
                            
                            <View className="flex-row gap-2">
                              {!isRealizado && (
                                <Pressable 
                                  onPress={() => handleConcluir(item.id)}
                                  className="bg-emerald-600 px-3 py-1.5 rounded-md active:bg-emerald-700"
                                >
                                  <Text className="text-white text-xs font-semibold">Concluir</Text>
                                </Pressable>
                              )}
                              
                              <Pressable 
                                onPress={() => openEdit(item)}
                                className="bg-slate-100 px-3 py-1.5 rounded-md active:bg-slate-200"
                              >
                                <Text className="text-slate-700 text-xs font-medium">Editar</Text>
                              </Pressable>

                              <Pressable 
                                onPress={() => handleDelete(item.id)}
                                className="bg-red-50 px-3 py-1.5 rounded-md active:bg-red-100"
                              >
                                <Text className="text-red-600 text-xs font-medium">Excluir</Text>
                              </Pressable>
                            </View>
                          </View>
                        </Card>
                      );
                    })}
                  </View>
                </View>
              ))}
            </ScrollView>
          )}
        </View>
      )}
    </Screen>
  );
}
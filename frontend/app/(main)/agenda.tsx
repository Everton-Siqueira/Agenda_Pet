import { useCallback, useMemo, useState } from "react";
import { Pressable, Text, View, TextInput, ScrollView } from "react-native";
import { useFocusEffect, useRouter } from "expo-router";
import { getErrorMessage } from "../../src/api/client";
import { atendimentoApi, petApi, servicoApi, tutorApi } from "../../src/api/petshop";
import { Screen } from "../../src/components/Page";
import { Button, Card, Chip, EmptyState, ErrorBanner, Input } from "../../src/components/ui";
import { confirmAction } from "../../src/utils/confirm";
import { formatDate, formatMoney, formatTime, TIME_SLOTS } from "../../src/utils/format";
import type { Atendimento, Pet, Servico, Tutor } from "../../src/types";
function formatarDataAgenda(data: string) {
  const partes = data.slice(0, 10).split(/[-/]/);

  if (partes.length !== 3) {
    return data;
  }

  // Data no formato AAAA-MM-DD ou AAAA/MM/DD
  if (partes[0].length === 4) {
    const [ano, mes, dia] = partes;
    return `${dia}/${mes}/${ano}`;
  }

  return data;
}

const emptyForm = {
  id_pet: "",
  data_atendimento: "",
  horario_atendimento: "09:00",
  id_servico: "",
  valor: "",
  status: "pendente",
};

export default function AgendaScreen() {
  const router = useRouter();

  const [atendimentos, setAtendimentos] = useState<Atendimento[]>([]);
  const [pets, setPets] = useState<Pet[]>([]);
  const [servicos, setServicos] = useState<Servico[]>([]);
  const [tutores, setTutores] = useState<Tutor[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [busca, setBusca] = useState("");
  const [buscaPetForm, setBuscaPetForm] = useState("");

  const petMap = useMemo(() => new Map((pets || []).map((pet) => [pet.id, pet])), [pets]);
  const tutorMap = useMemo(
  () => new Map((tutores || []).map((tutor) => [tutor.id, tutor])),
  [tutores]
);
  const servicoMap = useMemo(
    () => new Map((servicos || []).map((servico) => [servico.id, servico])),
    [servicos]
  );
  const petsOrdenados = useMemo(() => {
    return [...pets].sort((a, b) => a.nome_pet.localeCompare(b.nome_pet));
  }, [pets]);

  const servicosOrdenados = useMemo(() => {
    return [...servicos].sort((a, b) => a.nome_servico.localeCompare(b.nome_servico));
  }, [servicos]);

  const petsFiltradosNoForm = useMemo(() => {
    return petsOrdenados.filter((pet) =>
      pet.nome_pet.toLowerCase().includes(buscaPetForm.toLowerCase())
    );
  }, [petsOrdenados, buscaPetForm]);

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const [agenda, petList, servicoList, tutorList] = await Promise.all([
        atendimentoApi.list(),
        petApi.list(),
      servicoApi.list(),
      tutorApi.list(),
      ]);
      setAtendimentos(agenda);
      console.log(
      "DATAS RECEBIDAS DA API:",
      agenda.map((item) => ({
      id: item.id,
      data: item.data_atendimento,
      horario: item.horario_atendimento,
      }))
    );
      setPets(petList);
      setServicos(servicoList);
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
    setBuscaPetForm("");
    setFormOpen(true);
  }

  function openEdit(item: Atendimento) {
    setEditingId(item.id);
    
    let dataExibicao = String(item.data_atendimento);
    if (dataExibicao.includes("-")) {
      const [ano, mes, dia] = dataExibicao.split("-");
      dataExibicao = `${dia}/${mes}/${ano}`;
    }

    setForm({
      id_pet: String(item.id_pet),
      data_atendimento: dataExibicao,
      horario_atendimento: String(item.horario_atendimento).slice(0, 5),
      id_servico: String(item.id_servico),
      valor: String(item.valor),
      status: item.status || "pendente",
    });
    setBuscaPetForm("");
    setFormOpen(true);
  }
  async function handleSave() {
    setError(null);
    setSaving(true);

    const dataLimpaParaAPI = form.data_atendimento.replace(/\D/g, "").trim();

    const payload = {
      id_pet: Number(form.id_pet),
      data_atendimento: dataLimpaParaAPI,
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
        console.log("EDITANDO atendimento ID:", editingId);
    await atendimentoApi.update(editingId, payload);
      } else {
    console.log("CRIANDO novo atendimento");
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
      await atendimentoApi.updateStatus(id, "concluido");
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  const atendimentosFiltrados = atendimentos.filter((item) => {
    const nomePet = petMap.get(item.id_pet)?.nome_pet?.toLowerCase() ?? "";
    const tipoServico = servicoMap.get(item.id_servico)?.nome_servico?.toLowerCase() ?? "";
    const termoBusca = busca.toLowerCase();
    return nomePet.includes(termoBusca) || tipoServico.includes(termoBusca);
  });
  const gruposPorAbas = useMemo(() => {
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

    const converterParaData = (dataStr: string) => {
      if (dataStr.includes("-")) {
        const [ano, mes, dia] = dataStr.split("-");
        return new Date(Number(ano), Number(mes) - 1, Number(dia));
      }
      const [dia, mes, ano] = dataStr.split("/");
      return new Date(Number(ano), Number(mes) - 1, Number(dia));
    };

    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);

    const hojeLista: Array<{ data: string; atendimentos: Atendimento[] }> = [];
    const proximosLista: Array<{ data: string; atendimentos: Atendimento[] }> = [];
    const passadosLista: Array<{ data: string; atendimentos: Atendimento[] }> = [];

    Object.keys(grupos).forEach((dataStr) => {
      const dataObjeto = converterParaData(dataStr);
      const itemGrupo = { data: dataStr, atendimentos: grupos[dataStr] };

      if (dataObjeto.getTime() === hoje.getTime()) {
        hojeLista.push(itemGrupo);
      } else if (dataObjeto > hoje) {
        proximosLista.push(itemGrupo);
      } else {
        passadosLista.push(itemGrupo);
      }
    });

    proximosLista.sort((a, b) => converterParaData(a.data).getTime() - converterParaData(b.data).getTime());
    passadosLista.sort((a, b) => converterParaData(b.data).getTime() - converterParaData(a.data).getTime());

    return {
      hoje: hojeLista,
      proximos: proximosLista,
      passados: passadosLista,
    };
  }, [atendimentosFiltrados]);

  function renderizarCards(atendimentosLista: Atendimento[]) {
    return atendimentosLista.map((item) => {
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
                {servico ? servico.nome_servico : `Serviço #${item.id_servico}`}
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
              {formatMoney(Number(item.valor))}
            </Text>
            
            <View className="flex-row gap-2">
              {!isRealizado && (
                <Pressable 
                  onPress={() => handleConcluir(item.id)}
                  className="bg-emerald-600 px-3 py-1.5 rounded-md active:bg-emerald-700"
                >
                  <Text className="text-white text-xs font-semibold">Conclusão</Text>
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
    });
  }

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

      <View className="flex-row flex-wrap gap-2 mb-4">
        <Pressable onPress={() => router.replace("/agenda")} className="bg-indigo-600 px-4 py-2 rounded-lg">
          <Text className="text-white font-semibold">📅 Agenda</Text>
        </Pressable>
        <Pressable onPress={() => router.push("/tutores")} className="bg-slate-100 px-4 py-2 rounded-lg">
          <Text className="text-slate-700 font-semibold">👤 Tutores</Text>
        </Pressable>
        <Pressable onPress={() => router.push("/pets")} className="bg-slate-100 px-4 py-2 rounded-lg">
          <Text className="text-slate-700 font-semibold">🐶 Pets</Text>
        </Pressable>
        <Pressable onPress={() => router.push("/servicos")} className="bg-slate-100 px-4 py-2 rounded-lg">
          <Text className="text-slate-700 font-semibold">✂️ Serviços</Text>
        </Pressable>
        <Pressable onPress={() => router.push("/dashboard")} className="bg-slate-100 px-4 py-2 rounded-lg">
          <Text className="text-slate-700 font-semibold">📊 Dashboard</Text>
        </Pressable>
      </View>
      {formOpen ? (
        <ScrollView className="mb-4" showsVerticalScrollIndicator={false}>
          <Card className="gap-4 p-4">
            <Text className="text-lg font-semibold text-slate-900">
              {editingId ? "Editar atendimento" : "Novo atendimento"}
            </Text>
            
            {/* SELEÇÃO DE PET */}
            <View className="gap-2">
              <Text className="text-sm font-semibold text-slate-700">Buscar Pet para o Atendimento</Text>
              <TextInput
                style={{ height: 45, borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 10, paddingHorizontal: 14, backgroundColor: '#f8fafc', fontSize: 14 }}
                placeholder="🔍 Digite o nome do pet..."
                value={buscaPetForm}
                onChangeText={(txt) => setBuscaPetForm(txt)}
              />
              <View className="flex-row flex-wrap gap-2 mt-1">
                {buscaPetForm.trim() === "" ? (
                  <Text className="text-xs text-slate-400 italic p-1">Digite acima para listar os pets...</Text>
                ) : petsFiltradosNoForm.length === 0 ? (
                  <Text className="text-xs text-red-400 italic p-1">Nenhum pet encontrado com este nome.</Text>
                ) : (
                  petsFiltradosNoForm.map((pet) => (
                    <Chip
                      key={pet.id}
                      label={`${pet.nome_pet} (#${pet.id})`}
                      selected={form.id_pet === String(pet.id)}
                      onPress={() => setForm((current) => ({ ...current, id_pet: String(pet.id) }))}
                    />
                  ))
                )}
              </View>
            </View>
            
            {/* SELEÇÃO DE SERVIÇO */}
            <View className="gap-1">
              <Text className="text-sm text-slate-500 font-medium">Selecione o serviço (A-Z)</Text>
              <View className="flex-row flex-wrap gap-2">
                {servicosOrdenados.map((servico) => (
                  <Chip
                    key={servico.id}
                    label={`${servico.nome_servico} (${formatMoney(Number(servico.preco))})`}
                    selected={form.id_servico === String(servico.id)}
                    onPress={() =>
                      setForm((current) => ({
                        ...current,
                        id_servico: String(servico.id),
                        valor: String(servico.preco),
                      }))
                    }
                  />
                ))}
              </View>
            </View>
            
            {/* DATA */}
            <View className="gap-1">
              <Text className="text-sm font-medium text-slate-600">Data (DD/MM/AAAA)</Text>
              <TextInput
                style={{ height: 45, borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 8, paddingHorizontal: 12, backgroundColor: '#ffffff' }}
                placeholder="25/10/2026"
                value={form.data_atendimento}
                onChangeText={(txt) => setForm((current) => ({ ...current, data_atendimento: txt }))}
              />
            </View>
            
            {/* HORÁRIO */}
            <View className="gap-1">
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
            </View>

            {/* VALOR COBRADO */}
            <View className="gap-1">
              <Text className="text-sm font-medium text-slate-600">Valor Cobrado (R\$)</Text>
              <TextInput
                style={{ height: 45, borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 8, paddingHorizontal: 12, backgroundColor: '#ffffff' }}
                placeholder="70.00"
                value={form.valor}
                onChangeText={(txt) => setForm((current) => ({ ...current, valor: txt }))}
                keyboardType="numeric"
              />
            </View>

            <View className="mt-2">
              <Button title={saving ? "Salvando..." : "Salvar Agendamento"} onPress={handleSave} disabled={saving} />
            </View>
          </Card>
        </ScrollView>
      ) : (
        <View className="flex-1 gap-4">
          <Input placeholder="🔍 Filtrar agendamentos por pet ou serviço..." value={busca} onChangeText={setBusca} label={""} />

          <ScrollView showsVerticalScrollIndicator={false} className="gap-4">
            <Text className="text-lg font-bold text-slate-900 mt-2">📌 Hoje</Text>
            {gruposPorAbas.hoje.length === 0 ? (
              <Text className="text-sm text-slate-400 italic p-2">Nenhum atendimento para hoje.</Text>
            ) : (
              gruposPorAbas.hoje.map((grupo) => (
                <View key={grupo.data} className="gap-2">
                  {renderizarCards(grupo.atendimentos)}
                </View>
              ))
            )}

            <Text className="text-lg font-bold text-slate-900 mt-4">📅 Próximos Dias</Text>
            {gruposPorAbas.proximos.length === 0 ? (
              <Text className="text-sm text-slate-400 italic p-2">Nenhum próximo atendimento.</Text>
            ) : (
              gruposPorAbas.proximos.map((grupo) => (
                <View key={grupo.data} className="gap-2">
                  <Text className="text-xs font-semibold text-slate-500 px-1">{formatarDataAgenda(grupo.data)}</Text>
                  {renderizarCards(grupo.atendimentos)}
                </View>
              ))
            )}

            <Text className="text-lg font-bold text-slate-900 mt-4">⏳ Passados</Text>
            {gruposPorAbas.passados.length === 0 ? (
              <Text className="text-sm text-slate-400 italic p-2">Nenhum histórico anterior.</Text>
            ) : (
              gruposPorAbas.passados.map((grupo) => (
                <View key={grupo.data} className="gap-2">
                  <Text className="text-xs font-semibold text-slate-500 px-1">{formatarDataAgenda(grupo.data)}</Text>
                  {renderizarCards(grupo.atendimentos)}
                </View>
              ))
            )}
          </ScrollView>
        </View>
      )}
    </Screen>
  );
}
import { useCallback, useState } from "react";
import { Text, View } from "react-native";
import { useFocusEffect } from "expo-router";
import { API_URL, getErrorMessage } from "../../src/api/client"; // CORRIGIDO: Agora usa API_URL
import { dashboardApi } from "../../src/api/petshop";
import { Screen } from "../../src/components/Page";
import { Card, ErrorBanner } from "../../src/components/ui";
import { formatMoney } from "../../src/utils/format";

interface PeriodoMetricas {
  hoje: number;
  semana: number;
  mes: number;
  ano: number;
}

interface PeriodoFaturamento {
  hoje: number;
  semana: number;
  mes: number;
  ano: number;
}

interface NovaDashboardDados {
  total_pets_cadastrados: number;
  servicos: PeriodoMetricas;
  atendimentos: PeriodoMetricas;
  faturamento: PeriodoFaturamento;
  ranking_pets: Array<{ nome_pet: string; total_visitas: number }>;
}

export default function DashboardScreen() {
  const [dados, setDados] = useState<NovaDashboardDados | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const resposta = await dashboardApi.resumoCompleto();
      setDados(resposta);
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

  return (
    <Screen title="Painel de Controle" subtitle={`Indicadores Gerenciais · API ${API_URL}`} loading={loading}>
      <ErrorBanner message={error} />

      <View className="rounded-3xl bg-teal-800 p-5 mb-4">
        <Text className="text-sm text-teal-100 uppercase tracking-wider font-semibold">Total em Base</Text>
        <Text className="mt-1 text-4xl font-bold text-white">{dados?.total_pets_cadastrados ?? 0} Pets Cadastrados</Text>
      </View>

      <Card className="gap-4">
        <Text className="text-lg font-bold text-slate-900">Volumetria por Período</Text>
        
        <View className="border-b border-slate-100 pb-2 flex-row justify-between">
          <Text className="font-semibold text-slate-400 text-xs w-[30%]">PERÍODO</Text>
          <Text className="font-semibold text-slate-400 text-xs text-center flex-1">SERV. REALIZADOS</Text>
          <Text className="font-semibold text-slate-400 text-xs text-right flex-1">ATENDIMENTOS</Text>
        </View>

        <TableRow periodo="Hoje" servicos={dados?.servicos.hoje ?? 0} atendimentos={dados?.atendimentos.hoje ?? 0} />
        <TableRow periodo="Esta Semana" servicos={dados?.servicos.semana ?? 0} atendimentos={dados?.atendimentos.semana ?? 0} />
        <TableRow periodo="Este Mês" servicos={dados?.servicos.mes ?? 0} atendimentos={dados?.atendimentos.mes ?? 0} />
        <TableRow periodo="Este Ano" servicos={dados?.servicos.ano ?? 0} atendimentos={dados?.atendimentos.ano ?? 0} />
      </Card>

      <Card className="gap-3">
        <Text className="text-lg font-bold text-slate-900">Controle de Recebimentos</Text>
        <View className="gap-2 mt-1">
          <FaturamentoRow titulo="Faturamento de Hoje" valor={dados?.faturamento.hoje ?? 0} destaque={true} />
          <FaturamentoRow titulo="Acumulado da Semana" valor={dados?.faturamento.semana ?? 0} />
          <FaturamentoRow titulo="Fechamento do Mês" valor={dados?.faturamento.mes ?? 0} />
          <FaturamentoRow titulo="Consolidado do Ano" valor={dados?.faturamento.ano ?? 0} />
        </View>
      </Card>

      <Card className="gap-3 mb-6">
        <Text className="text-lg font-bold text-slate-900">🏆 Ranking de Assiduidade</Text>
        {(!dados?.ranking_pets || dados.ranking_pets.length === 0) ? (
          <Text className="text-sm text-slate-500 italic">Nenhum atendimento realizado.</Text>
        ) : (
          dados.ranking_pets.map((item, index) => (
            <View key={item.nome_pet} className="flex-row items-center justify-between py-1 border-b border-slate-50 border-dashed">
              <Text className="text-sm text-slate-700">
                <Text className="font-bold text-teal-800">{index + 1}º</Text> — {item.nome_pet}
              </Text>
              <Text className="text-sm font-semibold text-slate-900">{item.total_visitas} visitas</Text>
            </View>
          ))
        )}
      </Card>
    </Screen>
  );
}

function TableRow({ periodo, servicos, atendimentos }: { periodo: string; servicos: number; atendimentos: number }) {
  return (
    <View className="flex-row justify-between items-center py-1">
      <Text className="text-sm font-medium text-slate-600 w-[30%]">{periodo}</Text>
      <Text className="text-sm font-semibold text-slate-800 text-center flex-1">{servicos} itens</Text>
      <Text className="text-sm font-semibold text-slate-800 text-right flex-1">{atendimentos} check-ins</Text>
    </View>
  );
}

function FaturamentoRow({ titulo, valor, destaque = false }: { titulo: string; valor: number; destaque?: boolean }) {
  return (
    <View className={`flex-row justify-between items-center py-2 px-3 rounded-xl ${destaque ? "bg-teal-50" : "bg-slate-50"}`}>
      <Text className={`text-sm ${destaque ? "font-semibold text-teal-900" : "text-slate-600"}`}>{titulo}</Text>
      <Text className={`text-base font-bold ${destaque ? "text-teal-800" : "text-slate-800"}`}>{formatMoney(valor)}</Text>
    </View>
  );
}
import { useCallback, useState } from "react";
import { Text, View } from "react-native";
import { useFocusEffect, router } from "expo-router";
import { API_BASE_URL, getErrorMessage } from "../../src/api/client";
import { dashboardApi } from "../../src/api/petshop";
import { Screen } from "../../src/components/Page";
import { Button, Card, ErrorBanner } from "../../src/components/ui";
import { useAuth } from "../../src/context/AuthContext";
import { formatMoney } from "../../src/utils/format";
import type {
  AtendimentosPorDia,
  DashboardResumo,
  FaturamentoConsolidado,
  TopTutor,
} from "../../src/types";

export default function DashboardScreen() {
  const { session, logout } = useAuth();
  const [resumo, setResumo] = useState<DashboardResumo | null>(null);
  const [faturamento, setFaturamento] = useState<FaturamentoConsolidado | null>(null);
  const [topTutores, setTopTutores] = useState<TopTutor[]>([]);
  const [porDia, setPorDia] = useState<AtendimentosPorDia[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const [resumoData, faturamentoData, dias] = await Promise.all([
        dashboardApi.resumo(),
        dashboardApi.faturamento(),
        dashboardApi.atendimentosPorDia(),
      ]);
      setResumo(resumoData);
      setFaturamento(faturamentoData);
      setPorDia(dias);

      try {
        setTopTutores(await dashboardApi.topTutores());
      } catch {
        setTopTutores([]);
      }
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

  async function handleLogout() {
    await logout();
    router.replace("/");
  }

  const sessionLabel =
    session?.kind === "tutor" ? session.tutor.nome : session?.name ?? "Equipe";

  return (
    <Screen
      title="Painel"
      subtitle={`Conectado como ${sessionLabel} · API ${API_BASE_URL}`}
      loading={loading}
      headerRight={
        <View className="w-28">
          <Button title="Sair" variant="secondary" onPress={handleLogout} />
        </View>
      }
    >
      <ErrorBanner message={error} />

      <View className="flex-row flex-wrap gap-3">
        <Stat title="Pets" value={resumo?.total_pets ?? 0} />
        <Stat title="Serviços" value={resumo?.total_servicos ?? 0} />
        <Stat title="Atendimentos" value={resumo?.total_atendimentos ?? 0} />
      </View>

      <Card>
        <Text className="text-lg font-semibold text-slate-900">Faturamento</Text>
        <Text className="mt-2 text-3xl font-bold text-teal-800">
          {formatMoney(faturamento?.resumo_geral.faturamento_total)}
        </Text>
        <Text className="mt-1 text-sm text-slate-500">
          Ticket médio {formatMoney(faturamento?.resumo_geral.ticket_medio)}
        </Text>
      </Card>

      <Card className="gap-3">
        <Text className="text-lg font-semibold text-slate-900">Atendimentos por dia</Text>
        {porDia.length === 0 ? (
          <Text className="text-sm text-slate-500">Sem dados ainda.</Text>
        ) : (
          porDia.map((item) => (
            <View key={item.dia_semana} className="flex-row justify-between">
              <Text className="text-sm text-slate-600">{item.dia_semana}</Text>
              <Text className="text-sm font-semibold text-slate-900">{item.total_atendimentos}</Text>
            </View>
          ))
        )}
      </Card>

      <Card className="gap-3">
        <Text className="text-lg font-semibold text-slate-900">Top tutores</Text>
        {topTutores.length === 0 ? (
          <Text className="text-sm text-slate-500">
            Sem ranking no momento. Se a rota /dashboard/top-tutores não responder, o restante do painel continua.
          </Text>
        ) : (
          topTutores.map((item, index) => (
            <View key={`${item.nome_tutor}-${index}`} className="flex-row items-center justify-between">
              <Text className="flex-1 text-sm text-slate-700">{item.nome_tutor ?? "Tutor"}</Text>
              <Text className="text-sm font-semibold text-slate-900">
                {item.total_agendamentos} · {formatMoney(item.total_gasto)}
              </Text>
            </View>
          ))
        )}
      </Card>
    </Screen>
  );
}

function Stat({ title, value }: { title: string; value: number }) {
  return (
    <View className="min-w-[30%] flex-1 rounded-3xl bg-teal-800 px-4 py-5">
      <Text className="text-sm text-teal-100">{title}</Text>
      <Text className="mt-2 text-3xl font-bold text-white">{value}</Text>
    </View>
  );
}

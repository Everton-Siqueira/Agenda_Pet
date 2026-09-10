export type Tutor = {
  id: number;
  nome: string;
  celular: string;
  endereco: string;
};

export type Pet = {
  id: number;
  nome_pet: string;
  especie: string;
  id_tutor: number;
};

export type Servico = {
  id: number;
  tipo_servico: string;
  valor: number | string;
};

export type Atendimento = {
  id: number;
  id_pet: number;
  data_atendimento: string;
  horario_atendimento: string;
  id_servico: number;
  valor: number | string;
};

export type AtendimentoDetalhe = {
  id: number;
  data_atendimento: string;
  horario_atendimento: string;
  nome_tutor: string | null;
  nome_pet: string | null;
  servico: string | null;
  valor: number | string;
};

export type DashboardResumo = {
  total_pets: number;
  total_servicos: number;
  total_atendimentos: number;
};

export type FaturamentoConsolidado = {
  resumo_geral: {
    faturamento_total: number | string;
    ticket_medio: number | string;
    total_atendimentos: number;
  };
  faturamento_por_dia_semana: {
    dia_semana: string;
    total_atendimentos: number;
    faturamento: number | string;
  }[];
  faturamento_por_mes: {
    mes: string;
    total_atendimentos: number;
    faturamento: number | string;
  }[];
};

export type TopTutor = {
  nome_tutor: string | null;
  total_agendamentos: number;
  total_gasto: number | string;
};

export type AtendimentosPorDia = {
  dia_semana: string;
  total_atendimentos: number;
};

import { api } from "./client";
import type {
  Atendimento,
  AtendimentoDetalhe,
  AtendimentosPorDia,
  DashboardResumo,
  FaturamentoConsolidado,
  Pet,
  Servico,
  TopTutor,
  Tutor,
} from "../types";

export const tutorApi = {
  list: () => api.get<Tutor[]>("/tutor").then((res) => res.data),
  get: (id: number) => api.get<Tutor>(`/tutor/${id}`).then((res) => res.data),
  create: (payload: Omit<Tutor, "id">) =>
    api.post<{ message: string; id: number }>("/tutor", payload).then((res) => res.data),
  update: (id: number, payload: Omit<Tutor, "id">) =>
    api.put(`/tutor/${id}`, payload).then((res) => res.data),
  remove: (id: number) => api.delete(`/tutor/${id}`).then((res) => res.data),
};

export const petApi = {
  list: () => api.get<Pet[]>("/pet").then((res) => res.data),
  get: (id: number) => api.get<Pet>(`/pet/${id}`).then((res) => res.data),
  create: (payload: Omit<Pet, "id">) =>
    api.post<{ message: string; id: number }>("/pet", payload).then((res) => res.data),
  update: (id: number, payload: Omit<Pet, "id">) =>
    api.put(`/pet/${id}`, payload).then((res) => res.data),
  remove: (id: number) => api.delete(`/pet/${id}`).then((res) => res.data),
};

export const servicoApi = {
  list: () => api.get<Servico[]>("/servico").then((res) => res.data),
  get: (id: number) => api.get<Servico>(`/servico/${id}`).then((res) => res.data),
  create: (payload: Omit<Servico, "id">) =>
    api.post<Servico>("/servico", payload).then((res) => res.data),
  update: (id: number, payload: Omit<Servico, "id">) =>
    api.put(`/servico/${id}`, payload).then((res) => res.data),
  remove: (id: number) => api.delete(`/servico/${id}`).then((res) => res.data),
};

export const atendimentoApi = {
  list: () => api.get<Atendimento[]>("/atendimento").then((res) => res.data),
  get: (id: number) =>
    api.get<AtendimentoDetalhe>(`/atendimento/${id}`).then((res) => res.data),
  create: (payload: Omit<Atendimento, "id">) =>
    api.post<Atendimento>("/atendimento", payload).then((res) => res.data),
  update: (id: number, payload: Omit<Atendimento, "id">) =>
    api.put<Atendimento>(`/atendimento/${id}`, payload).then((res) => res.data),
  remove: (id: number) => api.delete(`/atendimento/${id}`).then((res) => res.data),
};

export const dashboardApi = {
  resumo: () => api.get<DashboardResumo>("/dashboard").then((res) => res.data),
  faturamento: () =>
    api.get<FaturamentoConsolidado>("/dashboard/faturamento-consolidado").then((res) => res.data),
  topTutores: () => api.get<TopTutor[]>("/dashboard/top-tutores").then((res) => res.data),
  atendimentosPorDia: () =>
    api.get<AtendimentosPorDia[]>("/dashboard/atendimentos-por-dia-semana").then((res) => res.data),
};

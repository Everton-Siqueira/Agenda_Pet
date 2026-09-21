import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { tutorApi } from "../api/petshop";
import { onlyDigits } from "../utils/format";
import type { Tutor } from "../types";

const STORAGE_KEY = "@agenda-pet/session";

export type Session =
  | { kind: "tutor"; tutor: Tutor }
  | { kind: "staff"; name: string };

type AuthContextValue = {
  session: Session | null;
  loading: boolean;
  loginByPhone: (celular: string) => Promise<void>;
  loginAsStaff: (name?: string) => Promise<void>;
  registerTutor: (payload: Omit<Tutor, "id">) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY)
      .then((raw) => {
        if (!raw) return;
        setSession(JSON.parse(raw) as Session);
      })
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, []);

  const persist = useCallback(async (next: Session | null) => {
    setSession(next);
    if (next) {
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } else {
      await AsyncStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const loginByPhone = useCallback(
    async (celular: string) => {
      const digits = onlyDigits(celular);
      if (digits.length < 10) {
        throw new Error("Informe um celular válido com DDD.");
      }

      const tutores = await tutorApi.list();
      const found = tutores.find((tutor) => onlyDigits(tutor.celular) === digits);

      if (!found) {
        throw new Error("Nenhum tutor encontrado com esse celular. Cadastre-se para continuar.");
      }

      await persist({ kind: "tutor", tutor: found });
    },
    [persist]
  );

  const loginAsStaff = useCallback(
    async (name = "Equipe") => {
      await persist({ kind: "staff", name });
    },
    [persist]
  );

  const registerTutor = useCallback(
    async (payload: Omit<Tutor, "id">) => {
      const created = await tutorApi.create(payload);
      await persist({
        kind: "tutor",
        tutor: { id: created.id, ...payload },
      });
    },
    [persist]
  );

  const logout = useCallback(async () => {
    await persist(null);
  }, [persist]);

  const value = useMemo(
    () => ({
      session,
      loading,
      loginByPhone,
      loginAsStaff,
      registerTutor,
      logout,
    }),
    [session, loading, loginByPhone, loginAsStaff, registerTutor, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider.");
  }
  return context;
}

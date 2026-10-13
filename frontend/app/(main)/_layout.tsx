import React, { useEffect } from 'react';
import { Stack, useRouter } from 'expo-router';
import { useAuth } from '../../src/context/AuthContext';
import { ActivityIndicator, View } from 'react-native';

export default function MainLayout() {
  const { session, loading } = useAuth();
  const router = useRouter();

  // Proteção em tempo de execução: se o carregamento terminar e o usuário não tiver sessão,
  // nós mandamos ele de volta para a tela de login para evitar o travamento interno.
  useEffect(() => {
    if (!loading && !session) {
      // Ajuste o caminho '/login' de acordo com a sua pasta raiz (ex: '/' ou '/login')
      router.replace('/login');
    }
  }, [session, loading]);

  // Enquanto valida o token em background, exibe um feedback visual limpo
  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F5F7FA' }}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  // Se o usuário não tiver sessão, bloqueia a renderização das telas internas
  // até que o useEffect acima dispare o redirecionamento seguro
  if (!session) {
    return null;
  }

  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="agenda" options={{ title: "Agenda Pet" }} />
      <Stack.Screen name="tutores" options={{ title: "Tutores" }} />
      <Stack.Screen name="pets" options={{ title: "Pets" }} />
      <Stack.Screen name="servicos" options={{ title: "Serviços" }} />
      <Stack.Screen name="dashboard" options={{ title: "Dashboard" }} />
    </Stack>
  );
}
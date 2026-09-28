import React from 'react';
import { Stack } from 'expo-router';
import { useAuth } from '../../src/context/AuthContext';
import { ActivityIndicator, View } from 'react-native';

export default function MainLayout() {
  const { session, loading } = useAuth();

  // Uma proteção extra: enquanto checa a sessão dentro do painel, exibe um carregando
  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F5F7FA' }}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  // Se por alguma falha o usuário cair aqui sem sessão, o layout de fora vai tratá-lo,
  // mas aqui nós apenas renderizamos as telas internas sem barras nativas feias no topo
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="agenda" options={{ title: "Agenda Pet" }} />
    </Stack>
  );
}
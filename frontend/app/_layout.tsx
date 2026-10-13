import React, { useEffect } from 'react';
import { Stack, useRouter } from 'expo-router';
import { useAuth } from '../../src/context/AuthContext';
import { ActivityIndicator, View } from 'react-native';

export default function MainLayout() {
  const { session, loading } = useAuth();
  const router = useRouter();

  // Expulsa de volta para a tela de login caso o token expire ou não exista
  useEffect(() => {
    if (!loading && !session) {
      router.replace('/');
    }
  }, [session, loading]);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F5F7FA' }}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

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
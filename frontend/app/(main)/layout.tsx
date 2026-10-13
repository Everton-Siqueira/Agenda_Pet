import React from 'react';
import { Stack } from 'expo-router';

export default function MainLayout() {
  // Removida a trava daqui para evitar o erro de contexto fora do escopo
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
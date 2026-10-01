import React, { useState } from 'react';
import { StyleSheet, Text, TextInput, TouchableOpacity, View, Alert, ActivityIndicator, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../src/context/AuthContext'; // 👈 IMPORTANTE: Caminho ajustado para o seu AuthContext
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { loginAsStaff } = useAuth(); // 👈 Puxa a função de login do Contexto global

  const handleLogin = async () => {
    console.log("LOGIN FOI CLICADO");

    if (!email || !senha) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos.');
      return;
    }

    setLoading(true);

    try {
      const apiUrl = 'http://192.168.100.114:8000';

      const response = await fetch(`${apiUrl}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
      },
      body: JSON.stringify({
        email: email.trim().toLowerCase(),
        senha: senha
      }),
    });

    const data = await response.json();

    if (response.status === 200) {
      await AsyncStorage.setItem(
        '@agenda-pet/token',
        data.access_token
      );

        console.log("1 - Login respondeu:", data);

      await loginAsStaff(data.usuario.nome);

      console.log("2 - loginAsStaff terminou");

      router.replace("/agenda");

    } else {
      console.log("ENTROU NO ELSE DO LOGIN");

      Alert.alert(
        'Erro de login',
        'E-mail ou senha incorretos. Verifique seus dados e tente novamente.'
      );
      }

  } catch (error: any) {
    Alert.alert(
      'Erro de Conexão',
      `Não foi possível alcançar o servidor.\nDetalhe: ${error?.message}`
    );

  } finally {
    setLoading(false);
  }
};

      const styles = StyleSheet.create({
        container: { flex: 1, backgroundColor: '#F5F7FA', justifyContent: 'center', padding: 20 },
        logo: { fontSize: 28, fontWeight: 'bold', color: '#1E293B', textAlign: 'center', marginBottom: 5 },
        subTitle: { fontSize: 16, color: '#64748B', textAlign: 'center', marginBottom: 30 },
        input: { backgroundColor: '#FFF', padding: 15, borderRadius: 8, fontSize: 16, marginBottom: 15, borderWidth: 1, borderColor: '#CBD5E1', color: '#1E293B' },
        button: { backgroundColor: '#4F46E5', padding: 15, borderRadius: 8, alignItems: 'center', marginTop: 10 },
        buttonText: { color: '#FFF', fontSize: 18, fontWeight: 'bold' }
    });
  }
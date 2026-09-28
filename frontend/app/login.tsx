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
    if (!email || !senha) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos.');
      return;
    }

    setLoading(true);
    try {
      // IP do seu servidor Python local
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
        // 1. Salva o Token bruto recebido do Python para as suas requisições futuras na API
        await AsyncStorage.setItem('@agenda-pet/token', data.access_token);
        
        // 2. 🌟 O SEGREDO: Avisa o Contexto de segurança que o funcionário logou com sucesso
        await loginAsStaff(data.usuario.nome);
        
        // 3. Redireciona de forma limpa para a agenda dentro da pasta (main)
        router.replace("/agenda");
      } else {
        const mensagemErro = data && data.detail ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : 'E-mail ou senha incorretos.';
        Alert.alert('Erro de Autenticação', mensagemErro);
      }
    } catch (error: any) {
      Alert.alert('Erro de Conexão', `Não foi possível alcançar o servidor.\nDetalhe: ${error?.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>🐾 Agenda Pet SaaS Teste Login</Text>
      <Text style={styles.subTitle}>Área do Funcionário</Text>

      <TextInput
        style={styles.input}
        placeholder="E-mail"
        placeholderTextColor="#888"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />

      <TextInput
        style={styles.input}
        placeholder="Senha"
        placeholderTextColor="#888"
        value={senha}
        onChangeText={setSenha}
        secureTextEntry
        autoCapitalize="none"
      />

      <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
        {loading ? <ActivityIndicator color="#FFF" /> : <Text style={styles.buttonText}>Entrar</Text>}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F7FA', justifyContent: 'center', padding: 20 },
  logo: { fontSize: 28, fontWeight: 'bold', color: '#1E293B', textAlign: 'center', marginBottom: 5 },
  subTitle: { fontSize: 16, color: '#64748B', textAlign: 'center', marginBottom: 30 },
  input: { backgroundColor: '#FFF', padding: 15, borderRadius: 8, fontSize: 16, marginBottom: 15, borderWidth: 1, borderColor: '#CBD5E1', color: '#1E293B' },
  button: { backgroundColor: '#4F46E5', padding: 15, borderRadius: 8, alignItems: 'center', marginTop: 10 },
  buttonText: { color: '#FFF', fontSize: 18, fontWeight: 'bold' }
});
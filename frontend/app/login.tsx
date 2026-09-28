import React, { useState } from 'react';
import { StyleSheet, Text, TextInput, TouchableOpacity, View, Alert, ActivityIndicator, Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import { useRouter } from 'expo-router';
import Constants from 'expo-constants';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async () => {
    if (!email || !senha) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos.');
      return;
    }

    setLoading(true);
    try {
      const debuggerHost = Constants.expoConfig?.hostUri;
      const ipAddress = debuggerHost ? debuggerHost.split(':')[0] : 'localhost';
      const apiUrl = `http://${ipAddress}:8000`;

      // Mensagem opcional de depuração para ver qual URL o celular gerou
      console.log("Tentando conectar na URL:", `${apiUrl}/api/login`);

      const response = await fetch(`${apiUrl}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha }),
      });

      const data = await response.json();

      if (response.status === 200) {
        if (Platform.OS === 'web') {
          localStorage.setItem('userToken', data.access_token);
          localStorage.setItem('userName', data.usuario.nome);
        } else {
          await SecureStore.setItemAsync('userToken', data.access_token);
          await SecureStore.setItemAsync('userName', data.usuario.nome);
        }
        router.replace('/(main)/agenda');
      } else {
        // Captura erros retornados intencionalmente pelo backend (ex: 401, 404, 500)
        Alert.alert(
          'Erro do Servidor (Status ' + response.status + ')',
          typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail) || 'Erro desconhecido.'
        );
      }
    } catch (error: any) {
      // CAPTURA DE ERRO CRUCIAL: Mostra o erro de rede ou falha de código em um alerta detalhado
      const mensagemErro = error?.message || 'Sem mensagem de erro';
      const nomeErro = error?.name || 'Erro Desconhecido';
      
      Alert.alert(
        'Falha Técnica Detectada',
        `Tipo: ${nomeErro}\nDetalhe: ${mensagemErro}\n\nVerifique se o seu FastAPI está rodando com "--host 0.0.0.0".`
      );
      
      console.error("Erro completo capturado no catch:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>🐾 Agenda Pet SaaS</Text>
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
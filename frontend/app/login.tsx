import React, { useState } from 'react';
import { StyleSheet, Text, TextInput, TouchableOpacity, View, Alert, ActivityIndicator, Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import { useRouter } from 'expo-router';

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
      // IP Fixo do seu PC atualizado conforme o seu comando ipconfig
      const apiUrl = 'http://192.168.100.114:8000';

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
        
        // Redireciona para a tela após o login bem-sucedido
        router.navigate({ pathname: "/(main)/agenda" as any });
      } else {
        // Exibe o erro exato que o seu FastAPI devolver (ex: e-mail incorreto, senha errada)
        Alert.alert('Erro de Autenticação', data.detail || 'E-mail ou senha incorretos.');
      }
    } catch (error: any) {
      // Exibe detalhadamente se houver falha de rede/conexão física
      Alert.alert('Erro de Conexão', `Não foi possível alcançar o servidor.\nDetalhe técnico: ${error?.message}`);
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
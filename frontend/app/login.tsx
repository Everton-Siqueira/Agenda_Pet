import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../src/context/AuthContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [loading, setLoading] = useState(false);

  const router = useRouter();
  const { loginAsStaff } = useAuth();

  const handleLogin = async () => {
    console.log('LOGIN FOI CLICADO');

    if (!email.trim() || !senha) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos.');
      return;
    }

    setLoading(true);

    try {
      const apiUrl = 'http://192.168.100.114:8000';

      console.log('1 - Tentando acessar a API...');

      const response = await fetch(`${apiUrl}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          senha: senha,
        }),
      });

      console.log('2 - Status da API:', response.status);

      const data = await response.json();

      console.log('3 - Resposta da API:', data);

      if (response.status === 200) {
        await AsyncStorage.setItem(
          '@agenda-pet/token',
          data.access_token
        );

        console.log('4 - Token salvo');

        await loginAsStaff(data.usuario.nome);

        console.log('5 - loginAsStaff terminou');

        console.log('6 - Indo para /agenda');

        router.replace('/agenda');

        return;
      }

      Alert.alert(
        'Erro de login',
        data?.detail ||
          'E-mail ou senha incorretos. Verifique seus dados e tente novamente.'
      );
    } catch (error: any) {
      console.log('ERRO NO LOGIN:', error);

      Alert.alert(
        'Erro de Conexão',
        `Não foi possível alcançar o servidor.\n\nDetalhe: ${
          error?.message || 'Erro desconhecido'
        }`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>Agenda Pet</Text>

      <Text style={styles.subTitle}>
        Acesse sua conta
      </Text>

      <TextInput
        style={styles.input}
        placeholder="E-mail"
        placeholderTextColor="#94A3B8"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        autoCorrect={false}
        editable={!loading}
      />

      <TextInput
        style={styles.input}
        placeholder="Senha"
        placeholderTextColor="#94A3B8"
        value={senha}
        onChangeText={setSenha}
        secureTextEntry
        autoCapitalize="none"
        editable={!loading}
      />

      <TouchableOpacity
        style={styles.button}
        onPress={handleLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#FFFFFF" />
        ) : (
          <Text style={styles.buttonText}>Entrar</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
    justifyContent: 'center',
    padding: 20,
  },

  logo: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1E293B',
    textAlign: 'center',
    marginBottom: 5,
  },

  subTitle: {
    fontSize: 16,
    color: '#64748B',
    textAlign: 'center',
    marginBottom: 30,
  },

  input: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 8,
    fontSize: 16,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    color: '#1E293B',
  },

  button: {
    backgroundColor: '#4F46E5',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
    minHeight: 52,
    justifyContent: 'center',
  },

  buttonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  Alert,
  ActivityIndicator,
  Modal,
  ScrollView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '/src/context/AuthContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [loading, setLoading] = useState(false);

  // Estados para o modal de cadastro de empresa
  const [modalVisible, setModalVisible] = useState(false);
  const [cadastroLoading, setCadastroLoading] = useState(false);
  const [nomeEmpresa, setNomeEmpresa] = useState('');
  const [cnpj, setCnpj] = useState('');
  const [nomeAdmin, setNomeAdmin] = useState('');
  const [emailAdmin, setEmailAdmin] = useState('');
  const [senhaAdmin, setSenhaAdmin] = useState('');

  const router = useRouter();
  const { loginAsStaff } = useAuth();
  
  // IP da sua máquina local configurado no backend
  const apiUrl = 'http://192.168.100.114:8000';

  const handleLogin = async () => {
    if (!email.trim() || !senha) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos.');
      return;
    }

    setLoading(true);

    try {
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

      const data = await response.json();

      if (response.status === 200) {
        await AsyncStorage.setItem('@agenda-pet/token', data.access_token);
        
        // Atualiza o estado global de autenticação
        await loginAsStaff(data.usuario.nome);
        
        // REDIRECIONAMENTO CORRIGIDO: Entra diretamente na pasta (main) vista na estrutura
        router.replace('/(main)/agenda');
        return;
      }

      Alert.alert(
        'Erro de login',
        data?.detail || 'E-mail ou senha incorretos. Verifique seus dados e tente novamente.'
      );
    } catch (error: any) {
      Alert.alert(
        'Erro de Conexão',
        `Não foi possível alcançar o servidor.\n\nDetalhe: ${error?.message || 'Erro desconhecido'}`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRegistrarEmpresa = async () => {
    if (!nomeEmpresa.trim() || !nomeAdmin.trim() || !emailAdmin.trim() || !senhaAdmin) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos obrigatórios.');
      return;
    }

    setCadastroLoading(true);

    try {
      const response = await fetch(`${apiUrl}/api/login/registrar-empresa`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          nome_empresa: nomeEmpresa.trim(),
          cnpj: cnpj.trim() || null,
          nome_admin: nomeAdmin.trim(),
          email_admin: emailAdmin.trim().toLowerCase(),
          senha_admin: senhaAdmin,
        }),
      });

      const data = await response.json();

      if (response.status === 200) {
        Alert.alert('Sucesso', 'Empresa e Administrador vinculados com sucesso!', [
          {
            text: 'OK',
            onPress: () => {
              setModalVisible(false);
              setEmail(emailAdmin.trim().toLowerCase()); // Preenche o e-mail no login automaticamente
              setSenha('');
              // Limpa o formulário de cadastro
              setNomeEmpresa('');
              setCnpj('');
              setNomeAdmin('');
              setEmailAdmin('');
              setSenhaAdmin('');
            },
          },
        ]);
        return;
      }

      Alert.alert('Erro no cadastro', data?.detail || 'Falha ao registrar empresa.');
    } catch (error: any) {
      Alert.alert('Erro de Conexão', 'Não foi possível se conectar ao servidor backend.');
    } finally {
      setCadastroLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>🐾 Agenda Pet SaaS</Text>
      <Text style={styles.subTitle}>Controle Multi-Tenant</Text>

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

      <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
        {loading ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.buttonText}>Entrar</Text>}
      </TouchableOpacity>

      <TouchableOpacity 
        style={styles.registerLink} 
        onPress={() => setModalVisible(true)}
        disabled={loading}
      >
        <Text style={styles.registerLinkText}>
          Ainda não tem cadastro? <Text style={{ fontWeight: 'bold', color: '#4F46E5' }}>Criar Empresa</Text>
        </Text>
      </TouchableOpacity>

      {/* MODAL DE CADASTRO DE EMPRESA */}
      <Modal visible={modalVisible} animationType="slide" transparent={true}>
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <ScrollView showsVerticalScrollIndicator={false}>
              <Text style={styles.modalTitle}>Cadastrar Empresa</Text>
              
              <Text style={styles.sectionLabel}>Dados Corporativos</Text>
              <TextInput
                style={styles.input}
                placeholder="Nome da Empresa *"
                placeholderTextColor="#94A3B8"
                value={nomeEmpresa}
                onChangeText={setNomeEmpresa}
              />
              <TextInput
                style={styles.input}
                placeholder="CNPJ (Opcional)"
                placeholderTextColor="#94A3B8"
                value={cnpj}
                onChangeText={setCnpj}
                keyboardType="numeric"
              />

              <Text style={styles.sectionLabel}>Conta do Administrador</Text>
              <TextInput
                style={styles.input}
                placeholder="Seu Nome Completo *"
                placeholderTextColor="#94A3B8"
                value={nomeAdmin}
                onChangeText={setNomeAdmin}
              />
              <TextInput
                style={styles.input}
                placeholder="E-mail Corporativo *"
                placeholderTextColor="#94A3B8"
                value={emailAdmin}
                onChangeText={setEmailAdmin}
                keyboardType="email-address"
                autoCapitalize="none"
              />
              <TextInput
                style={styles.input}
                placeholder="Senha de Acesso *"
                placeholderTextColor="#94A3B8"
                value={senhaAdmin}
                onChangeText={setSenhaAdmin}
                secureTextEntry
                autoCapitalize="none"
              />

              <TouchableOpacity 
                style={[styles.button, { marginTop: 15 }]} 
                onPress={handleRegistrarEmpresa}
                disabled={cadastroLoading}
              >
                {cadastroLoading ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.buttonText}>Finalizar Cadastro</Text>}
              </TouchableOpacity>

              <TouchableOpacity 
                style={styles.cancelButton} 
                onPress={() => setModalVisible(false)}
                disabled={cadastroLoading}
              >
                <Text style={styles.cancelButtonText}>Voltar ao Login</Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
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
  registerLink: {
    marginTop: 25,
    alignItems: 'center',
  },
  registerLinkText: {
    color: '#64748B',
    fontSize: 15,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: '#F5F7FA',
    borderRadius: 16,
    padding: 20,
    maxHeight: '90%',
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 20,
    textAlign: 'center',
  },
  sectionLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#4F46E5',
    marginBottom: 8,
    marginTop: 5,
    textTransform: 'uppercase',
  },
  cancelButton: {
    marginTop: 15,
    alignItems: 'center',
    padding: 10,
  },
  cancelButtonText: {
    color: '#64748B',
    fontSize: 16,
  },
});

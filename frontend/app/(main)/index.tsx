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
import { useAuth } from '@/src/context/AuthContext';
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
  const apiUrl = 'https://clavicle-groggily-devoutly.ngrok-free.dev';
  
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
        // 1. Salva o token localmente no dispositivo
        await AsyncStorage.setItem('@agenda-pet/token', data.access_token);
        
        // 2. Atualiza o estado global de autenticação
        try {
          await loginAsStaff(data.usuario.nome);
        } catch (authError) {
          console.log("Aviso no Contexto de Autenticação:", authError);
        }
        
        // 3. TENTATIVAS DE REDIRECIONAMENTO (BLINDADO)
        // Tentamos os caminhos possíveis para garantir que o Expo Router ache o arquivo agenda.tsx
        try {
          router.replace('/agenda');
        } catch (e) {
          try {
            router.replace('/(main)/agenda');
          } catch (err2) {
            router.push('/agenda');
          }
        }
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

      if (response.status === 200 || response.status === 201) {
        Alert.alert('Sucesso 🎉', 'Sua empresa e conta de administrador foram cadastradas com sucesso!', [
          {
            text: 'Ir para o Login',
            onPress: () => {
              // 1. Fecha o modal de cadastro automaticamente
              setModalVisible(false);
              
              // 2. Transfere o e-mail cadastrado direto para o campo de Login
              setEmail(emailAdmin.trim().toLowerCase()); 
              
              // 3. Limpa a senha do login para o usuário digitar a dele
              setSenha('');
              
              // 4. Limpa completamente os campos do formulário de cadastro para a próxima vez
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

      Alert.alert('Erro no cadastro', data?.detail || 'Falha ao registrar empresa. Verifique os dados.');
    } catch (error: any) {
      Alert.alert('Erro de Conexão', 'Não foi possível se conectar ao servidor backend. Verifique se o Ngrok/FastAPI está rodando.');
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

// ESTILOS VISUAIS EXPO NATIVE
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    justifyContent: 'center',
    padding: 24,
  },
  logo: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#1E293B',
    marginBottom: 4,
  },
  subTitle: {
    fontSize: 16,
    textAlign: 'center',
    color: '#64748B',
    marginBottom: 32,
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 8,
    padding: 14,
    fontSize: 16,
    color: '#1E293B',
    marginBottom: 16,
  },
  button: {
    backgroundColor: '#4F46E5',
    borderRadius: 8,
    padding: 14,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  registerLink: {
    marginTop: 24,
    alignItems: 'center',
  },
  registerLinkText: {
    fontSize: 14,
    color: '#64748B',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 24,
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
    marginTop: 10,
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  cancelButton: {
    marginTop: 12,
    padding: 14,
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: 15,
    color: '#64748B',
    fontWeight: '600',
  },
});
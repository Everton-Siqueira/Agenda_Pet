import axios from 'axios';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

const getBaseUrl = () => {
  // Se estiver rodando na Web (Navegador do PC)
  if (Platform.OS === 'web') {
    return 'http://localhost:8000';
  }

  // Pega o IP do computador que está rodando o servidor do Expo dinamicamente
  const hostUri = Constants.expoConfig?.hostUri;
  if (hostUri) {
    const ip = hostUri.split(':')[0]; // Extrai o IP (ex: 192.168.100.120)
    return `http://${ip}:8000`;
  }

  // Fallback caso não encontre
  return 'http://192.168.100.120:8000';
};

export const API_URL = getBaseUrl();

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export function getErrorMessage(error: any): string {
  if (error?.response?.data) {
    const data = error.response.data;
    if (typeof data === 'string') return data;
    if (data.detail) return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
    if (data.message) return data.message;
  }
  return error?.message || "Ocorreu um erro inesperado.";
}
import axios from 'axios';
import { Platform } from 'react-native';

const getBaseUrl = () => {
  // Se for o navegador do PC, usa o localhost direto (evita a trava de segurança do Ngrok no PC)
  if (Platform.OS === 'web') {
    return 'http://localhost:8000';
  }
  // Se for o celular, usa o link seguro do Ngrok para conectar pela internet
  return 'https://ngrok-free.dev';
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
import axios from 'axios';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const getBaseUrl = () => {
  if (Platform.OS === 'web') {
    return 'http://localhost:8000';
  }

  return 'https://clavicle-groggily-devoutly.ngrok-free.dev';
};

export const API_URL = getBaseUrl();

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Adiciona automaticamente o token de autenticação
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('@agenda-pet/token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export function getErrorMessage(error: any): string {
  if (error?.response?.data) {
    const data = error.response.data;

    if (typeof data === 'string') return data;

    if (data.detail) {
      return typeof data.detail === 'string'
        ? data.detail
        : JSON.stringify(data.detail);
    }

    if (data.message) return data.message;
  }

  return error?.message || "Ocorreu um erro inesperado.";
}
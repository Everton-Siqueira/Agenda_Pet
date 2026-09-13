import axios from 'axios';
import { Platform } from 'react-native';

// Substitua pelo IP atual da sua rede Wi-Fi obtido no 'ipconfig'
const IP_DA_SUA_REDE = "192.168.100.116"; 

const getBaseUrl = () => {
  // Se estiver rodando no Navegador do PC (Web)
  if (Platform.OS === 'web') {
    return 'http://localhost:8000';
  }
  // Se estiver rodando no Celular (Expo Go / Android / iOS)
  return `http://${IP_DA_SUA_REDE}:8000`;
};

export const API_URL = getBaseUrl();

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
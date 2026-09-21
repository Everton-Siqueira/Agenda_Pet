import axios from 'axios';

// Cole aqui o link completo que o ngrok gerou no seu terminal (deve começar com https://)
export const API_URL = 'https://clavicle-groggily-devoutly.ngrok-free.dev';

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
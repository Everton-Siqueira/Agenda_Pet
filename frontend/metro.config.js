const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

// 1. Busca a configuração padrão do Expo
const config = getDefaultConfig(__dirname);

// 2. Aplica a injeção de estilos do NativeWind especificando o arquivo global
module.exports = withNativeWind(config, { 
  input: "./global.css",
  projectRoot: __dirname 
});
import { Redirect, Tabs } from "expo-router";
import { Text } from "react-native";
import { useAuth } from "../../src/context/AuthContext";

export const unstable_settings = {
  initialRouteName: "agenda",
};

function TabLabel({ title, focused }: { title: string; focused: boolean }) {
  return (
    <Text className={`text-[11px] font-semibold ${focused ? "text-teal-800" : "text-slate-400"}`}>
      {title}
    </Text>
  );
}

export default function MainLayout() {
  const { session, loading } = useAuth();

  if (!loading && !session) {
    return <Redirect href="/" />;
  }

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: "#115e59",
        tabBarInactiveTintColor: "#94a3b8",
        tabBarStyle: {
          height: 68,
          paddingTop: 8,
          paddingBottom: 10,
          backgroundColor: "#ffffff",
          borderTopColor: "#e2e8f0",
        },
      }}
    >
      <Tabs.Screen name="index" options={{ href: null }} />
      <Tabs.Screen
        name="agenda"
        options={{
          title: "Agenda",
          tabBarLabel: ({ focused }) => <TabLabel title="Agenda" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="pets"
        options={{
          title: "Pets",
          tabBarLabel: ({ focused }) => <TabLabel title="Pets" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="tutores"
        options={{
          title: "Tutores",
          tabBarLabel: ({ focused }) => <TabLabel title="Tutores" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="servicos"
        options={{
          title: "Serviços",
          tabBarLabel: ({ focused }) => <TabLabel title="Serviços" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="dashboard"
        options={{
          title: "Painel",
          tabBarLabel: ({ focused }) => <TabLabel title="Painel" focused={focused} />,
        }}
      />
    </Tabs>
  );
}

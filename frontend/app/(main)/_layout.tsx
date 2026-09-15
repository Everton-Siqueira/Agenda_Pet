import { Tabs } from "expo-router";
import { Text } from "react-native";

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
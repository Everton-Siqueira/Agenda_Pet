import { ReactNode } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

type ScreenProps = {
  title: string;
  subtitle?: string;
  children: ReactNode;
  headerRight?: ReactNode;
  scroll?: boolean;
  loading?: boolean;
};

export function Screen({
  title,
  subtitle,
  children,
  headerRight,
  scroll = true,
  loading = false,
}: ScreenProps) {
  const body = loading ? (
    <View className="flex-1 items-center justify-center py-16">
      <ActivityIndicator size="large" color="#0f766e" />
    </View>
  ) : (
    children
  );

  return (
    <SafeAreaView className="flex-1 bg-slate-50" edges={["top", "left", "right"]}>
      <KeyboardAvoidingView
        className="flex-1"
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <View className="mx-auto w-full max-w-5xl flex-1 px-4 pb-6 pt-2">
          <View className="mb-5 flex-row items-start justify-between gap-3">
            <View className="flex-1">
              <Text className="text-2xl font-bold tracking-tight text-slate-900">{title}</Text>
              {subtitle ? (
                <Text className="mt-1 text-sm leading-5 text-slate-500">{subtitle}</Text>
              ) : null}
            </View>
            {headerRight}
          </View>
          {scroll ? (
            <ScrollView
              className="flex-1"
              contentContainerClassName="gap-4 pb-8"
              keyboardShouldPersistTaps="handled"
              showsVerticalScrollIndicator={false}
            >
              {body}
            </ScrollView>
          ) : (
            <View className="flex-1">{body}</View>
          )}
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

import {
  ActivityIndicator,
  Pressable,
  Text,
  TextInput,
  View,
  type TextInputProps,
  type ViewProps,
} from "react-native";

type ButtonProps = {
  title: string;
  onPress: () => void;
  variant?: "primary" | "secondary" | "ghost" | "danger";
  loading?: boolean;
  disabled?: boolean;
};

export function Button({
  title,
  onPress,
  variant = "primary",
  loading = false,
  disabled = false,
}: ButtonProps) {
  const variants = {
    primary: "bg-teal-700",
    secondary: "bg-white border border-teal-200",
    ghost: "bg-transparent",
    danger: "bg-rose-600",
  } as const;

  const textVariants = {
    primary: "text-white",
    secondary: "text-teal-800",
    ghost: "text-teal-800",
    danger: "text-white",
  } as const;

  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      className={`min-h-[48px] items-center justify-center rounded-2xl px-4 ${variants[variant]} ${
        disabled || loading ? "opacity-60" : "active:opacity-80"
      }`}
    >
      {loading ? (
        <ActivityIndicator color={variant === "primary" || variant === "danger" ? "#fff" : "#115e59"} />
      ) : (
        <Text className={`text-base font-semibold ${textVariants[variant]}`}>{title}</Text>
      )}
    </Pressable>
  );
}

export function Input({
  label,
  error,
  ...props
}: TextInputProps & { label: string; error?: string }) {
  return (
    <View className="gap-1.5">
      <Text className="text-sm font-medium text-slate-600">{label}</Text>
      <TextInput
        placeholderTextColor="#94a3b8"
        className="min-h-[48px] rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900"
        {...props}
      />
      {error ? <Text className="text-sm text-rose-600">{error}</Text> : null}
    </View>
  );
}

export function Card({ children, className = "", ...props }: ViewProps & { className?: string }) {
  return (
    <View
      className={`rounded-3xl border border-slate-100 bg-white p-4 shadow-sm ${className}`}
      {...props}
    >
      {children}
    </View>
  );
}

export function Chip({
  label,
  selected,
  onPress,
}: {
  label: string;
  selected?: boolean;
  onPress: () => void;
}) {
  return (
    <Pressable
      onPress={onPress}
      className={`rounded-full px-3 py-2 ${selected ? "bg-teal-700" : "bg-slate-100"}`}
    >
      <Text className={`text-sm font-medium ${selected ? "text-white" : "text-slate-700"}`}>
        {label}
      </Text>
    </Pressable>
  );
}

export function EmptyState({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <View className="items-center rounded-3xl border border-dashed border-slate-200 bg-white px-6 py-10">
      <Text className="text-center text-lg font-semibold text-slate-800">{title}</Text>
      <Text className="mt-2 text-center text-sm leading-5 text-slate-500">{subtitle}</Text>
    </View>
  );
}

export function ErrorBanner({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <View className="rounded-2xl bg-rose-50 px-4 py-3">
      <Text className="text-sm text-rose-700">{message}</Text>
    </View>
  );
}

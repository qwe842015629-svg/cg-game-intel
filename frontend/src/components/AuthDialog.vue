<template>
  <Dialog v-model="isOpen">
    <div v-if="registrationSuccess" class="space-y-4">
      <div class="text-center mb-4">
        <div
          class="w-16 h-16 mx-auto bg-gradient-to-br from-green-400 to-cyan-400 rounded-full flex items-center justify-center shadow-[0_0_30px_rgba(34,197,94,0.6)] animate-bounce"
        >
          <svg
            class="w-10 h-10 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="3"
              d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76"
            />
          </svg>
        </div>
      </div>

      <h2 class="text-2xl font-bold text-center text-green-400">
        {{ t("authDialog.registrationSuccessTitle") }}
      </h2>

      <div class="text-center space-y-3">
        <p class="text-sm text-muted-foreground">
          {{ t("authDialog.activationEmailSent") }}
        </p>
        <p class="text-lg font-bold text-cyan-400">{{ registerForm.email }}</p>
      </div>

      <div
        class="bg-cyan-500/10 border-2 border-cyan-500/30 rounded-xl p-4 space-y-3"
      >
        <h3 class="text-sm font-bold text-cyan-300 flex items-center gap-2">
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          {{ t("authDialog.nextStepsTitle") }}
        </h3>
        <ol class="space-y-2 text-xs text-cyan-100">
          <li class="flex items-start gap-2">
            <span
              class="flex-shrink-0 w-5 h-5 bg-cyan-500 text-black rounded-full flex items-center justify-center text-xs font-bold"
              >1</span
            >
            <span>{{
              t("authDialog.activationStep1", { email: registerForm.email })
            }}</span>
          </li>
          <li class="flex items-start gap-2">
            <span
              class="flex-shrink-0 w-5 h-5 bg-cyan-500 text-black rounded-full flex items-center justify-center text-xs font-bold"
              >2</span
            >
            <span>{{
              t("authDialog.activationStep2", { company: companyName })
            }}</span>
          </li>
          <li class="flex items-start gap-2">
            <span
              class="flex-shrink-0 w-5 h-5 bg-cyan-500 text-black rounded-full flex items-center justify-center text-xs font-bold"
              >3</span
            >
            <span>{{ t("authDialog.activationStep3") }}</span>
          </li>
          <li class="flex items-start gap-2">
            <span
              class="flex-shrink-0 w-5 h-5 bg-cyan-500 text-black rounded-full flex items-center justify-center text-xs font-bold"
              >4</span
            >
            <span>{{ t("authDialog.activationStep4") }}</span>
          </li>
        </ol>
      </div>

      <div class="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
        <p class="text-yellow-300 text-xs flex items-start gap-2">
          <svg
            class="w-4 h-4 flex-shrink-0 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <span>
            <strong>{{ t("authDialog.noEmailTitle") }}</strong
            ><br />
            {{ t("authDialog.noEmailDesc") }}
          </span>
        </p>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <Button @click="openEmail" class="w-full">{{
          t("authDialog.openEmail")
        }}</Button>
        <Button
          @click="closeActivationDialog"
          variant="outline"
          class="w-full"
          >{{ t("authDialog.close") }}</Button
        >
      </div>
    </div>

    <div v-else class="space-y-4">
      <h2 class="text-2xl font-bold">{{ t("authDialog.accountLogin") }}</h2>

      <Tabs :tabs="authTabs" v-model="activeTab">
        <div v-if="activeTab === 'login'" class="space-y-4 pt-4">
          <div>
            <label class="block text-sm font-medium mb-2">{{
              t("authDialog.emailLabel")
            }}</label>
            <Input
              v-model="loginForm.email"
              type="email"
              placeholder="your@email.com"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">{{
              t("authDialog.passwordLabel")
            }}</label>
            <Input
              v-model="loginForm.password"
              type="password"
              :placeholder="t('authDialog.passwordPlaceholder')"
            />
          </div>
          <Button @click="handleLogin" class="w-full">{{
            t("authDialog.loginButton")
          }}</Button>
        </div>

        <div v-if="activeTab === 'register'" class="space-y-4 pt-4">
          <div>
            <label class="block text-sm font-medium mb-2">{{
              t("authDialog.usernameLabel")
            }}</label>
            <Input
              v-model="registerForm.name"
              :placeholder="t('authDialog.usernamePlaceholder')"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">{{
              t("authDialog.emailLabel")
            }}</label>
            <Input
              v-model="registerForm.email"
              type="email"
              placeholder="your@email.com"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">{{
              t("authDialog.passwordLabel")
            }}</label>
            <Input
              v-model="registerForm.password"
              type="password"
              :placeholder="t('authDialog.passwordPlaceholder')"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">{{
              t("authDialog.confirmPasswordLabel")
            }}</label>
            <Input
              v-model="registerForm.confirmPassword"
              type="password"
              :placeholder="t('authDialog.passwordPlaceholder')"
            />
          </div>
          <Button @click="handleRegister" class="w-full">{{
            t("authDialog.registerButton")
          }}</Button>
        </div>
      </Tabs>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "../stores/auth";
import Dialog from "./ui/Dialog.vue";
import Tabs from "./ui/Tabs.vue";
import Input from "./ui/Input.vue";
import Button from "./ui/Button.vue";

interface Props {
  modelValue: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
}>();

const { t } = useI18n();
const authStore = useAuthStore();

const companyName = "CYPHER GAME BUY";
const isOpen = ref(props.modelValue);
const activeTab = ref("login");

const authTabs = computed(() => [
  {
    label: t("authDialog.tabs.login"),
    value: "login",
  },
  {
    label: t("authDialog.tabs.register"),
    value: "register",
  },
]);

const loginForm = ref({
  email: "",
  password: "",
});

const registerForm = ref({
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
});

const registrationSuccess = ref(false);

watch(
  () => props.modelValue,
  (val) => {
    isOpen.value = val;
  },
);

watch(isOpen, (val) => {
  emit("update:modelValue", val);
  if (!val) {
    registrationSuccess.value = false;
  }
});

const handleLogin = async () => {
  if (!loginForm.value.email.trim()) {
    window.alert(t("authDialog.emailRequired"));
    return;
  }

  if (!loginForm.value.password) {
    window.alert(t("authDialog.passwordRequired"));
    return;
  }

  try {
    await authStore.login(loginForm.value);
    window.alert(t("authDialog.loginSuccess"));
    isOpen.value = false;
    loginForm.value = { email: "", password: "" };
  } catch (error: any) {
    if (error.response?.data) {
      const errors = error.response.data;
      if (errors.non_field_errors) {
        window.alert(errors.non_field_errors.join(", "));
      } else if (errors.detail) {
        window.alert(errors.detail);
      } else {
        window.alert(t("authDialog.invalidCredentials"));
      }
      return;
    }

    window.alert(t("authDialog.loginFailed"));
  }
};

const handleRegister = async () => {
  if (!registerForm.value.name.trim()) {
    window.alert(t("authDialog.usernameRequired"));
    return;
  }

  if (!registerForm.value.email.trim()) {
    window.alert(t("authDialog.emailRequired"));
    return;
  }

  if (!registerForm.value.password) {
    window.alert(t("authDialog.passwordRequired"));
    return;
  }

  if (!registerForm.value.confirmPassword) {
    window.alert(t("authDialog.confirmPasswordRequired"));
    return;
  }

  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    window.alert(t("authDialog.passwordMismatch"));
    return;
  }

  if (registerForm.value.password.length < 8) {
    window.alert(t("authDialog.passwordTooShort"));
    return;
  }

  try {
    await authStore.register(registerForm.value);
    registrationSuccess.value = true;
  } catch (error: any) {
    if (error.response?.data) {
      const errors = error.response.data;
      if (errors.username) {
        window.alert(
          `${t("authDialog.fieldUsername")}${errors.username.join(", ")}`,
        );
      } else if (errors.email) {
        window.alert(`${t("authDialog.fieldEmail")}${errors.email.join(", ")}`);
      } else if (errors.password) {
        window.alert(
          `${t("authDialog.fieldPassword")}${errors.password.join(", ")}`,
        );
      } else if (errors.non_field_errors) {
        window.alert(errors.non_field_errors.join(", "));
      } else if (errors.detail) {
        window.alert(
          typeof errors.detail === "string"
            ? errors.detail
            : JSON.stringify(errors.detail),
        );
      } else {
        window.alert(
          typeof errors === "string" ? errors : JSON.stringify(errors),
        );
      }
      return;
    }

    window.alert(t("authDialog.registerFailed"));
  }
};

const openEmail = () => {
  const email = registerForm.value.email.trim();
  const domain = email.includes("@") ? email.split("@")[1].toLowerCase() : "";

  const emailUrls: Record<string, string> = {
    "qq.com": "https://mail.qq.com",
    "163.com": "https://mail.163.com",
    "126.com": "https://mail.126.com",
    "gmail.com": "https://mail.google.com",
    "outlook.com": "https://outlook.live.com",
    "hotmail.com": "https://outlook.live.com",
  };

  const url =
    emailUrls[domain] ||
    (domain ? `https://mail.${domain}` : "https://mail.google.com");
  window.open(url, "_blank");
};

const closeActivationDialog = () => {
  isOpen.value = false;
  registrationSuccess.value = false;
  registerForm.value = {
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  };
};
</script>

<style scoped>
@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-10px);
  }
}

.animate-bounce {
  animation: bounce 1s ease-in-out infinite;
}

.shadow-neon-green {
  box-shadow: 0 0 30px rgba(34, 197, 94, 0.6);
}
</style>

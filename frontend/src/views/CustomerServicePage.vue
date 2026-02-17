<template>
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-4xl mx-auto">
      <h1 
        class="text-3xl font-bold mb-8"
        :contenteditable="isEditMode"
        @blur="handleInlineEdit($event, 'page_title')"
      >{{ getPageConfig('page_title', pageConfigData.page_title || $t('customerServiceCenter')) }}</h1>
      <p 
        v-if="getPageConfig('page_description', pageConfigData.page_description)" 
        class="text-muted-foreground mb-8"
        :contenteditable="isEditMode"
        @blur="handleInlineEdit($event, 'page_description')"
      >{{ getPageConfig('page_description', pageConfigData.page_description) }}</p>

      <!-- 联系方式 -->
      <div v-if="pageConfigData.show_contact_methods" class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        <div v-for="method in contactMethods" :key="method.id" class="bg-card border border-border rounded-lg p-6">
          <component :is="getIconComponent(method.icon)" class="w-12 h-12 text-primary mb-4" />
          <h3 class="font-bold text-lg mb-2">{{ method.title }}</h3>
          <p class="text-muted-foreground mb-4">{{ method.description }}</p>
          <Button 
            v-if="method.button_link && method.button_link !== '#'"
            :variant="method.contact_type === 'online_chat' ? 'default' : 'outline'"
            :href="method.button_link"
            tag="a"
            :target="method.button_link.startsWith('http') ? '_blank' : '_self'"
          >
            {{ method.button_text }}
          </Button>
          <Button 
            v-else
            :variant="method.contact_type === 'online_chat' ? 'default' : 'outline'"
            disabled
          >
            {{ method.button_text }}
          </Button>
        </div>
      </div>

      <!-- 常见问题 -->
      <div v-if="pageConfigData.show_faq" class="bg-card border border-border rounded-lg p-6">
        <h2 
          class="font-bold text-2xl mb-6"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'faq_title')"
        >{{ getPageConfig('faq_title', pageConfigData.faq_title || $t('frequentlyAskedQuestions')) }}</h2>
        <div v-if="loadingFAQs" class="text-center py-8">
          <p class="text-muted-foreground">加载中...</p>
        </div>
        <div v-else class="space-y-4">
          <div 
            v-for="(faq, index) in faqs" 
            :key="faq.id"
            :class="['pb-4', index < faqs.length - 1 ? 'border-b border-border' : '']"
          >
            <h3 class="font-semibold mb-2">{{ faq.question }}</h3>
            <p class="text-muted-foreground">{{ faq.answer }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { MessageCircle, Mail, Phone, MessageSquare } from 'lucide-vue-next'
import Button from '../components/ui/Button.vue'
import { getContactMethods, getFAQs, getCustomerServiceConfig } from '../api/customerService'
import type { ContactMethod, FAQ, CustomerServiceConfig } from '../api/customerService'
import { useVisualEditor } from '../composables/useVisualEditor'

const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('customer_service', '客服中心页')

// 状态
const contactMethods = ref<ContactMethod[]>([])
const faqs = ref<FAQ[]>([])
const pageConfigData = ref<Partial<CustomerServiceConfig>>({
  page_title: '客服中心',
  show_contact_methods: true,
  show_faq: true,
  faq_title: '常见问题'
})
const loadingFAQs = ref(true)

// 获取图标组件
const getIconComponent = (iconName: string) => {
  const icons: Record<string, any> = {
    'MessageCircle': MessageCircle,
    'Mail': Mail,
    'Phone': Phone,
    'MessageSquare': MessageSquare,
  }
  return icons[iconName] || MessageCircle
}

// 加载数据
const loadData = async () => {
  try {
    // 加载页面配置
    const config = await getCustomerServiceConfig()
    pageConfigData.value = config
    console.log('成功加载客服页面配置:', config)
    
    // 加载联系方式
    if (config.show_contact_methods) {
      const methods = await getContactMethods()
      contactMethods.value = methods
      console.log('成功加载联系方式:', methods.length, '个')
    }
    
    // 加载常见问题
    if (config.show_faq) {
      loadingFAQs.value = true
      const faqList = await getFAQs()
      faqs.value = faqList
      console.log('成功加载常见问题:', faqList.length, '个')
    }
  } catch (error) {
    console.error('加载客服数据失败:', error)
  } finally {
    loadingFAQs.value = false
  }
}

// 组件加载时初始化
onMounted(() => {
  loadData()
})
</script>

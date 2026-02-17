<template>
  <div class="min-h-screen py-12">
    <div class="container mx-auto px-4 max-w-6xl">
      <section class="surface-card p-6 md:p-10 mb-8" v-motion-reveal="{ y: 24 }">
        <p class="text-xs uppercase tracking-[0.16em] text-muted-foreground mb-3">Contact</p>
        <h1 class="text-3xl md:text-5xl font-bold text-foreground mb-4">联系我们</h1>
        <p class="max-w-3xl text-base md:text-lg text-muted-foreground leading-relaxed">
          无论是充值咨询、订单问题还是商务合作，都可以通过以下方式联系我们。
        </p>
      </section>

      <section class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <article class="surface-card p-5" v-motion-reveal="{ delay: 50, y: 18 }">
          <h2 class="text-lg font-semibold text-foreground mb-3">邮箱</h2>
          <p class="text-sm text-muted-foreground mb-1">商务合作</p>
          <p class="text-sm text-foreground">business@cyphergamebuy.com</p>
          <p class="text-sm text-muted-foreground mt-3 mb-1">技术支持</p>
          <p class="text-sm text-foreground">support@cyphergamebuy.com</p>
        </article>

        <article class="surface-card p-5" v-motion-reveal="{ delay: 110, y: 18 }">
          <h2 class="text-lg font-semibold text-foreground mb-3">电话</h2>
          <p class="text-sm text-muted-foreground mb-1">客服热线</p>
          <p class="text-sm text-foreground">400-888-8888</p>
          <p class="text-sm text-muted-foreground mt-3 mb-1">服务时间</p>
          <p class="text-sm text-foreground">周一至周日 09:00 - 21:00</p>
        </article>

        <article class="surface-card p-5" v-motion-reveal="{ delay: 170, y: 18 }">
          <h2 class="text-lg font-semibold text-foreground mb-3">地址</h2>
          <p class="text-sm text-muted-foreground mb-1">公司地址</p>
          <p class="text-sm text-foreground">上海市浦东新区世纪大道 1001 号</p>
          <p class="text-sm text-muted-foreground mt-3 mb-1">邮编</p>
          <p class="text-sm text-foreground">200120</p>
        </article>
      </section>

      <section class="surface-card p-6 md:p-8 mb-8" v-motion-reveal="{ delay: 90, y: 20 }">
        <h2 class="text-2xl font-semibold text-foreground mb-6">在线留言</h2>
        <form class="space-y-4" @submit.prevent>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label class="block">
              <span class="block text-sm font-medium text-foreground mb-2">姓名</span>
              <input
                type="text"
                placeholder="请输入您的姓名"
                class="w-full h-11 px-3 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/35"
              />
            </label>

            <label class="block">
              <span class="block text-sm font-medium text-foreground mb-2">邮箱</span>
              <input
                type="email"
                placeholder="请输入您的邮箱"
                class="w-full h-11 px-3 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/35"
              />
            </label>
          </div>

          <label class="block">
            <span class="block text-sm font-medium text-foreground mb-2">主题</span>
            <input
              type="text"
              placeholder="请输入主题"
              class="w-full h-11 px-3 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/35"
            />
          </label>

          <label class="block">
            <span class="block text-sm font-medium text-foreground mb-2">消息内容</span>
            <textarea
              rows="6"
              placeholder="请输入您的问题或需求"
              class="w-full px-3 py-2.5 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/35 resize-y"
            ></textarea>
          </label>

          <button
            type="submit"
            v-magnetic="{ strength: 0.2, max: 12 }"
            class="inline-flex items-center justify-center px-6 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors"
          >
            提交留言
          </button>
        </form>
      </section>

      <section class="surface-card p-6 md:p-8" v-motion-reveal="{ delay: 130, y: 20 }">
        <h2 class="text-xl font-semibold text-foreground mb-4">关注我们</h2>
        <p class="text-sm text-muted-foreground mb-4">你也可以通过社媒获取活动与充值更新。</p>
        <div class="flex items-center gap-3">
          <a href="#" v-magnetic="{ strength: 0.16, max: 9 }" class="inline-flex items-center justify-center h-10 px-4 rounded-lg border border-border text-sm text-foreground hover:bg-muted transition-colors">X / Twitter</a>
          <a href="#" v-magnetic="{ strength: 0.16, max: 9 }" class="inline-flex items-center justify-center h-10 px-4 rounded-lg border border-border text-sm text-foreground hover:bg-muted transition-colors">Instagram</a>
          <a href="#" v-magnetic="{ strength: 0.16, max: 9 }" class="inline-flex items-center justify-center h-10 px-4 rounded-lg border border-border text-sm text-foreground hover:bg-muted transition-colors">LinkedIn</a>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

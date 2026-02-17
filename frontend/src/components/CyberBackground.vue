<template>
  <div class="fixed inset-0 -z-10 overflow-hidden bg-white">
    <!-- Grid pattern -->
    <div class="absolute inset-0 bg-[linear-gradient(to_right,#e5e7eb_1px,transparent_1px),linear-gradient(to_bottom,#e5e7eb_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-30"></div>
    
    <!-- Scan line effect -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-indigo-400 to-transparent opacity-20 animate-scan"></div>
    </div>
    
    <!-- Ambient glows -->
    <div class="absolute top-0 left-1/4 w-96 h-96 bg-indigo-200/20 rounded-full blur-[100px] animate-pulse-slow"></div>
    <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-200/20 rounded-full blur-[100px] animate-pulse-slow" style="animation-delay: 1.5s"></div>
    <div class="absolute top-1/2 left-1/2 w-96 h-96 bg-blue-200/20 rounded-full blur-[100px] animate-pulse-slow" style="animation-delay: 3s"></div>
    
    <!-- Noise overlay -->
    <div class="absolute inset-0 opacity-[0.02] bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIj48ZmlsdGVyIGlkPSJhIj48ZmVUdXJidWxlbmNlIGJhc2VGcmVxdWVuY3k9Ii43NSIgc3RpdGNoVGlsZXM9InN0aXRjaCIgdHlwZT0iZnJhY3RhbE5vaXNlIi8+PGZlQ29sb3JNYXRyaXggdHlwZT0ic2F0dXJhdGUiIHZhbHVlcz0iMCIvPjwvZmlsdGVyPjxwYXRoIGQ9Ik0wIDBoMzAwdjMwMEgweiIgZmlsdGVyPSJ1cmwoI2EpIiBvcGFjaXR5PSIuMDUiLz48L3N2Zz4=')]"></div>
  </div>
</template>

<script setup lang="ts">
// Cyberpunk background with grid, scan lines, and ambient glows
</script>

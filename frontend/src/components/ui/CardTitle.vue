<script setup lang="ts">
import { cn } from '@/lib/utils'
defineProps<{ class?: string }>()
</script>

<template>
  <h3 :class="cn('font-semibold leading-none tracking-tight text-[hsl(var(--foreground))]', $props.class)">
    <slot />
  </h3>
</template>

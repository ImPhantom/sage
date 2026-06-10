<script setup lang="ts">
import { cn } from '@/lib/utils'
defineProps<{ class?: string }>()
</script>

<template>
  <div :class="cn('rounded-xl border bg-[hsl(var(--card))] text-[hsl(var(--card-foreground))] shadow', $props.class)">
    <slot />
  </div>
</template>

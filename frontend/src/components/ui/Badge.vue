<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = defineProps<{
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success'
  class?: string
}>()

const variantClasses: Record<NonNullable<typeof props.variant>, string> = {
  default: 'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:bg-[hsl(var(--primary))]/80',
  secondary: 'bg-[hsl(var(--secondary))] text-[hsl(var(--secondary-foreground))] hover:bg-[hsl(var(--secondary))]/80',
  destructive: 'bg-[hsl(var(--destructive))] text-[hsl(var(--destructive-foreground))] hover:bg-[hsl(var(--destructive))]/80',
  outline: 'border text-[hsl(var(--foreground))]',
  success: 'bg-emerald-600 text-white hover:bg-emerald-500',
}
</script>

<template>
  <span
    :class="cn(
      'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
      variantClasses[props.variant ?? 'default'],
      props.class,
    )"
  >
    <slot />
  </span>
</template>

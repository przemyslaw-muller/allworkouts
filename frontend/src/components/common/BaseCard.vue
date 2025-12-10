<script setup lang="ts">
interface Props {
  padding?: boolean
  hover?: boolean
}

withDefaults(defineProps<Props>(), {
  padding: true,
  hover: false,
})
</script>

<template>
  <div :class="['card', padding ? 'p-4 sm:p-6' : '', hover ? 'card-hover' : '']">
    <slot />
  </div>
</template>

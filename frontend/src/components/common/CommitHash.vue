<script setup lang="ts">
declare const __COMMIT_HASH__: string

const commitHash = __COMMIT_HASH__
</script>

<template>
  <div class="fixed bottom-2 left-2 text-xs text-gray-400 select-none z-10">
    {{ commitHash }}
  </div>
</template>

/**
 * Main application entry point.
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/main.css'

// Create Vue application
const app = createApp(App)

// Create Pinia store
const pinia = createPinia()

// Install plugins
app.use(pinia)
app.use(router)

// Mount application
app.mount('#app')

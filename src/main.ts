import { createApp } from 'vue'
import App from './App.vue'
import { syncDocumentLanguage } from './i18n'
import './style.css'
import './fieldbook.css'

syncDocumentLanguage()
createApp(App).mount('#app')

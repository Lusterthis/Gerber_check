import { createApp } from 'vue'
import { createPinia } from 'pinia'

// 引入Element Plus
import ElementPlus from 'element-plus'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus) // 使用Element Plus
app.mount('#app')

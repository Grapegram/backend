# WebSocket API Guide для Frontend-разработчиков

## Содержание

1. [Обзор](#обзор)
2. [Подключение к WebSocket](#подключение-к-websocket)
3. [Авторизация](#авторизация)
4. [Формат сообщений](#формат-сообщений)
5. [События чата](#события-чата)
6. [События сообщений](#события-сообщений)
7. [Примеры кода](#примеры-кода)
8. [Обработка ошибок](#обработка-ошибок)

---

## Обзор

WebSocket API позволяет получать события в реальном времени для конкретного чата. После установки соединения и авторизации, клиент будет получать все события, происходящие в чате.

**Основные возможности:**
- Получение новых сообщений в реальном времени
- Уведомления об изменении сообщений и реакциях
- События управления чатом (добавление/удаление участников, изменение настроек)
- Автоматическая обработка истории событий при подключении

---

## Подключение к WebSocket

### Endpoint

```
ws://your-domain.com/ws/chat/{chat_id}
```

**Параметры:**
- `chat_id` (string) - ID чата, к которому вы хотите подключиться

### Пример подключения

```javascript
const chatId = "01234567-89ab-cdef-0123-456789abcdef";
const wsUrl = `ws://localhost:8000/ws/chat/${chatId}`;
const socket = new WebSocket(wsUrl);
```

---

## Авторизация

После установки соединения **необходимо** выполнить авторизацию, отправив токен доступа.

### Запрос авторизации

Отправьте JSON-сообщение с действием `authorize` и вашим JWT токеном:

```javascript
socket.onopen = () => {
  const authMessage = {
    action: "authorize",
    token: "your-jwt-token-here"
  };
  socket.send(JSON.stringify(authMessage));
};
```

### Ответ на авторизацию

**Успешная авторизация:**
```json
{
  "status": "authorized"
}
```

**Неудачная авторизация:**
```json
{
  "status": "unauthorized"
}
```

⚠️ **Важно:** До успешной авторизации вы не будете получать события из чата.

---

## Формат сообщений

Все события от сервера приходят в следующем формате:

```json
{
  "channel": "chat-{chat_id}",
  "data": {
    // данные события
  }
}
```

### Структура поля `data`

```json
{
  "event_id": "uuid-события",
  "occurred_at": "2025-12-03T10:30:00.000000",
  "event_name": "MessageSent",
  // ... дополнительные поля в зависимости от типа события
}
```

---

## События чата

### ChatCreated
Новый чат создан.

```json
{
  "event_name": "ChatCreated",
  "chat_id": "chat-uuid",
  "title": "Название чата",
  "chat_type": "group",
  "created_by": "user-uuid",
  "created_at": "2025-12-03T10:00:00.000000"
}
```

**Поля:**
- `chat_id` - ID чата
- `title` - Название чата
- `chat_type` - Тип чата (`private`, `group`, `channel`)
- `created_by` - ID пользователя, создавшего чат
- `created_at` - Время создания

---

### ChatTitleChanged
Название чата изменено.

```json
{
  "event_name": "ChatTitleChanged",
  "chat_id": "chat-uuid",
  "old_title": "Старое название",
  "new_title": "Новое название",
  "changed_by": "user-uuid",
  "changed_at": "2025-12-03T10:05:00.000000"
}
```

**Поля:**
- `old_title` - Предыдущее название
- `new_title` - Новое название
- `changed_by` - ID пользователя, изменившего название

---

### MemberAdded
Новый участник добавлен в чат.

```json
{
  "event_name": "MemberAdded",
  "chat_id": "chat-uuid",
  "member_id": "member-uuid",
  "user_id": "user-uuid",
  "role": "member",
  "added_by": "admin-user-uuid",
  "added_at": "2025-12-03T10:10:00.000000"
}
```

**Поля:**
- `member_id` - ID записи участника
- `user_id` - ID пользователя
- `role` - Роль участника (`owner`, `admin`, `member`)
- `added_by` - ID пользователя, добавившего участника

---

### MemberRemoved
Участник удален из чата.

```json
{
  "event_name": "MemberRemoved",
  "chat_id": "chat-uuid",
  "member_id": "member-uuid",
  "user_id": "user-uuid",
  "removed_by": "admin-user-uuid",
  "removed_at": "2025-12-03T10:15:00.000000"
}
```

---

### MemberRoleChanged
Роль участника изменена.

```json
{
  "event_name": "MemberRoleChanged",
  "chat_id": "chat-uuid",
  "member_id": "member-uuid",
  "old_role": "member",
  "new_role": "admin",
  "changed_by": "owner-user-uuid",
  "changed_at": "2025-12-03T10:20:00.000000"
}
```

**Поля:**
- `old_role` - Предыдущая роль
- `new_role` - Новая роль

---

### ChatAvatarChanged
Аватар чата изменен.

```json
{
  "event_name": "ChatAvatarChanged",
  "chat_id": "chat-uuid",
  "old_avatar": "path/to/old/avatar.jpg",
  "new_avatar": "path/to/new/avatar.jpg",
  "changed_by": "user-uuid",
  "changed_at": "2025-12-03T10:25:00.000000"
}
```

**Поля:**
- `old_avatar` - URL старого аватара (может быть `null`)
- `new_avatar` - URL нового аватара (может быть `null`)

---

### ChatArchived / ChatUnarchived
Чат архивирован или разархивирован.

```json
{
  "event_name": "ChatArchived",
  "chat_id": "chat-uuid",
  "archived_by": "user-uuid",
  "archived_at": "2025-12-03T10:30:00.000000"
}
```

---

### ChatDeleted
Чат удален.

```json
{
  "event_name": "ChatDeleted",
  "chat_id": "chat-uuid",
  "deleted_by": "user-uuid",
  "deleted_at": "2025-12-03T10:35:00.000000"
}
```

---

## События сообщений

### MessageSent
Новое сообщение отправлено.

```json
{
  "event_name": "MessageSent",
  "message_id": "message-uuid",
  "chat_id": "chat-uuid",
  "sender_id": "user-uuid",
  "text": "Текст сообщения",
  "images": [
    "https://storage.example.com/image1.jpg",
    "https://storage.example.com/image2.jpg"
  ],
  "sent_at": "2025-12-03T10:40:00.000000"
}
```

**Поля:**
- `message_id` - ID сообщения
- `sender_id` - ID отправителя
- `text` - Текст сообщения
- `images` - Массив URL изображений (может быть пустым)
- `sent_at` - Время отправки

⚠️ **Важно:** Поле `images` содержит готовые URL для отображения, включая подписанные ссылки для приватных хранилищ.

---

### MessageEdited
Сообщение отредактировано.

```json
{
  "event_name": "MessageEdited",
  "message_id": "message-uuid",
  "chat_id": "chat-uuid",
  "old_text": "Старый текст",
  "new_text": "Новый текст",
  "edited_by": "user-uuid",
  "edited_at": "2025-12-03T10:45:00.000000"
}
```

**Поля:**
- `old_text` - Предыдущий текст сообщения
- `new_text` - Новый текст сообщения
- `edited_by` - ID пользователя, отредактировавшего сообщение

---

### MessageDeleted
Сообщение удалено.

```json
{
  "event_name": "MessageDeleted",
  "message_id": "message-uuid",
  "chat_id": "chat-uuid",
  "deleted_by": "user-uuid",
  "deleted_at": "2025-12-03T10:50:00.000000"
}
```

---

### MessageReactionAdded
Реакция добавлена к сообщению.

```json
{
  "event_name": "MessageReactionAdded",
  "message_id": "message-uuid",
  "chat_id": "chat-uuid",
  "user_id": "user-uuid",
  "reaction": "👍",
  "added_at": "2025-12-03T10:55:00.000000"
}
```

**Поля:**
- `user_id` - ID пользователя, добавившего реакцию
- `reaction` - Эмодзи реакции

---

### MessageReactionRemoved
Реакция удалена с сообщения.

```json
{
  "event_name": "MessageReactionRemoved",
  "message_id": "message-uuid",
  "chat_id": "chat-uuid",
  "user_id": "user-uuid",
  "reaction": "👍",
  "removed_at": "2025-12-03T11:00:00.000000"
}
```

---

### MessageRead
Сообщение прочитано пользователем.

```json
{
  "event_name": "MessageRead",
  "message_id": "message-uuid",
  "chat_id": "chat-uuid",
  "user_id": "user-uuid",
  "read_at": "2025-12-03T11:05:00.000000"
}
```

**Поля:**
- `user_id` - ID пользователя, прочитавшего сообщение
- `read_at` - Время прочтения

---

## Примеры кода

### Полный пример на JavaScript

```javascript
class ChatWebSocket {
  constructor(chatId, token) {
    this.chatId = chatId;
    this.token = token;
    this.socket = null;
    this.isAuthorized = false;
    this.eventHandlers = new Map();
  }

  connect() {
    const wsUrl = `ws://localhost:8000/ws/chat/${this.chatId}`;
    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.authorize();
    };

    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.isAuthorized = false;
      // Попытка переподключения через 3 секунды
      setTimeout(() => this.connect(), 3000);
    };
  }

  authorize() {
    const authMessage = {
      action: "authorize",
      token: this.token
    };
    this.socket.send(JSON.stringify(authMessage));
  }

  handleMessage(message) {
    // Проверка статуса авторизации
    if (message.status === "authorized") {
      this.isAuthorized = true;
      console.log('Successfully authorized');
      return;
    }

    if (message.status === "unauthorized") {
      console.error('Authorization failed');
      return;
    }

    // Обработка событий
    if (message.data && message.data.event_name) {
      const eventName = message.data.event_name;
      const handlers = this.eventHandlers.get(eventName) || [];
      
      handlers.forEach(handler => {
        try {
          handler(message.data);
        } catch (error) {
          console.error(`Error handling ${eventName}:`, error);
        }
      });
    }
  }

  on(eventName, handler) {
    if (!this.eventHandlers.has(eventName)) {
      this.eventHandlers.set(eventName, []);
    }
    this.eventHandlers.get(eventName).push(handler);
  }

  off(eventName, handler) {
    if (!this.eventHandlers.has(eventName)) return;
    
    const handlers = this.eventHandlers.get(eventName);
    const index = handlers.indexOf(handler);
    if (index > -1) {
      handlers.splice(index, 1);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
    }
  }
}

// Использование
const chatWs = new ChatWebSocket('chat-uuid-here', 'your-jwt-token');

// Подписка на события
chatWs.on('MessageSent', (data) => {
  console.log('New message:', data);
  // Добавить сообщение в UI
  addMessageToUI(data);
});

chatWs.on('MessageEdited', (data) => {
  console.log('Message edited:', data);
  // Обновить сообщение в UI
  updateMessageInUI(data.message_id, data.new_text);
});

chatWs.on('MessageReactionAdded', (data) => {
  console.log('Reaction added:', data);
  // Обновить реакции в UI
  addReactionToUI(data.message_id, data.reaction, data.user_id);
});

chatWs.on('MemberAdded', (data) => {
  console.log('Member added:', data);
  // Обновить список участников
  addMemberToList(data.user_id);
});

// Подключение
chatWs.connect();
```

---

### Пример на TypeScript с типами

```typescript
interface WebSocketMessage {
  channel: string;
  data: EventData;
}

interface EventData {
  event_id: string;
  event_name: string;
  occurred_at: string;
  [key: string]: any;
}

interface MessageSentEvent extends EventData {
  event_name: 'MessageSent';
  message_id: string;
  chat_id: string;
  sender_id: string;
  text: string;
  images: string[];
  sent_at: string;
}

interface MessageEditedEvent extends EventData {
  event_name: 'MessageEdited';
  message_id: string;
  chat_id: string;
  old_text: string;
  new_text: string;
  edited_by: string;
  edited_at: string;
}

type ChatEvent = MessageSentEvent | MessageEditedEvent; // ... добавить другие типы

class TypedChatWebSocket {
  private socket: WebSocket | null = null;
  private eventHandlers = new Map<string, Array<(data: any) => void>>();
  
  constructor(
    private chatId: string,
    private token: string
  ) {}

  connect(): void {
    const wsUrl = `ws://localhost:8000/ws/chat/${this.chatId}`;
    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => this.authorize();
    this.socket.onmessage = (event) => {
      const message: WebSocketMessage = JSON.parse(event.data);
      this.handleMessage(message);
    };
  }

  private authorize(): void {
    this.socket?.send(JSON.stringify({
      action: "authorize",
      token: this.token
    }));
  }

  private handleMessage(message: WebSocketMessage): void {
    if ('status' in message) {
      console.log('Auth status:', message.status);
      return;
    }

    const eventName = message.data.event_name;
    const handlers = this.eventHandlers.get(eventName) || [];
    handlers.forEach(handler => handler(message.data));
  }

  on<T extends EventData>(
    eventName: string,
    handler: (data: T) => void
  ): void {
    if (!this.eventHandlers.has(eventName)) {
      this.eventHandlers.set(eventName, []);
    }
    this.eventHandlers.get(eventName)!.push(handler);
  }
}
```

---

### Пример с React Hook

```typescript
import { useEffect, useRef, useState } from 'react';

interface UseWebSocketOptions {
  chatId: string;
  token: string;
  onMessage?: (data: any) => void;
  autoReconnect?: boolean;
}

export const useWebSocket = ({
  chatId,
  token,
  onMessage,
  autoReconnect = true
}: UseWebSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isAuthorized, setIsAuthorized] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = () => {
    const wsUrl = `ws://localhost:8000/ws/chat/${chatId}`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      setIsConnected(true);
      // Авторизация
      socket.send(JSON.stringify({
        action: "authorize",
        token: token
      }));
    };

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.status === "authorized") {
        setIsAuthorized(true);
      } else if (message.status === "unauthorized") {
        setIsAuthorized(false);
      } else if (onMessage) {
        onMessage(message.data);
      }
    };

    socket.onclose = () => {
      setIsConnected(false);
      setIsAuthorized(false);
      
      if (autoReconnect) {
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      }
    };

    socketRef.current = socket;
  };

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [chatId, token]);

  return {
    isConnected,
    isAuthorized,
    socket: socketRef.current
  };
};

// Использование в компоненте
function ChatComponent({ chatId, token }) {
  const { isConnected, isAuthorized } = useWebSocket({
    chatId,
    token,
    onMessage: (data) => {
      console.log('Received event:', data);
      
      switch (data.event_name) {
        case 'MessageSent':
          // Обработка нового сообщения
          break;
        case 'MessageEdited':
          // Обработка редактирования
          break;
        // ... другие события
      }
    }
  });

  return (
    <div>
      <p>Connected: {isConnected ? 'Yes' : 'No'}</p>
      <p>Authorized: {isAuthorized ? 'Yes' : 'No'}</p>
    </div>
  );
}
```

---

## Обработка ошибок

### Типичные проблемы и решения

#### 1. Соединение не устанавливается

**Причины:**
- Неверный URL
- Неверный `chat_id`
- Проблемы с сетью

**Решение:**
```javascript
socket.onerror = (error) => {
  console.error('WebSocket error:', error);
  // Показать уведомление пользователю
  showNotification('Connection error. Please try again.');
};
```

#### 2. Авторизация не проходит

**Причины:**
- Истёкший токен
- Неверный токен
- Пользователь не имеет доступа к чату

**Решение:**
```javascript
socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.status === "unauthorized") {
    // Обновить токен и повторить авторизацию
    refreshToken().then(newToken => {
      socket.send(JSON.stringify({
        action: "authorize",
        token: newToken
      }));
    });
  }
};
```

#### 3. Разрыв соединения

**Решение с экспоненциальной задержкой:**
```javascript
class ReconnectingWebSocket {
  constructor(chatId, token) {
    this.chatId = chatId;
    this.token = token;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
  }

  connect() {
    const wsUrl = `ws://localhost:8000/ws/chat/${this.chatId}`;
    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      this.reconnectAttempts = 0; // Сброс счётчика при успешном подключении
      this.authorize();
    };

    this.socket.onclose = () => {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
        this.reconnectAttempts++;
        
        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        
        setTimeout(() => {
          this.connect();
        }, delay);
      } else {
        console.error('Max reconnect attempts reached');
        // Показать уведомление пользователю
      }
    };
  }
}
```

#### 4. Обработка некорректных данных

```javascript
socket.onmessage = (event) => {
  try {
    const message = JSON.parse(event.data);
    
    // Валидация структуры сообщения
    if (!message.data || !message.data.event_name) {
      console.warn('Invalid message format:', message);
      return;
    }
    
    this.handleMessage(message);
  } catch (error) {
    console.error('Error parsing message:', error);
  }
};
```

---

## Best Practices

### 1. Управление жизненным циклом

```javascript
// В React компонентах
useEffect(() => {
  const ws = new ChatWebSocket(chatId, token);
  ws.connect();

  return () => {
    ws.disconnect(); // Cleanup при размонтировании
  };
}, [chatId, token]);
```

### 2. Дедупликация событий

Если событие может приходить несколько раз (например, при переподключении), используйте `event_id` для дедупликации:

```javascript
const processedEventIds = new Set();

function handleEvent(event) {
  if (processedEventIds.has(event.event_id)) {
    return; // Событие уже обработано
  }
  
  processedEventIds.add(event.event_id);
  
  // Обработка события
  processEvent(event);
  
  // Очистка старых ID (опционально)
  if (processedEventIds.size > 1000) {
    const oldestIds = Array.from(processedEventIds).slice(0, 500);
    oldestIds.forEach(id => processedEventIds.delete(id));
  }
}
```

### 3. Обновление токена

```javascript
class ChatWebSocket {
  updateToken(newToken) {
    this.token = newToken;
    
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      // Повторная авторизация с новым токеном
      this.authorize();
    }
  }
}
```

### 4. Heartbeat (опционально)

Для обнаружения "мёртвых" соединений:

```javascript
class ChatWebSocket {
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        // Отправка ping (если поддерживается сервером)
        // или просто проверка состояния
        if (!this.lastMessageTime || 
            Date.now() - this.lastMessageTime > 60000) {
          console.warn('No messages for 60s, reconnecting...');
          this.reconnect();
        }
      }
    }, 30000); // Проверка каждые 30 секунд
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
  }
}
```

---

## Тестирование

### Пример с Mock WebSocket

```javascript
// mock-websocket.js
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = WebSocket.CONNECTING;
    
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      this.onopen?.();
    }, 0);
  }

  send(data) {
    console.log('Mock send:', data);
    
    const message = JSON.parse(data);
    if (message.action === 'authorize') {
      setTimeout(() => {
        this.onmessage?.({
          data: JSON.stringify({ status: 'authorized' })
        });
      }, 100);
    }
  }

  close() {
    this.readyState = WebSocket.CLOSED;
    this.onclose?.();
  }

  // Метод для имитации получения события
  simulateEvent(event) {
    this.onmessage?.({
      data: JSON.stringify({
        channel: `chat-${event.chat_id}`,
        data: event
      })
    });
  }
}

// Использование в тестах
const mockWs = new MockWebSocket('ws://test');
mockWs.simulateEvent({
  event_name: 'MessageSent',
  message_id: 'test-id',
  // ...
});
```

---

## Дополнительная информация

### Переменные окружения

Для разных окружений используйте соответствующие URL:

```javascript
const WS_URLS = {
  development: 'ws://localhost:8000',
  staging: 'wss://staging.grapegram.com',
  production: 'wss://grapegram.com'
};

const wsUrl = `${WS_URLS[process.env.NODE_ENV]}/ws/chat/${chatId}`;
```

### Безопасность

1. **Всегда используйте WSS (WebSocket Secure) в production**
2. **Не храните токены в localStorage** - используйте безопасные методы хранения
3. **Обновляйте токены до их истечения**
4. **Валидируйте все входящие данные**

---

## Поддержка

Если возникли вопросы или проблемы:

1. Проверьте логи в консоли браузера
2. Проверьте вкладку Network -> WS в DevTools
3. Убедитесь, что токен валиден
4. Проверьте права доступа к чату

При обнаружении багов создайте issue в репозитории с подробным описанием проблемы.

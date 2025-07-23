import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';

// Import slice reducers
import authReducer from './slices/authSlice';
import uiReducer from './slices/uiSlice';
import examReducer from './slices/examSlice';
import practiceReducer from './slices/practiceSlice';
import notificationReducer from './slices/notificationSlice';
import subjectReducer from './slices/subjectSlice';
import analyticsReducer from './slices/analyticsSlice';

// Root reducer
const rootReducer = combineReducers({
  auth: authReducer,
  ui: uiReducer,
  exam: examReducer,
  practice: practiceReducer,
  notifications: notificationReducer,
  subjects: subjectReducer,
  analytics: analyticsReducer,
});

// Persist configuration
const persistConfig = {
  key: 'medhasakthi',
  storage,
  whitelist: ['auth', 'ui'], // Only persist auth and ui state
  blacklist: ['exam', 'practice'], // Don't persist exam/practice state for security
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

// Configure store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export const persistor = persistStore(store);

// Types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

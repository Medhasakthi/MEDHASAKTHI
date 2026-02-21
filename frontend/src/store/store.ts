import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';

// Import slice reducers
import authReducer from './slices/authSlice';

// Root reducer
const rootReducer = combineReducers({
  auth: authReducer,
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

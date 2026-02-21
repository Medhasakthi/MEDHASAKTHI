# MEDHASAKTHI Mobile Admin App

React Native mobile application for MEDHASAKTHI Super Administrators to manage the entire platform on-the-go.

## 📱 Overview

The Mobile Admin App provides comprehensive platform management capabilities for MEDHASAKTHI Super Administrators, enabling them to:

- Monitor platform-wide analytics and performance
- Manage educational institutes and their subscriptions
- Handle support tickets and customer service
- Configure system settings and security
- Track revenue and billing information
- Oversee AI usage and costs

## 🚀 Features

### **📊 Dashboard**
- Real-time platform statistics
- Institute growth metrics
- User engagement analytics
- AI generation statistics
- Revenue tracking
- System health monitoring

### **🏫 Institute Management**
- Institute registration and verification
- Subscription plan management
- User analytics per institute
- Billing and payment tracking
- Performance monitoring
- Compliance oversight

### **📈 Advanced Analytics**
- Platform-wide metrics
- User growth trends
- AI usage statistics
- Revenue insights
- Performance benchmarking
- Custom report generation

### **🎧 Support Management**
- Support ticket dashboard
- Priority-based sorting
- Real-time notifications
- Customer communication
- Knowledge base access
- Performance metrics

### **⚙️ System Settings**
- Platform configuration
- Security settings
- Email configurations
- AI model settings
- Billing configurations
- Maintenance tools

## 🛠️ Technology Stack

### **Core Framework**
- **React Native 0.72** - Cross-platform mobile development
- **TypeScript** - Type safety and better development experience
- **React Navigation 6** - Navigation and routing

### **State Management**
- **Redux Toolkit** - Global state management
- **React Query** - Server state and caching
- **Redux Persist** - State persistence

### **UI/UX**
- **React Native Paper** - Material Design components
- **React Native Vector Icons** - Icon library
- **React Native Linear Gradient** - Gradient backgrounds
- **React Native SVG** - SVG support

### **Charts & Visualization**
- **React Native Chart Kit** - Chart components
- **React Native SVG Charts** - Advanced charting

### **Authentication & Security**
- **React Native Keychain** - Secure storage
- **React Native Biometrics** - Biometric authentication
- **React Native Device Info** - Device information

### **Networking & API**
- **Axios** - HTTP client
- **React Native Network Info** - Network status

### **Notifications & Communication**
- **React Native Push Notification** - Local notifications
- **Firebase Messaging** - Push notifications
- **React Native Toast Message** - Toast notifications

## 🚀 Quick Start

### **Prerequisites**
```bash
# Node.js 16+ and npm/yarn
node --version  # Should be 16+
npm --version   # Should be 8+

# React Native CLI
npm install -g react-native-cli

# For iOS development (macOS only)
# Xcode 12+ and CocoaPods
pod --version

# For Android development
# Android Studio and Android SDK
```

### **Installation**
```bash
# Clone and navigate to mobile admin
cd mobile-admin

# Install dependencies
npm install

# For iOS (macOS only)
cd ios && pod install && cd ..

# For Android - no additional setup needed
```

### **Development**
```bash
# Start Metro bundler
npm start

# Run on iOS (macOS only)
npm run ios

# Run on Android
npm run android

# Or use React Native CLI
npx react-native run-ios
npx react-native run-android
```

## 📱 App Structure

```
mobile-admin/
├── src/
│   ├── components/          # React Native components
│   │   ├── auth/           # Authentication screens
│   │   ├── dashboard/      # Dashboard components
│   │   ├── institutes/     # Institute management
│   │   ├── analytics/      # Analytics screens
│   │   ├── support/        # Support management
│   │   ├── settings/       # Settings screens
│   │   └── common/         # Reusable components
│   ├── contexts/           # React contexts
│   ├── navigation/         # Navigation configuration
│   ├── services/           # API services
│   ├── store/              # Redux store
│   ├── types/              # TypeScript types
│   ├── utils/              # Utility functions
│   └── theme/              # Theme and styling
├── android/                # Android-specific code
├── ios/                    # iOS-specific code
└── package.json
```

## 🎨 Design System

### **Color Palette**
```typescript
Primary: #667eea (Blue)
Secondary: #764ba2 (Purple)
Success: #4caf50 (Green)
Warning: #ff9800 (Orange)
Error: #f44336 (Red)
Info: #2196f3 (Blue)
```

### **Typography**
```typescript
Font Sizes: 10px - 32px
Font Weights: 300 - 700
Line Heights: 1.2 - 1.6
Font Family: System default
```

### **Spacing**
```typescript
xs: 4px, sm: 8px, md: 16px
lg: 24px, xl: 32px, xxl: 48px
```

## 🔐 Authentication

### **Login Features**
- Email/password authentication
- Two-factor authentication (2FA)
- Biometric login (fingerprint/face)
- Remember me functionality
- Secure token storage

### **Security**
- JWT token management
- Automatic token refresh
- Secure keychain storage
- Device registration
- Session management

## 📊 Dashboard Features

### **Real-time Metrics**
- Total institutes and users
- AI questions generated
- Monthly revenue
- Platform uptime

### **Interactive Charts**
- User growth trends
- Institute distribution
- Revenue analytics
- System performance

### **Quick Actions**
- Add new institute
- View support tickets
- System configuration
- Analytics deep dive

## 🏫 Institute Management

### **Institute Overview**
- Registration status
- Subscription details
- User statistics
- Performance metrics

### **Management Actions**
- Verify institutes
- Suspend/activate
- Update subscriptions
- View billing history

## 📈 Analytics Dashboard

### **Platform Analytics**
- User engagement metrics
- Feature usage statistics
- Performance benchmarks
- Growth trends

### **AI Usage Analytics**
- Question generation stats
- Model performance
- Cost analysis
- Success rates

## 🎧 Support System

### **Ticket Management**
- Priority-based sorting
- Status tracking
- Assignment system
- Response templates

### **Communication**
- In-app messaging
- Email integration
- Push notifications
- Escalation workflows

## ⚙️ System Configuration

### **Platform Settings**
- Maintenance mode
- Feature toggles
- Rate limiting
- Security policies

### **AI Configuration**
- Model selection
- Cost management
- Performance tuning
- Usage limits

## 🚀 Build & Deployment

### **Development Build**
```bash
# Debug build for testing
npm run android
npm run ios
```

### **Production Build**
```bash
# Android APK
npm run build:android

# iOS Archive
npm run build:ios
```

### **App Store Deployment**
```bash
# Android Play Store
# Upload APK/AAB to Google Play Console

# iOS App Store
# Upload to App Store Connect via Xcode
```

## 📱 Platform Support

### **iOS**
- iOS 12.0+
- iPhone and iPad support
- Dark mode support
- Accessibility features

### **Android**
- Android 6.0+ (API 23+)
- Phone and tablet support
- Material Design 3
- Adaptive icons

## 🧪 Testing

### **Unit Testing**
```bash
# Run unit tests
npm test

# Watch mode
npm run test:watch
```

### **E2E Testing**
```bash
# Detox E2E tests
npm run e2e:ios
npm run e2e:android
```

## 🔧 Development

### **Code Quality**
```bash
# Linting
npm run lint

# Type checking
npm run type-check

# Formatting
npm run format
```

### **Debugging**
- React Native Debugger
- Flipper integration
- Chrome DevTools
- Native debugging tools

## 📦 Dependencies

### **Core Dependencies**
- React Native 0.72
- React Navigation 6
- Redux Toolkit
- React Query
- TypeScript

### **UI Components**
- React Native Paper
- Vector Icons
- Linear Gradient
- Chart Kit

### **Security & Auth**
- Keychain
- Biometrics
- Device Info
- Network Info

## 🚀 Performance

### **Optimization**
- Code splitting
- Image optimization
- Bundle analysis
- Memory management

### **Monitoring**
- Crash reporting
- Performance metrics
- User analytics
- Error tracking

## 🤝 Contributing

### **Development Workflow**
1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

### **Code Standards**
- TypeScript compliance
- Component reusability
- Performance considerations
- Accessibility standards

## 📞 Support

### **Development Issues**
- Check React Native docs
- Verify device/simulator setup
- Review error logs
- Check network connectivity

### **Common Issues**
1. **Metro bundler errors**: Clear cache and restart
2. **iOS build failures**: Clean and rebuild
3. **Android build issues**: Check SDK versions
4. **Network errors**: Verify API endpoints

## 🎯 Roadmap

### **Phase 1** ✅
- Basic authentication
- Dashboard overview
- Navigation structure
- Theme system

### **Phase 2** 🚧
- Institute management
- Analytics dashboard
- Support system
- Settings configuration

### **Phase 3** 📋
- Real-time notifications
- Advanced analytics
- Offline capabilities
- Performance optimization

---

**🎉 Ready to manage the MEDHASAKTHI platform from anywhere!**

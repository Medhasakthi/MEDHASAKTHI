/**
 * Student Top App Bar Component
 * Layout: Left (Our Logo + Name) | Center (Institute Logo + Name) | Right (Actions)
 */
import React from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  StatusBar,
  SafeAreaView,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { colors, typography, spacing } from '../../theme';

interface StudentTopAppBarProps {
  instituteName?: string;
  instituteLogo?: string;
  onNotificationPress?: () => void;
  onProfilePress?: () => void;
  onMenuPress?: () => void;
  notificationCount?: number;
  showBackButton?: boolean;
  onBackPress?: () => void;
  title?: string;
}

const StudentTopAppBar: React.FC<StudentTopAppBarProps> = ({
  instituteName = 'Demo Institute',
  instituteLogo,
  onNotificationPress,
  onProfilePress,
  onMenuPress,
  notificationCount = 0,
  showBackButton = false,
  onBackPress,
  title,
}) => {
  return (
    <>
      <StatusBar backgroundColor={colors.primary} barStyle="light-content" />
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.container}>
          {/* Left Section - Our Logo and Name */}
          <View style={styles.leftSection}>
            {showBackButton ? (
              <TouchableOpacity
                style={styles.backButton}
                onPress={onBackPress}
                activeOpacity={0.7}
              >
                <Icon name="arrow-back" size={24} color={colors.white} />
              </TouchableOpacity>
            ) : (
              <View style={styles.logoContainer}>
                <View style={styles.ourLogo}>
                  <Image
                    source={require('../../assets/images/medhasakthi.png')}
                    style={styles.logoImage}
                    resizeMode="contain"
                  />
                </View>
                <Text style={styles.ourName}>MEDHASAKTHI</Text>
              </View>
            )}
          </View>

          {/* Center Section - Institute Logo and Name */}
          <View style={styles.centerSection}>
            {title ? (
              <Text style={styles.screenTitle} numberOfLines={1}>
                {title}
              </Text>
            ) : (
              <>
                <View style={styles.instituteLogoContainer}>
                  {instituteLogo ? (
                    <Image
                      source={{ uri: instituteLogo }}
                      style={styles.instituteLogo}
                      resizeMode="contain"
                    />
                  ) : (
                    <View style={styles.defaultInstituteLogo}>
                      <Icon name="school" size={20} color={colors.primary} />
                    </View>
                  )}
                </View>
                <Text style={styles.instituteName} numberOfLines={1}>
                  {instituteName}
                </Text>
              </>
            )}
          </View>

          {/* Right Section - Action Buttons */}
          <View style={styles.rightSection}>
            {/* Notification Button */}
            <TouchableOpacity
              style={styles.actionButton}
              onPress={onNotificationPress}
              activeOpacity={0.7}
            >
              <Icon name="notifications" size={22} color={colors.white} />
              {notificationCount > 0 && (
                <View style={styles.notificationBadge}>
                  <Text style={styles.notificationCount}>
                    {notificationCount > 99 ? '99+' : notificationCount.toString()}
                  </Text>
                </View>
              )}
            </TouchableOpacity>

            {/* Profile/Menu Button */}
            <TouchableOpacity
              style={styles.actionButton}
              onPress={onProfilePress || onMenuPress}
              activeOpacity={0.7}
            >
              <Icon 
                name={onProfilePress ? "account-circle" : "menu"} 
                size={22} 
                color={colors.white} 
              />
            </TouchableOpacity>
          </View>
        </View>
      </SafeAreaView>
    </>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    backgroundColor: colors.primary,
  },
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.primary,
    minHeight: 56,
  },
  leftSection: {
    flex: 1,
    alignItems: 'flex-start',
  },
  logoContainer: {
    alignItems: 'center',
  },
  ourLogo: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 2,
  },
  logoImage: {
    width: 20,
    height: 20,
  },
  ourName: {
    fontSize: typography.sizes.xs,
    fontWeight: typography.weights.bold,
    color: colors.white,
    textAlign: 'center',
  },
  backButton: {
    padding: spacing.xs,
    marginLeft: -spacing.xs,
  },
  centerSection: {
    flex: 2,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.sm,
  },
  screenTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.white,
    textAlign: 'center',
  },
  instituteLogoContainer: {
    marginBottom: spacing.xs,
  },
  instituteLogo: {
    width: 32,
    height: 32,
    borderRadius: 16,
  },
  defaultInstituteLogo: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.white,
    alignItems: 'center',
    justifyContent: 'center',
  },
  instituteName: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.white,
    textAlign: 'center',
    maxWidth: 120,
  },
  rightSection: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
  },
  actionButton: {
    padding: spacing.xs,
    marginLeft: spacing.sm,
    position: 'relative',
  },
  notificationBadge: {
    position: 'absolute',
    top: 2,
    right: 2,
    backgroundColor: colors.error,
    borderRadius: 10,
    minWidth: 18,
    height: 18,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 4,
  },
  notificationCount: {
    fontSize: typography.sizes.xs,
    fontWeight: typography.weights.bold,
    color: colors.white,
    lineHeight: 14,
  },
});

export default StudentTopAppBar;

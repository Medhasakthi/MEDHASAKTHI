/**
 * Student Profile Screen
 */
import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Image,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { colors, typography, spacing } from '../../theme';

interface ProfileOptionProps {
  icon: string;
  title: string;
  subtitle?: string;
  onPress?: () => void;
  showArrow?: boolean;
}

const ProfileOption: React.FC<ProfileOptionProps> = ({
  icon,
  title,
  subtitle,
  onPress,
  showArrow = true,
}) => (
  <TouchableOpacity
    style={styles.profileOption}
    onPress={onPress}
    activeOpacity={0.7}
  >
    <View style={styles.optionLeft}>
      <View style={styles.optionIcon}>
        <Icon name={icon} size={20} color={colors.primary} />
      </View>
      <View style={styles.optionText}>
        <Text style={styles.optionTitle}>{title}</Text>
        {subtitle && <Text style={styles.optionSubtitle}>{subtitle}</Text>}
      </View>
    </View>
    {showArrow && (
      <Icon name="chevron-right" size={20} color={colors.textSecondary} />
    )}
  </TouchableOpacity>
);

const ProfileScreen: React.FC = () => {
  const studentInfo = {
    name: 'John Doe',
    email: 'john.doe@student.edu',
    studentId: 'STU2024001',
    class: 'Grade 12 - Science',
    institute: 'Demo High School',
    joinDate: 'September 2023',
    avatar: null, // URL to avatar image
  };

  const handleOptionPress = (option: string) => {
    console.log(`${option} pressed`);
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Profile Header */}
      <View style={styles.profileHeader}>
        <View style={styles.avatarContainer}>
          {studentInfo.avatar ? (
            <Image source={{ uri: studentInfo.avatar }} style={styles.avatar} />
          ) : (
            <View style={styles.defaultAvatar}>
              <Icon name="person" size={40} color={colors.white} />
            </View>
          )}
          <TouchableOpacity 
            style={styles.editAvatarButton}
            onPress={() => handleOptionPress('edit-avatar')}
          >
            <Icon name="camera-alt" size={16} color={colors.white} />
          </TouchableOpacity>
        </View>
        
        <Text style={styles.studentName}>{studentInfo.name}</Text>
        <Text style={styles.studentEmail}>{studentInfo.email}</Text>
        <Text style={styles.studentId}>ID: {studentInfo.studentId}</Text>
      </View>

      {/* Student Details */}
      <View style={styles.detailsSection}>
        <Text style={styles.sectionTitle}>Student Information</Text>
        <View style={styles.detailsCard}>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Class</Text>
            <Text style={styles.detailValue}>{studentInfo.class}</Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Institute</Text>
            <Text style={styles.detailValue}>{studentInfo.institute}</Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Joined</Text>
            <Text style={styles.detailValue}>{studentInfo.joinDate}</Text>
          </View>
        </View>
      </View>

      {/* Profile Options */}
      <View style={styles.optionsSection}>
        <Text style={styles.sectionTitle}>Account Settings</Text>
        <View style={styles.optionsCard}>
          <ProfileOption
            icon="edit"
            title="Edit Profile"
            subtitle="Update your personal information"
            onPress={() => handleOptionPress('edit-profile')}
          />
          <ProfileOption
            icon="lock"
            title="Change Password"
            subtitle="Update your account password"
            onPress={() => handleOptionPress('change-password')}
          />
          <ProfileOption
            icon="notifications"
            title="Notifications"
            subtitle="Manage notification preferences"
            onPress={() => handleOptionPress('notifications')}
          />
          <ProfileOption
            icon="language"
            title="Language"
            subtitle="English"
            onPress={() => handleOptionPress('language')}
          />
        </View>
      </View>

      {/* Academic Options */}
      <View style={styles.optionsSection}>
        <Text style={styles.sectionTitle}>Academic</Text>
        <View style={styles.optionsCard}>
          <ProfileOption
            icon="assessment"
            title="Performance Analytics"
            subtitle="View detailed performance reports"
            onPress={() => handleOptionPress('analytics')}
          />
          <ProfileOption
            icon="schedule"
            title="Study Schedule"
            subtitle="Manage your study timetable"
            onPress={() => handleOptionPress('schedule')}
          />
          <ProfileOption
            icon="bookmark"
            title="Saved Materials"
            subtitle="Access your bookmarked content"
            onPress={() => handleOptionPress('saved-materials')}
          />
        </View>
      </View>

      {/* Support Options */}
      <View style={styles.optionsSection}>
        <Text style={styles.sectionTitle}>Support</Text>
        <View style={styles.optionsCard}>
          <ProfileOption
            icon="help"
            title="Help & FAQ"
            subtitle="Get answers to common questions"
            onPress={() => handleOptionPress('help')}
          />
          <ProfileOption
            icon="feedback"
            title="Send Feedback"
            subtitle="Share your thoughts with us"
            onPress={() => handleOptionPress('feedback')}
          />
          <ProfileOption
            icon="info"
            title="About"
            subtitle="App version and information"
            onPress={() => handleOptionPress('about')}
          />
        </View>
      </View>

      {/* Logout */}
      <View style={styles.logoutSection}>
        <TouchableOpacity
          style={styles.logoutButton}
          onPress={() => handleOptionPress('logout')}
          activeOpacity={0.7}
        >
          <Icon name="logout" size={20} color={colors.error} />
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  profileHeader: {
    backgroundColor: colors.surface,
    alignItems: 'center',
    padding: spacing.xl,
    marginBottom: spacing.md,
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: spacing.md,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
  },
  defaultAvatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  editAvatarButton: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.secondary,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: colors.surface,
  },
  studentName: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  studentEmail: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  studentId: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
    fontWeight: typography.weights.medium,
  },
  detailsSection: {
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  detailsCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    elevation: 2,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  detailLabel: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
  },
  detailValue: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.textPrimary,
  },
  optionsSection: {
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  optionsCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    elevation: 2,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  profileOption: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  optionLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  optionIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: `${colors.primary}20`,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  optionText: {
    flex: 1,
  },
  optionTitle: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  optionSubtitle: {
    fontSize: typography.sizes.xs,
    color: colors.textSecondary,
  },
  logoutSection: {
    padding: spacing.lg,
    marginBottom: spacing.xl,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.error,
  },
  logoutText: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.error,
    marginLeft: spacing.sm,
  },
});

export default ProfileScreen;

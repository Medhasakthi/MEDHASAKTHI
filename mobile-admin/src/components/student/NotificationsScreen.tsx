/**
 * Student Notifications Screen
 */
import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { colors, typography, spacing } from '../../theme';

interface NotificationItemProps {
  id: string;
  title: string;
  message: string;
  time: string;
  type: 'exam' | 'result' | 'announcement' | 'reminder';
  isRead: boolean;
  onPress?: () => void;
}

const NotificationItem: React.FC<NotificationItemProps> = ({
  id,
  title,
  message,
  time,
  type,
  isRead,
  onPress,
}) => {
  const getTypeIcon = () => {
    switch (type) {
      case 'exam':
        return 'quiz';
      case 'result':
        return 'assessment';
      case 'announcement':
        return 'campaign';
      case 'reminder':
        return 'schedule';
      default:
        return 'notifications';
    }
  };

  const getTypeColor = () => {
    switch (type) {
      case 'exam':
        return colors.primary;
      case 'result':
        return colors.success;
      case 'announcement':
        return colors.info;
      case 'reminder':
        return colors.warning;
      default:
        return colors.textSecondary;
    }
  };

  return (
    <TouchableOpacity
      style={[
        styles.notificationItem,
        !isRead && styles.unreadNotification,
      ]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.notificationContent}>
        <View style={[styles.typeIcon, { backgroundColor: getTypeColor() }]}>
          <Icon name={getTypeIcon()} size={20} color={colors.white} />
        </View>
        
        <View style={styles.notificationText}>
          <View style={styles.notificationHeader}>
            <Text style={[
              styles.notificationTitle,
              !isRead && styles.unreadTitle,
            ]}>
              {title}
            </Text>
            {!isRead && <View style={styles.unreadDot} />}
          </View>
          <Text style={styles.notificationMessage} numberOfLines={2}>
            {message}
          </Text>
          <Text style={styles.notificationTime}>{time}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );
};

const NotificationsScreen: React.FC = () => {
  const notifications = [
    {
      id: '1',
      title: 'Mathematics Exam Tomorrow',
      message: 'Your Mathematics final exam is scheduled for tomorrow at 10:00 AM. Please be prepared with your calculator and ID.',
      time: '2 hours ago',
      type: 'exam' as const,
      isRead: false,
    },
    {
      id: '2',
      title: 'Physics Quiz Result Available',
      message: 'Your Physics quiz result has been published. You scored 85% - Great job!',
      time: '5 hours ago',
      type: 'result' as const,
      isRead: false,
    },
    {
      id: '3',
      title: 'Important Announcement',
      message: 'The school will be closed on December 25th for Christmas holiday. All exams scheduled for that day will be rescheduled.',
      time: '1 day ago',
      type: 'announcement' as const,
      isRead: true,
    },
    {
      id: '4',
      title: 'Assignment Reminder',
      message: 'Chemistry assignment is due in 3 days. Make sure to submit it before the deadline.',
      time: '2 days ago',
      type: 'reminder' as const,
      isRead: true,
    },
    {
      id: '5',
      title: 'Biology Test Result',
      message: 'Your Biology test result is now available. Check your performance in the results section.',
      time: '3 days ago',
      type: 'result' as const,
      isRead: true,
    },
  ];

  const unreadCount = notifications.filter(n => !n.isRead).length;

  const handleNotificationPress = (notificationId: string) => {
    console.log(`Notification ${notificationId} pressed`);
  };

  const handleMarkAllRead = () => {
    console.log('Mark all as read');
  };

  const handleClearAll = () => {
    console.log('Clear all notifications');
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.title}>Notifications</Text>
          {unreadCount > 0 && (
            <View style={styles.unreadBadge}>
              <Text style={styles.unreadBadgeText}>{unreadCount}</Text>
            </View>
          )}
        </View>
        
        <View style={styles.headerActions}>
          {unreadCount > 0 && (
            <TouchableOpacity
              style={styles.actionButton}
              onPress={handleMarkAllRead}
            >
              <Text style={styles.actionButtonText}>Mark all read</Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity
            style={styles.actionButton}
            onPress={handleClearAll}
          >
            <Icon name="clear-all" size={20} color={colors.textSecondary} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Notifications List */}
      <ScrollView 
        style={styles.notificationsList}
        showsVerticalScrollIndicator={false}
      >
        {notifications.length > 0 ? (
          notifications.map((notification) => (
            <NotificationItem
              key={notification.id}
              id={notification.id}
              title={notification.title}
              message={notification.message}
              time={notification.time}
              type={notification.type}
              isRead={notification.isRead}
              onPress={() => handleNotificationPress(notification.id)}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Icon name="notifications-none" size={64} color={colors.textSecondary} />
            <Text style={styles.emptyTitle}>No notifications</Text>
            <Text style={styles.emptyMessage}>
              You're all caught up! New notifications will appear here.
            </Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.lg,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  title: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.textPrimary,
    marginRight: spacing.sm,
  },
  unreadBadge: {
    backgroundColor: colors.error,
    borderRadius: 10,
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    minWidth: 20,
    alignItems: 'center',
  },
  unreadBadgeText: {
    fontSize: typography.sizes.xs,
    fontWeight: typography.weights.bold,
    color: colors.white,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  actionButton: {
    padding: spacing.xs,
  },
  actionButtonText: {
    fontSize: typography.sizes.sm,
    color: colors.primary,
    fontWeight: typography.weights.medium,
  },
  notificationsList: {
    flex: 1,
  },
  notificationItem: {
    backgroundColor: colors.surface,
    marginHorizontal: spacing.lg,
    marginVertical: spacing.xs,
    borderRadius: 12,
    elevation: 1,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  unreadNotification: {
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
  },
  notificationContent: {
    flexDirection: 'row',
    padding: spacing.md,
  },
  typeIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  notificationText: {
    flex: 1,
  },
  notificationHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  notificationTitle: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.textPrimary,
    flex: 1,
  },
  unreadTitle: {
    fontWeight: typography.weights.semibold,
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.primary,
    marginLeft: spacing.xs,
  },
  notificationMessage: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.xs,
  },
  notificationTime: {
    fontSize: typography.sizes.xs,
    color: colors.textSecondary,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
    marginTop: spacing.xl * 2,
  },
  emptyTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.textPrimary,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  emptyMessage: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
});

export default NotificationsScreen;

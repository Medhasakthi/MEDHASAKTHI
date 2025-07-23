/**
 * Certificate Viewer Component for Students
 * Allows students to view their certificates and verify others
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  Share,
  Linking
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { colors } from '../../theme/colors';
import { typography } from '../../theme/typography';
import { spacing } from '../../theme/spacing';

// Types
interface Certificate {
  id: string;
  certificateNumber: string;
  verificationCode: string;
  title: string;
  recipientName: string;
  certificateType: string;
  status: string;
  score?: number;
  grade?: string;
  issuedAt: string;
  validUntil?: string;
  pdfUrl?: string;
  thumbnailUrl?: string;
  instituteName?: string;
}

interface CertificateViewerProps {
  studentId?: string;
}

export const CertificateViewer: React.FC<CertificateViewerProps> = ({ studentId }) => {
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(false);
  const [verificationCode, setVerificationCode] = useState('');
  const [verificationResult, setVerificationResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'my-certificates' | 'verify'>('my-certificates');

  useEffect(() => {
    if (activeTab === 'my-certificates') {
      loadMyCertificates();
    }
  }, [activeTab]);

  const loadMyCertificates = async () => {
    setLoading(true);
    try {
      // API call to load student's certificates
      // const response = await api.get(`/certificates?student_id=${studentId}`);
      // setCertificates(response.data.certificates);
      
      // Mock data for now
      const mockCertificates: Certificate[] = [
        {
          id: '1',
          certificateNumber: 'MEDH-20240722-A1B2',
          verificationCode: 'VER123456789',
          title: 'React Development Certification',
          recipientName: 'John Doe',
          certificateType: 'course_completion',
          status: 'issued',
          score: 95,
          grade: 'A+',
          issuedAt: '2024-07-22T10:30:00Z',
          validUntil: '2025-07-22T10:30:00Z',
          instituteName: 'Tech Institute'
        },
        {
          id: '2',
          certificateNumber: 'MEDH-20240721-C3D4',
          verificationCode: 'VER987654321',
          title: 'JavaScript Fundamentals',
          recipientName: 'John Doe',
          certificateType: 'achievement',
          status: 'issued',
          score: 88,
          grade: 'A',
          issuedAt: '2024-07-21T14:15:00Z',
          instituteName: 'Code Academy'
        }
      ];
      
      setCertificates(mockCertificates);
    } catch (error) {
      Alert.alert('Error', 'Failed to load certificates');
    } finally {
      setLoading(false);
    }
  };

  const verifyCertificate = async () => {
    if (!verificationCode.trim()) {
      Alert.alert('Error', 'Please enter a verification code');
      return;
    }

    setLoading(true);
    try {
      // API call to verify certificate
      // const response = await api.post('/certificates/verify', {
      //   verification_code: verificationCode
      // });
      
      // Mock verification result
      const mockResult = {
        is_valid: true,
        certificate: {
          certificateNumber: 'MEDH-20240722-A1B2',
          title: 'React Development Certification',
          recipientName: 'John Doe',
          instituteName: 'Tech Institute',
          issuedAt: '2024-07-22T10:30:00Z',
          status: 'issued'
        },
        verification_details: {
          verified_at: new Date().toISOString()
        }
      };
      
      setVerificationResult(mockResult);
      
      if (mockResult.is_valid) {
        Alert.alert('Success', 'Certificate verified successfully!');
      } else {
        Alert.alert('Invalid', 'Certificate verification failed');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to verify certificate');
    } finally {
      setLoading(false);
    }
  };

  const downloadCertificate = async (certificate: Certificate) => {
    try {
      if (certificate.pdfUrl) {
        await Linking.openURL(certificate.pdfUrl);
      } else {
        Alert.alert('Info', 'Certificate download will be available soon');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to download certificate');
    }
  };

  const shareCertificate = async (certificate: Certificate) => {
    try {
      const shareMessage = `🎓 I've earned a certificate!\n\n` +
        `Certificate: ${certificate.title}\n` +
        `Institution: ${certificate.instituteName}\n` +
        `Certificate Number: ${certificate.certificateNumber}\n` +
        `Verification Code: ${certificate.verificationCode}\n\n` +
        `Verify at: https://medhasakthi.com/verify`;

      await Share.share({
        message: shareMessage,
        title: 'My Certificate Achievement'
      });
    } catch (error) {
      Alert.alert('Error', 'Failed to share certificate');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'issued': return colors.success;
      case 'generated': return colors.primary;
      case 'draft': return colors.gray;
      case 'revoked': return colors.error;
      case 'expired': return colors.warning;
      default: return colors.gray;
    }
  };

  const getCertificateTypeIcon = (type: string) => {
    switch (type) {
      case 'course_completion': return 'school';
      case 'exam_pass': return 'quiz';
      case 'achievement': return 'emoji-events';
      case 'participation': return 'group';
      case 'professional': return 'work';
      case 'skill_verification': return 'verified';
      default: return 'certificate';
    }
  };

  const renderCertificateCard = (certificate: Certificate) => (
    <View key={certificate.id} style={styles.certificateCard}>
      <View style={styles.certificateHeader}>
        <View style={styles.certificateIcon}>
          <Icon 
            name={getCertificateTypeIcon(certificate.certificateType)} 
            size={24} 
            color={colors.primary} 
          />
        </View>
        <View style={styles.certificateInfo}>
          <Text style={styles.certificateTitle}>{certificate.title}</Text>
          <Text style={styles.instituteName}>{certificate.instituteName}</Text>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(certificate.status) }]}>
          <Text style={styles.statusText}>{certificate.status}</Text>
        </View>
      </View>

      <View style={styles.certificateDetails}>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Certificate Number:</Text>
          <Text style={styles.detailValue}>{certificate.certificateNumber}</Text>
        </View>
        
        {certificate.score && (
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Score:</Text>
            <Text style={styles.detailValue}>
              {certificate.score}% {certificate.grade && `(${certificate.grade})`}
            </Text>
          </View>
        )}

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Issued:</Text>
          <Text style={styles.detailValue}>
            {new Date(certificate.issuedAt).toLocaleDateString()}
          </Text>
        </View>

        {certificate.validUntil && (
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Valid Until:</Text>
            <Text style={styles.detailValue}>
              {new Date(certificate.validUntil).toLocaleDateString()}
            </Text>
          </View>
        )}
      </View>

      <View style={styles.certificateActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => downloadCertificate(certificate)}
        >
          <Icon name="download" size={20} color={colors.primary} />
          <Text style={styles.actionText}>Download</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => shareCertificate(certificate)}
        >
          <Icon name="share" size={20} color={colors.primary} />
          <Text style={styles.actionText}>Share</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => {
            setVerificationCode(certificate.verificationCode);
            setActiveTab('verify');
          }}
        >
          <Icon name="verified" size={20} color={colors.primary} />
          <Text style={styles.actionText}>Verify</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderMyCertificates = () => (
    <View style={styles.tabContent}>
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>Loading certificates...</Text>
        </View>
      ) : certificates.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Icon name="school" size={64} color={colors.gray} />
          <Text style={styles.emptyTitle}>No Certificates Yet</Text>
          <Text style={styles.emptyText}>
            Complete courses and exams to earn certificates
          </Text>
        </View>
      ) : (
        <ScrollView showsVerticalScrollIndicator={false}>
          {certificates.map(renderCertificateCard)}
        </ScrollView>
      )}
    </View>
  );

  const renderVerification = () => (
    <View style={styles.tabContent}>
      <View style={styles.verificationContainer}>
        <Text style={styles.verificationTitle}>Verify Certificate</Text>
        <Text style={styles.verificationSubtitle}>
          Enter a verification code to check certificate authenticity
        </Text>

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.verificationInput}
            placeholder="Enter verification code"
            value={verificationCode}
            onChangeText={setVerificationCode}
            autoCapitalize="characters"
          />
          <TouchableOpacity
            style={styles.verifyButton}
            onPress={verifyCertificate}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator size="small" color={colors.white} />
            ) : (
              <Text style={styles.verifyButtonText}>Verify</Text>
            )}
          </TouchableOpacity>
        </View>

        {verificationResult && (
          <View style={[
            styles.verificationResult,
            { backgroundColor: verificationResult.is_valid ? colors.successLight : colors.errorLight }
          ]}>
            <Icon 
              name={verificationResult.is_valid ? "verified" : "error"} 
              size={24} 
              color={verificationResult.is_valid ? colors.success : colors.error} 
            />
            <View style={styles.resultContent}>
              <Text style={[
                styles.resultTitle,
                { color: verificationResult.is_valid ? colors.success : colors.error }
              ]}>
                {verificationResult.is_valid ? 'Certificate Valid' : 'Certificate Invalid'}
              </Text>
              
              {verificationResult.is_valid && verificationResult.certificate && (
                <View style={styles.resultDetails}>
                  <Text style={styles.resultText}>
                    Title: {verificationResult.certificate.title}
                  </Text>
                  <Text style={styles.resultText}>
                    Recipient: {verificationResult.certificate.recipientName}
                  </Text>
                  <Text style={styles.resultText}>
                    Institution: {verificationResult.certificate.instituteName}
                  </Text>
                  <Text style={styles.resultText}>
                    Issued: {new Date(verificationResult.certificate.issuedAt).toLocaleDateString()}
                  </Text>
                </View>
              )}
            </View>
          </View>
        )}
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'my-certificates' && styles.activeTab]}
          onPress={() => setActiveTab('my-certificates')}
        >
          <Icon 
            name="school" 
            size={20} 
            color={activeTab === 'my-certificates' ? colors.primary : colors.gray} 
          />
          <Text style={[
            styles.tabText,
            activeTab === 'my-certificates' && styles.activeTabText
          ]}>
            My Certificates
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, activeTab === 'verify' && styles.activeTab]}
          onPress={() => setActiveTab('verify')}
        >
          <Icon 
            name="verified" 
            size={20} 
            color={activeTab === 'verify' ? colors.primary : colors.gray} 
          />
          <Text style={[
            styles.tabText,
            activeTab === 'verify' && styles.activeTabText
          ]}>
            Verify
          </Text>
        </TouchableOpacity>
      </View>

      {/* Tab Content */}
      {activeTab === 'my-certificates' ? renderMyCertificates() : renderVerification()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: colors.primary,
  },
  tabText: {
    marginLeft: spacing.xs,
    fontSize: typography.sizes.sm,
    color: colors.gray,
  },
  activeTabText: {
    color: colors.primary,
    fontWeight: typography.weights.semibold,
  },
  tabContent: {
    flex: 1,
    padding: spacing.md,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: spacing.sm,
    fontSize: typography.sizes.sm,
    color: colors.gray,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyTitle: {
    marginTop: spacing.md,
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.text,
  },
  emptyText: {
    marginTop: spacing.xs,
    fontSize: typography.sizes.sm,
    color: colors.gray,
    textAlign: 'center',
  },
  certificateCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    elevation: 2,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  certificateHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  certificateIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.sm,
  },
  certificateInfo: {
    flex: 1,
  },
  certificateTitle: {
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.semibold,
    color: colors.text,
  },
  instituteName: {
    fontSize: typography.sizes.sm,
    color: colors.gray,
    marginTop: 2,
  },
  statusBadge: {
    paddingHorizontal: spacing.xs,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: typography.sizes.xs,
    color: colors.white,
    fontWeight: typography.weights.medium,
    textTransform: 'capitalize',
  },
  certificateDetails: {
    marginBottom: spacing.sm,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  detailLabel: {
    fontSize: typography.sizes.sm,
    color: colors.gray,
  },
  detailValue: {
    fontSize: typography.sizes.sm,
    color: colors.text,
    fontWeight: typography.weights.medium,
  },
  certificateActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.sm,
  },
  actionButton: {
    alignItems: 'center',
  },
  actionText: {
    marginTop: 4,
    fontSize: typography.sizes.xs,
    color: colors.primary,
  },
  verificationContainer: {
    flex: 1,
  },
  verificationTitle: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  verificationSubtitle: {
    fontSize: typography.sizes.sm,
    color: colors.gray,
    textAlign: 'center',
    marginBottom: spacing.xl,
  },
  inputContainer: {
    flexDirection: 'row',
    marginBottom: spacing.lg,
  },
  verificationInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    fontSize: typography.sizes.md,
    marginRight: spacing.sm,
  },
  verifyButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    minWidth: 80,
  },
  verifyButtonText: {
    color: colors.white,
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.semibold,
  },
  verificationResult: {
    flexDirection: 'row',
    padding: spacing.md,
    borderRadius: 8,
    alignItems: 'flex-start',
  },
  resultContent: {
    flex: 1,
    marginLeft: spacing.sm,
  },
  resultTitle: {
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.semibold,
    marginBottom: spacing.xs,
  },
  resultDetails: {
    marginTop: spacing.xs,
  },
  resultText: {
    fontSize: typography.sizes.sm,
    color: colors.text,
    marginBottom: 2,
  },
});

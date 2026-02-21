/**
 * Talent Exam Interface for Students
 * Provides exam taking interface with real-time monitoring and proctoring
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  ActivityIndicator,
  Dimensions,
  BackHandler
} from 'react-native';
import { RadioButton, Checkbox } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { colors } from '../../theme/colors';
import { typography } from '../../theme/typography';
import { spacing } from '../../theme/spacing';

// Types
interface Question {
  id: string;
  questionNumber: number;
  questionText: string;
  questionType: 'single_choice' | 'multiple_choice' | 'numerical';
  options?: string[];
  correctAnswer?: string | string[];
  marks: number;
  negativeMarks?: number;
  subject?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  imageUrl?: string;
}

interface ExamSession {
  id: string;
  examId: string;
  examTitle: string;
  studentName: string;
  duration: number; // in minutes
  totalQuestions: number;
  totalMarks: number;
  startTime: Date;
  endTime: Date;
  currentQuestion: number;
  responses: { [questionId: string]: string | string[] };
  isSubmitted: boolean;
  timeRemaining: number; // in seconds
}

interface ExamInterfaceProps {
  sessionId: string;
  onExamComplete: (responses: any) => void;
  onExamExit: () => void;
}

export const ExamInterface: React.FC<ExamInterfaceProps> = ({
  sessionId,
  onExamComplete,
  onExamExit
}) => {
  const [session, setSession] = useState<ExamSession | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<{ [questionId: string]: string | string[] }>({});
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [showWarningModal, setShowWarningModal] = useState(false);
  const [warningCount, setWarningCount] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(true);
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const proctorRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    loadExamSession();
    setupProctoring();
    
    // Prevent back button
    const backHandler = BackHandler.addEventListener('hardwareBackPress', () => {
      handleExitWarning();
      return true;
    });

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (proctorRef.current) clearInterval(proctorRef.current);
      backHandler.remove();
    };
  }, []);

  useEffect(() => {
    if (session && !session.isSubmitted) {
      startTimer();
    }
  }, [session]);

  const loadExamSession = async () => {
    try {
      // API call to load exam session
      // const response = await api.get(`/talent-exams/sessions/${sessionId}`);
      
      // Mock data for now
      const mockSession: ExamSession = {
        id: sessionId,
        examId: 'exam1',
        examTitle: 'Annual Talent Exam Class 10',
        studentName: 'John Doe',
        duration: 180,
        totalQuestions: 50,
        totalMarks: 100,
        startTime: new Date(),
        endTime: new Date(Date.now() + 180 * 60 * 1000),
        currentQuestion: 1,
        responses: {},
        isSubmitted: false,
        timeRemaining: 180 * 60 // 3 hours in seconds
      };

      const mockQuestions: Question[] = Array.from({ length: 50 }, (_, i) => ({
        id: `q${i + 1}`,
        questionNumber: i + 1,
        questionText: `This is question ${i + 1}. Choose the correct answer from the options below.`,
        questionType: 'single_choice',
        options: [
          `Option A for question ${i + 1}`,
          `Option B for question ${i + 1}`,
          `Option C for question ${i + 1}`,
          `Option D for question ${i + 1}`
        ],
        correctAnswer: 'A',
        marks: 2,
        negativeMarks: 0.5,
        subject: i < 20 ? 'Mathematics' : i < 35 ? 'Science' : 'English',
        difficulty: i < 15 ? 'easy' : i < 35 ? 'medium' : 'hard'
      }));

      setSession(mockSession);
      setQuestions(mockQuestions);
      setTimeRemaining(mockSession.timeRemaining);
      setResponses(mockSession.responses);
    } catch (error) {
      Alert.alert('Error', 'Failed to load exam session');
    } finally {
      setLoading(false);
    }
  };

  const startTimer = () => {
    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const setupProctoring = () => {
    // Setup proctoring checks
    proctorRef.current = setInterval(() => {
      checkProctoringViolations();
    }, 5000);
  };

  const checkProctoringViolations = () => {
    // Check for app switching, screen recording, etc.
    // This would integrate with native modules for actual proctoring
    
    // Mock violation detection
    const hasViolation = Math.random() < 0.01; // 1% chance for demo
    
    if (hasViolation) {
      setWarningCount(prev => {
        const newCount = prev + 1;
        if (newCount >= 3) {
          handleAutoSubmit('Multiple proctoring violations detected');
        } else {
          setShowWarningModal(true);
        }
        return newCount;
      });
    }
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerChange = (questionId: string, answer: string | string[]) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: answer
    }));
    
    // Auto-save response
    saveResponse(questionId, answer);
  };

  const saveResponse = async (questionId: string, answer: string | string[]) => {
    try {
      // API call to save response
      // await api.post(`/talent-exams/sessions/${sessionId}/responses`, {
      //   questionId,
      //   answer
      // });
    } catch (error) {
      console.error('Failed to save response:', error);
    }
  };

  const navigateToQuestion = (index: number) => {
    if (index >= 0 && index < questions.length) {
      setCurrentQuestionIndex(index);
    }
  };

  const handleSubmitExam = async () => {
    setSubmitting(true);
    try {
      // API call to submit exam
      // const response = await api.post(`/talent-exams/sessions/${sessionId}/submit`, {
      //   responses,
      //   submissionTime: new Date().toISOString()
      // });
      
      if (timerRef.current) clearInterval(timerRef.current);
      if (proctorRef.current) clearInterval(proctorRef.current);
      
      onExamComplete(responses);
    } catch (error) {
      Alert.alert('Error', 'Failed to submit exam. Please try again.');
    } finally {
      setSubmitting(false);
      setShowSubmitModal(false);
    }
  };

  const handleAutoSubmit = (reason: string = 'Time expired') => {
    Alert.alert(
      'Exam Auto-Submitted',
      `Your exam has been automatically submitted. Reason: ${reason}`,
      [{ text: 'OK', onPress: () => handleSubmitExam() }]
    );
  };

  const handleExitWarning = () => {
    Alert.alert(
      'Exit Exam?',
      'Are you sure you want to exit the exam? Your progress will be saved but you may not be able to resume.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Exit', style: 'destructive', onPress: onExamExit }
      ]
    );
  };

  const getQuestionStatus = (index: number): 'answered' | 'marked' | 'unanswered' => {
    const question = questions[index];
    if (responses[question.id]) {
      return 'answered';
    }
    return 'unanswered';
  };

  const getAnsweredCount = (): number => {
    return Object.keys(responses).length;
  };

  const renderQuestion = () => {
    if (!questions[currentQuestionIndex]) return null;
    
    const question = questions[currentQuestionIndex];
    const currentResponse = responses[question.id];

    return (
      <View style={styles.questionContainer}>
        <View style={styles.questionHeader}>
          <Text style={styles.questionNumber}>
            Question {question.questionNumber} of {questions.length}
          </Text>
          <View style={styles.questionMeta}>
            <Text style={styles.marks}>+{question.marks} marks</Text>
            {question.negativeMarks && (
              <Text style={styles.negativeMarks}>-{question.negativeMarks} marks</Text>
            )}
          </View>
        </View>

        <Text style={styles.questionText}>{question.questionText}</Text>

        {question.questionType === 'single_choice' && question.options && (
          <View style={styles.optionsContainer}>
            {question.options.map((option, index) => (
              <TouchableOpacity
                key={index}
                style={[
                  styles.optionItem,
                  currentResponse === String.fromCharCode(65 + index) && styles.selectedOption
                ]}
                onPress={() => handleAnswerChange(question.id, String.fromCharCode(65 + index))}
              >
                <RadioButton
                  value={String.fromCharCode(65 + index)}
                  status={currentResponse === String.fromCharCode(65 + index) ? 'checked' : 'unchecked'}
                  onPress={() => handleAnswerChange(question.id, String.fromCharCode(65 + index))}
                />
                <Text style={styles.optionText}>
                  {String.fromCharCode(65 + index)}. {option}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {question.questionType === 'multiple_choice' && question.options && (
          <View style={styles.optionsContainer}>
            {question.options.map((option, index) => {
              const optionValue = String.fromCharCode(65 + index);
              const isSelected = Array.isArray(currentResponse) && currentResponse.includes(optionValue);
              
              return (
                <TouchableOpacity
                  key={index}
                  style={[styles.optionItem, isSelected && styles.selectedOption]}
                  onPress={() => {
                    const currentArray = Array.isArray(currentResponse) ? currentResponse : [];
                    const newResponse = isSelected
                      ? currentArray.filter(item => item !== optionValue)
                      : [...currentArray, optionValue];
                    handleAnswerChange(question.id, newResponse);
                  }}
                >
                  <Checkbox
                    status={isSelected ? 'checked' : 'unchecked'}
                    onPress={() => {
                      const currentArray = Array.isArray(currentResponse) ? currentResponse : [];
                      const newResponse = isSelected
                        ? currentArray.filter(item => item !== optionValue)
                        : [...currentArray, optionValue];
                      handleAnswerChange(question.id, newResponse);
                    }}
                  />
                  <Text style={styles.optionText}>
                    {optionValue}. {option}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        )}
      </View>
    );
  };

  const renderNavigationPanel = () => (
    <View style={styles.navigationPanel}>
      <Text style={styles.navigationTitle}>Question Navigation</Text>
      <View style={styles.questionGrid}>
        {questions.map((_, index) => (
          <TouchableOpacity
            key={index}
            style={[
              styles.questionButton,
              currentQuestionIndex === index && styles.currentQuestionButton,
              getQuestionStatus(index) === 'answered' && styles.answeredQuestionButton
            ]}
            onPress={() => navigateToQuestion(index)}
          >
            <Text
              style={[
                styles.questionButtonText,
                currentQuestionIndex === index && styles.currentQuestionButtonText,
                getQuestionStatus(index) === 'answered' && styles.answeredQuestionButtonText
              ]}
            >
              {index + 1}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      
      <View style={styles.legendContainer}>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: colors.success }]} />
          <Text style={styles.legendText}>Answered ({getAnsweredCount()})</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: colors.gray }]} />
          <Text style={styles.legendText}>Not Answered ({questions.length - getAnsweredCount()})</Text>
        </View>
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading exam...</Text>
      </View>
    );
  }

  if (!session) {
    return (
      <View style={styles.errorContainer}>
        <Icon name="error" size={64} color={colors.error} />
        <Text style={styles.errorText}>Failed to load exam session</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.examInfo}>
          <Text style={styles.examTitle}>{session.examTitle}</Text>
          <Text style={styles.studentName}>{session.studentName}</Text>
        </View>
        
        <View style={styles.timerContainer}>
          <Icon name="timer" size={20} color={timeRemaining < 300 ? colors.error : colors.primary} />
          <Text style={[
            styles.timerText,
            timeRemaining < 300 && styles.timerWarning
          ]}>
            {formatTime(timeRemaining)}
          </Text>
        </View>
      </View>

      {/* Main Content */}
      <View style={styles.mainContent}>
        <ScrollView style={styles.questionSection}>
          {renderQuestion()}
        </ScrollView>
        
        <View style={styles.sidebar}>
          {renderNavigationPanel()}
        </View>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <TouchableOpacity
          style={styles.navButton}
          onPress={() => navigateToQuestion(currentQuestionIndex - 1)}
          disabled={currentQuestionIndex === 0}
        >
          <Icon name="chevron-left" size={24} color={colors.white} />
          <Text style={styles.navButtonText}>Previous</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.submitButton}
          onPress={() => setShowSubmitModal(true)}
        >
          <Text style={styles.submitButtonText}>Submit Exam</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navButton}
          onPress={() => navigateToQuestion(currentQuestionIndex + 1)}
          disabled={currentQuestionIndex === questions.length - 1}
        >
          <Text style={styles.navButtonText}>Next</Text>
          <Icon name="chevron-right" size={24} color={colors.white} />
        </TouchableOpacity>
      </View>

      {/* Submit Confirmation Modal */}
      <Modal
        visible={showSubmitModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowSubmitModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Submit Exam?</Text>
            <Text style={styles.modalText}>
              You have answered {getAnsweredCount()} out of {questions.length} questions.
              {'\n\n'}
              Once submitted, you cannot make any changes. Are you sure you want to submit?
            </Text>
            
            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={styles.modalCancelButton}
                onPress={() => setShowSubmitModal(false)}
              >
                <Text style={styles.modalCancelText}>Cancel</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={styles.modalSubmitButton}
                onPress={handleSubmitExam}
                disabled={submitting}
              >
                {submitting ? (
                  <ActivityIndicator size="small" color={colors.white} />
                ) : (
                  <Text style={styles.modalSubmitText}>Submit</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Warning Modal */}
      <Modal
        visible={showWarningModal}
        transparent
        animationType="fade"
        onRequestClose={() => setShowWarningModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.warningModalContent}>
            <Icon name="warning" size={48} color={colors.warning} />
            <Text style={styles.warningTitle}>Proctoring Warning</Text>
            <Text style={styles.warningText}>
              Suspicious activity detected. Please ensure you are following exam guidelines.
              {'\n\n'}
              Warning {warningCount} of 3. After 3 warnings, your exam will be auto-submitted.
            </Text>
            
            <TouchableOpacity
              style={styles.warningButton}
              onPress={() => setShowWarningModal(false)}
            >
              <Text style={styles.warningButtonText}>I Understand</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const { width, height } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: typography.sizes.md,
    color: colors.text,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  errorText: {
    marginTop: spacing.md,
    fontSize: typography.sizes.lg,
    color: colors.error,
    textAlign: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: colors.white,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    elevation: 2,
  },
  examInfo: {
    flex: 1,
  },
  examTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.bold,
    color: colors.text,
  },
  studentName: {
    fontSize: typography.sizes.sm,
    color: colors.gray,
  },
  timerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primaryLight,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 8,
  },
  timerText: {
    marginLeft: spacing.xs,
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.bold,
    color: colors.primary,
    fontFamily: 'monospace',
  },
  timerWarning: {
    color: colors.error,
  },
  mainContent: {
    flex: 1,
    flexDirection: 'row',
  },
  questionSection: {
    flex: 2,
    backgroundColor: colors.white,
  },
  sidebar: {
    flex: 1,
    backgroundColor: colors.background,
    borderLeftWidth: 1,
    borderLeftColor: colors.border,
  },
  questionContainer: {
    padding: spacing.lg,
  },
  questionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  questionNumber: {
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.semibold,
    color: colors.primary,
  },
  questionMeta: {
    alignItems: 'flex-end',
  },
  marks: {
    fontSize: typography.sizes.sm,
    color: colors.success,
    fontWeight: typography.weights.medium,
  },
  negativeMarks: {
    fontSize: typography.sizes.xs,
    color: colors.error,
  },
  questionText: {
    fontSize: typography.sizes.md,
    lineHeight: 24,
    color: colors.text,
    marginBottom: spacing.lg,
  },
  optionsContainer: {
    marginTop: spacing.md,
  },
  optionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    backgroundColor: colors.white,
  },
  selectedOption: {
    borderColor: colors.primary,
    backgroundColor: colors.primaryLight,
  },
  optionText: {
    flex: 1,
    marginLeft: spacing.sm,
    fontSize: typography.sizes.md,
    color: colors.text,
  },
  navigationPanel: {
    padding: spacing.md,
  },
  navigationTitle: {
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.semibold,
    color: colors.text,
    marginBottom: spacing.md,
  },
  questionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  questionButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.gray,
    borderRadius: 8,
    marginBottom: spacing.xs,
  },
  currentQuestionButton: {
    backgroundColor: colors.primary,
  },
  answeredQuestionButton: {
    backgroundColor: colors.success,
  },
  questionButtonText: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.white,
  },
  currentQuestionButtonText: {
    color: colors.white,
  },
  answeredQuestionButtonText: {
    color: colors.white,
  },
  legendContainer: {
    marginTop: spacing.lg,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  legendColor: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: spacing.xs,
  },
  legendText: {
    fontSize: typography.sizes.sm,
    color: colors.text,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: colors.white,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    elevation: 2,
  },
  navButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 8,
  },
  navButtonText: {
    color: colors.white,
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
  },
  submitButton: {
    backgroundColor: colors.success,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: 8,
  },
  submitButtonText: {
    color: colors.white,
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.bold,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.lg,
    margin: spacing.lg,
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.bold,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  modalText: {
    fontSize: typography.sizes.md,
    color: colors.text,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: spacing.lg,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  modalCancelButton: {
    flex: 1,
    backgroundColor: colors.gray,
    paddingVertical: spacing.sm,
    borderRadius: 8,
    marginRight: spacing.sm,
  },
  modalCancelText: {
    color: colors.white,
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.medium,
    textAlign: 'center',
  },
  modalSubmitButton: {
    flex: 1,
    backgroundColor: colors.success,
    paddingVertical: spacing.sm,
    borderRadius: 8,
    marginLeft: spacing.sm,
  },
  modalSubmitText: {
    color: colors.white,
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.bold,
    textAlign: 'center',
  },
  warningModalContent: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.lg,
    margin: spacing.lg,
    maxWidth: 350,
    alignItems: 'center',
  },
  warningTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.bold,
    color: colors.warning,
    textAlign: 'center',
    marginTop: spacing.sm,
    marginBottom: spacing.md,
  },
  warningText: {
    fontSize: typography.sizes.md,
    color: colors.text,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: spacing.lg,
  },
  warningButton: {
    backgroundColor: colors.warning,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: 8,
  },
  warningButtonText: {
    color: colors.white,
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.bold,
  },
});

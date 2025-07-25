import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  Slider,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Psychology as AIIcon,
  Quiz as QuizIcon,
  CheckCircle as CheckIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  Lightbulb as LightbulbIcon
} from '@mui/icons-material';

interface Subject {
  id: string;
  name: string;
  gradeLevel: string;
}

interface GeneratedQuestion {
  id: string;
  questionText: string;
  questionType: 'multiple_choice' | 'true_false' | 'short_answer';
  options?: { [key: string]: string };
  correctAnswer: string | boolean;
  explanation: string;
  difficultyLevel: 'easy' | 'medium' | 'hard';
  topic: string;
  learningObjective: string;
  generationMethod: 'ai_openai' | 'template';
  qualityScore?: number;
}

interface GenerationRequest {
  subjectId: string;
  topic: string;
  questionType: 'multiple_choice' | 'true_false' | 'short_answer';
  difficultyLevel: 'easy' | 'medium' | 'hard';
  count: number;
  additionalContext?: string;
}

const AIQuestionGenerator: React.FC = () => {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [generatedQuestions, setGeneratedQuestions] = useState<GeneratedQuestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<GeneratedQuestion | null>(null);
  const [editDialog, setEditDialog] = useState(false);
  const [previewDialog, setPreviewDialog] = useState(false);
  
  const [generationRequest, setGenerationRequest] = useState<GenerationRequest>({
    subjectId: '',
    topic: '',
    questionType: 'multiple_choice',
    difficultyLevel: 'medium',
    count: 5,
    additionalContext: ''
  });

  const [advancedSettings, setAdvancedSettings] = useState({
    useAI: true,
    includeExplanations: true,
    validateQuality: true,
    autoSave: false
  });

  useEffect(() => {
    loadSubjects();
  }, []);

  const loadSubjects = async () => {
    try {
      const response = await fetch('/api/v1/school-subjects', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setSubjects(data);
    } catch (error) {
      // Handle error loading subjects
    }
  };

  const handleGenerateQuestions = async () => {
    if (!generationRequest.subjectId || !generationRequest.topic) {
      return;
    }

    try {
      setLoading(true);
      
      const response = await fetch('/api/v1/ai/generate-questions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(generationRequest)
      });

      if (response.ok) {
        const questions = await response.json();
        setGeneratedQuestions(questions);
      }
    } catch (error) {
      // Handle error generating questions
    } finally {
      setLoading(false);
    }
  };

  const handleSaveQuestion = async (question: GeneratedQuestion) => {
    try {
      const response = await fetch('/api/v1/questions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(question)
      });

      if (response.ok) {
        // Show success message
        // Question saved successfully
      }
    } catch (error) {
      // Handle error saving question
    }
  };

  const handleEditQuestion = (question: GeneratedQuestion) => {
    setSelectedQuestion({ ...question });
    setEditDialog(true);
  };

  const handleUpdateQuestion = () => {
    if (selectedQuestion) {
      const updatedQuestions = generatedQuestions.map(q => 
        q.id === selectedQuestion.id ? selectedQuestion : q
      );
      setGeneratedQuestions(updatedQuestions);
      setEditDialog(false);
      setSelectedQuestion(null);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  const getQualityColor = (score?: number) => {
    if (!score) {
      return 'default';
    }
    if (score >= 80) {
      return 'success';
    }
    if (score >= 60) {
      return 'warning';
    }
    return 'error';
  };

  const QuestionCard: React.FC<{ question: GeneratedQuestion }> = ({ question }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
          <Box flex={1}>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <Chip 
                label={question.questionType.replace('_', ' ')} 
                size="small" 
                color="primary"
              />
              <Chip 
                label={question.difficultyLevel} 
                size="small" 
                color={getDifficultyColor(question.difficultyLevel) as any}
              />
              {question.qualityScore && (
                <Chip 
                  label={`Quality: ${question.qualityScore}%`} 
                  size="small" 
                  color={getQualityColor(question.qualityScore) as any}
                />
              )}
              <Chip 
                label={question.generationMethod === 'ai_openai' ? 'AI Generated' : 'Template'} 
                size="small" 
                variant="outlined"
                icon={question.generationMethod === 'ai_openai' ? <AIIcon /> : <LightbulbIcon />}
              />
            </Box>
            <Typography variant="h6" gutterBottom>
              {question.questionText}
            </Typography>
          </Box>
          <Box display="flex" gap={1}>
            <Tooltip title="Edit Question">
              <IconButton onClick={() => handleEditQuestion(question)} size="small">
                <EditIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Preview">
              <IconButton 
                onClick={() => {
                  setSelectedQuestion(question);
                  setPreviewDialog(true);
                }}
                size="small"
              >
                <QuizIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Save to Question Bank">
              <IconButton onClick={() => handleSaveQuestion(question)} size="small">
                <SaveIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {question.questionType === 'multiple_choice' && question.options && (
          <Box mb={2}>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Options:
            </Typography>
            {Object.entries(question.options).map(([key, value]) => (
              <Typography 
                key={key} 
                variant="body2" 
                sx={{ 
                  ml: 2, 
                  color: key === question.correctAnswer ? 'success.main' : 'text.primary',
                  fontWeight: key === question.correctAnswer ? 'bold' : 'normal'
                }}
              >
                {key}. {value} {key === question.correctAnswer && <CheckIcon fontSize="small" />}
              </Typography>
            ))}
          </Box>
        )}

        {question.questionType === 'true_false' && (
          <Box mb={2}>
            <Typography variant="body2" color="textSecondary">
              Correct Answer: <strong style={{ color: question.correctAnswer ? 'green' : 'red' }}>
                {question.correctAnswer ? 'True' : 'False'}
              </strong>
            </Typography>
          </Box>
        )}

        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="body2">View Details</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" gutterBottom>
              <strong>Topic:</strong> {question.topic}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Learning Objective:</strong> {question.learningObjective}
            </Typography>
            <Typography variant="body2">
              <strong>Explanation:</strong> {question.explanation}
            </Typography>
          </AccordionDetails>
        </Accordion>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        AI Question Generator
      </Typography>

      <Grid container spacing={3}>
        {/* Generation Controls */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Generate Questions
              </Typography>
              
              <FormControl fullWidth margin="normal">
                <InputLabel>Subject</InputLabel>
                <Select
                  value={generationRequest.subjectId}
                  onChange={(e) => setGenerationRequest({ 
                    ...generationRequest, 
                    subjectId: e.target.value 
                  })}
                >
                  {subjects.map((subject) => (
                    <MenuItem key={subject.id} value={subject.id}>
                      {subject.name} ({subject.gradeLevel})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Topic"
                value={generationRequest.topic}
                onChange={(e) => setGenerationRequest({ 
                  ...generationRequest, 
                  topic: e.target.value 
                })}
                margin="normal"
                placeholder="e.g., Photosynthesis, Algebra, World War II"
              />

              <FormControl fullWidth margin="normal">
                <InputLabel>Question Type</InputLabel>
                <Select
                  value={generationRequest.questionType}
                  onChange={(e) => setGenerationRequest({ 
                    ...generationRequest, 
                    questionType: e.target.value as any
                  })}
                >
                  <MenuItem value="multiple_choice">Multiple Choice</MenuItem>
                  <MenuItem value="true_false">True/False</MenuItem>
                  <MenuItem value="short_answer">Short Answer</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth margin="normal">
                <InputLabel>Difficulty Level</InputLabel>
                <Select
                  value={generationRequest.difficultyLevel}
                  onChange={(e) => setGenerationRequest({
                    ...generationRequest,
                    difficultyLevel: e.target.value as 'easy' | 'medium' | 'hard'
                  })}
                >
                  <MenuItem value="easy">Easy</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="hard">Hard</MenuItem>
                </Select>
              </FormControl>

              <Box sx={{ mt: 2, mb: 2 }}>
                <Typography gutterBottom>Number of Questions: {generationRequest.count}</Typography>
                <Slider
                  value={generationRequest.count}
                  onChange={(e, value) => setGenerationRequest({ 
                    ...generationRequest, 
                    count: value as number
                  })}
                  min={1}
                  max={20}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              <TextField
                fullWidth
                label="Additional Context (Optional)"
                value={generationRequest.additionalContext}
                onChange={(e) => setGenerationRequest({ 
                  ...generationRequest, 
                  additionalContext: e.target.value 
                })}
                margin="normal"
                multiline
                rows={3}
                placeholder="Any specific requirements or context for the questions..."
              />

              {/* Advanced Settings */}
              <Accordion sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="body2">Advanced Settings</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={advancedSettings.useAI}
                        onChange={(e) => setAdvancedSettings({
                          ...advancedSettings,
                          useAI: e.target.checked
                        })}
                      />
                    }
                    label="Use AI Generation"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={advancedSettings.includeExplanations}
                        onChange={(e) => setAdvancedSettings({
                          ...advancedSettings,
                          includeExplanations: e.target.checked
                        })}
                      />
                    }
                    label="Include Explanations"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={advancedSettings.validateQuality}
                        onChange={(e) => setAdvancedSettings({
                          ...advancedSettings,
                          validateQuality: e.target.checked
                        })}
                      />
                    }
                    label="Quality Validation"
                  />
                </AccordionDetails>
              </Accordion>

              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleGenerateQuestions}
                disabled={loading || !generationRequest.subjectId || !generationRequest.topic}
                startIcon={loading ? <CircularProgress size={20} /> : <AIIcon />}
                sx={{ mt: 3 }}
              >
                {loading ? 'Generating...' : 'Generate Questions'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Generated Questions */}
        <Grid item xs={12} md={8}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Generated Questions ({generatedQuestions.length})
            </Typography>
            {generatedQuestions.length > 0 && (
              <Button
                startIcon={<RefreshIcon />}
                onClick={handleGenerateQuestions}
                disabled={loading}
              >
                Regenerate
              </Button>
            )}
          </Box>

          {generatedQuestions.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <AIIcon sx={{ fontSize: 60, color: 'grey.400', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No questions generated yet
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Fill in the form on the left and click "Generate Questions" to get started
              </Typography>
            </Paper>
          ) : (
            <Box>
              {generatedQuestions.map((question) => (
                <QuestionCard key={question.id} question={question} />
              ))}
            </Box>
          )}
        </Grid>
      </Grid>

      {/* Edit Question Dialog */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Question</DialogTitle>
        <DialogContent>
          {selectedQuestion && (
            <Box sx={{ pt: 1 }}>
              <TextField
                fullWidth
                label="Question Text"
                value={selectedQuestion.questionText}
                onChange={(e) => setSelectedQuestion({
                  ...selectedQuestion,
                  questionText: e.target.value
                })}
                margin="normal"
                multiline
                rows={3}
              />
              
              {selectedQuestion.questionType === 'multiple_choice' && selectedQuestion.options && (
                <Box mt={2}>
                  <Typography variant="h6" gutterBottom>Options</Typography>
                  {Object.entries(selectedQuestion.options).map(([key, value]) => (
                    <TextField
                      key={key}
                      fullWidth
                      label={`Option ${key}`}
                      value={value}
                      onChange={(e) => setSelectedQuestion({
                        ...selectedQuestion,
                        options: {
                          ...selectedQuestion.options!,
                          [key]: e.target.value
                        }
                      })}
                      margin="normal"
                    />
                  ))}
                </Box>
              )}

              <TextField
                fullWidth
                label="Explanation"
                value={selectedQuestion.explanation}
                onChange={(e) => setSelectedQuestion({
                  ...selectedQuestion,
                  explanation: e.target.value
                })}
                margin="normal"
                multiline
                rows={3}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancel</Button>
          <Button onClick={handleUpdateQuestion} variant="contained">
            Update Question
          </Button>
        </DialogActions>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog open={previewDialog} onClose={() => setPreviewDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Question Preview</DialogTitle>
        <DialogContent>
          {selectedQuestion && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedQuestion.questionText}
              </Typography>
              
              {selectedQuestion.questionType === 'multiple_choice' && selectedQuestion.options && (
                <Box mt={2}>
                  {Object.entries(selectedQuestion.options).map(([key, value]) => (
                    <Typography key={key} variant="body1" sx={{ mb: 1 }}>
                      {key}. {value}
                    </Typography>
                  ))}
                </Box>
              )}
              
              <Alert severity="info" sx={{ mt: 2 }}>
                <strong>Correct Answer:</strong> {selectedQuestion.correctAnswer?.toString()}
              </Alert>
              
              <Alert severity="success" sx={{ mt: 1 }}>
                <strong>Explanation:</strong> {selectedQuestion.explanation}
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AIQuestionGenerator;

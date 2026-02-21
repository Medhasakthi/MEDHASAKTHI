/**
 * AI Question Generator Component
 */
'use client';

import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Alert,
  Chip,
  Grid,
  Paper,
  Divider,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  AutoAwesome,
  ExpandMore,
  Preview,
  Save,
  Refresh,
  Settings,
  Psychology,
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';

import { apiService } from '../../services/api';
import {
  QuestionGenerationRequest,
  QuestionType,
  DifficultyLevel,
  Subject,
  Topic,
  Question,
} from '../../types/question';

// Validation schema
const generationSchema = yup.object({
  subject_id: yup.string().required('Subject is required'),
  topic_id: yup.string().optional(),
  question_type: yup.string().required('Question type is required'),
  difficulty_level: yup.string().required('Difficulty level is required'),
  count: yup.number().min(1).max(50).required('Count is required'),
  grade_level: yup.string().optional(),
  learning_objective: yup.string().optional(),
  context: yup.string().optional(),
});

type GenerationFormData = yup.InferType<typeof generationSchema>;

interface QuestionGeneratorProps {
  onQuestionsGenerated?: (questions: Question[]) => void;
}

export default function QuestionGenerator({ onQuestionsGenerated }: QuestionGeneratorProps) {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState<Question[]>([]);
  const [generationStats, setGenerationStats] = useState<{
    time: number;
    cost: number;
    success_rate: number;
  } | null>(null);

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<GenerationFormData>({
    resolver: yupResolver(generationSchema),
    defaultValues: {
      subject_id: '',
      topic_id: '',
      question_type: QuestionType.MULTIPLE_CHOICE,
      difficulty_level: DifficultyLevel.INTERMEDIATE,
      count: 5,
      grade_level: '',
      learning_objective: '',
      context: '',
    },
  });

  const selectedSubjectId = watch('subject_id');

  // Load subjects on component mount
  useEffect(() => {
    loadSubjects();
  }, []);

  // Load topics when subject changes
  useEffect(() => {
    if (selectedSubjectId) {
      loadTopics(selectedSubjectId);
    } else {
      setTopics([]);
    }
  }, [selectedSubjectId]);

  const loadSubjects = async () => {
    try {
      const data = await apiService.getSubjects();
      setSubjects(data);
    } catch (error) {
      toast.error('Failed to load subjects');
    }
  };

  const loadTopics = async (subjectId: string) => {
    try {
      const data = await apiService.getTopics(subjectId);
      setTopics(data);
    } catch (error) {
      toast.error('Failed to load topics');
    }
  };

  const onSubmit = async (data: GenerationFormData) => {
    try {
      setIsGenerating(true);
      setGeneratedQuestions([]);
      
      const request: QuestionGenerationRequest = {
        subject_id: data.subject_id,
        topic_id: data.topic_id || undefined,
        question_type: data.question_type as QuestionType,
        difficulty_level: data.difficulty_level as DifficultyLevel,
        count: data.count,
        grade_level: data.grade_level || undefined,
        learning_objective: data.learning_objective || undefined,
        context: data.context || undefined,
      };

      const response = await apiService.generateQuestions(request);
      
      if (response.success) {
        setGeneratedQuestions(response.questions);
        setGenerationStats({
          time: response.generation_time,
          cost: response.cost || 0,
          success_rate: (response.questions_generated / data.count) * 100,
        });
        
        toast.success(`Generated ${response.questions_generated} questions successfully!`);
        
        if (onQuestionsGenerated) {
          onQuestionsGenerated(response.questions);
        }
      } else {
        toast.error(response.message);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate questions');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleReset = () => {
    reset();
    setGeneratedQuestions([]);
    setGenerationStats(null);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'success';
      case 'intermediate': return 'warning';
      case 'advanced': return 'error';
      case 'expert': return 'secondary';
      default: return 'default';
    }
  };

  const getQuestionTypeIcon = (type: string) => {
    switch (type) {
      case 'multiple_choice': return '🔘';
      case 'true_false': return '✓✗';
      case 'fill_in_blank': return '___';
      case 'short_answer': return '📝';
      case 'essay': return '📄';
      default: return '❓';
    }
  };

  return (
    <Box>
      <Card>
        <CardHeader
          avatar={<Psychology color="primary" />}
          title="AI Question Generator"
          subheader="Generate high-quality questions using artificial intelligence"
          action={
            <Tooltip title="Advanced Settings">
              <IconButton>
                <Settings />
              </IconButton>
            </Tooltip>
          }
        />
        
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <Grid container spacing={3}>
              {/* Subject Selection */}
              <Grid item xs={12} md={6}>
                <FormControl fullWidth error={!!errors.subject_id}>
                  <InputLabel>Subject</InputLabel>
                  <Controller
                    name="subject_id"
                    control={control}
                    render={({ field }) => (
                      <Select {...field} label="Subject">
                        {subjects.map((subject) => (
                          <MenuItem key={subject.id} value={subject.id}>
                            {subject.name} ({subject.code})
                          </MenuItem>
                        ))}
                      </Select>
                    )}
                  />
                  {errors.subject_id && (
                    <Typography variant="caption" color="error">
                      {errors.subject_id.message}
                    </Typography>
                  )}
                </FormControl>
              </Grid>

              {/* Topic Selection */}
              <Grid item xs={12} md={6}>
                <FormControl fullWidth disabled={!selectedSubjectId}>
                  <InputLabel>Topic (Optional)</InputLabel>
                  <Controller
                    name="topic_id"
                    control={control}
                    render={({ field }) => (
                      <Select {...field} label="Topic (Optional)">
                        <MenuItem value="">All Topics</MenuItem>
                        {topics.map((topic) => (
                          <MenuItem key={topic.id} value={topic.id}>
                            {topic.name}
                          </MenuItem>
                        ))}
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>

              {/* Question Type */}
              <Grid item xs={12} md={4}>
                <FormControl fullWidth error={!!errors.question_type}>
                  <InputLabel>Question Type</InputLabel>
                  <Controller
                    name="question_type"
                    control={control}
                    render={({ field }) => (
                      <Select {...field} label="Question Type">
                        <MenuItem value={QuestionType.MULTIPLE_CHOICE}>
                          🔘 Multiple Choice
                        </MenuItem>
                        <MenuItem value={QuestionType.TRUE_FALSE}>
                          ✓✗ True/False
                        </MenuItem>
                        <MenuItem value={QuestionType.FILL_IN_BLANK}>
                          ___ Fill in Blank
                        </MenuItem>
                        <MenuItem value={QuestionType.SHORT_ANSWER}>
                          📝 Short Answer
                        </MenuItem>
                        <MenuItem value={QuestionType.ESSAY}>
                          📄 Essay
                        </MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>

              {/* Difficulty Level */}
              <Grid item xs={12} md={4}>
                <FormControl fullWidth error={!!errors.difficulty_level}>
                  <InputLabel>Difficulty Level</InputLabel>
                  <Controller
                    name="difficulty_level"
                    control={control}
                    render={({ field }) => (
                      <Select {...field} label="Difficulty Level">
                        <MenuItem value={DifficultyLevel.BEGINNER}>
                          🟢 Beginner
                        </MenuItem>
                        <MenuItem value={DifficultyLevel.INTERMEDIATE}>
                          🟡 Intermediate
                        </MenuItem>
                        <MenuItem value={DifficultyLevel.ADVANCED}>
                          🔴 Advanced
                        </MenuItem>
                        <MenuItem value={DifficultyLevel.EXPERT}>
                          🟣 Expert
                        </MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>

              {/* Count */}
              <Grid item xs={12} md={4}>
                <Controller
                  name="count"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Number of Questions"
                      type="number"
                      inputProps={{ min: 1, max: 50 }}
                      error={!!errors.count}
                      helperText={errors.count?.message}
                    />
                  )}
                />
              </Grid>

              {/* Advanced Options */}
              <Grid item xs={12}>
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="subtitle2">Advanced Options</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={4}>
                        <Controller
                          name="grade_level"
                          control={control}
                          render={({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              label="Grade Level"
                              placeholder="e.g., 10, 12, College"
                            />
                          )}
                        />
                      </Grid>
                      
                      <Grid item xs={12} md={8}>
                        <Controller
                          name="learning_objective"
                          control={control}
                          render={({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              label="Learning Objective"
                              placeholder="e.g., Solve linear equations"
                            />
                          )}
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Controller
                          name="context"
                          control={control}
                          render={({ field }) => (
                            <TextField
                              {...field}
                              fullWidth
                              multiline
                              rows={3}
                              label="Additional Context"
                              placeholder="Provide any additional context for question generation..."
                            />
                          )}
                        />
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              </Grid>

              {/* Action Buttons */}
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button
                    variant="outlined"
                    onClick={handleReset}
                    startIcon={<Refresh />}
                    disabled={isGenerating}
                  >
                    Reset
                  </Button>
                  
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<AutoAwesome />}
                    disabled={isGenerating}
                    sx={{
                      background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                    }}
                  >
                    {isGenerating ? 'Generating...' : 'Generate Questions'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>

          {/* Generation Progress */}
          {isGenerating && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="body2" gutterBottom>
                Generating questions using AI...
              </Typography>
              <LinearProgress />
            </Box>
          )}

          {/* Generation Stats */}
          {generationStats && (
            <Box sx={{ mt: 3 }}>
              <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                <Typography variant="subtitle2" gutterBottom>
                  Generation Statistics
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      Time: {generationStats.time.toFixed(2)}s
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      Success Rate: {generationStats.success_rate.toFixed(1)}%
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      Cost: ${generationStats.cost.toFixed(4)}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Generated Questions Preview */}
      {generatedQuestions.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Generated Questions ({generatedQuestions.length})
          </Typography>
          
          {generatedQuestions.map((question, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ mr: 2 }}>
                    {getQuestionTypeIcon(question.question_type)} Question {index + 1}
                  </Typography>
                  <Chip
                    label={question.difficulty_level}
                    color={getDifficultyColor(question.difficulty_level) as any}
                    size="small"
                  />
                  {question.ai_generated && (
                    <Chip
                      label="AI Generated"
                      color="primary"
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  )}
                </Box>
                
                <Typography variant="body1" paragraph>
                  {question.question_text}
                </Typography>
                
                {question.options && (
                  <Box sx={{ ml: 2, mb: 2 }}>
                    {question.options.map((option, optIndex) => (
                      <Typography
                        key={optIndex}
                        variant="body2"
                        sx={{
                          color: option.is_correct ? 'success.main' : 'text.primary',
                          fontWeight: option.is_correct ? 'bold' : 'normal',
                        }}
                      >
                        {option.id}. {option.text}
                        {option.is_correct && ' ✓'}
                      </Typography>
                    ))}
                  </Box>
                )}
                
                {question.correct_answer && (
                  <Typography variant="body2" color="success.main" sx={{ mb: 1 }}>
                    <strong>Answer:</strong> {question.correct_answer}
                  </Typography>
                )}
                
                {question.explanation && (
                  <Typography variant="body2" color="text.secondary">
                    <strong>Explanation:</strong> {question.explanation}
                  </Typography>
                )}
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );
}

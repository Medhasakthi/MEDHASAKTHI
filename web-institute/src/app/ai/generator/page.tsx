/**
 * AI Question Generator Page
 */
'use client';

import React from 'react';
import { Box, Typography } from '@mui/material';

import DashboardLayout from '../../../components/layout/DashboardLayout';
import QuestionGenerator from '../../../components/ai/QuestionGenerator';
import { withAuth } from '../../../contexts/AuthContext';

function AIGeneratorPage() {
  const handleQuestionsGenerated = (questions: any[]) => {
    console.log('Questions generated:', questions);
    // Handle the generated questions (e.g., save to question bank, show preview, etc.)
  };

  return (
    <DashboardLayout>
      <Box>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            AI Question Generator
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Generate high-quality questions using artificial intelligence. Customize the type, difficulty, and subject to create perfect questions for your exams.
          </Typography>
        </Box>

        <QuestionGenerator onQuestionsGenerated={handleQuestionsGenerated} />
      </Box>
    </DashboardLayout>
  );
}

export default withAuth(AIGeneratorPage);

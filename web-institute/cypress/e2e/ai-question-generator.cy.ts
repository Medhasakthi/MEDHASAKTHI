/**
 * End-to-End tests for AI Question Generator
 */

describe('AI Question Generator', () => {
  beforeEach(() => {
    // Login as admin before each test
    cy.login('admin@demo-school.edu', 'admin123!');
    cy.visit('/ai/generator');
  });

  it('should display the AI question generator interface', () => {
    cy.get('[data-testid="ai-generator-title"]').should('contain', 'AI Question Generator');
    cy.get('[data-testid="subject-select"]').should('be.visible');
    cy.get('[data-testid="question-type-select"]').should('be.visible');
    cy.get('[data-testid="difficulty-select"]').should('be.visible');
    cy.get('[data-testid="generate-button"]').should('be.visible');
  });

  it('should generate multiple choice questions successfully', () => {
    // Select subject
    cy.get('[data-testid="subject-select"]').click();
    cy.get('[data-value="mathematics"]').click();

    // Select topic
    cy.get('[data-testid="topic-select"]').click();
    cy.get('[data-value="algebra"]').click();

    // Select question type
    cy.get('[data-testid="question-type-select"]').click();
    cy.get('[data-value="multiple_choice"]').click();

    // Select difficulty
    cy.get('[data-testid="difficulty-select"]').click();
    cy.get('[data-value="intermediate"]').click();

    // Set question count
    cy.get('[data-testid="question-count-input"]').clear().type('3');

    // Add learning objective
    cy.get('[data-testid="learning-objective-input"]')
      .type('Students should be able to solve quadratic equations');

    // Generate questions
    cy.get('[data-testid="generate-button"]').click();

    // Wait for generation to complete
    cy.get('[data-testid="generation-progress"]', { timeout: 30000 }).should('be.visible');
    cy.get('[data-testid="generation-complete"]', { timeout: 60000 }).should('be.visible');

    // Verify questions were generated
    cy.get('[data-testid="generated-question"]').should('have.length', 3);
    
    // Check first question structure
    cy.get('[data-testid="generated-question"]').first().within(() => {
      cy.get('[data-testid="question-text"]').should('not.be.empty');
      cy.get('[data-testid="question-option"]').should('have.length', 4);
      cy.get('[data-testid="correct-answer"]').should('exist');
      cy.get('[data-testid="explanation"]').should('not.be.empty');
    });
  });

  it('should generate true/false questions successfully', () => {
    // Select subject and topic
    cy.get('[data-testid="subject-select"]').click();
    cy.get('[data-value="science"]').click();
    
    cy.get('[data-testid="topic-select"]').click();
    cy.get('[data-value="physics"]').click();

    // Select true/false question type
    cy.get('[data-testid="question-type-select"]').click();
    cy.get('[data-value="true_false"]').click();

    // Set difficulty and count
    cy.get('[data-testid="difficulty-select"]').click();
    cy.get('[data-value="beginner"]').click();
    
    cy.get('[data-testid="question-count-input"]').clear().type('2');

    // Generate questions
    cy.get('[data-testid="generate-button"]').click();

    // Wait for completion
    cy.get('[data-testid="generation-complete"]', { timeout: 60000 }).should('be.visible');

    // Verify true/false questions
    cy.get('[data-testid="generated-question"]').should('have.length', 2);
    cy.get('[data-testid="generated-question"]').first().within(() => {
      cy.get('[data-testid="question-option"]').should('have.length', 2);
      cy.get('[data-testid="question-option"]').should('contain', 'True');
      cy.get('[data-testid="question-option"]').should('contain', 'False');
    });
  });

  it('should handle advanced options correctly', () => {
    // Expand advanced options
    cy.get('[data-testid="advanced-options-toggle"]').click();
    cy.get('[data-testid="advanced-options-panel"]').should('be.visible');

    // Set advanced options
    cy.get('[data-testid="grade-level-select"]').click();
    cy.get('[data-value="10"]').click();

    cy.get('[data-testid="context-input"]')
      .type('This question is part of the midterm examination covering chapters 1-5');

    cy.get('[data-testid="bloom-taxonomy-select"]').click();
    cy.get('[data-value="application"]').click();

    // Set basic options
    cy.get('[data-testid="subject-select"]').click();
    cy.get('[data-value="mathematics"]').click();

    cy.get('[data-testid="question-type-select"]').click();
    cy.get('[data-value="short_answer"]').click();

    cy.get('[data-testid="difficulty-select"]').click();
    cy.get('[data-value="advanced"]').click();

    cy.get('[data-testid="question-count-input"]').clear().type('1');

    // Generate with advanced options
    cy.get('[data-testid="generate-button"]').click();
    cy.get('[data-testid="generation-complete"]', { timeout: 60000 }).should('be.visible');

    // Verify question was generated with advanced context
    cy.get('[data-testid="generated-question"]').should('have.length', 1);
  });

  it('should show generation progress and statistics', () => {
    // Set up basic generation
    cy.get('[data-testid="subject-select"]').click();
    cy.get('[data-value="english"]').click();

    cy.get('[data-testid="question-type-select"]').click();
    cy.get('[data-value="fill_blank"]').click();

    cy.get('[data-testid="difficulty-select"]').click();
    cy.get('[data-value="intermediate"]').click();

    cy.get('[data-testid="question-count-input"]').clear().type('5');

    // Start generation
    cy.get('[data-testid="generate-button"]').click();

    // Check progress indicators
    cy.get('[data-testid="generation-progress"]').should('be.visible');
    cy.get('[data-testid="progress-bar"]').should('be.visible');
    cy.get('[data-testid="progress-text"]').should('contain', 'Generating');

    // Wait for completion
    cy.get('[data-testid="generation-complete"]', { timeout: 60000 }).should('be.visible');

    // Check statistics
    cy.get('[data-testid="generation-stats"]').should('be.visible');
    cy.get('[data-testid="generation-time"]').should('contain', 'seconds');
    cy.get('[data-testid="success-rate"]').should('contain', '%');
    cy.get('[data-testid="cost-estimate"]').should('contain', '$');
  });

  it('should allow editing generated questions', () => {
    // Generate a question first
    cy.get('[data-testid="subject-select"]').click();
    cy.get('[data-value="mathematics"]').click();

    cy.get('[data-testid="question-type-select"]').click();
    cy.get('[data-value="multiple_choice"]').click();

    cy.get('[data-testid="difficulty-select"]').click();
    cy.get('[data-value="beginner"]').click();

    cy.get('[data-testid="question-count-input"]').clear().type('1');
    cy.get('[data-testid="generate-button"]').click();

    cy.get('[data-testid="generation-complete"]', { timeout: 60000 }).should('be.visible');

    // Edit the generated question
    cy.get('[data-testid="edit-question-button"]').first().click();
    cy.get('[data-testid="question-editor"]').should('be.visible');

    // Modify question text
    cy.get('[data-testid="question-text-editor"]')
      .clear()
      .type('What is the value of x in the equation 2x + 4 = 10?');

    // Modify an option
    cy.get('[data-testid="option-editor"]').first()
      .clear()
      .type('x = 3');

    // Save changes
    cy.get('[data-testid="save-question-button"]').click();

    // Verify changes were saved
    cy.get('[data-testid="question-text"]').should('contain', '2x + 4 = 10');
    cy.get('[data-testid="question-option"]').first().should('contain', 'x = 3');
  });

  it('should save questions to question bank', () => {
    // Generate questions
    cy.get('[data-testid="subject-select"]').click();
    cy.get('[data-value="science"]').click();

    cy.get('[data-testid="question-type-select"]').click();
    cy.get('[data-value="multiple_choice"]').click();

    cy.get('[data-testid="difficulty-select"]').click();
    cy.get('[data-value="intermediate"]').click();

    cy.get('[data-testid="question-count-input"]').clear().type('2');
    cy.get('[data-testid="generate-button"]').click();

    cy.get('[data-testid="generation-complete"]', { timeout: 60000 }).should('be.visible');

    // Select questions to save
    cy.get('[data-testid="question-checkbox"]').first().check();
    cy.get('[data-testid="question-checkbox"]').last().check();

    // Save to question bank
    cy.get('[data-testid="save-to-bank-button"]').click();
    cy.get('[data-testid="save-confirmation"]').should('be.visible');
    cy.get('[data-testid="save-success-message"]').should('contain', 'Questions saved successfully');

    // Verify questions appear in question bank
    cy.visit('/questions');
    cy.get('[data-testid="question-item"]').should('have.length.at.least', 2);
  });

  it('should handle generation errors gracefully', () => {
    // Mock API to return error
    cy.intercept('POST', '/api/v1/ai/generate-questions', {
      statusCode: 500,
      body: { detail: 'AI service temporarily unavailable' }
    }).as('generateError');

    // Attempt to generate questions
    cy.get('[data-testid="subject-select"]').click();
    cy.get('[data-value="mathematics"]').click();

    cy.get('[data-testid="question-type-select"]').click();
    cy.get('[data-value="multiple_choice"]').click();

    cy.get('[data-testid="generate-button"]').click();

    // Wait for error response
    cy.wait('@generateError');

    // Check error handling
    cy.get('[data-testid="error-message"]').should('be.visible');
    cy.get('[data-testid="error-message"]').should('contain', 'AI service temporarily unavailable');
    cy.get('[data-testid="retry-button"]').should('be.visible');
  });

  it('should validate form inputs', () => {
    // Try to generate without selecting required fields
    cy.get('[data-testid="generate-button"]').click();

    // Check validation messages
    cy.get('[data-testid="subject-error"]').should('contain', 'Subject is required');
    cy.get('[data-testid="question-type-error"]').should('contain', 'Question type is required');
    cy.get('[data-testid="difficulty-error"]').should('contain', 'Difficulty is required');

    // Test question count validation
    cy.get('[data-testid="question-count-input"]').clear().type('0');
    cy.get('[data-testid="generate-button"]').click();
    cy.get('[data-testid="count-error"]').should('contain', 'Must be between 1 and 50');

    cy.get('[data-testid="question-count-input"]').clear().type('51');
    cy.get('[data-testid="generate-button"]').click();
    cy.get('[data-testid="count-error"]').should('contain', 'Must be between 1 and 50');
  });

  it('should show cost estimation', () => {
    // Set up generation parameters
    cy.get('[data-testid="subject-select"]').click();
    cy.get('[data-value="mathematics"]').click();

    cy.get('[data-testid="question-type-select"]').click();
    cy.get('[data-value="essay"]').click();

    cy.get('[data-testid="difficulty-select"]').click();
    cy.get('[data-value="expert"]').click();

    cy.get('[data-testid="question-count-input"]').clear().type('10');

    // Check cost estimation appears
    cy.get('[data-testid="cost-estimate"]').should('be.visible');
    cy.get('[data-testid="cost-estimate"]').should('contain', '$');
    cy.get('[data-testid="cost-estimate"]').should('contain', 'Estimated cost');

    // Cost should update when parameters change
    cy.get('[data-testid="question-count-input"]').clear().type('20');
    cy.get('[data-testid="cost-estimate"]').should('not.contain', '$0.00');
  });

  it('should support bulk operations', () => {
    // Generate multiple questions
    cy.get('[data-testid="subject-select"]').click();
    cy.get('[data-value="mathematics"]').click();

    cy.get('[data-testid="question-type-select"]').click();
    cy.get('[data-value="multiple_choice"]').click();

    cy.get('[data-testid="difficulty-select"]').click();
    cy.get('[data-value="intermediate"]').click();

    cy.get('[data-testid="question-count-input"]').clear().type('5');
    cy.get('[data-testid="generate-button"]').click();

    cy.get('[data-testid="generation-complete"]', { timeout: 60000 }).should('be.visible');

    // Select all questions
    cy.get('[data-testid="select-all-checkbox"]').check();
    cy.get('[data-testid="question-checkbox"]').should('be.checked');

    // Test bulk actions
    cy.get('[data-testid="bulk-actions-menu"]').click();
    
    // Test bulk save
    cy.get('[data-testid="bulk-save-action"]').click();
    cy.get('[data-testid="bulk-save-confirmation"]').should('be.visible');

    // Test bulk delete
    cy.get('[data-testid="bulk-actions-menu"]').click();
    cy.get('[data-testid="bulk-delete-action"]').click();
    cy.get('[data-testid="bulk-delete-confirmation"]').should('be.visible');
  });
});

// Custom commands for login
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
    }
  }
}

Cypress.Commands.add('login', (email: string, password: string) => {
  cy.session([email, password], () => {
    cy.visit('/login');
    cy.get('[data-testid="email-input"]').type(email);
    cy.get('[data-testid="password-input"]').type(password);
    cy.get('[data-testid="login-button"]').click();
    cy.url().should('include', '/dashboard');
  });
});

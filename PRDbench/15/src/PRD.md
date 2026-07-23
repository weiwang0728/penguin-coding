### Career Development Assessment and Interview Preparation System PRD

#### 1. Overview
This system is an integrated career development support tool designed to help users with competency diagnosis, interview preparation, and career planning using scientific evaluation methods. Based on the Competency Model and Behavioral Interview theory, it provides features such as question generation, mock interviews, competency assessment, and visual analysis to help users comprehensively improve their career competitiveness.

#### 2. Core Functional Requirements

##### 2.1 Program Startup and Main Menu
- Upon startup, the program displays the main menu, including the following entry points:
  - Career Competency Question Bank Generation
  - Mock Interview and Evaluation
  - Career Development Plan Generation

##### 2.2 Career Competency Question Bank Module
- Supports generating four types of questions: 
  - Single-choice (knowledge understanding)
  - Multiple-choice (competency judgment)
  - True/False (attitude evaluation)
  - Scenario analysis (behavior description)
- Users can customize the number of each question type (1-50 questions) and difficulty levels (Beginner/Intermediate/Advanced)
- Questions must cover six major competency dimensions: Professional Knowledge, Problem Solving, Teamwork, Communication, Learning Ability, and Professionalism
- Each question should have a standard answer, competency dimension tags, and a detailed explanation; scenario questions must include explanations structured according to the STAR method (Situation, Task, Action, Result)
- Support exporting the generated question bank as an Excel file (default filename: generated_question_bank.xlsx), with fields for questions, options, answers, explanations, and competency dimensions

##### 2.3 Mock Interview and Evaluation System
- Provides two interview modes: Structured Interview (preset question bank) and Random Interview (dynamically generated questions)
- Supports a timer feature that displays a countdown in the interface, records the time taken for each question and the total duration
- Users can input answers, and the system automatically scores responses according to predefined criteria (score range: 1-5 points)
- Scoring dimensions must include:
  - Completeness of Answer (20%)
  - Logical Clarity (25%)
  - Professional Depth (30%)
  - Fluency of Expression (25%)
- After the interview, a comprehensive evaluation report is generated, which must include: radar chart of scores for each competency dimension and specific improvement suggestions based on user performance

##### 2.4 Career Development Plan Generator
- Based on Career Anchor Theory, use a 12-question inventory to evaluate users' career anchor types (Technology/Management/Creativity/Autonomy, etc., 8 types)
- Combine competency assessment results to generate a personalized development pathway, including:
  - Top 3 prioritized competencies for improvement
  - Recommended types and sources of learning resources
  - Staged goal-setting (short-term/mid-term/long-term)
- Support exporting the development plan to Markdown format (default filename: career_development_plan.md), which must contain both an action timeline and milestones for competency improvement

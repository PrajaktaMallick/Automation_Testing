import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import styled from 'styled-components';
import { FaCheckCircle, FaTimesCircle, FaClock, FaPlay, FaArrowLeft, FaImage } from 'react-icons/fa';
import { format } from 'date-fns';
import { getTestSession } from '../services/api';

const TestResultsContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
`;

const BackButton = styled(Link)`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #667eea;
  text-decoration: none;
  margin-bottom: 1rem;
  font-weight: 600;

  &:hover {
    text-decoration: underline;
  }
`;

const Header = styled.div`
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
`;

const TestTitle = styled.h1`
  color: #333;
  margin-bottom: 0.5rem;
`;

const TestMeta = styled.div`
  color: #666;
  margin-bottom: 1rem;
`;

const StatusBadge = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  background-color: ${props => {
    switch (props.status) {
      case 'passed': return '#e8f5e8';
      case 'failed': return '#ffeaea';
      case 'running': return '#fff3e0';
      default: return '#f5f5f5';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'passed': return '#4CAF50';
      case 'failed': return '#f44336';
      case 'running': return '#ff9800';
      default: return '#666';
    }
  }};
`;

const Summary = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
`;

const SummaryItem = styled.div`
  text-align: center;
`;

const SummaryNumber = styled.div`
  font-size: 2rem;
  font-weight: bold;
  color: ${props => props.color || '#333'};
`;

const SummaryLabel = styled.div`
  color: #666;
  font-size: 0.9rem;
`;

const StepsContainer = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const StepsHeader = styled.div`
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e0e0e0;
  background: #f8f9fa;
`;

const StepsTitle = styled.h2`
  color: #333;
  margin: 0;
`;

const StepsList = styled.div`
  padding: 1rem;
`;

const StepItem = styled.div`
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 1rem;
  overflow: hidden;
  transition: all 0.2s;

  &:hover {
    border-color: #667eea;
  }
`;

const StepHeader = styled.div`
  padding: 1rem;
  background: ${props => {
    switch (props.status) {
      case 'passed': return '#f8fff8';
      case 'failed': return '#fff8f8';
      case 'running': return '#fffaf0';
      default: return '#f8f9fa';
    }
  }};
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const StepInfo = styled.div`
  flex: 1;
`;

const StepNumber = styled.span`
  background: #667eea;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  margin-right: 1rem;
`;

const StepCommand = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
`;

const StepAction = styled.div`
  color: #666;
  font-size: 0.9rem;
`;

const StepStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: ${props => {
    switch (props.status) {
      case 'passed': return '#4CAF50';
      case 'failed': return '#f44336';
      case 'running': return '#ff9800';
      default: return '#666';
    }
  }};
`;

const StepDetails = styled.div`
  padding: 1rem;
  background: #fafafa;
`;

const StepResult = styled.div`
  margin-bottom: 1rem;
`;

const ResultLabel = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
`;

const ResultValue = styled.div`
  color: #666;
  font-family: monospace;
  background: white;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
`;

const ErrorMessage = styled.div`
  color: #f44336;
  background: #fff5f5;
  padding: 0.75rem;
  border-radius: 4px;
  border-left: 4px solid #f44336;
  margin-bottom: 1rem;
`;

const ScreenshotContainer = styled.div`
  margin-top: 1rem;
`;

const ScreenshotButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;

  &:hover {
    background: #5a6fd8;
  }
`;

const ScreenshotModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
`;

const ScreenshotImage = styled.img`
  max-width: 100%;
  max-height: 100%;
  border-radius: 8px;
`;

function TestResults() {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedScreenshot, setSelectedScreenshot] = useState(null);

  useEffect(() => {
    loadSession();
  }, [sessionId]);

  const loadSession = async () => {
    try {
      const data = await getTestSession(sessionId);
      setSession(data);
    } catch (error) {
      console.error('Failed to load session:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed': return <FaCheckCircle />;
      case 'failed': return <FaTimesCircle />;
      case 'running': return <FaPlay />;
      default: return <FaClock />;
    }
  };

  const openScreenshot = (screenshotPath) => {
    setSelectedScreenshot(screenshotPath);
  };

  const closeScreenshot = () => {
    setSelectedScreenshot(null);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!session) {
    return <div>Test session not found</div>;
  }

  return (
    <TestResultsContainer>
      <BackButton to="/">
        <FaArrowLeft />
        Back to Dashboard
      </BackButton>

      <Header>
        <TestTitle>{session.name}</TestTitle>
        <TestMeta>
          Created: {format(new Date(session.created_at), 'MMM dd, yyyy HH:mm')}
          {session.description && ` • ${session.description}`}
        </TestMeta>
        <StatusBadge status={session.status}>
          {getStatusIcon(session.status)}
          {session.status}
        </StatusBadge>

        <Summary>
          <SummaryItem>
            <SummaryNumber>{session.total_steps}</SummaryNumber>
            <SummaryLabel>Total Steps</SummaryLabel>
          </SummaryItem>
          <SummaryItem>
            <SummaryNumber color="#4CAF50">{session.passed_steps}</SummaryNumber>
            <SummaryLabel>Passed</SummaryLabel>
          </SummaryItem>
          <SummaryItem>
            <SummaryNumber color="#f44336">{session.failed_steps}</SummaryNumber>
            <SummaryLabel>Failed</SummaryLabel>
          </SummaryItem>
        </Summary>
      </Header>

      <StepsContainer>
        <StepsHeader>
          <StepsTitle>Test Steps</StepsTitle>
        </StepsHeader>
        <StepsList>
          {session.steps?.map((step) => (
            <StepItem key={step.id}>
              <StepHeader status={step.status}>
                <StepInfo>
                  <StepCommand>
                    <StepNumber>{step.step_number}</StepNumber>
                    {step.original_command}
                  </StepCommand>
                  {step.translatedAction && (
                    <StepAction>
                      {step.translatedAction.description || `${step.translatedAction.type}: ${step.translatedAction.target}`}
                    </StepAction>
                  )}
                </StepInfo>
                <StepStatus status={step.status}>
                  {getStatusIcon(step.status)}
                  {step.status}
                </StepStatus>
              </StepHeader>
              
              {(step.actual_result || step.error_message || step.screenshot_path) && (
                <StepDetails>
                  {step.actual_result && (
                    <StepResult>
                      <ResultLabel>Result:</ResultLabel>
                      <ResultValue>{step.actual_result}</ResultValue>
                    </StepResult>
                  )}
                  
                  {step.error_message && (
                    <ErrorMessage>{step.error_message}</ErrorMessage>
                  )}
                  
                  {step.screenshot_path && (
                    <ScreenshotContainer>
                      <ScreenshotButton onClick={() => openScreenshot(step.screenshot_path)}>
                        <FaImage />
                        View Screenshot
                      </ScreenshotButton>
                    </ScreenshotContainer>
                  )}
                </StepDetails>
              )}
            </StepItem>
          ))}
        </StepsList>
      </StepsContainer>

      {selectedScreenshot && (
        <ScreenshotModal onClick={closeScreenshot}>
          <ScreenshotImage 
            src={selectedScreenshot} 
            alt="Test step screenshot"
            onClick={(e) => e.stopPropagation()}
          />
        </ScreenshotModal>
      )}
    </TestResultsContainer>
  );
}

export default TestResults;

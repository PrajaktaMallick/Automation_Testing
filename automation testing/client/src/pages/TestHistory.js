import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { FaCheckCircle, FaTimesCircle, FaClock, FaPlay, FaTrash, FaEye } from 'react-icons/fa';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import { getTestSessions, deleteTestSession } from '../services/api';

const HistoryContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
`;

const Header = styled.div`
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  text-align: center;
`;

const Title = styled.h1`
  color: #333;
  margin-bottom: 0.5rem;
`;

const Subtitle = styled.p`
  color: #666;
`;

const TestsContainer = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const TestsHeader = styled.div`
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e0e0e0;
  background: #f8f9fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const TestsTitle = styled.h2`
  color: #333;
  margin: 0;
`;

const TestsCount = styled.span`
  color: #666;
  font-size: 0.9rem;
`;

const TestsList = styled.div`
  padding: 1rem;
`;

const TestItem = styled.div`
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 1rem;
  overflow: hidden;
  transition: all 0.2s;

  &:hover {
    border-color: #667eea;
    transform: translateY(-1px);
  }
`;

const TestHeader = styled.div`
  padding: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const TestInfo = styled.div`
  flex: 1;
`;

const TestName = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
`;

const TestMeta = styled.div`
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
`;

const TestDescription = styled.div`
  color: #888;
  font-size: 0.9rem;
`;

const TestStats = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-right: 1rem;
`;

const StatItem = styled.div`
  text-align: center;
`;

const StatNumber = styled.div`
  font-weight: bold;
  color: ${props => props.color || '#333'};
`;

const StatLabel = styled.div`
  font-size: 0.8rem;
  color: #666;
`;

const StatusBadge = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
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

const Actions = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  
  ${props => {
    switch (props.variant) {
      case 'view':
        return `
          background: #667eea;
          color: white;
          &:hover { background: #5a6fd8; }
        `;
      case 'delete':
        return `
          background: #f44336;
          color: white;
          &:hover { background: #d32f2f; }
        `;
      default:
        return `
          background: #f5f5f5;
          color: #333;
          &:hover { background: #e0e0e0; }
        `;
    }
  }}
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 3rem;
  color: #666;
`;

const EmptyTitle = styled.h3`
  margin-bottom: 1rem;
  color: #333;
`;

const CreateTestLink = styled(Link)`
  color: #667eea;
  text-decoration: none;
  font-weight: 600;

  &:hover {
    text-decoration: underline;
  }
`;

function TestHistory() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await getTestSessions();
      setSessions(data);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (sessionId, sessionName) => {
    if (window.confirm(`Are you sure you want to delete "${sessionName}"?`)) {
      try {
        await deleteTestSession(sessionId);
        toast.success('Test deleted successfully');
        setSessions(prev => prev.filter(s => s.id !== sessionId));
      } catch (error) {
        console.error('Failed to delete session:', error);
      }
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

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <HistoryContainer>
      <Header>
        <Title>Test History</Title>
        <Subtitle>View and manage all your test sessions</Subtitle>
      </Header>

      <TestsContainer>
        <TestsHeader>
          <TestsTitle>All Tests</TestsTitle>
          <TestsCount>{sessions.length} test{sessions.length !== 1 ? 's' : ''}</TestsCount>
        </TestsHeader>
        
        <TestsList>
          {sessions.length === 0 ? (
            <EmptyState>
              <EmptyTitle>No tests yet</EmptyTitle>
              <p>
                <CreateTestLink to="/create">Create your first test</CreateTestLink> to get started
              </p>
            </EmptyState>
          ) : (
            sessions.map(session => (
              <TestItem key={session.id}>
                <TestHeader>
                  <TestInfo>
                    <TestName>{session.name}</TestName>
                    <TestMeta>
                      {format(new Date(session.created_at), 'MMM dd, yyyy HH:mm')}
                      {session.updated_at !== session.created_at && (
                        <> • Updated {format(new Date(session.updated_at), 'MMM dd, yyyy HH:mm')}</>
                      )}
                    </TestMeta>
                    {session.description && (
                      <TestDescription>{session.description}</TestDescription>
                    )}
                  </TestInfo>
                  
                  <TestStats>
                    <StatItem>
                      <StatNumber>{session.total_steps}</StatNumber>
                      <StatLabel>Total</StatLabel>
                    </StatItem>
                    <StatItem>
                      <StatNumber color="#4CAF50">{session.passed_steps}</StatNumber>
                      <StatLabel>Passed</StatLabel>
                    </StatItem>
                    <StatItem>
                      <StatNumber color="#f44336">{session.failed_steps}</StatNumber>
                      <StatLabel>Failed</StatLabel>
                    </StatItem>
                  </TestStats>

                  <StatusBadge status={session.status}>
                    {getStatusIcon(session.status)}
                    {session.status}
                  </StatusBadge>

                  <Actions>
                    <ActionButton 
                      variant="view"
                      as={Link}
                      to={`/test/${session.id}`}
                    >
                      <FaEye />
                      View
                    </ActionButton>
                    <ActionButton 
                      variant="delete"
                      onClick={() => handleDelete(session.id, session.name)}
                    >
                      <FaTrash />
                      Delete
                    </ActionButton>
                  </Actions>
                </TestHeader>
              </TestItem>
            ))
          )}
        </TestsList>
      </TestsContainer>
    </HistoryContainer>
  );
}

export default TestHistory;

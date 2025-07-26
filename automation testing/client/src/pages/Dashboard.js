import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { FaPlus, FaPlay, FaClock, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';
import { format } from 'date-fns';
import { getTestSessions } from '../services/api';

const DashboardContainer = styled.div`
  display: grid;
  gap: 2rem;
`;

const WelcomeSection = styled.section`
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
`;

const Title = styled.h1`
  color: #333;
  margin-bottom: 1rem;
  font-size: 2.5rem;
`;

const Subtitle = styled.p`
  color: #666;
  font-size: 1.2rem;
  margin-bottom: 2rem;
`;

const ActionButton = styled(Link)`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-2px);
  }
`;

const StatsSection = styled.section`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
`;

const StatCard = styled.div`
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const StatIcon = styled.div`
  font-size: 2rem;
  color: ${props => props.color || '#667eea'};
`;

const StatContent = styled.div`
  flex: 1;
`;

const StatNumber = styled.div`
  font-size: 2rem;
  font-weight: bold;
  color: #333;
`;

const StatLabel = styled.div`
  color: #666;
  font-size: 0.9rem;
`;

const RecentTestsSection = styled.section`
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const SectionTitle = styled.h2`
  color: #333;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const TestList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const TestItem = styled(Link)`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;

  &:hover {
    border-color: #667eea;
    transform: translateY(-1px);
  }
`;

const TestInfo = styled.div`
  flex: 1;
`;

const TestName = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
`;

const TestMeta = styled.div`
  color: #666;
  font-size: 0.9rem;
`;

const TestStatus = styled.div`
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

function Dashboard() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    passed: 0,
    failed: 0,
    running: 0
  });

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await getTestSessions();
      setSessions(data.slice(0, 5)); // Show only recent 5
      
      // Calculate stats
      const newStats = data.reduce((acc, session) => {
        acc.total++;
        acc[session.status] = (acc[session.status] || 0) + 1;
        return acc;
      }, { total: 0, passed: 0, failed: 0, running: 0 });
      
      setStats(newStats);
    } catch (error) {
      console.error('Failed to load sessions:', error);
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

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <DashboardContainer>
      <WelcomeSection>
        <Title>Welcome to Automated Web Testing</Title>
        <Subtitle>
          Create and run web tests using natural language commands
        </Subtitle>
        <ActionButton to="/create">
          <FaPlus />
          Create New Test
        </ActionButton>
      </WelcomeSection>

      <StatsSection>
        <StatCard>
          <StatIcon color="#667eea">
            <FaPlay />
          </StatIcon>
          <StatContent>
            <StatNumber>{stats.total}</StatNumber>
            <StatLabel>Total Tests</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color="#4CAF50">
            <FaCheckCircle />
          </StatIcon>
          <StatContent>
            <StatNumber>{stats.passed}</StatNumber>
            <StatLabel>Passed</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color="#f44336">
            <FaTimesCircle />
          </StatIcon>
          <StatContent>
            <StatNumber>{stats.failed}</StatNumber>
            <StatLabel>Failed</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color="#ff9800">
            <FaClock />
          </StatIcon>
          <StatContent>
            <StatNumber>{stats.running}</StatNumber>
            <StatLabel>Running</StatLabel>
          </StatContent>
        </StatCard>
      </StatsSection>

      <RecentTestsSection>
        <SectionTitle>
          <FaClock />
          Recent Tests
        </SectionTitle>
        <TestList>
          {sessions.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
              No tests yet. <Link to="/create">Create your first test</Link>
            </div>
          ) : (
            sessions.map(session => (
              <TestItem key={session.id} to={`/test/${session.id}`}>
                <TestInfo>
                  <TestName>{session.name}</TestName>
                  <TestMeta>
                    {format(new Date(session.created_at), 'MMM dd, yyyy HH:mm')} • 
                    {session.total_steps} steps
                  </TestMeta>
                </TestInfo>
                <TestStatus status={session.status}>
                  {getStatusIcon(session.status)}
                  {session.status}
                </TestStatus>
              </TestItem>
            ))
          )}
        </TestList>
      </RecentTestsSection>
    </DashboardContainer>
  );
}

export default Dashboard;

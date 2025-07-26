import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FaPlus, FaTrash, FaPlay, FaSpinner } from 'react-icons/fa';
import toast from 'react-hot-toast';
import { createTestSession, executeTestSession } from '../services/api';

const CreateTestContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const Card = styled.div`
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  color: #333;
  margin-bottom: 2rem;
  text-align: center;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  min-height: 100px;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const CommandsSection = styled.div`
  margin-bottom: 2rem;
`;

const CommandItem = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  align-items: flex-start;
`;

const CommandInput = styled(TextArea)`
  flex: 1;
  min-height: 60px;
`;

const CommandNumber = styled.div`
  background: #667eea;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9rem;
  margin-top: 0.75rem;
`;

const Button = styled.button`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  
  ${props => {
    switch (props.variant) {
      case 'primary':
        return `
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          &:hover { transform: translateY(-2px); }
        `;
      case 'secondary':
        return `
          background: #f5f5f5;
          color: #333;
          &:hover { background: #e0e0e0; }
        `;
      case 'danger':
        return `
          background: #f44336;
          color: white;
          &:hover { background: #d32f2f; }
        `;
      default:
        return `
          background: #667eea;
          color: white;
          &:hover { background: #5a6fd8; }
        `;
    }
  }}

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
`;

const RemoveButton = styled.button`
  background: #f44336;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-top: 0.75rem;
  transition: background-color 0.2s;

  &:hover {
    background: #d32f2f;
  }
`;

const ExampleCommands = styled.div`
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
`;

const ExampleTitle = styled.h4`
  color: #333;
  margin-bottom: 0.5rem;
`;

const ExampleList = styled.ul`
  color: #666;
  font-size: 0.9rem;
  margin-left: 1rem;
`;

function CreateTest() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    targetUrl: '',
    commands: ['']
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCommandChange = (index, value) => {
    const newCommands = [...formData.commands];
    newCommands[index] = value;
    setFormData(prev => ({
      ...prev,
      commands: newCommands
    }));
  };

  const addCommand = () => {
    setFormData(prev => ({
      ...prev,
      commands: [...prev.commands, '']
    }));
  };

  const removeCommand = (index) => {
    if (formData.commands.length > 1) {
      const newCommands = formData.commands.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        commands: newCommands
      }));
    }
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      toast.error('Test name is required');
      return false;
    }
    if (!formData.targetUrl.trim()) {
      toast.error('Target URL is required');
      return false;
    }
    if (!formData.targetUrl.startsWith('http')) {
      toast.error('Target URL must start with http:// or https://');
      return false;
    }
    if (formData.commands.filter(cmd => cmd.trim()).length === 0) {
      toast.error('At least one command is required');
      return false;
    }
    return true;
  };

  const handleCreateAndRun = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      // Filter out empty commands
      const cleanCommands = formData.commands.filter(cmd => cmd.trim());
      
      const testData = {
        ...formData,
        commands: cleanCommands
      };

      // Create test session
      const session = await createTestSession(testData);
      toast.success('Test created successfully!');

      // Execute the test
      await executeTestSession(session.sessionId);
      toast.success('Test execution started!');

      // Navigate to results page
      navigate(`/test/${session.sessionId}`);
    } catch (error) {
      console.error('Error creating/running test:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <CreateTestContainer>
      <Card>
        <Title>Create New Test</Title>
        
        <FormGroup>
          <Label>Test Name *</Label>
          <Input
            type="text"
            placeholder="e.g., Login Flow Test"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
          />
        </FormGroup>

        <FormGroup>
          <Label>Description</Label>
          <TextArea
            placeholder="Describe what this test does..."
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
          />
        </FormGroup>

        <FormGroup>
          <Label>Target URL *</Label>
          <Input
            type="url"
            placeholder="https://example.com"
            value={formData.targetUrl}
            onChange={(e) => handleInputChange('targetUrl', e.target.value)}
          />
        </FormGroup>

        <CommandsSection>
          <Label>Test Commands *</Label>
          
          <ExampleCommands>
            <ExampleTitle>Example Commands:</ExampleTitle>
            <ExampleList>
              <li>Navigate to https://example.com</li>
              <li>Click the "Login" button</li>
              <li>Type "user@example.com" in the email field</li>
              <li>Type "password123" in the password field</li>
              <li>Click the "Sign In" button</li>
              <li>Verify the page contains "Welcome"</li>
            </ExampleList>
          </ExampleCommands>

          {formData.commands.map((command, index) => (
            <CommandItem key={index}>
              <CommandNumber>{index + 1}</CommandNumber>
              <CommandInput
                placeholder="Enter a natural language command..."
                value={command}
                onChange={(e) => handleCommandChange(index, e.target.value)}
              />
              {formData.commands.length > 1 && (
                <RemoveButton onClick={() => removeCommand(index)}>
                  <FaTrash />
                </RemoveButton>
              )}
            </CommandItem>
          ))}

          <Button variant="secondary" onClick={addCommand}>
            <FaPlus />
            Add Command
          </Button>
        </CommandsSection>

        <ButtonGroup>
          <Button 
            variant="primary" 
            onClick={handleCreateAndRun}
            disabled={loading}
          >
            {loading ? <FaSpinner className="fa-spin" /> : <FaPlay />}
            {loading ? 'Creating & Running...' : 'Create & Run Test'}
          </Button>
        </ButtonGroup>
      </Card>
    </CreateTestContainer>
  );
}

export default CreateTest;

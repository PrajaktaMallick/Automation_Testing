import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { FaRobot, FaPlus, FaHistory, FaHome } from 'react-icons/fa';

const HeaderContainer = styled.header`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const HeaderContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.5rem;
  font-weight: bold;
`;

const Nav = styled.nav`
  display: flex;
  gap: 1rem;
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: background-color 0.2s;
  background-color: ${props => props.$active ? 'rgba(255, 255, 255, 0.2)' : 'transparent'};

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
`;

function Header() {
  const location = useLocation();

  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo>
          <FaRobot />
          Automated Web Testing
        </Logo>
        <Nav>
          <NavLink to="/" $active={location.pathname === '/'}>
            <FaHome />
            Dashboard
          </NavLink>
          <NavLink to="/create" $active={location.pathname === '/create'}>
            <FaPlus />
            Create Test
          </NavLink>
          <NavLink to="/history" $active={location.pathname === '/history'}>
            <FaHistory />
            History
          </NavLink>
        </Nav>
      </HeaderContent>
    </HeaderContainer>
  );
}

export default Header;
